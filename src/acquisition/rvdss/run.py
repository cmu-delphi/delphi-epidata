"""
Defines command line interface for the rvdss indicator. Current data (covering the most recent epiweek) and historical data (covering all data before the most recent epiweek) can be generated together or separately.

Defines top-level functions to fetch data and save to disk or DB.
"""

import pandas as pd
import os
import argparse

from utils import fetch_dashboard_data, check_most_recent_update_date,get_dashboard_update_date
from constants import DASHBOARD_BASE_URL, RESP_DETECTIONS_OUTPUT_FILE, POSITIVE_TESTS_OUTPUT_FILE, COUNTS_OUTPUT_FILE,UPDATE_DATES_FILE
from pull_historic import fetch_report_data,fetch_historical_dashboard_data

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
    
        ## TODO: what is the base path for these files?
        base_path = "."
    
        data_dict = fetch_dashboard_data(DASHBOARD_BASE_URL)
    
        table_types = {
            "respiratory_detection": RESP_DETECTIONS_OUTPUT_FILE,
            "positive": POSITIVE_TESTS_OUTPUT_FILE,
            # "count": COUNTS_OUTPUT_FILE, # Dashboards don't contain this data.
        }
        for tt in table_types.keys():
            data = data_dict[tt]
    
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
    else:
        print("Data is already up to date")        
    
def update_historical_data():
    ## TODO: what is the base path for these files?
    base_path = "."

    report_dict_list = fetch_report_data() # a dict for every season, and every seasonal dict has 2/3 tables inside
    
    # a dict with an entry for every week that has an archival dashboard, and each entry has 2/3 tables
    dashboard_dict_list = fetch_historical_dashboard_data()

    table_types = {
        "respiratory_detection": RESP_DETECTIONS_OUTPUT_FILE,
        "positive": POSITIVE_TESTS_OUTPUT_FILE,
        "count": COUNTS_OUTPUT_FILE,
    }
    for tt in table_types.keys():
        # Merge tables together from dashboards and reports for each table type.
        dashboard_data = [elem.get(tt, pd.DataFrame()) for elem in dashboard_dict_list] # a list of all the dashboard tables
        report_data = [elem.get(tt, None) for elem in report_dict_list] # a list of the report table
        
        all_report_tables = pd.concat(report_data)
        all_dashboard_tables = pd.concat(dashboard_data)
        
        data = pd.concat([all_report_tables, all_dashboard_tables])
        
        # Write the tables to separate csvs
        if not data.empty:
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
        "-hist",
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
