"""Common database code used by multiple `covid_hosp` scrapers."""

# standard library
from collections import namedtuple
from contextlib import contextmanager
import math

# third party
import mysql.connector
import pandas as pd

# first party
import delphi.operations.secrets as secrets
from delphi_utils import get_structured_logger

Columndef = namedtuple("Columndef", "csv_name sql_name dtype")

class Database:

  def __init__(self,
               connection,
               table_name=None,
               hhs_dataset_id=None,
               columns_and_types=None,
               key_columns=None,
               additional_fields=None):
    """Create a new Database object.

    Parameters
    ----------
    connection
      An open connection to a database.
    table_name : str
      The name of the table which holds the dataset.
    hhs_dataset_id : str
      The 9-character healthdata.gov identifier for this dataset.
    columns_and_types : tuple[str, str, Callable]
      List of 3-tuples of (CSV header name, SQL column name, data type) for
      all the columns in the CSV file.
    additional_fields : tuple[str]
      List of 2-tuples of (value, SQL column name) fordditional fields to include
      at the end of the row which are not present in the CSV data.
    """

    self.connection = connection
    self.table_name = table_name
    self.hhs_dataset_id = hhs_dataset_id
    self.publication_col_name = "issue" if table_name == 'covid_hosp_state_timeseries' else \
      'publication_date'
    self.columns_and_types = {
      c.csv_name: c
      for c in (columns_and_types if columns_and_types is not None else [])
    }
    self.key_columns = key_columns if key_columns is not None else []
    self.additional_fields = additional_fields if additional_fields is not None else []

  @classmethod
  def logger(database_class):
    return get_structured_logger(f"{database_class.__module__}")

  @classmethod
  @contextmanager
  def connect(database_class, mysql_connector_impl=mysql.connector):
    """Connect to a database and provide the connection as a context manager.

    As long as the context manager exits normally, the connection's transaction
    will be committed. Otherwise, if the context is exited by an Exception, the
    transaction will be rolled back.

    In any case, the connection will be gracefully closed upon exiting the
    context manager.
    """

    # connect to the database
    user, password = secrets.db.epi
    connection = mysql_connector_impl.connect(
        host=secrets.db.host,
        user=user,
        password=password,
        database='epidata')

    try:
      # provide the connection to the context manager
      yield database_class(connection)

      # rollback by default; the following commit will only take place if no
      # exception was raised in calling code
      connection.commit()
    finally:
      # close the connection in any case
      connection.close()

  @contextmanager
  def new_cursor(self):
    """Create and provide a database cursor as a context manager.

    The cursor will be gracefully closed upon exiting the context manager.
    """

    cursor = self.connection.cursor()
    try:
      yield cursor
    finally:
      cursor.close()

  def contains_revision(self, revision):
    """Return whether the given revision already exists in the database.

    Parameters
    ----------
    revision : str
      Unique revision string.

    Returns
    -------
    bool
      True iff the revision already exists.
    """

    with self.new_cursor() as cursor:
      cursor.execute('''
        SELECT
          count(1) > 0
        FROM
          `covid_hosp_meta`
        WHERE
          `hhs_dataset_id` = %s AND `revision_timestamp` = %s
      ''', (self.hhs_dataset_id, revision))
      for (result,) in cursor:
        return bool(result)

  def insert_metadata(self, publication_date, revision, meta_json, logger=False):
    """Add revision metadata to the database.

    Parameters
    ----------
    publication_date : int
      Date when the dataset was published in YYYYMMDD format.
    revision : str
      Unique revision string.
    meta_json : str
      Metadata serialized as a JSON string.
    logger structlog.Logger [optional; default False]
      Logger to receive messages
    """

    with self.new_cursor() as cursor:
      cursor.execute('''
        INSERT INTO
          `covid_hosp_meta` (
            `dataset_name`,
            `hhs_dataset_id`,
            `publication_date`,
            `revision_timestamp`,
            `metadata_json`,
            `acquisition_datetime`
          )
        VALUES
          (%s, %s, %s, %s, %s, NOW())
      ''', (self.table_name, self.hhs_dataset_id, publication_date, revision, meta_json))

  def insert_dataset(self, publication_date, dataframe, logger=False):
    """Add a dataset to the database.

    Parameters
    ----------
    publication_date : int
      Date when the dataset was published in YYYYMMDD format.
    dataframe : pandas.DataFrame
      The dataset.
    logger structlog.Logger [optional; default False]
      Logger to receive messages.
    """
    dataframe_columns_and_types = [
      x for x in self.columns_and_types.values() if x.csv_name in dataframe.columns
    ]

    def nan_safe_dtype(dtype, value):
      if isinstance(value, float) and math.isnan(value):
        return None
      return dtype(value)

    # first convert keys and save the results; we'll need them later
    for csv_name in self.key_columns:
      dataframe.loc[:, csv_name] = dataframe[csv_name].map(self.columns_and_types[csv_name].dtype)

    col_names = [f'`{i.sql_name}`' for i in dataframe_columns_and_types + self.additional_fields]
    value_placeholders = ', '.join(['%s'] * (2 + len(col_names))) # extra 2 for `id` and `self.publication_col_name` cols
    columnstring = ', '.join(col_names)
    sql = f'REPLACE INTO `{self.table_name}` (`id`, `{self.publication_col_name}`, {columnstring}) VALUES ({value_placeholders})'
    id_and_publication_date = (0, publication_date)
    num_values = len(dataframe.index)
    if logger:
      logger.info('updating values', count=num_values)
    n = 0
    rows_affected = 0
    many_values = []
    with self.new_cursor() as cursor:
      for index, row in dataframe.iterrows():
        values = []
        for c in dataframe_columns_and_types:
          values.append(nan_safe_dtype(c.dtype, row[c.csv_name]))
        many_values.append(id_and_publication_date +
          tuple(values) +
          tuple(i.csv_name for i in self.additional_fields))
        n += 1
        # insert in batches because one at a time is slow and all at once makes
        # the connection drop :(
        if n % 5_000 == 0:
          try:
            cursor.executemany(sql, many_values)
            rows_affected += cursor.rowcount
            many_values = []
          except Exception as e:
            if logger:
              logger.error('error on insert', publ_date=publication_date, in_lines=(n-5_000, n), index=index, values=values, exception=e)
            raise e
      # insert final batch
      if many_values:
        cursor.executemany(sql, many_values)
        rows_affected += cursor.rowcount
      if logger:
        # NOTE: REPLACE INTO marks 2 rows affected for a "replace" (one for a delete and one for a re-insert)
        # which allows us to count rows which were updated
        logger.info('rows affected', total=rows_affected, updated=rows_affected-num_values)

    # deal with non/seldomly updated columns used like a fk table (if this database needs it)
    if hasattr(self, 'AGGREGATE_KEY_COLS'):
      if logger:
        logger.info('updating keys')
      ak_cols = self.AGGREGATE_KEY_COLS

      # restrict data to just the key columns and remove duplicate rows
      # sort by key columns to ensure that the last ON DUPLICATE KEY overwrite
      # uses the most-recent aggregate key information
      ak_data = (dataframe[set(ak_cols + self.key_columns)]
                 .sort_values(self.key_columns)[ak_cols]
                 .drop_duplicates())
      # cast types
      for col in ak_cols:
          ak_data[col] = ak_data[col].map(
            lambda value: nan_safe_dtype(self.columns_and_types[col].dtype, value)
          )
      # fix NULLs
      ak_data = ak_data.to_numpy(na_value=None).tolist()

      # create string of tick-quoted and comma-seperated column list
      ak_cols_str = ','.join(f'`{col}`' for col in ak_cols)
      # ...and ticked and comma-sep'd "column=column" list for ON UPDATE (to keep only the most recent values for each pk)
      ak_updates_str = ','.join(f'`{col}`=v.{col}' for col in ak_cols)
      # ...and string of VALUES placeholders
      values_str = ','.join( ['%s'] * len(ak_cols) )
      # use aggregate key table alias
      ak_table = self.table_name + '_key'
      # assemble full SQL statement
      ak_insert_sql = f'INSERT INTO `{ak_table}` ({ak_cols_str}) VALUES ({values_str}) AS v ON DUPLICATE KEY UPDATE {ak_updates_str}'
      if logger:
        logger.info("database query", sql=ak_insert_sql)

      # commit the data
      with self.new_cursor() as cur:
        cur.executemany(ak_insert_sql, ak_data)


  def get_max_issue(self, logger=False):
    """Fetch the most recent issue.

    This is used to bookend what updates we pull in from the HHS metadata.
    """
    with self.new_cursor() as cursor:
      cursor.execute(f'''
        SELECT
          max(publication_date)
        from
          `covid_hosp_meta`
        WHERE
          hhs_dataset_id = "{self.hhs_dataset_id}"
      ''')
      for (result,) in cursor:
        if result is not None:
          return pd.Timestamp(str(result))
      if logger:
        logger.warn("get_max_issue", msg="no matching results in meta table; returning 1900/1/1 epoch")
      return pd.Timestamp("1900/1/1")
