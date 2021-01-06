from shutil import move

import delphi.operations.secrets as secrets
import pandas as pd
import sqlalchemy
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter

SENSOR_CSV_PATH = "/common/covidcast-nowcast/receiving/"
TABLE_NAME = "covidcast_nowcast"
DB_NAME = "epidata"
CSV_DTYPES = {"source": str,
              "signal": str,
              "time_value": int,
              "value": float,
              "geo": str}


def main(csv_path: str = SENSOR_CSV_PATH) -> None:
    """
    Parse all files in a given directory and insert them into sensor table.

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
    Read CSV file, parse filename to add relevant data columns, and return DataFrame.

    Parameters
    ----------
    filepath
        Path to CSV file.
    attributes
         (source, signal, time_type, geo_type, time_value, issue, lag) tuple
         returned by CsvImport.find_csv_files

    Returns
    -------
        DataFrame with an issue column based on current date and time_value, signal, source,
        and geo_type columns based on filename.
    """
    source, signal, time_type, geo_type, time_value, issue_value, lag_value = attributes
    data = pd.read_csv(filepath, dtypes=CSV_DTYPES)
    data["source"] = source
    data["signal"] = signal
    data["time_type"] = time_value
    data["geo_type"] = geo_type
    data["time_value"] = time_value
    data["issue"] = issue_value
    data["lag"] = lag_value
    return data


if __name__ == "__main__":
    main()
