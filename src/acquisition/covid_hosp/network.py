# third party
import pandas
import requests


class Network:

  METADATA_URL = (
    'https://healthdata.gov/api/3/action/package_show'
    '?id=83b4a668-9321-4d8c-bc4f-2bef66c49050&page=0'
  )

  def fetch_metadata(requests_impl=requests):
    """Download and return metadata.

    Returns
    -------
    object
      The metadata object.
    """

    print(f'fetching metadata at {Network.METADATA_URL}')
    return requests_impl.get(Network.METADATA_URL).json()

  def fetch_dataset(url, pandas_impl=pandas):
    """Download and return a dataset.

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
    return pandas_impl.read_csv(url)
