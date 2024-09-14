import pandas as pd
import os
import utils

base_url = "https://health-infobase.canada.ca/src/data/respiratory-virus-detections/"

weekly_data = utils.get_weekly_data(base_url,2024).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
positive_data = utils.get_revised_data(base_url)

path1 = './season_2024_2025_respiratory_detections.csv'
path2 = './season_2024_2025_positive_tests.csv'

if os.path.exists(path1)==False:
    weekly_data.to_csv(path1,index=True)
else:
    old_detection_data = pd.read_csv(path1).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
    if weekly_data.index.isin(old_detection_data.index).any() == False:
        old_detection_data= pd.concat([old_detection_data,weekly_data],axis=0)
        old_detection_data.to_csv(path1,index=True)

if os.path.exists(path2)==False:
    positive_data.to_csv(path2,index=True)
else:
    old_positive_data = pd.read_csv(path2).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
    if positive_data.index.isin(old_positive_data.index).any() == False:
        old_positive_data= pd.concat([old_positive_data,positive_data],axis=0)
        old_positive_data.to_csv(path2,index=True)
    
   