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

# TODO: i think this can be removed now? note: it's not referenced anymore in csv_to_database
class CovidcastRow():
  """A container for all the values of a single covidcast row."""

  # TODO: 'issue' has become 'asof'.  update those variable names.

  @staticmethod
  def fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag, is_wip):
    if row_value is None: return None
    return CovidcastRow(source, signal, time_type, geo_type, time_value,
                        row_value.geo_value,
                        row_value.value,
                        row_value.stderr,
                        row_value.sample_size,
                        row_value.missing_value,
                        row_value.missing_stderr,
                        row_value.missing_sample_size,
                        issue, lag, is_wip)

  @staticmethod
  def fromCsvRows(row_values, source, signal, time_type, geo_type, time_value, issue, lag, is_wip):
    # NOTE: returns a generator, as row_values is expected to be a generator
    return (CovidcastRow.fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag, is_wip)
            for row_value in row_values)

  def __init__(self, source, signal, time_type, geo_type, time_value, geo_value, value, stderr, 
    sample_size, missing_value, missing_stderr, missing_sample_size, asof, lag, is_wip):
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
    self.asof = asof
    self.lag = lag
    self.is_wip = is_wip
    self.ref_id = None


class Database:
  """A collection of covidcast database operations."""

  DATABASE_NAME = 'epidata'

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

  def count_all_rows(self):
    """Return the total number of rows in table `covidcast`."""

    self._cursor.execute(f'SELECT count(1) FROM `covidcast`')

    for (num,) in self._cursor:
      return num

  def get_dataref_id_map(self, source, signal, time_type, geo_type, time_value, geo_value_list):

    # insert any non-existant references...
    create_references_sql = f'''
      INSERT INTO `data_reference` (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`) 
      VALUES ('{source}', '{signal}', '{time_type}', '{geo_type}', {time_value}, %s)
      ON DUPLICATE KEY UPDATE `id` = VALUES(`id`);
    '''
    gvl_tuple = [(gv,) for gv in geo_value_list] # TODO: do we need a list of tuples or can we save a line??
    self._cursor.executemany(create_references_sql, gvl_tuple) ######geo_value_list)
    # NOTE: its kinda ok if we create these and then dont delete them on a failed file import or something...
    #   they will probably end up being used later, and as long as `latest_datapoint_id` is NULL,
    #   we will treat that row as if it essentially does not exist.

    # retrieve geo_value-->ref.id mapping 
    get_ref_ids_sql = f'''
      SELECT `geo_value`, `id`
      FROM `data_reference`
      WHERE `source`='{source}' 
        AND `signal`='{signal}' 
        AND `time_type`='{time_type}' 
        AND `geo_type`='{geo_type}' 
        AND `time_value`={time_value};
    '''
    self._cursor.execute(get_ref_ids_sql)
    return dict(list(self._cursor))


  def insert_datapoints_bulk(self, row_list):
    tmp_table_name = 'tmp_insert_datapoint_table'

    # this heavily borrows from the `datapoint` table in src/ddl/covidcast.sql, but lacks the auto_increment `id`
    create_tmp_table_sql = f'''
      CREATE TABLE `{tmp_table_name}` (
        `data_reference_id` bigint(20) unsigned NOT NULL, 
        `asof` int(11) NOT NULL,
        `value_first_updated_timestamp` int(11) NOT NULL,
        `value_updated_timestamp` int(11) NOT NULL,
        `value` double,
        `stderr` double,
        `sample_size` double,
        `lag` int(11) NOT NULL,
        `missing_value` int(1) DEFAULT 0,
        `missing_stderr` int(1) DEFAULT 0,
        `missing_sample_size` int(1) DEFAULT 0,
        UNIQUE KEY(`data_reference_id`, `asof`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''

    drop_tmp_table_sql = f'DROP TABLE {tmp_table_name}'

    insert_tmp_datapoints_sql = f'''
      INSERT INTO `{tmp_table_name}` 
        (`data_reference_id`, `asof`, `value_first_updated_timestamp`, `value_updated_timestamp`, 
         `value`, `stderr`, `sample_size`, `lag`, `missing_value`, `missing_stderr`, `missing_sample_size`) 
      VALUES 
        (%s, %s, UNIX_TIMESTAMP(NOW()), UNIX_TIMESTAMP(NOW()),
         %s, %s, %s, %s, %s, %s, %s);
    '''
    # NOTE: see comment below on insert_or_update_datapoint_sql re: `value_first_updated_timestamp`

    # TODO: enumerate * in SELECT below
    insert_or_update_datapoint_sql = f'''
      INSERT INTO `datapoint`
        (`data_reference_id`, `asof`, `value_first_updated_timestamp`, `value_updated_timestamp`, `value`, `stderr`,
         `sample_size`,`lag`,`missing_value`,`missing_stderr`,`missing_sample_size`)
      SELECT * FROM `{tmp_table_name}`
      ON DUPLICATE KEY UPDATE
        `value_updated_timestamp` = VALUES(`value_updated_timestamp`),
        `value` = VALUES(`value`),
        `stderr` = VALUES(`stderr`),
        `sample_size` = VALUES(`sample_size`),
        `lag` = VALUES(`lag`),
        `missing_value` = VALUES(`missing_value`),
        `missing_stderr` = VALUES(`missing_stderr`),
        `missing_sample_size` = VALUES(`missing_sample_size`)
    '''
    # NOTE: `value_first_updated_timestamp` is not in DUPLICATE case.
    #   this is really just a sanity check, as it should never differ from `value_updated_timestamp`
    # TODO: remove `value_first_updated_timestamp` once we are sure we are not overwriting rows

    # NOTE: PAY ATTENTION TO JOIN / LEFT/RIGHT INNER/OUTER / ETC

    #TODO: update the latest pointers
    get_latest_datapoint_ids_sql = f'''
      SELECT new_p.`id` AS new_p_id, ref.`id` AS ref_id
      -- ^ the "latest" points that shall be pointed to by which references
      FROM `{tmp_table_name}` tmp_p 
        JOIN `datapoint` new_p 
          ON tmp_p.`data_reference_id`=new_p.`data_reference_id` AND tmp_p.`asof`=new_p.`asof` 
        -- ^ so new_p's are what we just inserted into `datapoint`
        JOIN `data_reference` ref 
          ON ref.`id`=new_p.`data_reference_id` 
        -- ^ and we get the `data_reference`s that're associated with those new points
        LEFT JOIN `datapoint` old_p
          ON old_p.`id`=ref.`latest_datapoint_id`
        -- ^ and we find what the current `asof`s are set to for those references
        --   ...and keep `data_refence`s without a latest pointer (ie NULL, hence the LEFT)
      -- v but we only care about `asof`s that are more recent (or NULL) and thus should be updated
      WHERE old_p.`asof` <= new_p.`asof` OR ref.`latest_datapoint_id` IS NULL;
    '''
    
    # TODO: take the output of above statement and shove it into the below statement
    update_latest_datapoint_ids_sql = f'''UPDATE `data_reference` SET `latest_datapoint_id`=%s WHERE `id`=%s;'''

    # TODO: consider handling csv_rows as a generator instead of a list

    self._cursor.execute(create_tmp_table_sql)

    try:
      args = [(r.ref_id, r.asof, r.value, r.stderr, r.sample_size,
               r.lag, r.missing_value, r.missing_stderr, r.missing_sample_size)
              for r in row_list]
      self._cursor.executemany(insert_tmp_datapoints_sql, args)
      self._cursor.execute(insert_or_update_datapoint_sql)
      self._cursor.execute(get_latest_datapoint_ids_sql)
      self._cursor.executemany(update_latest_datapoint_ids_sql, list(self._cursor))

      # TODO: do we care about [updated] row counts?  it may be moot because of this?
      #       "the SQL connector does not support returning number of rows affected (see PEP 249)"
    except Exception as e:
      raise e
    finally:
      self._cursor.execute(drop_tmp_table_sql)
    return self._cursor.rowcount
  
  # TODO: !
  def compute_covidcast_meta(self, table_name='covidcast', use_index=True):
    """Compute and return metadata on all non-WIP COVIDcast signals."""
    logger = get_structured_logger("compute_covidcast_meta")
    index_hint = ""
    if use_index:
      index_hint = "USE INDEX (for_metadata)"

    n_threads = max(1, cpu_count()*9//10) # aka number of concurrent db connections, which [sh|c]ould be ~<= 90% of the #cores available to SQL server
    # NOTE: this may present a small problem if this job runs on different hardware than the db,
    #       but we should not run into that issue in prod.

    srcsigs = Queue() # multi-consumer threadsafe!

    sql = f'SELECT `source`, `signal` FROM `{table_name}` GROUP BY `source`, `signal` ORDER BY `source` ASC, `signal` ASC;'

    self._cursor.execute(sql)
    for source, signal in list(self._cursor): # self._cursor is a generator; this lets us use the cursor for subsequent queries inside the loop
      sql = f"SELECT `is_wip` FROM `{table_name}` WHERE `source`=%s AND `signal`=%s LIMIT 1"
      self._cursor.execute(sql, (source, signal))
      is_wip = int(self._cursor.fetchone()[0]) # casting to int as it comes out as a '0' or '1' bytearray; bool('0')==True :(
      if not is_wip:
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
        `{table_name}` {index_hint}
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
      logger.info("starting thread: " + threading.current_thread().name)
      #  set up new db connection for thread
      worker_dbc = Database()
      worker_dbc.connect(connector_impl=self._connector_impl)
      w_cursor = worker_dbc._cursor
      try:
        while True:
          (source, signal) = srcsigs.get_nowait() # this will throw the Empty caught below
          w_cursor.execute(inner_sql, (source, signal))
          with meta_lock:
            meta.extend(list(
              dict(zip(w_cursor.column_names, x)) for x in w_cursor
            ))
          srcsigs.task_done()
      except Empty:
        logger.info("no jobs left, thread terminating: " + threading.current_thread().name)
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
    logger.error("threads terminated")

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
