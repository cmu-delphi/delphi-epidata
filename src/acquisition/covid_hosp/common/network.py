# third party
import pandas


class Network:
  METADATA_URL_TEMPLATE = \
      'https://healthdata.gov/api/views/%s/rows.csv'

  def fetch_metadata_for_dataset(dataset_id, logger=False):
    """Download and return metadata.

    Parameters
    ----------
    dataset_id : str
      healthdata.gov dataset identifier of the dataset.
    logger : structlog.Logger [optional; default False]
      Logger to receive messages.

    Returns
    -------
    object
      The metadata object.
    """
    url = Network.METADATA_URL_TEMPLATE % dataset_id
    if logger:
      logger.info('fetching metadata', url=url)
    df = Network.fetch_dataset(url)
    df["Update Date"] = pandas.to_datetime(df["Update Date"])
    df.sort_values("Update Date", inplace=True)
    df.set_index("Update Date", inplace=True)
    return df

  def fetch_dataset(url, pandas_impl=pandas, logger=False):
    """Download and return a dataset.

    Type inference is disabled in favor of explicit type casting at the
    database abstraction layer. Pandas behavior is to represent non-missing
    values as strings and missing values as `math.nan`.

    Parameters
    ----------
    url : str
      URL to the dataset in CSV format.
    logger : structlog.Logger [optional; default False]
      Logger to receive messages.

    Returns
    -------
    pandas.DataFrame
      The dataset.
    """
    if logger:
      logger.info('fetching dataset', url=url)
    return pandas_impl.read_csv(url, dtype=str)
