# first party
from delphi.epidata.acquisition.covid_hosp.common.network import Network as BaseNetwork


class Network(BaseNetwork):

  DATASET_ID = 'd475cc4e-83cd-4c16-be57-9105f300e0bc'

  def fetch_metadata(*args, **kwags):
    """Download and return metadata.

    See `fetch_metadata_for_dataset`.
    """

    return Network.fetch_metadata_for_dataset(
        *args, **kwags, dataset_id=Network.DATASET_ID)
