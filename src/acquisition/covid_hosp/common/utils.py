"""Code shared among multiple `covid_hosp` scrapers."""

# standard library
import datetime
import re

import pandas as pd

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

    return int(date[:10].replace('/', '').replace('-', ''))

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

  def issues_to_fetch(metadata, newer_than, older_than):
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
    Returns
    -------
      Dictionary of {issue day: list of (download urls, index)}
      for issues after newer_than and before older_than
    """
    daily_issues = {}
    for index in sorted(set(metadata.index)):
      day = index.date()
      if day > newer_than and day < older_than:
        urls = metadata.loc[index, "Archive Link"]
        urls_list = [(urls, index)] if isinstance(urls, str) else [(url, index) for url in urls]
        if day not in daily_issues:
          daily_issues[day] = urls_list
        else:
          daily_issues[day] += urls_list
    return daily_issues

  @staticmethod
  def merge_by_key_cols(dfs, key_cols):
    """Merge a list of data frames as a series of updates.

    Parameters:
    -----------
      dfs : list(pd.DataFrame)
        Data frames to merge, ordered from earliest to latest.
      key_cols: list(str)
        Columns to use as the index.

    Returns a single data frame containing the most recent data for each state+date.
    """

    dfs = [df.set_index(key_cols) for df in dfs
           if not all(k in df.index.names for k in key_cols)]
    result = dfs[0]
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
    metadata = network.fetch_metadata()
    with database.connect() as db:
      max_issue = db.get_max_issue()
      older_than = datetime.datetime.today().date() if newer_than is None else older_than
      newer_than = max_issue if newer_than is None else newer_than
      daily_issues = Utils.issues_to_fetch(metadata, newer_than, older_than)
      if not daily_issues:
        print("no new issues, nothing to do")
        return False
      for issue, revisions in daily_issues.items():
        issue_int = int(issue.strftime("%Y%m%d"))
        # download the dataset and add it to the database
        dataset = Utils.merge_by_key_cols([network.fetch_dataset(url) for url, _ in revisions],
                                          db.KEY_COLS)
        db.insert_dataset(issue_int, dataset)
        # add metadata to the database using the last revision seen.
        last_url, last_index = revisions[-1]
        metadata_json = metadata.loc[last_index].reset_index().to_json()
        db.insert_metadata(issue_int, last_url, metadata_json)

        print(f'successfully acquired {len(dataset)} rows')

      # note that the transaction is committed by exiting the `with` block
      return True
