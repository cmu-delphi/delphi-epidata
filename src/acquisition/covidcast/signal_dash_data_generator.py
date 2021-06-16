"""Updates the signal dashboard data."""

# standard library
import argparse
import sys
import time
import datetime
import mysql.connector
import pandas as pd

from dataclasses import dataclass
from typing import Dict, List

# first party
import covidcast
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger


LOOKBACK_DAYS_FOR_COVERAGE = 28


@dataclass
class DashboardSignal:
    """Container class for information about dashboard signals."""

    db_id: int
    name: str
    source: str
    covidcast_signal: str
    latest_coverage_update: datetime.date
    latest_status_update: datetime.date


@dataclass
class DashboardSignalCoverage:
    """Container class for coverage of a dashboard signal"""

    signal_id: int
    date: datetime.date
    geo_type: str
    count: int


@dataclass
class DashboardSignalStatus:
    """Container class for status of a dashboard signal"""

    signal_id: int
    date: datetime.date
    latest_issue: datetime.date
    latest_time_value: datetime.date


class Database:
    """Storage for dashboard data."""

    DATABASE_NAME = "epidata"
    SIGNAL_TABLE_NAME = "dashboard_signal"
    STATUS_TABLE_NAME = "dashboard_signal_status"
    COVERAGE_TABLE_NAME = "dashboard_signal_coverage"

    def __init__(self, connector_impl=mysql.connector):
        """Establish a connection to the database."""

        u, p = secrets.db.epi
        self._connection = connector_impl.connect(host=secrets.db.host, user=u, password=p, database=Database.DATABASE_NAME)
        self._cursor = self._connection.cursor()

    def rowcount(self) -> int:
        """Get the last modified row count"""
        return self._cursor.rowcount

    def write_status(self, status_list: List[DashboardSignalStatus]) -> None:
        """Write the provided status to the database."""
        insert_statement = f"""INSERT INTO `{Database.STATUS_TABLE_NAME}`
            (`signal_id`, `date`, `latest_issue`, `latest_time_value`)
            VALUES
            (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                `latest_issue`=VALUES(`latest_issue`),
                `latest_time_value`=VALUES(`latest_time_value`)
            """
        status_as_tuples = [(x.signal_id, x.date, x.latest_issue, x.latest_time_value) for x in status_list]
        self._cursor.executemany(insert_statement, status_as_tuples)

        latest_status_dates: Dict[int, datetime.date] = {}
        for x in status_list:
            latest_status_date = latest_status_dates.get(x.signal_id)
            if not latest_status_date or x.date > latest_status_date:
                latest_status_dates[x.signal_id] = x.date
        latest_status_tuples = [(v, k) for k, v in latest_status_dates.items()]

        update_statement = f"""UPDATE `{Database.SIGNAL_TABLE_NAME}`
            SET `latest_status_update` = GREATEST(`latest_status_update`, %s)
            WHERE `id` =  %s
            """
        self._cursor.executemany(update_statement, latest_status_tuples)

        self._connection.commit()

    def write_coverage(self, coverage_list: List[DashboardSignalCoverage]) -> None:
        """Write the provided coverage to the database."""
        insert_statement = f"""INSERT INTO `{Database.COVERAGE_TABLE_NAME}`
            (`signal_id`, `date`, `geo_type`, `count`)
            VALUES
            (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `count` = VALUES(`count`)
            """
        coverage_as_tuples = [(x.signal_id, x.date, x.geo_type, x.count) for x in coverage_list]
        self._cursor.executemany(insert_statement, coverage_as_tuples)

        latest_coverage_dates: Dict[int, datetime.date] = {}
        oldest_coverage_dates: Dict[int, datetime.date] = {}
        for x in coverage_list:
            latest_coverage_date = latest_coverage_dates.get(x.signal_id)
            oldest_coverage_date = oldest_coverage_dates.get(x.signal_id)
            if not latest_coverage_date or x.date > latest_coverage_date:
                latest_coverage_dates[x.signal_id] = x.date
            if not oldest_coverage_date or x.date < oldest_coverage_date:
                oldest_coverage_dates[x.signal_id] = x.date

        latest_coverage_tuples = [(v, k) for k, v in latest_coverage_dates.items()]
        oldest_coverage_tuples = [(v, k) for k, v in oldest_coverage_dates.items()]

        update_statement = f"""UPDATE `{Database.SIGNAL_TABLE_NAME}`
            SET `latest_coverage_update` = GREATEST(`latest_coverage_update`, %s)
            WHERE `id` =  %s
            """
        self._cursor.executemany(update_statement, latest_coverage_tuples)

        delete_statement = f"""DELETE FROM `{Database.COVERAGE_TABLE_NAME}`
            WHERE `date` < %s
            AND `signal_id` = %s
            """
        self._cursor.executemany(delete_statement, oldest_coverage_tuples)

        self._connection.commit()

    def get_enabled_signals(self) -> List[DashboardSignal]:
        """Retrieve all enabled signals from the database"""
        select_statement = f"""SELECT `id`,
            `name`,
            `source`,
            `covidcast_signal`,
            `latest_coverage_update`,
            `latest_status_update`
            FROM `{Database.SIGNAL_TABLE_NAME}`
            WHERE `enabled`
            """
        self._cursor.execute(select_statement)
        enabled_signals: List[DashboardSignal] = []
        for result in self._cursor.fetchall():
            enabled_signals.append(DashboardSignal(db_id=result[0], name=result[1], source=result[2], covidcast_signal=result[3], latest_coverage_update=result[4], latest_status_update=result[5]))
        return enabled_signals


def get_argument_parser():
    """Define command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", help="filename for log output")
    return parser


def get_latest_issue_from_metadata(dashboard_signal: DashboardSignal, metadata: pd.DataFrame) -> datetime.date:
    """Get the most recent issue date for the signal."""
    df_for_source: pd.DataFrame = metadata[(metadata.data_source == dashboard_signal.source) & (metadata.signal == dashboard_signal.covidcast_signal)]
    max_issue = df_for_source["max_issue"].max()
    return pd.to_datetime(str(max_issue), format="%Y%m%d").date()


def get_latest_time_value_from_metadata(dashboard_signal: DashboardSignal, metadata: pd.DataFrame) -> datetime.date:
    """Get the most recent date with data for the signal."""
    df_for_source: pd.DataFrame = metadata[(metadata.data_source == dashboard_signal.source) & (metadata.signal == dashboard_signal.covidcast_signal)]
    return df_for_source["max_time"].max().date()


def get_coverage(dashboard_signal: DashboardSignal, metadata: pd.DataFrame) -> List[DashboardSignalCoverage]:
    """Get the most recent coverage for the signal."""
    latest_time_value = get_latest_time_value_from_metadata(dashboard_signal, metadata)
    start_day = latest_time_value - datetime.timedelta(days=LOOKBACK_DAYS_FOR_COVERAGE)
    latest_data: pd.DataFrame = covidcast.signal(dashboard_signal.source, dashboard_signal.covidcast_signal, end_day=latest_time_value, start_day=start_day)
    latest_data_without_megacounties: pd.DataFrame = latest_data[~latest_data["geo_value"].str.endswith("000")]
    count_by_geo_type_df = latest_data_without_megacounties.groupby(["geo_type", "data_source", "time_value", "signal"]).size().to_frame("count").reset_index()

    signal_coverage_list: List[DashboardSignalCoverage] = []

    for _, row in count_by_geo_type_df.iterrows():
        signal_coverage = DashboardSignalCoverage(signal_id=dashboard_signal.db_id, date=row["time_value"].date(), geo_type=row["geo_type"], count=row["count"])
        signal_coverage_list.append(signal_coverage)

    return signal_coverage_list


def main(args):
    """Generate data for the signal dashboard.

    `args`: parsed command-line arguments
    """
    log_file = None
    if args:
        log_file = args.log_file

    logger = get_structured_logger("signal_dash_data_generator", filename=log_file, log_exceptions=False)
    start_time = time.time()

    database = Database()

    signals_to_generate = database.get_enabled_signals()
    logger.info("Starting generating dashboard data.", enabled_signals=[signal.name for signal in signals_to_generate])

    metadata: pd.DataFrame = covidcast.metadata()

    signal_status_list: List[DashboardSignalStatus] = []
    coverage_list: List[DashboardSignalCoverage] = []

    for dashboard_signal in signals_to_generate:
        latest_issue = get_latest_issue_from_metadata(dashboard_signal, metadata)
        latest_time_value = get_latest_time_value_from_metadata(dashboard_signal, metadata)
        latest_coverage = get_coverage(dashboard_signal, metadata)

        signal_status_list.append(DashboardSignalStatus(signal_id=dashboard_signal.db_id, date=datetime.date.today(), latest_issue=latest_issue, latest_time_value=latest_time_value))
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

    logger.info("Generated signal dashboard data", total_runtime_in_seconds=round(time.time() - start_time, 2))
    return True


if __name__ == "__main__":
    if not main(get_argument_parser().parse_args()):
        sys.exit(1)
