import pandas as pd


def fetch_archived_dashboard_urls():
    ## TODO: paste in Christine's code for scraping this list https://health-infobase.canada.ca/respiratory-virus-detections/archive.html

def fetch_dashboard_data(url = None):
    """Get data from current or archived dashboard"""
    pass


def fetch_current_dashboard_data():
    return fetch_dashboard_data(DEFAULT_DASHBOARD_URL)

def update_current_data(start_date, end_date):
    data = fetch_current_dashboard_data()
    update_database(data)

def update_historical_data():
    report_dict_list = fetch_report_data()
    dashboard_dict_list = fetch_historical_dashboard_data()

    table_types = (
        "respiratory_detection",
        "positive",
        "count",
    )
    for tt in table_types:
        ## TODO: need to merge tables together from dashboards and reports. Expect 3 tables out.
        pass
        # ??
        data = [report_data, dashboard_data].concat()

    # Write the three tables to separate csvs
    all_respiratory_detection_tables.to_csv(path+"/" + RESP_COUNTS_OUTPUT_FILE, index=True)
    all_positive_tables.to_csv(path+"/" + POSITIVE_TESTS_OUTPUT_FILE, index=True)

    # Write the number of detections table to csv if it exists (i.e has rows)
    if len(all_number_tables) != 0:
        all_number_tables.to_csv(path+"/number_of_detections.csv", index=True)

    update_database(data)


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
