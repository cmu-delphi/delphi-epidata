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

Columndef = namedtuple("Columndef", "csv_name sql_name dtype")

class Database:

  def __init__(self,
               connection,
               table_name=None,
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
    columns_and_types : tuple[str, str, Callable]
      List of 3-tuples of (CSV header name, SQL column name, data type) for
      all the columns in the CSV file.
    additional_fields : tuple[str]
      List of 2-tuples of (value, SQL column name) fordditional fields to include
      at the end of the row which are not present in the CSV data.
    """

    self.connection = connection
    self.table_name = table_name
    self.publication_col_name = "issue" if table_name == 'covid_hosp_state_timeseries' else \
      'publication_date'
    self.columns_and_types = {
      c.csv_name: c
      for c in (columns_and_types if columns_and_types is not None else [])
    }
    self.key_columns = key_columns if key_columns is not None else []
    self.additional_fields = additional_fields if additional_fields is not None else []

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
          `dataset_name` = %s AND `revision_timestamp` = %s
      ''', (self.table_name, revision))
      for (result,) in cursor:
        return bool(result)

  def insert_metadata(self, publication_date, revision, meta_json):
    """Add revision metadata to the database.

    Parameters
    ----------
    publication_date : int
      Date when the dataset was published in YYYYMMDD format.
    revision : str
      Unique revision string.
    meta_json : str
      Metadata serialized as a JSON string.
    """

    with self.new_cursor() as cursor:
      cursor.execute('''
        INSERT INTO
          `covid_hosp_meta` (
            `dataset_name`,
            `publication_date`,
            `revision_timestamp`,
            `metadata_json`,
            `acquisition_datetime`
          )
        VALUES
          (%s, %s, %s, %s, NOW())
      ''', (self.table_name, publication_date, revision, meta_json))

  def insert_dataset(self, publication_date, dataframe):
    """Add a dataset to the database.

    Parameters
    ----------
    publication_date : int
      Date when the dataset was published in YYYYMMDD format.
    dataframe : pandas.DataFrame
      The dataset.
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

    num_columns = 2 + len(dataframe_columns_and_types) + len(self.additional_fields)
    value_placeholders = ', '.join(['%s'] * num_columns)
    columns = ', '.join(f'`{i.sql_name}`' for i in dataframe_columns_and_types + self.additional_fields)
    sql = f'INSERT INTO `{self.table_name}` (`id`, `{self.publication_col_name}`, {columns}) ' \
          f'VALUES ({value_placeholders})'
    id_and_publication_date = (0, publication_date)
    with self.new_cursor() as cursor:
      for _, row in dataframe.iterrows():
        values = []
        for c in dataframe_columns_and_types:
          values.append(nan_safe_dtype(c.dtype, row[c.csv_name]))
        cursor.execute(sql,
                       id_and_publication_date +
                       tuple(values) +
                       tuple(i.csv_name for i in self.additional_fields))

    # deal with non/seldomly updated columns used like a fk table (if this database needs it)
    if hasattr(self, 'AGGREGATE_KEY_COLS'):
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

      # commit the data
      with self.new_cursor() as cur:
        cur.executemany(ak_insert_sql, ak_data)


  def get_max_issue(self):
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
          dataset_name = "{self.table_name}"
      ''')
      for (result,) in cursor:
        if result is not None:
          return pd.Timestamp(str(result))
      return pd.Timestamp("1900/1/1")
