"""A utility class that handles database operations related to covidcast.

See src/ddl/covidcast.sql for an explanation of each field.
"""

# third party
import mysql.connector
import numpy as np

# first party
import delphi.operations.secrets as secrets


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

  def insert_or_update(
      self,
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
      value,
      stderr,
      sample_size,
      issue,
      lag):
    """
    Insert a new row, or update an existing row, in the `covidcast` table.

    This has the intentional side effect of updating the primary timestamp.
    """

    sql = '''
      INSERT INTO `covidcast` VALUES
        (0, %s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(NOW()), %s, %s, %s, 0, NULL, %s, %s)
      ON DUPLICATE KEY UPDATE
        `timestamp1` = VALUES(`timestamp1`),
        `value` = VALUES(`value`),
        `stderr` = VALUES(`stderr`),
        `sample_size` = VALUES(`sample_size`)
    '''

    args = (
      source,
      signal,
      time_type,
      geo_type,
      time_value,
      geo_value,
      value,
      stderr,
      sample_size,
      issue,
      lag
    )

    self._cursor.execute(sql, args)

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
        `timestamp2` = UNIX_TIMESTAMP(NOW()),
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

  def get_all_record_values_of_timeseries_with_potentially_stale_direction(self, temporary_table=None):
    """
    [TODO]
    """

    create_tmp_table_sql = f'''
    CREATE TEMPORARY TABLE `{temporary_table}` (
      `id` int(11) NOT NULL,
      `source` varchar(32),
      `signal` varchar(32),
      `time_type` varchar(12),
      `geo_type` varchar(12),
      `geo_value` varchar(12),
      `time_value` int(11),
      `timestamp1` int(11),
      `value` double,
      `timestamp2` int(11),
      `direction` int(11),
      PRIMARY KEY(`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''

    latest_issues_sql = f'''
    SELECT 
      `id`,
      `source`,
      `signal`,
      `time_type`,
      `geo_type`,
      `geo_value`,
      `time_value`,
      `timestamp1`,
      `value`,
      `timestamp2`,
      `direction`
    FROM
    (
      SELECT
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`,
        `time_value`,
        MAX(`issue`) AS `issue`
      FROM `covidcast`
      WHERE
        `time_type` = 'day'
      GROUP BY
        `source`,
        `signal`,
        `time_type`,
        `geo_type`,
        `geo_value`,
        `time_value`
    ) b
    LEFT JOIN `covidcast` a
    USING (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`)
    '''

    cte_definition = f'''
    WITH `latest_issues` AS
    (
      {latest_issues_sql}
    )
    '''

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
        MAX(`timestamp1`) > MIN(`timestamp2`)
    '''

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
      `timestamp1`,
      `value`,
      `timestamp2`,
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
    """
    [TODO]
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
    """
    [TODO]
    """
    sql = f'DROP TEMPORARY TABLE `{tmp_table_name}`;'
    self._cursor.execute(sql)

  def update_timestamp2_from_temporary_table(self, tmp_table_name):
    """
    [TODO]
    """
    sql = f'''
      UPDATE
        `covidcast`
      RIGHT JOIN
        `{tmp_table_name}` t
      ON
        `covidcast`.id=t.id
      SET
        `covidcast`.timestamp2=UNIX_TIMESTAMP(NOW())
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
        MAX(`timestamp1`) AS `max_timestamp1`,
        MIN(`timestamp2`) AS `min_timestamp2`,
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
        MAX(`timestamp1`) > MIN(`timestamp2`)
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
        `timestamp1`,
        `timestamp2`
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

  def update_timeseries_timestamp2(
      self, source, signal, time_type, geo_type, geo_value):
    """Update the `timestamp2` column for an entire time-series.

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
        `timestamp2` = UNIX_TIMESTAMP(NOW())
      WHERE
        `source` = %s AND
        `signal` = %s AND
        `time_type` = %s AND
        `geo_type` = %s AND
        `geo_value` = %s
    '''

    args = (source, signal, time_type, geo_type, geo_value)
    self._cursor.execute(sql, args)

  def update_covidcast_meta_cache(self, epidata_json):
    """Updates the `covidcast_meta_cache` table."""

    sql = '''
      UPDATE
        `covidcast_meta_cache`
      SET
        `timestamp` = UNIX_TIMESTAMP(NOW()),
        `epidata` = %s
    '''

    self._cursor.execute(sql, (epidata_json,))
