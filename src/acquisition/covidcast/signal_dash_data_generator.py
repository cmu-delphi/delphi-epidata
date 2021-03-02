"""Updates the cache for the `covidcast_meta` endpiont."""

# standard library
import argparse
import covidcast
import sys
import time
import datetime
from enum import Enum

# first party
from logger import get_structured_logger


class DashboardSignal(Enum):
    # TODO: store this in config file or DB table instead of enum
    CHANGE = ("change", "chng")
    QUIDEL = ("quidel", "quidel")

    def __init__(self, signal_name, source):
        self.signal_name = signal_name
        self.source = source


def get_argument_parser():
    """Define command line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", help="filename for log output")
    return parser


def get_latest_issue_date_from_metadata(dashboard_signal, metadata):
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    return df_for_source["max_issue"].max()


def get_latest_data_date_from_metadata(dashboard_signal, metadata):
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    return df_for_source["max_time"].max()


def get_most_recent_issue_row_count(dashboard_signal, metadata):
    # TODO: Read database directly to calculate
    return None


def get_coverage(dashboard_signal, metadata):
    latest_data_date = get_latest_data_date_from_metadata(
        dashboard_signal, metadata)
    df_for_source = metadata[metadata.data_source == dashboard_signal.source]
    # we need to do something smarter here -- both make this part of config (and allow multiple signals) and/or
    # aggregate across all sources for a signal
    signal = df_for_source["signal"].iloc[0]
    latest_data = covidcast.signal(
        dashboard_signal.source,
        signal,
        end_day=latest_data_date,
        start_day=latest_data_date)
    coverage = latest_data[["time_value", "geo_type", "geo_value"]].copy()
    coverage.insert(0, 'signal_name', dashboard_signal.signal_name)
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
            (dashboard_signal.signal_name,
             datetime.date.today(),
             latest_issue_date,
             latest_data_date,
             latest_row_count))
        coverage_list.append(latest_coverage)

    print(signal_status_list)
    print(coverage_list)

    # TODO: Insert signal_status_list and coverage_list into DB

    logger.info(
        "Generated signal dashboard data",
        total_runtime_in_seconds=round(time.time() - start_time, 2))
    return True


if __name__ == '__main__':
    if not main(get_argument_parser().parse_args()):
        sys.exit(1)
