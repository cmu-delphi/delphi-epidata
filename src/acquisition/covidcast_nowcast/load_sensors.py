from shutil import move
from datetime import datetime
import os
import time

import delphi.operations.secrets as secrets
import pandas as pd
import sqlalchemy
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter

SENSOR_CSV_PATH = "/common/covidcast_nowcast/receiving/"
SUCCESS_DIR = "archive/successful"
FAIL_DIR = "archive/failed"
TABLE_NAME = "covidcast_nowcast"
DB_NAME = "epidata"
CSV_DTYPES = {"sensor_name": str, "geo_value": str, "value": float}


def main(csv_path: str = SENSOR_CSV_PATH) -> None:
    """
    Parse all files in a given directory and insert them into the sensor table in the database.

    For all the files found recursively in csv_path that match the naming scheme specified by
    CsvImporter.find_csv_files(), attempt to load and insert them into the database. Files which do
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
    for filepath, attribute in CsvImporter.find_issue_specific_csv_files(csv_path):
        if attribute is None:
            _move_after_processing(filepath, success=False)
            continue
        try:
            data = load_and_prepare_file(filepath, attribute)
            with engine.connect() as conn:
                method = _create_upsert_method(sqlalchemy.MetaData(conn))
                data.to_sql(TABLE_NAME, engine, if_exists="append", method=method, index=False)
        except Exception:
            _move_after_processing(filepath, success=False)
            raise
        _move_after_processing(filepath, success=True)


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


def _move_after_processing(filepath, success):
    archive_dir = SUCCESS_DIR if success else FAIL_DIR
    new_dir = os.path.dirname(filepath).replace(
        "receiving", archive_dir)
    os.makedirs(new_dir, exist_ok=True)
    move(filepath, filepath.replace("receiving", archive_dir))
    print(f"{filepath} moved to {archive_dir}")


def _create_upsert_method(meta):
    def method(table, conn, keys, data_iter):
        sql_table = sqlalchemy.Table(table.name, meta, autoload=True)
        insert_stmt = sqlalchemy.dialects.mysql.insert(sql_table).values([dict(zip(keys, data)) for data in data_iter])
        upsert_stmt = insert_stmt.on_duplicate_key_update({x.name: x for x in insert_stmt.inserted})
        conn.execute(upsert_stmt)
    return method


if __name__ == "__main__":
    main()
