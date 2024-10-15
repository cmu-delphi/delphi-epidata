"""
Defines command line interface for the rvdss indicator. Current data (covering the most recent epiweek) and historical data (covering all data before the most recent epiweek) can be generated together or separately.

Defines top-level functions to fetch data and save to disk or DB.
"""

import pandas as pd
import os

from delphi.epidata.acquisition.rvdss.utils import get_weekly_data, get_revised_data, get_dashboard_update_date
from delphi.epidata.acquisition.rvdss.constants import DASHBOARD_BASE_URL, RESP_DETECTIONS_OUTPUT_FILE, POSITIVE_TESTS_OUTPUT_FILE, COUNTS_OUTPUT_FILE


def update_current_data():
    ## TODO: what is the base path for these files?
    base_path = "."

    data_dict = fetch_dashboard_data(DASHBOARD_BASE_URL, 2024)

    table_types = {
        "respiratory_detection": RESP_DETECTIONS_OUTPUT_FILE,
        "positive": POSITIVE_TESTS_OUTPUT_FILE,
        # "count": COUNTS_OUTPUT_FILE, # Dashboards don't contain this data.
    }
    for tt in table_types.keys():
        data = data_dict[table_types]

        # Write the tables to separate csvs
        path = base_path + "/" + table_types[tt]

        # Since this function generates new data weekly, we need to combine it with the existing data, if it exists.
        if not os.path.exists(path):
            data.to_csv(path,index=True)
        else:
            old_data = pd.read_csv(path).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

            # If index already exists in the data on disk, don't add the new data -- we may have already run the weekly data fetch.
            ## TODO: The check on index maybe should be stricter? Although we do deduplication upstream, so this probably won't find true duplicates
            if not data.index.isin(old_data.index).any():
                old_data= pd.concat([old_data,data],axis=0)
                old_data.to_csv(path,index=True)

        # ## TODO
        # update_database(data)


def update_historical_data():
    ## TODO: what is the base path for these files?
    base_path = "."

    report_dict_list = fetch_report_data()
    dashboard_dict_list = fetch_historical_dashboard_data()

    table_types = {
        "respiratory_detection": RESP_DETECTIONS_OUTPUT_FILE,
        "positive": POSITIVE_TESTS_OUTPUT_FILE,
        "count": COUNTS_OUTPUT_FILE,
    }
    for tt in table_types.keys():
        # Merge tables together from dashboards and reports for each table type.
        dashboard_data = [elem.get(tt, None) for elem in dashboard_dict_list]
        report_data = [elem.get(tt, None) for elem in report_dict_list]
        data = [report_data, dashboard_data].concat()

        # Write the tables to separate csvs
        data.to_csv(base_path +"/" + table_types[tt], index=True)

        # ## TODO
        # update_database(data)


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    # fmt: off
    parser.add_argument(
        "--current",
        "-c",
        action="store_true",
        help="fetch current data, that is, data for the latest epiweek"
    )
    parser.add_argument(
        "--historical",
        "-h",
        action="store_true",
        help="fetch historical data, that is, data for all available time periods other than the latest epiweek"
    )
    # fmt: on
    args = parser.parse_args()

    current_flag, historical_flag = (
        args.current,
        args.historical,
    )
    if not current_flag and not historical_flag:
        raise Exception("no data was requested")

    # Decide what to update
    if current_flag:
        update_current_data()
    if historical_flag:
        update_historical_data()


if __name__ == "__main__":
    main()
