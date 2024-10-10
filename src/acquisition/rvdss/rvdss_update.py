"""
Script to fetch new data, after data reporting moved to the dashboard
format. This covers dates following the 2023-2024 season (exclusive).
"""

import pandas as pd
import os

from delphi.epidata.acquisition.rvdss.utils import get_weekly_data, get_revised_data, get_dashboard_update_date
from delphi.epidata.acquisition.rvdss.constants import DASHBOARD_BASE_URL, RESP_COUNTS_OUTPUT_FILE, POSITIVE_TESTS_OUTPUT_FILE


def main():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    update_date = get_dashboard_update_date(DASHBOARD_BASE_URL,headers)
    weekly_data = get_weekly_data(DASHBOARD_BASE_URL,2024,headers,update_date).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
    positive_data = get_revised_data(DASHBOARD_BASE_URL,headers,update_date)

    path1 = './' + RESP_COUNTS_OUTPUT_FILE
    path2 = './' + POSITIVE_TESTS_OUTPUT_FILE

    if not os.path.exists(path1):
        weekly_data.to_csv(path1,index=True)
    else:
        old_detection_data = pd.read_csv(path1).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        if not weekly_data.index.isin(old_detection_data.index).any():
            old_detection_data= pd.concat([old_detection_data,weekly_data],axis=0)
            old_detection_data.to_csv(path1,index=True)

    if not os.path.exists(path2):
        positive_data.to_csv(path2,index=True)
    else:
        old_positive_data = pd.read_csv(path2).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        if not positive_data.index.isin(old_positive_data.index).any():
            old_positive_data= pd.concat([old_positive_data,positive_data],axis=0)
            old_positive_data.to_csv(path2,index=True)
    
if __name__ == '__main__':
    main()