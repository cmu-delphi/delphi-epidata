"""Code shared among multiple `covid_hosp` scrapers."""

# standard library
import datetime
import re

import pandas as pd

from delphi.epidata.acquisition.common.logger import get_structured_logger

class CovidHospException(Exception):
  """Exception raised exclusively by `covid_hosp` utilities."""


class Utils:

  # regex to extract issue date from revision field
  # example revision: "Mon, 11/16/2020 - 00:55"
  REVISION_PATTERN = re.compile(r'^.*\s(\d+)/(\d+)/(\d+)\s.*$')

  def launch_if_main(entrypoint, runtime_name):
    """Call the given function in the main entry point, otherwise no-op."""

    if runtime_name == '__main__':
      entrypoint()

  def int_from_date(date):
    """Convert a YYYY/MM/DD date from a string to a YYYYMMDD int.

    Parameters
    ----------
    date : str
      Date in "YYYY/MM/DD.*" format.

    Returns
    -------
    int
      Date in YYYYMMDD format.
    """
    if isinstance(date, str):
      return int(date[:10].replace('/', '').replace('-', ''))
    return date

  def parse_bool(value):
    """Convert a string to a boolean.

    Parameters
    ----------
    value : str
      Boolean-like value, like "true" or "false".

    Returns
    -------
    bool
      If the string contains some version of "true" or "false".
    None
      If the string is None or empty.

    Raises
    ------
    CovidHospException
      If the string constains something other than a version of "true" or
      "false".
    """

    if not value:
      return None
    if value.lower() == 'true':
      return True
    if value.lower() == 'false':
      return False
    raise CovidHospException(f'cannot convert "{value}" to bool')

  def limited_string_fn(length):
    def limited_string(value):
      value = str(value)
      if len(value) > length:
        raise CovidHospException(f"Value '{value}':{len(value)} longer than max {length}")
      return value
    return limited_string

  def issues_to_fetch(metadata, newer_than, older_than, logger=False):
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
    for index in sorted(set(metadata.index)):
      day = index.date()
      if day > newer_than and day < older_than:
        urls = metadata.loc[index, "Archive Link"]
        urls_list = [(urls, index)] if isinstance(urls, str) else [(url, index) for url in urls]
        if day not in daily_issues:
          daily_issues[day] = urls_list
        else:
          daily_issues[day] += urls_list
      elif day >= older_than:
        n_beyond += 1
    if n_beyond > 0:
      if logger:
        logger.info("issues available", on_or_newer=older_than, count=n_beyond)
    return daily_issues

  @staticmethod
  def merge_by_key_cols(dfs, key_cols, logger=False):
    """Merge a list of data frames as a series of updates.

    Parameters:
    -----------
      dfs : list(pd.DataFrame)
        Data frames to merge, ordered from earliest to latest.
      key_cols: list(str)
        Columns to use as the index.
      logger structlog.Logger [optional; default False]
        Logger to receive messages

    Returns a single data frame containing the most recent data for each state+date.
    """

    dfs = [df.set_index(key_cols) for df in dfs
           if not all(k in df.index.names for k in key_cols)]
    result = dfs[0]
    if logger and len(dfs) > 7:
      logger.warning(
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
      new_rows = df.loc[[i for i in df.index.to_list() if i not in result.index.to_list()]]
      result = pd.concat([result, new_rows])

    # convert the index rows back to columns
    return result.reset_index(level=key_cols)

  @staticmethod
  def update_dataset(database, network, newer_than=None, older_than=None):
    """Acquire the most recent dataset, unless it was previously acquired.

    Parameters
    ----------
    database : delphi.epidata.acquisition.covid_hosp.common.database.Database
      A `Database` subclass for a particular dataset.
    network : delphi.epidata.acquisition.covid_hosp.common.network.Network
      A `Network` subclass for a particular dataset.
    newer_than : date
      Lower bound (exclusive) of days to get issues for.
    older_than : date
      Upper bound (exclusive) of days to get issues for

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """
    logger = get_structured_logger(f"{database.__class__.__module__}.{database.__class__.__name__}.update_dataset")
    
    metadata = network.fetch_metadata(logger=logger)
    datasets = []
    with database.connect() as db:
      max_issue = db.get_max_issue(logger=logger)

    older_than = datetime.datetime.today().date() if newer_than is None else older_than
    newer_than = max_issue if newer_than is None else newer_than
    daily_issues = Utils.issues_to_fetch(metadata, newer_than, older_than, logger=logger)
    if not daily_issues:
      logger.info("no new issues; nothing to do")
      return False
    for issue, revisions in daily_issues.items():
      issue_int = int(issue.strftime("%Y%m%d"))
      # download the dataset and add it to the database
      dataset = Utils.merge_by_key_cols([network.fetch_dataset(url) for url, _ in revisions],
                                        db.KEY_COLS,
                                        logger=logger)
      # add metadata to the database
      all_metadata = []
      for url, index in revisions:
        all_metadata.append((url, metadata.loc[index].reset_index().to_json()))
      datasets.append((
        issue_int,
        dataset,
        all_metadata
      ))
    with database.connect() as db:
      for issue_int, dataset, all_metadata in datasets:
        db.insert_dataset(issue_int, dataset, logger=logger)
        for url, metadata_json in all_metadata:
          db.insert_metadata(issue_int, url, metadata_json, logger=logger)
        logger.info("acquired rows", count=len(dataset))

      # note that the transaction is committed by exiting the `with` block
      return True
