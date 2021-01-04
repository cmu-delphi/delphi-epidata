import os
import urllib.request
import json
import pandas as pd
from delphi.epidata.acquisition.mobility.database import database

site_url = "https://covid19-static.cdn-apple.com"
index_url = "https://covid19-static.cdn-apple.com/covid19-mobility-data/current/v3/index.json"
directory = 'Apple_Mobility'


def get_mobility_link():
    """Get Apple Mobility data link
    """

    # get link
    with urllib.request.urlopen(index_url) as url:
        json_link = json.loads(url.read().decode())
        base_path = json_link['basePath']
        csv_path = json_link['regions']['en-us']['csvPath']
        link = site_url + \
               base_path + csv_path
    return link


def get_mobility_data():
    """Download Apple Mobility data in CSV format
    """
    # create directory if it don't exist
    if not os.path.exists(directory) and directory != '':
        os.makedirs(directory)
    else:
        files = os.listdir(directory)
        for file in files:
            os.remove(directory + '/' + file)

    urllib.request.urlretrieve(get_mobility_link(), os.path.join(directory, "apple_mobility_data_US.csv"))


def build_report():
    """Build cleaned mobility data
    """
    mobilityData = pd.read_csv(os.path.join(directory, "apple_mobility_data_US.csv"), low_memory=False)
    mobilityData = mobilityData.drop(columns=['alternative_name'])
    mobilityData['country'] = mobilityData.apply(
        lambda x: x['region'] if x['geo_type'] == 'country/region' else x['country'],
        axis=1)

    mobilityData = mobilityData[mobilityData.country == "United States"].drop(columns=[
        'country'])
    mobilityData['sub-region'] = mobilityData['sub-region'].fillna(
        mobilityData['region']).replace({"United States": "Total"})
    mobilityData['region'] = mobilityData.apply(lambda x: x['region'] if (
            x['geo_type'] == 'city' or x['geo_type'] == 'county') else 'Total', axis=1)
    mobilityData = mobilityData.rename(
        columns={
            'sub-region': 'state',
            'region': 'county_and_city'})

    mobilityData = mobilityData.melt(
        id_vars=[
            'geo_type',
            'state',
            'county_and_city',
            'transportation_type'],
        var_name='date')
    mobilityData['value'] = mobilityData['value'] - 100

    mobilityData = mobilityData.pivot_table(
        index=[
            'geo_type',
            'state',
            'county_and_city',
            'date'],
        columns='transportation_type').reset_index()
    mobilityData.columns = [t + (v if v != "value" else "")
                            for v, t in mobilityData.columns]

    mobilityData = mobilityData.loc[:, ['state', 'county_and_city', 'geo_type',
                                        'date', 'driving', 'transit', 'walking']]
    mobilityData = mobilityData.sort_values(
        by=['state', 'county_and_city', 'geo_type', 'date']).reset_index(drop=True)
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
        db.insert_apple_data(subset)


if __name__ == '__main__':
    # get data
    get_mobility_data()
    # build reports
    mobilityData_US = build_report()
    # insert into database
    split_df(mobilityData_US, 10000)
