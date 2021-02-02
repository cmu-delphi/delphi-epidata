"""
Acquires the "COVID-19 Reported Patient Impact and Hospital Capacity by State"
dataset provided by the US Department of Health & Human Services
via healthdata.gov.
"""

import json

# first party
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network


class Update:

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
    # since they aren't surfaced in metadata. :,(

    # get dataset details from metadata
    metadata = network.fetch_metadata()
    url, revision = Utils.extract_resource_details(metadata)
    issue = Utils.get_issue_from_revision(revision)
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
      metadata_json = json.dumps(metadata)
      db.insert_metadata(issue, revision, metadata_json)

      urls = network.fetch_revisions(max_issue) + [url]
      print(f'acquiring {len(urls)} daily updates')
      n = 0
      dataset = None
      for url in urls:
        # download the dataset and add it to the database
        # overwrite older files with data from newer files
        new = network.fetch_dataset(url)
        if dataset is None:
          dataset = new
        else:
          dataset.update(new)
          
      db.insert_dataset(issue, dataset)

      print(f'successfully acquired {len(dataset)} rows (not excluding overlap)')
    return True


# main entry point
Utils.launch_if_main(Update.run, __name__)
