# third party

import requests

# first party
from delphi.epidata.acquisition.covid_hosp.common.network import Network as BaseNetwork

class Network(BaseNetwork):

  DATASET_ID = '6xf2-c3ie'
  ROOT = 'https://healthdata.gov'

  @staticmethod
  def fetch_metadata(*args, **kwags):
    """Download and return metadata.

    See `fetch_metadata_for_dataset`.
    """

    return Network.fetch_metadata_for_dataset(
        *args, **kwags, dataset_id=Network.DATASET_ID)

  @staticmethod
  def fetch_revisions(metadata, newer_than):
    """
    Extract all dataset URLs from metadata for issues after newer_than.

    Parameters
    ----------
    metadata DataFrame
      Metadata DF containing all rows of metadata from data source page.

    newer_than Timestamp or datetime
      Date and time of issue to use as lower bound for new URLs.

    Returns
    -------
      List of URLs of issues after newer_than
    """
    return list(metadata.loc[metadata.index > newer_than, "Archive Link"])
