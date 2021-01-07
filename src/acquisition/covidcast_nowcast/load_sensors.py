from shutil import move
import time

import delphi.operations.secrets as secrets
import pandas as pd
import sqlalchemy
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter

SENSOR_CSV_PATH = "/common/covidcast-nowcast/receiving/"
TABLE_NAME = "covidcast_nowcast"
DB_NAME = "epidata"
CSV_DTYPES = {"geo_value": str, "value": float}


def main(csv_path: str = SENSOR_CSV_PATH) -> None:
    """
    Parse all files in a given directory and insert them into database sensor table.

    For all the files found recursively in csv_path that match the naming scheme specified by
    CsvImporter.find_csv_files(), attempt to load the insert them into the database. Files which do
    not match the naming scheme will be moved to an archive/failed folder and skipped, and files
    which raise an error during loading/uploading will be moved to the archive/failed folder and
    have the error raised.

    Parameters
    ----------
    csv_path
        Path to folder containing files to load.

    Returns
    -------
        None.
    """
    user, pw = secrets.db.epi
    engine = sqlalchemy.create_engine(f"mysql+pymysql://{user}:{pw}@{secrets.db.host}/{DB_NAME}")
    for filepath, attributes in CsvImporter.find_csv_files(csv_path):
        if attributes is None:
            move(filepath, filepath.replace("receiving", "archive/failed"))
            continue
        try:
            data = load_and_prepare_file(filepath, attributes)
            data.to_sql(TABLE_NAME, engine, if_exists="append", index=False)
        except Exception:
            move(filepath, filepath.replace("receiving", "archive/failed"))
            raise
        move(filepath, filepath.replace("receiving", "archive/successful"))


def load_and_prepare_file(filepath: str, attributes: tuple) -> pd.DataFrame:
    """
    Read CSV file into a DataFrame and add relevant attributes as new columns to match DB table.

    Parameters
    ----------
    filepath
        Path to CSV file.
    attributes
         (source, signal, time_type, geo_type, time_value, issue, lag) tuple
         returned by CsvImport.find_csv_files

    Returns
    -------
        DataFrame with additional attributes added as columns based on filename and current date.
    """
    source, signal, time_type, geo_type, time_value, issue_value, lag_value = attributes
    data = pd.read_csv(filepath, dtype=CSV_DTYPES)
    data["source"] = source
    data["signal"] = signal
    data["time_type"] = time_type
    data["geo_type"] = geo_type
    data["time_value"] = time_value
    data["issue"] = issue_value
    data["lag"] = lag_value
    data["value_updated_timestamp"] = int(time.time())
    return data


if __name__ == "__main__":
    main()
