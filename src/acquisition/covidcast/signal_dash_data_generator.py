"""Updates the signal dashboard data."""

# standard library
import argparse
import sys
import time
import datetime
import mysql.connector
import pandas as pd

from dataclasses import dataclass
from typing import List

# first party
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger
from delphi.epidata.client.delphi_epidata import Epidata


@dataclass
class DashboardSignal:
    """Container class for information about dashboard signals."""

    db_id: int
    name: str
    source: str


@dataclass
class DashboardSignalCoverage:
    """Container class for coverage of a dashboard signal"""

    signal_id: int
    date: datetime.date
    geo_type: str
    geo_value: str


@dataclass
class DashboardSignalStatus:
    """Container class for status of a dashboard signal"""

    signal_id: int
    date: datetime.date
    latest_issue: datetime.date
    latest_time_value: datetime.date


class Database:
    """Storage for dashboard data."""

    DATABASE_NAME = 'epidata'
    SIGNAL_TABLE_NAME = 'dashboard_signal'
    STATUS_TABLE_NAME = 'dashboard_signal_status'
    COVERAGE_TABLE_NAME = 'dashboard_signal_coverage'

    def __init__(self, connector_impl=mysql.connector):
        """Establish a connection to the database."""
        u, p = secrets.db.epi
        self._connection = connector_impl.connect(
            host=secrets.db.host,
            user=u,
            password=p,
            database=Database.DATABASE_NAME)
        self._cursor = self._connection.cursor()

    def rowcount(self) -> int:
        """Get the last modified row count"""
        return self._cursor.rowcount

    def write_status(self, status_list: List[DashboardSignalStatus]) -> None:
        """Write the provided status to the database."""
        insert_statement = f'''INSERT INTO `{Database.STATUS_TABLE_NAME}`
            (`signal_id`, `date`, `latest_issue`, `latest_time_value`)
            VALUES
            (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `latest_issue`=VALUES(`latest_issue`),
                `latest_time_value`=VALUES(`latest_time_value`)
            '''
        status_as_tuples = [
            (x.signal_id, x.date, x.latest_issue, x.latest_time_value)
            for x in status_list]
        self._cursor.executemany(insert_statement, status_as_tuples)
        self._connection.commit()

    def write_coverage(
            self, coverage_list: List[DashboardSignalCoverage]) -> None:
        """Write the provided coverage to the database."""
        insert_statement = f'''INSERT INTO `{Database.COVERAGE_TABLE_NAME}`
            (`signal_id`, `date`, `geo_type`, `geo_value`)
            VALUES
            (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `signal_id` = `signal_id`
            '''
        coverage_as_tuples = [
            (x.signal_id, x.date, x.geo_type, x.geo_value)
            for x in coverage_list]
        self._cursor.executemany(insert_statement, coverage_as_tuples)
        self._connection.commit()

    def get_enabled_signals(self) -> List[DashboardSignal]:
        """Retrieve all enabled signals from the database"""
        select_statement = f'''SELECT `id`, `name`, `source`
            FROM `{Database.SIGNAL_TABLE_NAME}`
            WHERE `enabled`
            '''
        self._cursor.execute(select_statement)
        enabled_signals = []
        for result in self._cursor.fetchall():
            enabled_signals.append(
                DashboardSignal(
                    db_id=result[0],
                    name=result[1],
                    source=result[2]))
        return enabled_signals


def get_argument_parser():
    """Define command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", help="filename for log output")
    return parser


def get_latest_issue_from_metadata(dashboard_signal, metadata):
    """Get the most recent issue date for the signal."""
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    max_issue = df_for_source["max_issue"].max()
    return pd.to_datetime(str(max_issue), format="%Y%m%d")


def get_latest_time_value_from_metadata(dashboard_signal, metadata):
    """Get the most recent date with data for the signal."""
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    return df_for_source["max_time"].max().date()


def get_coverage(dashboard_signal: DashboardSignal,
                 metadata) -> List[DashboardSignalCoverage]:
    """Get the most recent coverage for the signal."""
    latest_time_value = get_latest_time_value_from_metadata(
        dashboard_signal, metadata)
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    # we need to do something smarter here -- make this part of config
    # (and allow multiple signals) and/or aggregate across all signals
    # for a source
    signal = df_for_source["signal"].iloc[0]
    latest_data = Epidata.covidcast.signal(
        dashboard_signal.source,
        signal,
        end_day=latest_time_value,
        start_day=latest_time_value)

    signal_coverage_list = []
    for _, row in latest_data.iterrows():
        signal_coverage = DashboardSignalCoverage(
            signal_id=dashboard_signal.db_id,
            date=pd.to_datetime(
                row['time_value']).date(),
            geo_type=row['geo_type'],
            geo_value=row['geo_value'])
        signal_coverage_list.append(signal_coverage)

    return signal_coverage_list


def main(args):
    """Generate data for the signal dashboard.

    `args`: parsed command-line arguments
    """
    log_file = None
    if args:
        log_file = args.log_file

    logger = get_structured_logger(
        "signal_dash_data_generator",
        filename=log_file, log_exceptions=False)
    start_time = time.time()

    database = Database()

    signals_to_generate = database.get_enabled_signals()
    logger.info("Starting generating dashboard data.", enabled_signals=[
                signal.name for signal in signals_to_generate])

    metadata = Epidata.covidcast.metadata()

    signal_status_list: List[DashboardSignalStatus] = []
    coverage_list: List[DashboardSignalCoverage] = []

    for dashboard_signal in signals_to_generate:
        latest_issue = get_latest_issue_from_metadata(
            dashboard_signal,
            metadata)
        latest_time_value = get_latest_time_value_from_metadata(
            dashboard_signal, metadata)
        latest_coverage = get_coverage(dashboard_signal, metadata)

        signal_status_list.append(
            DashboardSignalStatus(
                signal_id=dashboard_signal.db_id,
                date=datetime.date.today(),
                latest_issue=latest_issue,
                latest_time_value=latest_time_value))
        coverage_list.extend(latest_coverage)

    try:
        database.write_status(signal_status_list)
        logger.info("Wrote status.", rowcount=database.rowcount())
    except mysql.connector.Error as exception:
        logger.exception(exception)

    try:
        database.write_coverage(coverage_list)
        logger.info("Wrote coverage.", rowcount=database.rowcount())
    except mysql.connector.Error as exception:
        logger.exception(exception)

    logger.info(
        "Generated signal dashboard data",
        total_runtime_in_seconds=round(time.time() - start_time, 2))
    return True


if __name__ == '__main__':
    if not main(get_argument_parser().parse_args()):
        sys.exit(1)
