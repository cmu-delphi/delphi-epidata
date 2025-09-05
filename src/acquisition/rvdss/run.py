"""
Defines command line interface for the rvdss indicator. Current data (covering the most recent epiweek) and historical data (covering all data before the most recent epiweek) can be generated together or separately.

Defines top-level functions to fetch data and save to disk or DB.
"""

import pandas as pd
import argparse
from datetime import datetime

from delphi.epidata.acquisition.rvdss.utils import fetch_current_dashboard_data, check_most_recent_update_date,get_dashboard_update_date, combine_tables, duplicate_provincial_detections,expand_detections_columns
from delphi.epidata.acquisition.rvdss.constants import DASHBOARD_BASE_URL, RESP_DETECTIONS_OUTPUT_FILE, POSITIVE_TESTS_OUTPUT_FILE,UPDATE_DATES_FILE
from delphi.epidata.acquisition.rvdss.pull_historic import fetch_report_data,fetch_historical_dashboard_data
from delphi.epidata.acquisition.rvdss.database import update
from delphi_utils import get_structured_logger

def update_current_data(logger):
    logger.info("Updating current data")
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
        
        # current dashboard only needs one table
        new_data = expand_detections_columns(data)
        new_data = duplicate_provincial_detections(new_data)
        
        # update database
        update(data,logger)
        logger.info("Finished updating current data")
    else:
        logger.info("Data is already up to date")
        

def update_historical_data(logger):
    logger.info("Updating historical data")
    
    report_dict_list = fetch_report_data() # a dict for every season, and every seasonal dict has 2/3 tables inside

    # a dict with an entry for every week that has an archival dashboard, and each entry has 2/3 tables
    dashboard_dict_list = fetch_historical_dashboard_data()
    

    table_types = {
    "respiratory_detection": RESP_DETECTIONS_OUTPUT_FILE,
    "positive": POSITIVE_TESTS_OUTPUT_FILE
    }
    
    hist_dict_list = {}
    for tt in table_types.keys():
        # Merge tables together from dashboards and reports for each table type.
        dashboard_data = [elem.get(tt, pd.DataFrame()) for elem in dashboard_dict_list] # a list of all the dashboard tables
        report_data = [elem.get(tt, pd.DataFrame()) for elem in report_dict_list] # a list of the report table

        all_dashboard_tables = pd.concat(dashboard_data)
        all_report_data = pd.concat(report_data)
        
        if all_dashboard_tables.empty == False and all_report_data.empty == False:
            all_dashboard_tables=all_dashboard_tables.reset_index()
            all_dashboard_tables=all_dashboard_tables.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

        hist_dict_list[tt] = pd.concat([all_report_data, all_dashboard_tables])
        
    # Combine all rables into a single table
    data = combine_tables(hist_dict_list)
    
    #update database
    update(data,logger)
    logger.info("Finished updating historic data")
    
def patch_seasons(season_start_years,logger):
    season_end_years = [y+1 for y in season_start_years]
    logger.info("Starting to Patch in Seasons")
    for start, end in zip(season_start_years, season_end_years):
        logger.info(f"Patching in data from the {start}-{end} season")
    
        if start >=2024:
            data = pd.read_csv(f"{start}_{end}_respiratory_detections.csv")
            
            # current dashboard only needs one table
            new_data = expand_detections_columns(data)
            new_data = duplicate_provincial_detections(new_data)
            
            #update database
            update(new_data,logger)
        else:
            resp_data = pd.read_csv(f"{start}_{end}_respiratory_detections.csv")
            pos_data = pd.read_csv(f"{start}_{end}_positive_tests.csv")
            data_dict={"positive":pos_data,"respiratory_detection":resp_data} 
            
            # Combine all rables into a single table
            data = combine_tables(data_dict)
            
            #update database
            update(data,logger)
        logger.info("Finished patching in {season[0]}-{season[1]} season")
    logger.info("Finished Patching in Seasons")

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
        help="patch in missings seasons, which are unarchived and must be obtained through csvs"
        # TODO: Look into passing a file name
    )
    # fmt: on
    args = parser.parse_args()

    current_flag, historical_flag, patch_flag = (
        args.current,
        args.historical,
        args.patch
    )
    
    # Create logger name, 'rvdss' + the current date
    logger_filename = "rvdss_"+datetime.today().strftime('%Y_%m_%d')+".log"
    
    logger = get_structured_logger(
            __name__,
            filename= logger_filename,
            log_exceptions=True,
        )
    
    if not current_flag and not historical_flag and not patch_flag:
        logger.error("no data was requested")
        raise Exception("no data was requested")

    # Decide what to update
    if current_flag:
        update_current_data(logger)
    if historical_flag:
        update_historical_data(logger)
    if patch_flag:
        patch_seasons(season_start_years=[2013,2014,2024], logger=logger)
        

if __name__ == "__main__":
    main()
