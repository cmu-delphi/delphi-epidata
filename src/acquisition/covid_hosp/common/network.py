import pandas


class Network:
    METADATA_URL_TEMPLATE = 'https://healthdata.gov/api/views/%s/rows.csv'

    def fetch_metadata_for_dataset(dataset_id):
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
        df = Network.fetch_dataset(url)
        df["Update Date"] = pandas.to_datetime(df["Update Date"])
        df.sort_values("Update Date", inplace=True)
        df.set_index("Update Date", inplace=True)
        return df

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
