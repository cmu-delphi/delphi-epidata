# first party
from delphi.epidata.acquisition.covid_hosp.common.network import Network as BaseNetwork


class Network(BaseNetwork):

  DATASET_ID = '83b4a668-9321-4d8c-bc4f-2bef66c49050'

  def fetch_metadata(*args, **kwags):
    """Download and return metadata.

    See `fetch_metadata_for_dataset`.
    """

    return Network.fetch_metadata_for_dataset(
        *args, **kwags, dataset_id=Network.DATASET_ID)
