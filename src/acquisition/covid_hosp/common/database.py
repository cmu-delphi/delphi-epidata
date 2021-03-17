"""Common database code used by multiple `covid_hosp` scrapers."""

# standard library
from contextlib import contextmanager
import math

# third party
import mysql.connector
import pandas as pd

# first party
import delphi.operations.secrets as secrets


class Database:

  def __init__(self,
               connection,
               table_name=None,
               columns_and_types=None,
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
    self.columns_and_types = columns_and_types
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

    num_columns = 2 + len(self.columns_and_types) + len(self.additional_fields)
    value_placeholders = ', '.join(['%s'] * num_columns)
    columns = ', '.join(f'`{i[1]}`' for i in self.columns_and_types + self.additional_fields)
    sql = f'INSERT INTO `{self.table_name}` (`id`, `{self.publication_col_name}`, {columns}) ' \
          f'VALUES ({value_placeholders})'
    id_and_publication_date = (0, publication_date)
    with self.new_cursor() as cursor:
      for _, row in dataframe.iterrows():
        values = []
        for name, _, dtype in self.columns_and_types:
          if isinstance(row[name], float) and math.isnan(row[name]):
            values.append(None)
          else:
            values.append(dtype(row[name]))
        cursor.execute(sql,
                       id_and_publication_date +
                       tuple(values) +
                       tuple(i[0] for i in self.additional_fields))

  def get_max_issue(self):
    """Fetch the most recent issue.

    This is used to bookend what links we scrape from the HHS revisions page.
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
