"""A utility class that handles database operations related to covidcast.

See src/ddl/covidcast.sql for an explanation of each field.
"""

# third party
import json
import mysql.connector
import numpy as np
from math import ceil, sqrt

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

    # TODO: this heavily copypastas src/ddl/covidcast.sql -- theres got to be a better way
    create_tmp_table_sql = f'''
      CREATE TABLE `{tmp_table_name}` (
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
    drop_tmp_table_sql = f'DROP TABLE {tmp_table_name}'

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


    # TODO: consider handling cc_rows as a generator instead of a list
    self._cursor.execute(create_tmp_table_sql)
    meta_cache = self.retrieve_covidcast_meta_cache()
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

        # use the temp table to compute meta just for new data, 
        # then merge with the global meta
        meta_update = self.compute_covidcast_meta(table_name=tmp_table_name)
        meta_cache = Database.merge_cache_dicts(meta_cache, meta_update)

        self._cursor.execute(insert_or_update_sql)
        self._cursor.execute(zero_is_latest_issue_sql)
        self._cursor.execute(set_is_latest_issue_sql)
        self._cursor.execute(truncate_tmp_table_sql)
        self.update_covidcast_meta_cache_from_dict(meta_cache)

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

  def compute_covidcast_meta(self, table_name='covidcast'):
    """Compute and return metadata on all non-WIP COVIDcast signals."""

    meta = []

    signal_list = []
    sql = f'SELECT `source`, `signal` FROM `{table_name}` GROUP BY `source`, `signal` ORDER BY `source` ASC, `signal` ASC;'
    self._cursor.execute(sql)
    for source, signal in list(self._cursor): # self._cursor is a generator; this lets us use the cursor for subsequent queries inside the loop
      sql = f"SELECT `is_wip` FROM `{table_name}` WHERE `source`=%s AND `signal`=%s LIMIT 1"
      self._cursor.execute(sql, (source, signal))
      is_wip = int(self._cursor.fetchone()[0]) # casting to int as it comes out as a '0' or '1' bytearray; bool('0')==True :(
      if not is_wip:
        signal_list.append((source, signal))

    for source, signal in signal_list:

      sql = f'''
      SELECT
        `source` AS `data_source`,
        `signal`,
        `time_type`,
        `geo_type`,
        MIN(`time_value`) AS `min_time`,
        MAX(`time_value`) AS `max_time`,
        COUNT(DISTINCT `geo_value`) AS `num_locations`,
        COUNT(`value`) AS `num_points`,
        MIN(`value`) AS `min_value`,
        MAX(`value`) AS `max_value`,
        ROUND(AVG(`value`),7) AS `mean_value`,
        ROUND(STD(`value`),7) AS `stdev_value`,
        MAX(`value_updated_timestamp`) AS `last_update`,
        MAX(`issue`) as `max_issue`,
        MIN(`lag`) as `min_lag`,
        MAX(`lag`) as `max_lag`
      FROM
        `{table_name}`
      WHERE
        `source` = %s AND
        `signal` = %s AND
        is_latest_issue = 1
      GROUP BY
        `time_type`,
        `geo_type`
      ORDER BY
        `time_type` ASC,
        `geo_type` ASC
      '''
      self._cursor.execute(sql, (source, signal))
      meta.extend(list(dict(zip(self._cursor.column_names,x)) for x in self._cursor))

    return meta
  
  def update_covidcast_meta_cache(self, metadata, table_name='covidcast_meta_cache'): # TODO: remove arg
    """Updates the `covidcast_meta_cache` table."""

    sql = f'''
      UPDATE
        `{table_name}`
      SET
        `timestamp` = UNIX_TIMESTAMP(NOW()),
        `epidata` = %s
    '''
    epidata_json = json.dumps(metadata)

    self._cursor.execute(sql, (epidata_json,))

  def retrieve_covidcast_meta_cache(self, table_name='covidcast_meta_cache_test'): # TODO: remove arg
    """Useful for viewing cache entries (was used in debugging)"""

    sql = f'''
      SELECT `epidata`
      FROM `{table_name}` -- TODO: remove '_test' after successfully testing incremental cache updates
      ORDER BY `timestamp` DESC
      LIMIT 1;
    '''
    self._cursor.execute(sql)
    cache_json = self._cursor.fetchone()[0]
    cache = json.loads(cache_json)
    cache_hash = {}
    for entry in cache:
      cache_hash[(entry['data_source'], entry['signal'], entry['time_type'], entry['geo_type'])] = entry
    if not len(cache) and table_name=='covidcast_meta_cache_test': # TODO: remove line
      print("test cache empty -- falling back to regular cache ; this should happen ONLY ONCE (after regular cache populated)") # TODO: remove line
      return self.retrieve_covidcast_meta_cache(table_name='covidcast_meta_cache') # TODO: remove line
    return cache_hash

  def update_covidcast_meta_cache_from_dict(self, cache_hash):
    """Updates the `covidcast_meta_cache` table from the dict version of the cache, ordered by key"""

    cache_list = [cache_hash[k] for k in sorted(cache_hash)]
    self.update_covidcast_meta_cache(cache_list, table_name='covidcast_meta_cache_test') # TODO: remove arg

  @staticmethod
  def merge_cache_dicts(base_cache, cache_update):
    """merges two covidcast metadata caches (in dict form), modifying (and returning) the first"""

    for data_id in cache_update:
      if data_id not in base_cache:
        base_cache[data_id] = cache_update[data_id]
        continue

      mainstats = base_cache[data_id].copy() # copy this entry so we can update the whole thing in one assignment
      updtstats = cache_update[data_id]

      # combined stdev formula shamelessly stolen from:
      # https://math.stackexchange.com/questions/2971315/how-do-i-combine-standard-deviations-of-two-groups
      sx, xbar, n = [mainstats[i] for i in ('stdev_value', 'mean_value', 'num_points')]
      sy, ybar, m = [updtstats[i] for i in ('stdev_value', 'mean_value', 'num_points')]
      comb_mean = ( xbar*n + ybar*m ) / (n+m)
      comb_sd = sqrt(
        ( (n-1)*sx*sx + (m-1)*sy*sy ) / (n+m-1)
        +
        n*m*(xbar-ybar)**2 / ((n+m)*(n+m-1))
      )

      mainstats['num_points'] = m + n
      mainstats['stdev_value'] = comb_sd
      mainstats['mean_value'] = comb_mean
      for stat in ('max_lag', 'max_value', 'max_time', 'max_issue', 'last_update', 'num_locations'):
        mainstats[stat] = max(mainstats[stat], updtstats[stat])
      for stat in ('min_lag', 'min_value', 'min_time'):
        mainstats[stat] = min(mainstats[stat], updtstats[stat])

      base_cache[data_id] = mainstats # write copy back to base_cache

    return base_cache
