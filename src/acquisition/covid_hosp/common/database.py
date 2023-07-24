"""Common database code used by multiple `covid_hosp` scrapers."""

# standard library
from contextlib import contextmanager
import datetime
import math

# third party
import mysql.connector
import pandas as pd

# first party
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.covid_hosp.common.network import Network
from delphi.epidata.common.logger import get_structured_logger
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething

class Database:

  DATASET_NAME = None

  def __init__(self):
    """
    Create a new Database object.
    """
    self.logger = get_structured_logger(f"{self.__module__}")
    # Make sure connection is reset - set this in connect()
    self.connection = None

    if self.DATASET_NAME is None:
      raise NameError('no dataset given!') # Must be defined by subclasses

    chs = CovidHospSomething()
    # The name of the table which holds the dataset.
    self.table_name = chs.get_ds_table_name(self.DATASET_NAME)
    # The 9-character healthdata.gov identifier for this dataset.
    self.hhs_dataset_id = chs.get_ds_dataset_id(self.DATASET_NAME)
    self.metadata_id = chs.get_ds_metadata_id(self.DATASET_NAME)
    self.issue_column = chs.get_ds_issue_column(self.DATASET_NAME)
    # List of 3-tuples of (CSV header name, SQL column name, data type) for all the columns in the CSV file.
    self.columns_and_types = {c.csv_name: c for c in chs.get_ds_ordered_csv_cols(self.DATASET_NAME)}
    self.key_columns = chs.get_ds_key_cols(self.DATASET_NAME)
    self.aggregate_key_columns = chs.get_ds_aggregate_key_cols(self.DATASET_NAME)

  @contextmanager
  def connect(self, mysql_connector_impl=mysql.connector):
    """Connect to a database and provide the connection as a context manager.

    As long as the context manager exits normally, the connection's transaction
    will be committed. Otherwise, if the context is exited by an Exception, the
    transaction will be rolled back.

    In any case, the connection will be gracefully closed upon exiting the
    context manager.
    """

    # connect to the database
    user, password = secrets.db.epi
    self.connection = mysql_connector_impl.connect(
        host=secrets.db.host,
        user=user,
        password=password,
        database='epidata')

    try:
      # provide the connection to the context manager
      yield self

      # rollback by default; the following commit will only take place if no
      # exception was raised in calling code
      self.connection.commit()
    finally:
      # close the connection in any case and make sure self.connection is reset
      self.connection.close()
      self.connection = None

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

  # TODO: this may need further changes once https://github.com/cmu-delphi/delphi-epidata/pull/1224 is merged
  def update_dataset(self, newer_than=None, older_than=None):
    """Acquire the most recent dataset, unless it was previously acquired.

    Parameters
    ----------
    newer_than : date
      Lower bound (exclusive) of days to get issues for.
    older_than : date
      Upper bound (exclusive) of days to get issues for

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """
    logger = self.logger
    with self.connect() as db:
      max_issue = db.get_max_issue()

    older_than = datetime.datetime.today().date() if newer_than is None else older_than
    newer_than = max_issue if newer_than is None else newer_than
    metadata = Network.fetch_metadata(self.metadata_id, logger=logger)
    daily_issues = self.issues_to_fetch(metadata, newer_than, older_than)
    if not daily_issues:
      logger.info("no new issues; nothing to do")
      return False
    datasets = []
    for issue, revisions in daily_issues.items():
      issue_int = int(issue.strftime("%Y%m%d"))
      # download the dataset and add it to the database
      dataset = self.merge_by_key_cols([Network.fetch_dataset(url, logger=logger) for url, _ in revisions])
      # add metadata to the database
      all_metadata = []
      for url, index in revisions:
        all_metadata.append((url, metadata.loc[index].reset_index().to_json()))
      datasets.append((
        issue_int,
        dataset,
        all_metadata
      ))
    with self.connect() as db:
      for issue_int, dataset, all_metadata in datasets:
        db.insert_dataset(issue_int, dataset)
        for url, metadata_json in all_metadata:
          db.insert_metadata(issue_int, url, metadata_json)
        logger.info("acquired rows", count=len(dataset))

      # note that the transaction is committed by exiting the `with` block
      return True

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
            `hhs_dataset_id`,
            `publication_date`,
            `revision_timestamp`,
            `metadata_json`,
            `acquisition_datetime`
          )
        VALUES
          (%s, %s, %s, %s, %s, NOW())
      ''', (self.table_name, self.hhs_dataset_id, publication_date, revision, meta_json))

  def insert_dataset(self, publication_date, dataframe):
    """Add a dataset to the database.

    Parameters
    ----------
    publication_date : int
      Date when the dataset was published in YYYYMMDD format.
    dataframe : pandas.DataFrame
      The dataset.
    """
    logger = self.logger
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

    num_columns = 2 + len(dataframe_columns_and_types)
    value_placeholders = ', '.join(['%s'] * num_columns)
    columns = ', '.join(f'`{i.sql_name}`' for i in dataframe_columns_and_types)
    sql = f'INSERT INTO `{self.table_name}` (`id`, `{self.issue_column}`, {columns}) ' \
          f'VALUES ({value_placeholders})'
    id_and_publication_date = (0, publication_date)
    logger.info('updating values', count=len(dataframe.index))
    n = 0
    many_values = []
    with self.new_cursor() as cursor:
      for index, row in dataframe.iterrows():
        values = []
        for c in dataframe_columns_and_types:
          values.append(nan_safe_dtype(c.dtype, row[c.csv_name]))
        many_values.append(id_and_publication_date +
          tuple(values))
        n += 1
        # insert in batches because one at a time is slow and all at once makes
        # the connection drop :(
        if n % 5_000 == 0:
          try:
            cursor.executemany(sql, many_values)
            many_values = []
          except Exception as e:
            logger.error('error on insert', publ_date=publication_date, in_lines=(n-5_000, n), index=index, values=values, exception=e)
            raise e
      # insert final batch
      if many_values:
        cursor.executemany(sql, many_values)

    # deal with non/seldomly updated columns used like a fk table (if this database needs it)
    if len(self.aggregate_key_columns) > 0:
      logger.info('updating keys')
      ak_cols = self.aggregate_key_columns

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
      logger.info("database query", sql=ak_insert_sql)

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
          hhs_dataset_id = "{self.hhs_dataset_id}"
      ''')
      for (result,) in cursor:
        if result is not None:
          return pd.Timestamp(str(result))
      self.logger.warn("get_max_issue", msg="no matching results in meta table; returning 1900/1/1 epoch")
      return pd.Timestamp("1900/1/1")

  def issues_to_fetch(self, metadata, newer_than, older_than):
    """
    Construct all issue dates and URLs to be ingested based on metadata.

    Parameters
    ----------
    metadata pd.DataFrame
      HHS metadata indexed by issue date and with column "Archive Link"
    newer_than Date
      Lower bound (exclusive) of days to get issues for.
    older_than Date
      Upper bound (exclusive) of days to get issues for
    logger structlog.Logger [optional; default False]
      Logger to receive messages
    Returns
    -------
      Dictionary of {issue day: list of (download urls, index)}
      for issues after newer_than and before older_than
    """
    daily_issues = {}
    n_beyond = 0
    n_selected = 0
    for index in sorted(set(metadata.index)):
      day = index.date()
      if day > newer_than and day < older_than:
        urls = metadata.loc[index, "Archive Link"]
        urls_list = [(urls, index)] if isinstance(urls, str) else [(url, index) for url in urls]
        if day not in daily_issues:
          daily_issues[day] = urls_list
        else:
          daily_issues[day] += urls_list
        n_selected += len(urls_list)
      elif day >= older_than:
        n_beyond += 1
    if n_beyond > 0:
      self.logger.info("issues available beyond selection", on_or_newer=older_than, count=n_beyond)
    self.logger.info("issues selected", newer_than=str(newer_than), older_than=str(older_than), count=n_selected)
    return daily_issues

  def merge_by_key_cols(self, dfs):
    """Merge a list of data frames as a series of updates.

    Parameters:
    -----------
      dfs : list(pd.DataFrame)
        Data frames to merge, ordered from earliest to latest.
      key_cols: list(str)
        Columns to use as the index.

    Returns a single data frame containing the most recent data for each state+date.
    """

    dfs = [df.set_index(self.key_columns) for df in dfs
           if not all(k in df.index.names for k in self.key_columns)]
    result = dfs[0]
    if len(dfs) > 7:
      self.logger.warning(
        "expensive operation",
        msg="concatenating more than 7 files may result in long running times",
        count=len(dfs))
    for df in dfs[1:]:
      # update values for existing keys
      result.update(df)
      # add any new keys.
      ## repeated concatenation in pandas is expensive, but (1) we don't expect
      ## batch sizes to be terribly large (7 files max) and (2) this way we can
      ## more easily capture the next iteration's updates to any new keys
      result_index_set = set(result.index.to_list())
      new_rows = df.loc[[i for i in df.index.to_list() if i not in result_index_set]]
      result = pd.concat([result, new_rows])

    # convert the index rows back to columns
    return result.reset_index(level=self.key_columns)
