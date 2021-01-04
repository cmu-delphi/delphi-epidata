import os
import urllib.request
import pandas as pd
from delphi.epidata.acquisition.mobility.database import database

url = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"
directory = 'Google_Mobility'


def get_mobility_data():
    """Download Google Mobility data in CSV format
    """
    # create directory if it don't exist
    if not os.path.exists(directory) and directory != '':
        os.makedirs(directory)
    else:
        files = os.listdir(directory)
        for file in files:
            os.remove(directory + '/' + file)

    urllib.request.urlretrieve(url, os.path.join(directory, "google_mobility_data_US.csv"))


def build_report():
    """Build cleaned Google report
    """
    mobilityData = pd.read_csv(os.path.join(directory, "google_mobility_data_US.csv"), low_memory=False)
    mobilityData.columns = mobilityData.columns.str.replace(
        r'_percent_change_from_baseline', '')
    mobilityData.columns = mobilityData.columns.str.replace(r'_', ' ')
    mobilityData = mobilityData.rename(columns={'country region': 'country'})
    mobilityData = mobilityData[(mobilityData['country'] == "United States")]
    mobilityData = mobilityData.rename(
        columns={
            'sub region 1': 'state',
            'sub region 2': 'county'})
    mobilityData = mobilityData.loc[:,
                   ['state',
                    'county',
                    'date',
                    'retail and recreation',
                    'grocery and pharmacy',
                    'parks',
                    'transit stations',
                    'workplaces',
                    'residential']]
    mobilityData['state'].fillna('Total', inplace=True)
    mobilityData['county'].fillna('Total', inplace=True)
    mobilityData.fillna(0, inplace=True)
    return mobilityData


def split_df(df, size):
    """Split df and insert into database.
    """
    db = database.Database()
    for i in range(0, df.shape[0], size):
        start = i
        end = min(i + size - 1, df.shape[0])
        subset = df.iloc[start:end]
        db.insert_google_data(subset)


if __name__ == '__main__':
    # get Google data
    get_mobility_data()
    # build reports
    mobilityData_US = build_report()
    # Insert into database
    split_df(mobilityData_US, 100000)
