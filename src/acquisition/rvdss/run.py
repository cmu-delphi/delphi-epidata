# TODO: this is pseudocode and may not run or may not run correctly

import pandas as pd

def fetch_report_urls(season):
    """Get all report URLs from a season's report index page"""
    pass

# TODO: consider how to encode a "season" object, maybe as a tuple of start/end years `(2023, 2024)`, or a string `2023-2024`.
def fetch_one_season_from_report(season):
    report_urls = fetch_report_urls(season)
    df_list = [fetch_one_report(url) for url in report_urls]
    df = pd.concat(df_list)

    return df

def fetch_one_dashboard(url = None):
    """Get data from current or archived dashboard"""
    # If no url is provided, fetch data from the current dashboard (whose URL is static).
    if not url:
        url = DEFAULT_DASHBOARD_URL

    # TODO: put rest of scraping code in here
    pass

def fetch_report_data(start_date, end_date):
    included_seasons = compute_seasons_in_range(start_date, end_date)

    # Fetch all reports made for each season.
    # We do this because fetching reports is pretty fast, and it saves us from
    # having to parse either URLs or text on the webpage. We will drop data
    # outside the requested range later.
    df_list = [fetch_one_season_from_report(season) for season in included_seasons]
    df = pd.concat(df_list)

    # Only keep data that was issued within the requested date range.
    df = df[start_date <= df.issue <= end_date]

    return df

def fetch_historical_dashboard_data(start_date, end_date):
    included_weeks = compute_weeks_in_range(start_date, end_date)
    included_report_urls = construct_archived_dashboard_urls(included_weeks)

    df_list = [fetch_one_dashboard(url) for url in included_report_urls]
    df = pd.concat(df_list)

    return df

def fetch_historical_dashboard_data(start_date, end_date):
    create all historical_dashboard_urls included in date range
    loop over urls:
        fetch_dashboard_data(historical_dashboard_url)

    included_seasons = compute_seasons_in_range(start_date, end_date)
    df_list = [fetch_one_season_from_report(season) for season in included_seasons]
    df = pd.concat(df_list)
    df = df[start_date <= df.issue <= end_date]

    return df

def fetch_current_dashboard_data():
    fetch_dashboard_data(current_dashboard_url)

def fetch_data(start_date, end_date):
  if (start_date, end_date) not exist:
    data = fetch_current_dashboard_data()
  else:
    early_range, late_range = split_date_range_by_dashboard_release_date(start_date, end_date)
    report_data = fetch_report_data(early_range)
    dashboard_data = fetch_historical_dashboard_data(late_range)

    data = [report_data, dashboard_data].concat()

  return data