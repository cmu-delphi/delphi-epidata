"""A utility class that handles database operations related to covidcast.

See src/ddl/covidcast.sql for an explanation of each field.
"""

# third party
import json
import mysql.connector
import numpy as np
from math import ceil

# first party
import delphi.operations.secrets as secrets



class CovidcastRow():
  """A container for all the values of a single covidcast row."""

  @staticmethod
  def fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag, is_wip):
    if row_value is None: return None
    return CovidcastRow(source, signal, time_type, geo_type, time_value,
                        row_value.geo_value,
                        row_value.value,
                        row_value.stderr,
                        row_value.sample_size,
                        issue, lag, is_wip)

  @staticmethod
  def fromCsvRows(row_values, source, signal, time_type, geo_type, time_value, issue, lag, is_wip):
    # NOTE: returns a generator, as row_values is expected to be a generator
    return (CovidcastRow.fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag, is_wip)
            for row_value in row_values)

  def __init__(self, source, signal, time_type, geo_type, time_value, geo_value, value, stderr, sample_size, issue, lag, is_wip):
    self.id = None
    self.source = source
    self.signal = signal
    self.time_type = time_type
    self.geo_type = geo_type
    self.time_value = time_value
    self.geo_value = geo_value      # from CSV row
    self.value = value              # ...
    self.stderr = stderr            # ...
    self.sample_size = sample_size  # from CSV row
    self.direction_updated_timestamp = 0
    self.direction = None
    self.issue = issue
    self.lag = lag
    self.is_wip = is_wip


class Database:
  """A collection of covidcast database operations."""

  DATABASE_NAME = 'epidata'

  def connect(self, connector_impl=mysql.connector):
    """Establish a connection to the database."""

    u, p = secrets.db.epi
    self._connection = connector_impl.connect(
        host=secrets.db.host,
        user=u,
        password=p,
        database=Database.DATABASE_NAME)
    self._cursor = self._connection.cursor()

  def commit(self):
    self._connection.commit()

  def rollback(self):
    self._connection.rollback()

  def disconnect(self, commit):
    """Close the database connection.

    commit: if true, commit changes, otherwise rollback
    """

    self._cursor.close()
    if commit:
      self._connection.commit()
    self._connection.close()

  def count_all_rows(self):
    """Return the total number of rows in table `covidcast`."""

    self._cursor.execute('SELECT count(1) FROM `covidcast`')

    for (num,) in self._cursor:
      return num

  def insert_or_update_bulk(self, cc_rows):
    return self.insert_or_update_batch(cc_rows)

  def insert_or_update_batch(self, cc_rows, batch_size=2**20, commit_partial=False):
    """
    Insert new rows (or update existing) in the `covidcast` table.

    This has the intentional side effect of updating the primary timestamp.


    """

    tmp_table_name = 'tmp_insert_update_table'

    create_tmp_table_sql = f'''
      CREATE TEMPORARY TABLE `{tmp_table_name}` (
        `source` varchar(32) NOT NULL,
        `signal` varchar(64) NOT NULL,
        `time_type` varchar(12) NOT NULL,
        `geo_type` varchar(12) NOT NULL,
        `time_value` int(11) NOT NULL,
        `geo_value` varchar(12) NOT NULL,
        `value_updated_timestamp` int(11) NOT NULL,
        `value` double NOT NULL,
        `stderr` double,
        `sample_size` double,
        `direction_updated_timestamp` int(11) NOT NULL,
        `direction` int(11),
        `issue` int(11) NOT NULL,
        `lag` int(11) NOT NULL,
        `is_latest_issue` BINARY(1) NOT NULL,
        `is_wip` BINARY(1) NOT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''

    truncate_tmp_table_sql = f'TRUNCATE TABLE {tmp_table_name};'
    drop_tmp_table_sql = f'DROP TEMPORARY TABLE {tmp_table_name}'

    insert_into_tmp_sql = f'''
      INSERT INTO `{tmp_table_name}`
        (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`,
        `value_updated_timestamp`, `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, `direction`,
        `issue`, `lag`, `is_latest_issue`, `is_wip`)
      VALUES
        (%s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(NOW()), %s, %s, %s, 0, NULL, %s, %s, 0, %s)
    '''

    insert_or_update_sql = f'''
      INSERT INTO `covidcast`
        (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`,
        `value_updated_timestamp`, `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, `direction`,
        `issue`, `lag`, `is_latest_issue`, `is_wip`)
      SELECT * FROM `{tmp_table_name}`
      ON DUPLICATE KEY UPDATE
        `value_updated_timestamp` = VALUES(`value_updated_timestamp`),
        `value` = VALUES(`value`),
        `stderr` = VALUES(`stderr`),
        `sample_size` = VALUES(`sample_size`)
    '''
    zero_is_latest_issue_sql = f'''
      UPDATE
      (
        SELECT DISTINCT `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`
        FROM `{tmp_table_name}`
      ) AS TMP
      LEFT JOIN `covidcast`
      USING (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`)
      SET `is_latest_issue`=0
    '''
    set_is_latest_issue_sql = f'''
      UPDATE
      (
        SELECT `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`, MAX(`issue`) AS `issue`
        FROM
        (
          SELECT DISTINCT `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`
          FROM `{tmp_table_name}`
        ) AS TMP
        LEFT JOIN `covidcast`
        USING (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`)
        GROUP BY `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`
      ) AS TMP
      LEFT JOIN `covidcast`
      USING (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`, `issue`)
      SET `is_latest_issue`=1
    '''

    # TODO: ^ do we want to reset `direction_updated_timestamp` and `direction` in the duplicate key case?

    # TODO: consider handling cc_rows as a generator instead of a list
    self._cursor.execute(create_tmp_table_sql)

    try:

      num_rows = len(cc_rows)
      total = 0
      if not batch_size:
        batch_size = num_rows
      num_batches = ceil(num_rows/batch_size)
      for batch_num in range(num_batches):
        start = batch_num * batch_size
        end = min(num_rows, start + batch_size)
        length = end - start

        args = [(
          row.source,
          row.signal,
          row.time_type,
          row.geo_type,
          row.time_value,
          row.geo_value,
          row.value,
          row.stderr,
          row.sample_size,
          row.issue,
          row.lag,
          row.is_wip
        ) for row in cc_rows[start:end]]


        result = self._cursor.executemany(insert_into_tmp_sql, args)
        self._cursor.execute(insert_or_update_sql)
        self._cursor.execute(zero_is_latest_issue_sql)
        self._cursor.execute(set_is_latest_issue_sql)
        self._cursor.execute(truncate_tmp_table_sql)

        if result is None:
          # the SQL connector does not support returning number of rows affected
          total = None
        else:
          total += result
        if commit_partial:
          self._connection.commit()
    except Exception as e:
      raise e
    finally:
      self._cursor.execute(drop_tmp_table_sql)
      return total

  def get_data_stdev_across_locations(self, max_day):
    """
    Return the standard deviation of daily data over all locations, for all
    (source, signal, geo_type) tuples.

    `max_day`: base the standard deviation on data up to, and including, but
      not after, this day (e.g. for a stable result over time)
    """

    sql = '''
      SELECT
        `source`,
        `signal`,
        `geo_type`,
        COALESCE(STD(`value`), 0) AS `aggregate_stdev`
      FROM
        `covidcast`
      WHERE
        `time_type` = 'day' AND
        `time_value` <= %s
      GROUP BY
        `source`,
        `signal`,
        `geo_type`
    '''

    args = (max_day,)
    self._cursor.execute(sql, args)
    return list(self._cursor)

  def update_direction(
      self,
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
      direction):
    """
    Update the `direction` column for a given row in the `covidcast` table.

    This has the intentional side effect of updating the secondary timestamp.
    """

    sql = '''
      UPDATE
        `covidcast`
      SET
        `direction_updated_timestamp` = UNIX_TIMESTAMP(NOW()),
        `direction` = %s
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = %s AND
        `geo_type` = %s AND
        `time_value` = %s AND
        `geo_value` = %s
    '''

    args = (
      direction,
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
    )

    self._cursor.execute(sql, args)

  def get_all_record_values_of_timeseries_with_potentially_stale_direction(self, temporary_table=None,
                                                                           partition_condition='(TRUE)'):
    """Return the rows of all daily time-series with potentially stale directions,
    only rows corresponding to the most recent issue for each time_value is returned.

    `temporary_table`: if provided, a temporary table with the name `temporary_table`
                       is created and the result is also stored in that table.
    `partition_condition`: a condition that defines the partition to be processed.
    """

    create_tmp_table_sql = f'''
    CREATE TEMPORARY TABLE `{temporary_table}` (
      `id` int(11) NOT NULL,
      `source` varchar(32),
      `signal` varchar(64),
      `time_type` varchar(12),
      `geo_type` varchar(12),
      `geo_value` varchar(12),
      `time_value` int(11),
      `value_updated_timestamp` int(11),
      `value` double,
      `direction_updated_timestamp` int(11),
      `direction` int(11),
      PRIMARY KEY(`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''

    # A query that selects all rows from `covidcast` that have latest issue-date
    # for any (time-series-key, time_value) with time_type='day'.
    latest_issues_sql = f'''
    SELECT
      `id`,
      `source`,
      `signal`,
      `time_type`,
      `geo_type`,
      `geo_value`,
      `time_value`,
      `value_updated_timestamp`,
      `value`,
      `direction_updated_timestamp`,
      `direction`
    FROM `covidcast`
    WHERE `is_latest_issue` = 1 AND
        `time_type` = 'day' AND
        {partition_condition}
    '''

    cte_definition = f'''
    WITH `latest_issues` AS
    (
      {latest_issues_sql}
    )
    '''

    # A query that selects the keys of time-series with potentially stale directions.
    stale_ts_key_sql = f'''
      SELECT
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`
      FROM
        `latest_issues` AS t1
      GROUP BY
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`
      HAVING
        MAX(`value_updated_timestamp`) > MIN(`direction_updated_timestamp`)
    '''

    # A query that selects rows of the time-series selected by stale_ts_key_sql query.
    stale_ts_records_with_latest_issues_sql = f'''
    {cte_definition}
    SELECT
      `id`,
      `source`,
      `signal`,
      `time_type`,
      `geo_type`,
      `geo_value`,
      `time_value`,
      `value_updated_timestamp`,
      `value`,
      `direction_updated_timestamp`,
      `direction`
    FROM ({stale_ts_key_sql}) AS t2
    LEFT JOIN `latest_issues` AS t3
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`)
    '''

    if temporary_table is None:
      self._cursor.execute(stale_ts_records_with_latest_issues_sql)
      return list(self._cursor)

    self._cursor.execute(create_tmp_table_sql)
    final_sql = f'''
      INSERT INTO `{temporary_table}`
      SELECT *
      FROM ({stale_ts_records_with_latest_issues_sql}) AS c;
      '''
    self._cursor.execute(final_sql)
    self._cursor.execute(f"SELECT * FROM `{temporary_table}`;")
    return list(self._cursor)

  def batched_update_direction(self, new_direction_value, id_list, batch_size=1024):
    """Updates the `direction` column of rows with ids in `id_list` to `new_direction_value`,
    the update query is executed in batches of `batch_size` rows at a time.

    `new_direction_value`: the new value to be stored in `direction` column.
    `id_list`: a list of ids of rows that will change to `new_direction_value`.
    `batch_size`: batch size of the update query.
    """
    if np.isnan(new_direction_value):
      new_direction_value = 'NULL'
    for start in range(0, len(id_list), batch_size):
      sql = f'''
        UPDATE
          `covidcast`
        SET
          `covidcast`.direction={str(new_direction_value)}
        WHERE
          `covidcast`.id IN ({','.join([str(x) for x in id_list[start:start+batch_size]])})
        '''
      self._cursor.execute(sql)

  def drop_temporary_table(self, tmp_table_name):
    """Drops temporary table from the Database.

    `tmp_table_name`: name of temporary table to be dropped.
    """
    sql = f'DROP TEMPORARY TABLE `{tmp_table_name}`;'
    self._cursor.execute(sql)

  def update_direction_updated_timestamp_from_temporary_table(self, tmp_table_name):
    """Updates the `direction_updated_timestamp` column of `covidcast` table for all the rows with id value in `tmp_table_name`.

    `tmp_table_name`: name of the temporary table.
    """
    sql = f'''
      UPDATE
        `covidcast`
      RIGHT JOIN
        `{tmp_table_name}` t
      ON
        `covidcast`.id=t.id
      SET
        `covidcast`.direction_updated_timestamp=UNIX_TIMESTAMP(NOW())
      '''
    self._cursor.execute(sql)


  def get_keys_with_potentially_stale_direction(self):
    """
    Return the `covidcast` table composite key for each unique time-series for
    which all `direction` values can not be guaranteed to be fresh.

    Note that this is limited to `time_type` of 'day' as direction is not yet
    defined at other time scales.
    """

    sql = '''
      SELECT
        `source`,
        `signal`,
        `geo_type`,
        `geo_value`,
        MAX(`value_updated_timestamp`) AS `max_value_updated_timestamp`,
        MIN(`direction_updated_timestamp`) AS `min_direction_updated_timestamp`,
        MIN(`time_value`) AS `min_day`,
        MAX(`time_value`) AS `max_day`,
        COUNT(1) AS `series_length`
      FROM
        `covidcast`
      WHERE
        `time_type` = 'day'
      GROUP BY
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`
      HAVING
        MAX(`value_updated_timestamp`) > MIN(`direction_updated_timestamp`)
    '''

    self._cursor.execute(sql)
    return list(self._cursor)

  def get_daily_timeseries_for_direction_update(
      self, source, signal, geo_type, geo_value, min_day, max_day):
    """Return the indicated `covidcast` time-series, including timestamps."""

    sql = '''
      SELECT
        DATEDIFF(`time_value`, %s) AS `offset`,
        `time_value` AS `day`,
        `value`,
        `value_updated_timestamp`,
        `direction_updated_timestamp`
      FROM
        `covidcast`
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = 'day' AND
        `geo_type` = %s AND
        `geo_value` = %s AND
        `time_value` BETWEEN %s AND %s
      ORDER BY
        `time_value` ASC
    '''

    args = (min_day, source, signal, geo_type, geo_value, min_day, max_day)
    self._cursor.execute(sql, args)
    return list(self._cursor)

  def update_timeseries_direction_updated_timestamp(
      self, source, signal, time_type, geo_type, geo_value):
    """Update the `direction_updated_timestamp` column for an entire time-series.

    For daily time-series, this implies that all `direction` values in the
    specified time-series are confirmed fresh as of the current time. Even if
    they happened to be computed at an earlier time, this update indicates that
    those values are still fresh.

    This has no meaningful implication for non-daily time-series.
    """

    sql = '''
      UPDATE
        `covidcast`
      SET
        `direction_updated_timestamp` = UNIX_TIMESTAMP(NOW())
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = %s AND
        `geo_type` = %s AND
        `geo_value` = %s
    '''

    args = (source, signal, time_type, geo_type, geo_value)
    self._cursor.execute(sql, args)


  def get_covidcast_meta(self):
    """Compute and return metadata on all non-WIP COVIDcast signals."""

    meta = []

    sql = 'SELECT `source`, `signal` FROM covidcast WHERE NOT `is_wip` GROUP BY `source`, `signal` ORDER BY `source` ASC, `signal` ASC;'
    self._cursor.execute(sql)
    signals = [ss for ss in self._cursor] #NOTE: this obfuscation protects the integrity of the cursor; using the cursor as a generator will cause contention w/ subsequent queries
    for source, signal in signals:

      # calculate the min issues per combination
      sql = '''
      SELECT
        `time_type`,
        `geo_type`,
        MIN(`issue`) as `min_issue`
      FROM
        `covidcast`
      WHERE
        `source` = %s AND
        `signal` = %s
      GROUP BY
        `time_type`,
        `geo_type`
      '''
      self._cursor.execute(sql, (source, signal))
      min_issue_lookup = {f'{x[0]}:{x[1]}': x[2] for x in self._cursor}

      # calculate statistics for the latest issue entries
      sql = '''
      SELECT
        `source` AS `data_source`,
        `signal`,
        `time_type`,
        `geo_type`,
        MIN(`time_value`) AS `min_time`,
        MAX(`time_value`) AS `max_time`,
        COUNT(DISTINCT `geo_value`) AS `num_locations`,
        MIN(`value`) AS `min_value`,
        MAX(`value`) AS `max_value`,
        ROUND(AVG(`value`),7) AS `mean_value`,
        ROUND(STD(`value`),7) AS `stdev_value`,
        MAX(`value_updated_timestamp`) AS `last_update`,
        MIN(`issue`) as `min_issue`,
        MAX(`issue`) as `max_issue`,
        MIN(`lag`) as `min_lag`,
        MAX(`lag`) as `max_lag`
      FROM
        `covidcast`
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `is_latest_issue` is TRUE
      GROUP BY
        `time_type`,
        `geo_type`
      ORDER BY
        `time_type` ASC,
        `geo_type` ASC
      '''
      self._cursor.execute(sql, (source, signal))

      for x in self._cursor:
        entry = dict(zip(self._cursor.column_names, x))
        # merge in the min issue
        key = f"{entry['time_type']}:{entry['geo_type']}"
        entry['min_issue'] = min_issue_lookup.get(key, entry['max_issue'])
        meta.append(entry)
    return meta

  def update_covidcast_meta_cache(self, metadata):
    """Updates the `covidcast_meta_cache` table."""

    sql = '''
      UPDATE
        `covidcast_meta_cache`
      SET
        `timestamp` = UNIX_TIMESTAMP(NOW()),
        `epidata` = %s
    '''
    epidata_json = json.dumps(metadata)

    self._cursor.execute(sql, (epidata_json,))

  def retrieve_covidcast_meta_cache(self):
    """Useful for viewing cache entries (was used in debugging)"""

    sql = '''
      SELECT `epidata`
      FROM `covidcast_meta_cache`
      ORDER BY `timestamp` DESC
      LIMIT 1;
    '''
    self._cursor.execute(sql)
    cache_json = self._cursor.fetchone()[0]
    cache = json.loads(cache_json)
    cache_hash = {}
    for entry in cache:
      cache_hash[(entry['data_source'], entry['signal'], entry['time_type'], entry['geo_type'])] = entry
    return cache_hash
