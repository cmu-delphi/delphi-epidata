# third party
import pandas
import requests


class Network:
# This code is a temporary (two weeks or so) fix until the legacy API is fully retired. Code using this style of URL will be phased out entirely then
# This needs to migrate to the new healthdata.gov API, which is different
  METADATA_URL_TEMPLATE = \
      'https://legacy.healthdata.gov/api/3/action/package_show?id=%s&page=0'

  def fetch_metadata_for_dataset(dataset_id, requests_impl=requests):
    """Download and return metadata.

    Parameters
    ----------
    dataset_id : str
      healthdata.gov dataset identifier of the dataset.

    Returns
    -------
    object
      The metadata object.
    """

    url = Network.METADATA_URL_TEMPLATE % dataset_id
    print(f'fetching metadata at {url}')
    return requests_impl.get(url).json()

  def fetch_dataset(url, pandas_impl=pandas):
    """Download and return a dataset.

    Type inference is disabled in favor of explicit type casting at the
    database abstraction layer. Pandas behavior is to represent non-missing
    values as strings and missing values as `math.nan`.

    Parameters
    ----------
    url : str
      URL to the dataset in CSV format.

    Returns
    -------
    pandas.DataFrame
      The dataset.
    """

    print(f'fetching dataset at {url}')
    return pandas_impl.read_csv(url, dtype=str)
