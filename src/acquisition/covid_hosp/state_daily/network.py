# third party
from bs4 import BeautifulSoup
import requests

# first party
from delphi.epidata.acquisition.covid_hosp.common.network import Network as BaseNetwork
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils

class Network(BaseNetwork):

  DATASET_ID = '7823dd0e-c8c4-4206-953e-c6d2f451d6ed'
  ROOT = "https://healthdata.gov"
  REVISIONS = '/node/3281086/revisions'

  def fetch_metadata(*args, **kwags):
    """Download and return metadata.

    See `fetch_metadata_for_dataset`.
    """

    return Network.fetch_metadata_for_dataset(
        *args, **kwags, dataset_id=Network.DATASET_ID)

  def fetch_revisions(newer_than):
    urls = []
    soup = BeautifulSoup(requests.get(Network.ROOT + Network.REVISIONS).content, "html.parser")
    views = [
      a['href'] for a in soup.select("tr.diff-revision a[href^='/node']")
      if Utils.get_issue_from_revision(a.text) > newer_than
    ]
    for view in views:
      view_soup = BeautifulSoup(requests.get(Network.ROOT + view).content, "html.parser")
      urls.append(view_soup.select_one(".download a")['href'])
    return urls
