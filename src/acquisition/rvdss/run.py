import pandas as pd


def fetch_report_urls(season):
    """Get all report URLs from a season's report index page"""
    pass

## TODO: consider how to encode a "season" object, maybe as a tuple of start/end years `(2023, 2024)`, or a string `2023-2024`.
## TODO: I think there's already a fn for this that includes the loop and seasons
def fetch_one_season_from_report(season):
    report_urls = fetch_report_urls(season)
    df_list = [fetch_one_report(url) for url in report_urls]
    df = pd.concat(df_list)

    return df

def fetch_dashboard_data(url = None):
    """Get data from current or archived dashboard"""
    pass

def fetch_report_data():
    seasons = [...]

    # Fetch all reports made for all seasons.
    ## TODO: I think there's already a fn for this that includes the loop and seasons
    df_list = [fetch_one_season_from_report(season) for season in seasons]
    df = pd.concat(df_list)

    return df

def fetch_historical_dashboard_data():
    included_report_urls = fetch_archived_dashboard_urls()
    df_list = [fetch_dashboard_data(url) for url in included_report_urls]
    df = pd.concat(df_list)

    return df

def fetch_historical_dashboard_data():
    create/scrape all historical_dashboard_urls
    loop over urls:
        fetch_dashboard_data(historical_dashboard_url)

    df = pd.concat(df_list)

    return df

def fetch_current_dashboard_data():
    return fetch_dashboard_data(DEFAULT_DASHBOARD_URL)

def update_current_data(start_date, end_date):
  data = fetch_current_dashboard_data()
  update_database(data)

def update_historical_data():
  report_data = fetch_report_data()
  dashboard_data = fetch_historical_dashboard_data()

  data = [report_data, dashboard_data].concat()

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
