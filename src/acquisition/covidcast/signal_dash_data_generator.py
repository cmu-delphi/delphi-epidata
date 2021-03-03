"""Updates the cache for the `covidcast_meta` endpiont."""

# standard library
import argparse
import covidcast
import sys
import time
import datetime
import mysql.connector
import pandas as pd
from enum import Enum

# first party
from logger import get_structured_logger

class DashboardSignal(Enum):
    # TODO: store this in config file or DB table instead of enum
    CHANGE = ("change", "chng", 1)
    QUIDEL = ("quidel", "quidel", 2)

    def __init__(self, signal_name, source, db_id):
        self.signal_name = signal_name
        self.source = source
        self.db_id = db_id

class Database:
    """Storage for dashboard data."""

    DATABASE_NAME = 'epidata'
    STATUS_TABLE_NAME = 'dashboard_indicator_status'
    COVERAGE_TABLE_NAME = 'dashboard_indicator_coverage'

    def __init__(self, connector_impl=mysql.connector):
        """Establish a connection to the database."""
        self._connection = connector_impl.connect(
            host="localhost",
            user="test",
            password="test",
            database=Database.DATABASE_NAME)
        self._cursor = self._connection.cursor()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def disconnect(self, commit):
        """Close the database connection.

        commit: if true, commit changes, otherwise rollback
        """
        self._cursor.close()
        if commit:
            self._connection.commit()
            self._connection.close()
    
    def write_status(self, status_list):
        insert_statement = f'''INSERT INTO `{Database.STATUS_TABLE_NAME}` 
            (`indicator_id`, `date`, `latest_issue_date`, `latest_data_date`)
            VALUES
            (%s, %s, %s, %s)
            '''
        self._cursor.executemany(insert_statement, status_list)
        self.commit()

    def write_coverage(self, coverage_list):
        insert_statement = f'''INSERT INTO `{Database.COVERAGE_TABLE_NAME}` 
            (`indicator_id`, `date`, `geo_type`, `geo_value`)
            VALUES
            (%s, %s, %s, %s)
            '''
        self._cursor.executemany(insert_statement, coverage_list)
        self.commit()



def get_argument_parser():
    """Define command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", help="filename for log output")
    return parser


def get_latest_issue_date_from_metadata(dashboard_signal, metadata):
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    max_int = df_for_source["max_issue"].max()
    return pd.to_datetime(str(max_int), format="%Y%m%d")


def get_latest_data_date_from_metadata(dashboard_signal, metadata):
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    return df_for_source["max_time"].max().date()


def get_most_recent_issue_row_count(dashboard_signal, metadata):
    # TODO: Read database directly to calculate
    return None


def get_coverage(dashboard_signal, metadata):
    latest_data_date = get_latest_data_date_from_metadata(
        dashboard_signal, metadata)
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    # we need to do something smarter here -- make this part of config (and allow multiple signals) and/or
    # aggregate across all sources for a signal
    signal = df_for_source["signal"].iloc[0]
    latest_data = covidcast.signal(
        dashboard_signal.source,
        signal,
        end_day=latest_data_date,
        start_day=latest_data_date)
    coverage = latest_data[["time_value", "geo_type", "geo_value"]].head(10).copy()
    coverage['time_value'] = pd.to_datetime(coverage['time_value']).apply(lambda x: x.date())
    coverage.insert(0, 'signal_id', dashboard_signal.db_id)
    coverage_list = list(coverage.itertuples(index=False, name=None))
    return coverage_list


def get_dashboard_signals_to_generate():
    # TODO: read this from a config file or DB table
    return [DashboardSignal.CHANGE, DashboardSignal.QUIDEL]


def main(args):
    """Generate data for the signal dashboard.

    `args`: parsed command-line arguments
    """
    log_file = None
    if (args):
        log_file = args.log_file

    logger = get_structured_logger(
        "metadata_cache_updater",
        filename=log_file, log_exceptions=False)
    start_time = time.time()

    database = Database()

    signals_to_generate = get_dashboard_signals_to_generate()
    print(signals_to_generate)

    metadata = covidcast.metadata()

    signal_status_list = []
    coverage_list = []
    for dashboard_signal in signals_to_generate:
        latest_issue_date = get_latest_issue_date_from_metadata(
            dashboard_signal,
            metadata)
        latest_data_date = get_latest_data_date_from_metadata(
            dashboard_signal, metadata)
        latest_row_count = get_most_recent_issue_row_count(
            dashboard_signal, metadata)
        latest_coverage = get_coverage(dashboard_signal, metadata)

        signal_status_list.append(
            (dashboard_signal.db_id,
             datetime.date.today(),
             latest_issue_date,
             latest_data_date))
        coverage_list.extend(latest_coverage)

    print(coverage_list)
    try:
        database.write_status(signal_status_list)
    except mysql.connector.Error as e:
        logger.exception(e)
        
    try:
        database.write_coverage(coverage_list)
    except mysql.connector.Error as e:
        logger.exception(e)

    logger.info(
        "Generated signal dashboard data",
        total_runtime_in_seconds=round(time.time() - start_time, 2))
    return True


if __name__ == '__main__':
    if not main(get_argument_parser().parse_args()):
        sys.exit(1)
