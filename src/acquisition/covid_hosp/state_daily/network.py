# third party
from bs4 import BeautifulSoup
import requests

# first party
from delphi.epidata.acquisition.covid_hosp.common.network import Network as BaseNetwork
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils

class Network(BaseNetwork):

  DATASET_ID = '7823dd0e-c8c4-4206-953e-c6d2f451d6ed'
  ROOT = 'https://healthdata.gov'
  REVISIONS = '/node/3281086/revisions'

  @staticmethod
  def fetch_metadata(*args, **kwags):
    """Download and return metadata.

    See `fetch_metadata_for_dataset`.
    """

    return Network.fetch_metadata_for_dataset(
        *args, **kwags, dataset_id=Network.DATASET_ID)

  @staticmethod
  def fetch_revisions(newer_than):
    """Scrape CSV urls from the HHS revisions pages.

    newer_than : int YYYYMMDD
      issue date of the most recent daily files already in the database.

    The revisions page is a big table showing recent revisions to the state
    daily dataset. Each row represents a single revision with a link to a
    separate page where a download is available for that revision.

    The first row is different, and links directly back to the main dataset
    page. Since this row represents the current published version, and the URL
    for that CSV is included in the metadata, we do not retrieve it here.

    The link for each revision is a date in the same format as
    `revision_timestamp` from the metadata, so we bookend which links we retrieve
    by checking against the issue code (newer_than) for the last issue we
    imported.

    This approach will break under the following conditions:
     - Automation starts the update routine after the first file of a batch is
       uploaded by HHS, but before the final file of the batch is uploaded (HHS
       typically uploads in the evenings, but there are some midmorning and
       afternoon batches in the revision history, so who knows)
     - HHS uploads batches on two days in a row, and the first batch isn't completed
       until after midnight (causing files from two distinct batches to have the
       same date in the link from the revisions page)
    """
    urls = []
    soup = BeautifulSoup(requests.get(Network.ROOT + Network.REVISIONS).content, 'html.parser')
    views = [
      a['href'] for a in soup.select('tr.diff-revision a[href^="/node"]')
      if Utils.get_issue_from_revision(a.text) > newer_than
    ]
    for view in views:
      view_soup = BeautifulSoup(requests.get(Network.ROOT + view).content, 'html.parser')
      urls.append(view_soup.select_one('.download a')['href'])
    return urls
