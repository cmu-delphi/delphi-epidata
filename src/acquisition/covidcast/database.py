"""A utility class that handles database operations related to covidcast.

See src/ddl/covidcast.sql for an explanation of each field.
"""

# third party
import json
import mysql.connector
import numpy as np
from math import ceil

from queue import Queue, Empty
import threading
from multiprocessing import cpu_count

# first party
import delphi.operations.secrets as secrets

from delphi.epidata.acquisition.covidcast.logger import get_structured_logger

class CovidcastRow():
  """A container for all the values of a single covidcast row."""

  @staticmethod
  def fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag):
    if row_value is None: return None
    return CovidcastRow(source, signal, time_type, geo_type, time_value,
                        row_value.geo_value,
                        row_value.value,
                        row_value.stderr,
                        row_value.sample_size,
                        row_value.missing_value,
                        row_value.missing_stderr,
                        row_value.missing_sample_size,
                        issue, lag)

  @staticmethod
  def fromCsvRows(row_values, source, signal, time_type, geo_type, time_value, issue, lag):
    # NOTE: returns a generator, as row_values is expected to be a generator
    return (CovidcastRow.fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag)
            for row_value in row_values)

  def __init__(self, source, signal, time_type, geo_type, time_value, geo_value, value, stderr, 
               sample_size, missing_value, missing_stderr, missing_sample_size, issue, lag):
    self.id = None
    self.source = source
    self.signal = signal
    self.time_type = time_type
    self.geo_type = geo_type
    self.time_value = time_value
    self.geo_value = geo_value      # from CSV row
    self.value = value              # ...
    self.stderr = stderr            # ...
    self.sample_size = sample_size  # ...
    self.missing_value = missing_value # ...
    self.missing_stderr = missing_stderr # ...
    self.missing_sample_size = missing_sample_size # from CSV row
    self.direction_updated_timestamp = 0
    self.direction = None
    self.issue = issue
    self.lag = lag


class Database:
  """A collection of covidcast database operations."""

  DATABASE_NAME = 'covid'

  latest_table = "signal_latest_v" # technically VIEW and not a TABLE, but...
  history_table = "signal_history_v" # ...also a VIEW
  load_table = "signal_load"

  def connect(self, connector_impl=mysql.connector):
    """Establish a connection to the database."""
    u, p = secrets.db.epi
    self._connector_impl = connector_impl
    self._connection = self._connector_impl.connect(
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

  def count_all_rows(self, tablename=None):
    """Return the total number of rows in table `covidcast`."""

    if tablename is None:
      tablename = self.history_table

    self._cursor.execute(f'SELECT count(1) FROM `{tablename}`')

    for (num,) in self._cursor:
      return num

  def count_all_history_rows(self):
    return self.count_all_rows(self.history_table)

  def count_all_latest_rows(self):
    return self.count_all_rows(self.latest_table)

  def insert_or_update_bulk(self, cc_rows):
    return self.insert_or_update_batch(cc_rows)

  def insert_or_update_batch(self, cc_rows, batch_size=2**20, commit_partial=False):
    """
    Insert new rows (or update existing) into the load table.
    Data inserted this way will not be available to clients until the appropriate steps from src/dbjobs/ have run
    """

    # NOTE: `value_update_timestamp` is hardcoded to "NOW" (which is appropriate) and 
    #       `is_latest_issue` is hardcoded to 1 (which is temporary and addressed later in this method)
    insert_into_loader_sql = f'''
      INSERT INTO `{self.load_table}`
        (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`,
        `value_updated_timestamp`, `value`, `stderr`, `sample_size`, `issue`, `lag`, 
        `is_latest_issue`, `missing_value`, `missing_stderr`, `missing_sample_size`)
      VALUES
        (%s, %s, %s, %s, %s, %s, 
        UNIX_TIMESTAMP(NOW()), %s, %s, %s, %s, %s, 
        1, %s, %s, %s)
    '''

    # all load table entries are already marked "is_latest_issue".
    # if an entry in the load table is NOT in the latest table, it is clearly now the latest value for that key (so we do nothing (thanks to INNER join)).
    # if an entry *IS* in both load and latest tables, but latest table issue is newer, unmark is_latest_issue in load.
    fix_is_latest_issue_sql = f'''
        UPDATE 
            `{self.load_table}` JOIN `{self.latest_table}` 
                USING (`source`, `signal`, `geo_type`, `geo_value`, `time_type`, `time_value`) 
            SET `{self.load_table}`.`is_latest_issue`=0 
            WHERE `{self.load_table}`.`issue` < `{self.latest_table}`.`issue`
    '''

    if 0 != self.count_all_rows(self.load_table):
      # TODO: determine if this should be fatal?!
      logger = get_structured_logger("insert_or_update_batch")
      logger.warn("Non-zero count in the load table!!!  This indicates scheduling of acqusition and dbjobs may be out of sync.")

    # TODO: consider handling cc_rows as a generator instead of a list

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
          row.missing_value,
          row.missing_stderr,
          row.missing_sample_size
        ) for row in cc_rows[start:end]]


        self._cursor.executemany(insert_into_loader_sql, args)
        modified_row_count = self._cursor.rowcount
        self._cursor.execute(fix_is_latest_issue_sql)

        if modified_row_count is None or modified_row_count == -1:
          # the SQL connector does not support returning number of rows affected (see PEP 249)
          total = None
        else:
          total += modified_row_count
        if commit_partial:
          self._connection.commit()
    except Exception as e:
      # TODO: rollback???  truncate table???  something???
      raise e
    return total

  def delete_batch(self, cc_deletions):
    """
    Remove rows specified by a csv file or list of tuples.

    If cc_deletions is a filename, the file should include a header row and use the following field order:
    - geo_id
    - value (ignored)
    - stderr (ignored)
    - sample_size (ignored)
    - issue (YYYYMMDD format)
    - time_value (YYYYMMDD format)
    - geo_type
    - signal
    - source

    If cc_deletions is a list of tuples, the tuples should use the following field order (=same as above, plus time_type):
    - geo_id
    - value (ignored)
    - stderr (ignored)
    - sample_size (ignored)
    - issue (YYYYMMDD format)
    - time_value (YYYYMMDD format)
    - geo_type
    - signal
    - source
    - time_type
    """
    tmp_table_name = "tmp_delete_table"
    create_tmp_table_sql = f'''
CREATE OR REPLACE TABLE {tmp_table_name} LIKE covidcast;
'''

    amend_tmp_table_sql = f'''
ALTER TABLE {tmp_table_name} ADD COLUMN covidcast_id bigint unsigned;
'''

    load_tmp_table_infile_sql = f'''
LOAD DATA INFILE "{cc_deletions}"
INTO TABLE {tmp_table_name}
FIELDS TERMINATED BY ","
IGNORE 1 LINES
(`geo_value`, `value`, `stderr`, `sample_size`, `issue`, `time_value`, `geo_type`, `signal`, `source`)
SET time_type="day";
'''

    load_tmp_table_insert_sql = f'''
INSERT INTO {tmp_table_name}
(`geo_value`, `value`, `stderr`, `sample_size`, `issue`, `time_value`, `geo_type`, `signal`, `source`, `time_type`,
`value_updated_timestamp`, `direction_updated_timestamp`, `lag`, `direction`, `is_latest_issue`)
VALUES
(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
0, 0, 0, 0, 0)
'''

    add_id_sql = f'''
UPDATE {tmp_table_name} d INNER JOIN covidcast c USING
(`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`, `issue`)
SET d.covidcast_id=c.id, d.is_latest_issue=c.is_latest_issue;
'''

    delete_sql = f'''
DELETE c FROM {tmp_table_name} d INNER JOIN covidcast c WHERE d.covidcast_id=c.id;
'''

    fix_latest_issue_sql = f'''
UPDATE
(SELECT `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`, MAX(`issue`) AS `issue`
    FROM
    (SELECT DISTINCT `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`
        FROM {tmp_table_name} WHERE `is_latest_issue`=1) AS was_latest
    LEFT JOIN covidcast c
    USING (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`)
    GROUP BY `source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`
) AS TMP
LEFT JOIN `covidcast`
USING (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`, `issue`)
SET `covidcast`.`is_latest_issue`=1;
'''

    drop_tmp_table_sql = f'DROP TABLE {tmp_table_name}'
    try:
      self._cursor.execute(create_tmp_table_sql)
      self._cursor.execute(amend_tmp_table_sql)
      if isinstance(cc_deletions, str):
        self._cursor.execute(load_tmp_table_infile_sql)
      elif isinstance(cc_deletions, list):
        self._cursor.executemany(load_tmp_table_insert_sql, cc_deletions)
      else:
        raise Exception(f"Bad deletions argument: need a filename or a list of tuples; got a {type(cc_deletions)}")
      self._cursor.execute(add_id_sql)
      self._cursor.execute(delete_sql)
      self._cursor.execute(fix_latest_issue_sql)
      self._connection.commit()
    except Exception as e:
      raise e
    finally:
      self._cursor.execute(drop_tmp_table_sql)

  def compute_covidcast_meta(self, table_name=None):
    """Compute and return metadata on all COVIDcast signals."""
    logger = get_structured_logger("compute_covidcast_meta")

    if table_name is None:
      table_name = self.latest_table

    n_threads = max(1, cpu_count()*9//10) # aka number of concurrent db connections, which [sh|c]ould be ~<= 90% of the #cores available to SQL server
    # NOTE: this may present a small problem if this job runs on different hardware than the db,
    #       but we should not run into that issue in prod.
    logger.info(f"using {n_threads} workers")

    srcsigs = Queue() # multi-consumer threadsafe!
    sql = f'SELECT `source`, `signal` FROM `{table_name}` GROUP BY `source`, `signal` ORDER BY `source` ASC, `signal` ASC;'
    self._cursor.execute(sql)
    for source, signal in self._cursor:
      srcsigs.put((source, signal))

    inner_sql = f'''
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

    meta = []
    meta_lock = threading.Lock()

    def worker():
      name = threading.current_thread().name
      logger.info("starting thread", thread=name)
      #  set up new db connection for thread
      worker_dbc = Database()
      worker_dbc.connect(connector_impl=self._connector_impl)
      w_cursor = worker_dbc._cursor
      try:
        while True:
          (source, signal) = srcsigs.get_nowait() # this will throw the Empty caught below
          logger.info("starting pair", thread=name, pair=f"({source}, {signal})")
          w_cursor.execute(inner_sql, (source, signal))
          with meta_lock:
            meta.extend(list(
              dict(zip(w_cursor.column_names, x)) for x in w_cursor
            ))
          srcsigs.task_done()
      except Empty:
        logger.info("no jobs left, thread terminating", thread=name)
      finally:
        worker_dbc.disconnect(False) # cleanup

    threads = []
    for n in range(n_threads):
      t = threading.Thread(target=worker, name='MetacacheThread-'+str(n))
      t.start()
      threads.append(t)

    srcsigs.join()
    logger.info("jobs complete")
    for t in threads:
      t.join()
    logger.info("all threads terminated")

    # sort the metadata because threaded workers dgaf
    sorting_fields = "data_source signal time_type geo_type".split()
    sortable_fields_fn = lambda x: [(field, x[field]) for field in sorting_fields]
    prepended_sortables_fn = lambda x: sortable_fields_fn(x) + list(x.items())
    tuple_representation = list(map(prepended_sortables_fn, meta))
    tuple_representation.sort()
    meta = list(map(dict, tuple_representation)) # back to dict form

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
