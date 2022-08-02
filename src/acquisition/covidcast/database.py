"""A utility class that handles database operations related to covidcast.

See src/ddl/covidcast.sql for an explanation of each field.
"""

# third party
from typing import Iterable, Sequence
import mysql.connector
from math import ceil

import delphi.operations.secrets as secrets

from .logger import get_structured_logger
from .covidcast_row import CovidcastRow


# constants for the codes used in the `process_status` column of `signal_load`
class _PROCESS_STATUS(object):
  INSERTING = 'i'
  LOADED = 'l'
  BATCHING = 'b'
PROCESS_STATUS = _PROCESS_STATUS()


class Database:
  """A collection of covidcast database operations."""

  def __init__(self):
    self.load_table = "signal_load"
    self.latest_table = "signal_latest" # NOTE: careful!  probably want to use variable `latest_view` instead for semantics purposes
    self.latest_view = self.latest_table + "_v"
    self.history_table = "signal_history" # NOTE: careful!  probably want to use variable `history_view` instead for semantics purposes
    self.history_view = self.history_table + "_v"

    self._connector_impl = mysql.connector
    self._db_credential_user, self._db_credential_password = secrets.db.epi
    self._db_host = secrets.db.host
    self._db_database = 'covid'

  def connect(self, connector_impl=None, host=None, user=None, password=None, database=None):
    """Establish a connection to the database."""
    self._connector_impl = connector_impl if connector_impl is not None else self._connector_impl
    self._db_host = host if host is not None else self._db_host
    self._db_credential_user = user if user is not None else self._db_credential_user
    self._db_credential_password = password if password is not None else self._db_credential_password
    self._db_database = database if database is not None else self._db_database

    self._connection = self._connector_impl.connect(
        host=self._db_host,
        user=self._db_credential_user,
        password=self._db_credential_password,
        database=self._db_database
    )
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
      tablename = self.history_view

    self._cursor.execute(f'SELECT count(1) FROM `{tablename}`')

    for (num,) in self._cursor:
      return num

  def count_all_history_rows(self):
    return self.count_all_rows(self.history_view)

  def count_all_latest_rows(self):
    return self.count_all_rows(self.latest_view)

  def count_insertstatus_rows(self):
    self._cursor.execute(f"SELECT count(1) from `{self.load_table}` where `process_status`='{PROCESS_STATUS.INSERTING}'")

    for (num,) in self._cursor:
      return num

  def insert_or_update_bulk(self, cc_rows: Iterable[CovidcastRow]):
    return self.insert_or_update_batch(cc_rows)

  def insert_or_update_batch(self, cc_rows: Sequence[CovidcastRow], batch_size: int = 2**20, commit_partial: bool = False):
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
        `is_latest_issue`, `missing_value`, `missing_stderr`, `missing_sample_size`,
        `process_status`)
      VALUES
        (%s, %s, %s, %s, %s, %s, 
        UNIX_TIMESTAMP(NOW()), %s, %s, %s, %s, %s, 
        1, %s, %s, %s, 
        '{PROCESS_STATUS.INSERTING}')
    '''

    # all load table entries are already marked "is_latest_issue".
    # if an entry in the load table is NOT in the latest table, it is clearly now the latest value for that key (so we do nothing (thanks to INNER join)).
    # if an entry *IS* in both load and latest tables, but latest table issue is newer, unmark is_latest_issue in load.
    fix_is_latest_issue_sql = f'''
        UPDATE 
            `{self.load_table}` JOIN `{self.latest_view}`
                USING (`source`, `signal`, `geo_type`, `geo_value`, `time_type`, `time_value`) 
            SET `{self.load_table}`.`is_latest_issue`=0 
            WHERE `{self.load_table}`.`issue` < `{self.latest_view}`.`issue`
                  AND `process_status` = '{PROCESS_STATUS.INSERTING}'
    '''

    update_status_sql = f'''
        UPDATE `{self.load_table}`
            SET `process_status` = '{PROCESS_STATUS.LOADED}'
            WHERE `process_status` = '{PROCESS_STATUS.INSERTING}'
    '''

    if 0 != self.count_insertstatus_rows():
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
        self._cursor.execute(update_status_sql)

        if modified_row_count is None or modified_row_count == -1:
          # the SQL connector does not support returning number of rows affected (see PEP 249)
          total = None
        else:
          total += modified_row_count
        if commit_partial:
          self._connection.commit()
    except Exception as e:
      # TODO: rollback???  something???
      raise e
    return total

  def run_dbjobs(self):

    signal_load_set_comp_keys = f'''
        UPDATE `{self.load_table}`
        SET compressed_signal_key = md5(CONCAT(`source`,`signal`)),
            compressed_geo_key = md5(CONCAT(`geo_type`,`geo_value`))
    '''

    signal_load_mark_batch = f'''
        UPDATE `{self.load_table}` 
        SET process_status = '{PROCESS_STATUS.BATCHING}'
    '''

    signal_dim_add_new_load = f'''
        INSERT INTO signal_dim (`source`, `signal`, `compressed_signal_key`) 
            SELECT DISTINCT `source`, `signal`, compressed_signal_key 
                FROM `{self.load_table}` 
                WHERE compressed_signal_key NOT IN 
                    (SELECT DISTINCT compressed_signal_key 
                     FROM signal_dim)
    '''

    geo_dim_add_new_load = f'''
        INSERT INTO geo_dim (`geo_type`, `geo_value`, `compressed_geo_key`) 
            SELECT DISTINCT `geo_type`, `geo_value`, compressed_geo_key 
                FROM `{self.load_table}` 
                WHERE compressed_geo_key NOT IN 
                    (SELECT DISTINCT compressed_geo_key 
                     FROM geo_dim)
    '''

    signal_history_load = f'''
        INSERT INTO signal_history 
            (signal_data_id, signal_key_id, geo_key_id, demog_key_id, issue, data_as_of_dt, 
             time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, 
             computation_as_of_dt, is_latest_issue, missing_value, missing_stderr, missing_sample_size, `legacy_id`)
        SELECT
            signal_data_id, sd.signal_key_id, gd.geo_key_id, 0, issue, data_as_of_dt, 
                time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, 
                computation_as_of_dt, is_latest_issue, missing_value, missing_stderr, missing_sample_size, `legacy_id`
            FROM `{self.load_table}` sl
                INNER JOIN signal_dim sd
                    USE INDEX(`compressed_signal_key_ind`)
                    ON sd.compressed_signal_key = sl.compressed_signal_key
                INNER JOIN geo_dim gd
                    USE INDEX(`compressed_geo_key_ind`)
                    ON gd.compressed_geo_key = sl.compressed_geo_key
            WHERE process_status = '{PROCESS_STATUS.BATCHING}'
        ON DUPLICATE KEY UPDATE
            `signal_data_id` = sl.`signal_data_id`,
            `value_updated_timestamp` = sl.`value_updated_timestamp`,
            `value` = sl.`value`,
            `stderr` = sl.`stderr`,
            `sample_size` = sl.`sample_size`,
            `lag` = sl.`lag`,
            `missing_value` = sl.`missing_value`,
            `missing_stderr` = sl.`missing_stderr`,
            `missing_sample_size` = sl.`missing_sample_size`
    '''

    signal_latest_load = f'''
        INSERT INTO signal_latest 
            (signal_data_id, signal_key_id, geo_key_id, demog_key_id, issue, data_as_of_dt, 
             time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, 
             computation_as_of_dt, missing_value, missing_stderr, missing_sample_size)
        SELECT
            signal_data_id, sd.signal_key_id, gd.geo_key_id, 0, issue, data_as_of_dt, 
                time_type, time_value, `value`, stderr, sample_size, `lag`, value_updated_timestamp, 
                computation_as_of_dt, missing_value, missing_stderr, missing_sample_size
            FROM `{self.load_table}` sl 
                INNER JOIN signal_dim sd 
                    USE INDEX(`compressed_signal_key_ind`) 
                    ON sd.compressed_signal_key = sl.compressed_signal_key 
                INNER JOIN geo_dim gd 
                    USE INDEX(`compressed_geo_key_ind`) 
                    ON gd.compressed_geo_key = sl.compressed_geo_key 
            WHERE process_status = '{PROCESS_STATUS.BATCHING}'
                AND is_latest_issue = 1
        ON DUPLICATE KEY UPDATE
            `signal_data_id` = sl.`signal_data_id`,
            `value_updated_timestamp` = sl.`value_updated_timestamp`,
            `value` = sl.`value`,
            `stderr` = sl.`stderr`,
            `sample_size` = sl.`sample_size`,
            `issue` = sl.`issue`,
            `lag` = sl.`lag`,
            `missing_value` = sl.`missing_value`,
            `missing_stderr` = sl.`missing_stderr`,
            `missing_sample_size` = sl.`missing_sample_size` 
    '''

    signal_load_delete_processed = f'''
        DELETE FROM `{self.load_table}` 
        WHERE  process_status <> '{PROCESS_STATUS.LOADED}'
    '''

    print('signal_load_set_comp_keys:')
    self._cursor.execute(signal_load_set_comp_keys)
    print('signal_load_mark_batch:')
    self._cursor.execute(signal_load_mark_batch)
    print('signal_dim_add_new_load:')
    self._cursor.execute(signal_dim_add_new_load)
    print('geo_dim_add_new_load:')
    self._cursor.execute(geo_dim_add_new_load)
    print('signal_history_load:')
    self._cursor.execute(signal_history_load)
    print('signal_latest_load:')
    self._cursor.execute(signal_latest_load)
    print('signal_load_delete_processed:')
    self._cursor.execute(signal_load_delete_processed)
    print("done.")

    return self

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
    # composite keys:
    short_comp_key = "`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`"
    long_comp_key = short_comp_key + ", `issue`"

    create_tmp_table_sql = f'''
CREATE OR REPLACE TABLE {tmp_table_name} LIKE {self.load_table};
'''

    amend_tmp_table_sql = f'''
ALTER TABLE {tmp_table_name} ADD COLUMN delete_history_id BIGINT UNSIGNED,
                             ADD COLUMN delete_latest_id BIGINT UNSIGNED,
                             ADD COLUMN update_latest BINARY(1) DEFAULT 0;
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
`value_updated_timestamp`, `lag`, `is_latest_issue`)
VALUES
(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
0, 0, 0)
'''

    add_history_id_sql = f'''
UPDATE {tmp_table_name} d INNER JOIN {self.history_view} h USING ({long_comp_key})
SET d.delete_history_id=h.signal_data_id;
'''

    # if a row we are deleting also appears in the 'latest' table (with a matching 'issue')...
    mark_for_update_latest_sql = f'''
UPDATE {tmp_table_name} d INNER JOIN {self.latest_view} ell USING ({long_comp_key})
SET d.update_latest=1, d.delete_latest_id=ell.signal_data_id;
'''

    delete_history_sql = f'''
DELETE h FROM {tmp_table_name} d INNER JOIN {self.history_table} h ON d.delete_history_id=h.signal_data_id;
'''

    # ...remove it from 'latest'...
    delete_latest_sql = f'''
DELETE ell FROM {tmp_table_name} d INNER JOIN {self.latest_table} ell ON d.delete_latest_id=ell.signal_data_id;
'''

    # ...and re-write that record with its next-latest issue (from 'history') instead.
    # NOTE: this must be executed *AFTER* `delete_history_sql` to ensure we get the correct `issue`
    #       AND also after `delete_latest_sql` so that we dont get a key collision on insert.
    update_latest_sql = f'''
INSERT INTO signal_latest
  (issue,
  signal_data_id, signal_key_id, geo_key_id, time_type, time_value,
  value, stderr, sample_size, `lag`, value_updated_timestamp,
  missing_value, missing_stderr, missing_sample_size)
SELECT
  MAX(h.issue),
  h.signal_data_id, h.signal_key_id, h.geo_key_id, h.time_type, h.time_value,
  h.value, h.stderr, h.sample_size, h.`lag`, h.value_updated_timestamp,
  h.missing_value, h.missing_stderr, h.missing_sample_size
FROM {self.history_view} h JOIN {tmp_table_name} d USING ({short_comp_key})
WHERE d.update_latest=1 GROUP BY {short_comp_key};
'''

    drop_tmp_table_sql = f'DROP TABLE {tmp_table_name}'

    total = None
    try:
      self._cursor.execute(create_tmp_table_sql)
      self._cursor.execute(amend_tmp_table_sql)
      if isinstance(cc_deletions, str):
        self._cursor.execute(load_tmp_table_infile_sql)
      elif isinstance(cc_deletions, list):
        def split_list(lst, n):
          for i in range(0, len(lst), n):
            yield lst[i:(i+n)]
        for deletions_batch in split_list(cc_deletions, 100000):
          self._cursor.executemany(load_tmp_table_insert_sql, deletions_batch)
      else:
        raise Exception(f"Bad deletions argument: need a filename or a list of tuples; got a {type(cc_deletions)}")
      self._cursor.execute(add_history_id_sql)
      self._cursor.execute(mark_for_update_latest_sql)
      self._cursor.execute(delete_history_sql)
      total = self._cursor.rowcount
      # TODO: consider reporting rows removed and/or replaced in latest table as well
      self._cursor.execute(delete_latest_sql)
      self._cursor.execute(update_latest_sql)
      self._connection.commit()

      if total == -1:
        # the SQL connector does not support returning number of rows affected (see PEP 249)
        total = None
    except Exception as e:
      raise e
    finally:
      self._cursor.execute(drop_tmp_table_sql)
    return total
