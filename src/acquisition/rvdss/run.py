"""
Defines command line interface for the rvdss indicator. Current data (covering the most recent epiweek) and historical data (covering all data before the most recent epiweek) can be generated together or separately.

Defines top-level functions to fetch data and save to disk or DB.
"""

import pandas as pd
import os
import argparse

from delphi.epidata.acquisition.rvdss.utils import fetch_dashboard_data, check_most_recent_update_date,get_dashboard_update_date, combine_tables, duplicate_provincial_detections,expand_detections_columns
from delphi.epidata.acquisition.rvdss.constants import DASHBOARD_BASE_URL, RESP_DETECTIONS_OUTPUT_FILE, POSITIVE_TESTS_OUTPUT_FILE, COUNTS_OUTPUT_FILE,UPDATE_DATES_FILE
from delphi.epidata.acquisition.rvdss.pull_historic import fetch_report_data,fetch_historical_dashboard_data
from delphi.epidata.acquisition.rvdss.database import respiratory_detections_cols, pct_positive_cols, detections_counts_cols, expected_table_names, expected_columns, get_num_rows, update

def update_current_data():
    ## Check if data for current update date has already been fetched
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    update_date = get_dashboard_update_date(DASHBOARD_BASE_URL, headers)
    already_updated = check_most_recent_update_date(update_date,UPDATE_DATES_FILE)

    if not already_updated:
        with open(UPDATE_DATES_FILE, 'a') as testfile:
            testfile.write(update_date+ "\n")

        data = fetch_current_dashboard_data(DASHBOARD_BASE_URL)
        # update database
        update(data)
    else:
        print("Data is already up to date")

def update_historical_data():
    report_dict_list = fetch_report_data() # a dict for every season, and every seasonal dict has 2/3 tables inside

    # a dict with an entry for every week that has an archival dashboard, and each entry has 2/3 tables
    dashboard_dict_list = fetch_historical_dashboard_data()
    

    table_types = {
    "respiratory_detection": RESP_DETECTIONS_OUTPUT_FILE,
    "positive": POSITIVE_TESTS_OUTPUT_FILE,
    "count": COUNTS_OUTPUT_FILE
    }
    
    hist_dict_list = {}
    for tt in table_types.keys():
        # Merge tables together from dashboards and reports for each table type.
        dashboard_data = [elem.get(tt, pd.DataFrame()) for elem in dashboard_dict_list] # a list of all the dashboard tables
        report_data = [elem.get(tt, None) for elem in report_dict_list] # a list of the report table

        all_report_tables = pd.concat(report_data)
        all_dashboard_tables = pd.concat(dashboard_data)
       
        if all_dashboard_tables.empty == False and all_report_tables.empty == False:
            all_dashboard_tables=all_dashboard_tables.reset_index()
            all_dashboard_tables=all_dashboard_tables.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

        hist_dict_list[tt] = pd.concat([all_report_tables, all_dashboard_tables])

    # Combine all rables into a single table
    data = combine_tables(hist_dict_list)
    
    #update database
    update(data)
    

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
        "-hist",
        action="store_true",
        help="fetch historical data, that is, data for all available time periods other than the latest epiweek"
    )
    parser.add_argument(
        "--patch",
        "-pat",
        action="store_true",
        help="path in the 2024-2025 season, which is unarchived and must be obtained through a csv"
    )
    # fmt: on
    args = parser.parse_args()

    current_flag, historical_flag, patch_flag = (
        args.current,
        args.historical,
        args.patch
    )
    if not current_flag and not historical_flag and not patch_flag:
        raise Exception("no data was requested")

    # Decide what to update
    if current_flag:
        update_current_data()
    if historical_flag:
        update_historical_data()
    if patch_flag:
        # TODO: update from csv the 2024-2025 season


if __name__ == "__main__":
    main()
