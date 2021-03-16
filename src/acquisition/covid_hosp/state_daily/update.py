"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State"
dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""
# standard library
import json

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network


class Update:

  @staticmethod
  def run(network=Network):
    """Acquire the most recent dataset, unless it was previously acquired.

    Returns
    -------
    bool
      Whether a new dataset was acquired.
    """

    #return Utils.update_dataset(Database, network)

    # can't use Utils here because daily files are posted in batches and we want
    # all files in the batch. These have to be scraped from the Revisions page,
    # since they aren't surfaced in metadata. :(
    # then we merge them into an issue based on their publish date.

    # get dataset details from metadata
    metadata = network.fetch_metadata()
    issue = max(metadata.index)
    revision = metadata.loc[issue, "Archive Link"]
    print(f'issue: {issue}')
    print(f'revision: {revision}')

    # connect to the database
    with Database.connect() as db:

      # bail if the dataset has already been acquired
      if db.contains_revision(revision):
        print('already have this revision, nothing to do')
        return False

      max_issue = db.get_max_issue()
      # add metadata to the database
      metadata_json = metadata.loc[issue].to_json()
      issue_int = int(issue.strftime("%Y%m%d"))
      db.insert_metadata(issue_int, revision, metadata_json)

      urls = network.fetch_revisions(metadata, max_issue)
      print(f'acquiring {len(urls)} daily updates')
      dataset = Update.merge_by_state_date(
        [network.fetch_dataset(url) for url in urls]
      )

      db.insert_dataset(issue_int, dataset)

      print(f'successfully acquired {len(dataset)} rows (not excluding overlap)')
    return True

  @staticmethod
  def merge_by_state_date(dfs):
    """Merge a list of data frames as a series of updates.

    Parameters:
    -----------
      dfs : list(pd.DataFrame)
        Data frames to merge, ordered from earliest to latest.

    Returns a single data frame containing the most recent data for each state+date.
    """
    key_cols = ['state', 'reporting_cutoff_start']
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


# main entry point
Utils.launch_if_main(Update.run, __name__)
