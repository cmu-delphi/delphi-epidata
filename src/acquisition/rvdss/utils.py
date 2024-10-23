import requests
import pandas as pd
import io
import regex as re
from epiweeks import Week
from datetime import datetime
import math
from unidecode import unidecode
import string

from delphi.epidata.acquisition.rvdss.constants import (
        VIRUSES, GEOS, REGIONS, NATION, FIRST_WEEK_OF_YEAR,
        DASHBOARD_UPDATE_DATE_FILE, DASHBOARD_DATA_FILE
    )

def abbreviate_virus(full_name):
    lowercase=full_name.lower()
    keys = (re.escape(k) for k in VIRUSES.keys())
    pattern = re.compile(r'\b(' + '|'.join(keys) + r')\b')
    result = pattern.sub(lambda x: VIRUSES[x.group()], lowercase)
    return(result)

def abbreviate_geo(full_name):
    lowercase=full_name.lower()
    lowercase = re.sub("province of ","",lowercase)
    lowercase=re.sub("\.|\*","",lowercase)
    lowercase=re.sub("/territoires","",lowercase) 
    lowercase=re.sub("^cana$","can",lowercase)
    lowercase =lowercase.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation),'.'+"'"))
    lowercase=re.sub(' +', ' ', lowercase)
    
    new_name=unidecode(lowercase) 
    new_name=re.sub(' +', ' ', new_name)
    
    keys = (re.escape(k) for k in GEOS.keys())
    pattern = re.compile(r'^\b(' + '|'.join(keys) + r')\b$')

    result = pattern.sub(lambda x: GEOS[x.group()], new_name)
    
    if result == new_name:
        result = lowercase
    return(result)

def create_geo_types(geo,default_geo):
    if geo in NATION:
        geo_type="nation"
    elif geo in REGIONS:
        geo_type="region"
    else:
        geo_type = default_geo
    return(geo_type)

def check_date_format(date_string):
    if not re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}",date_string):
        if re.search(r"/",date_string):
            new_date = re.sub(r"/","-",date_string)
            new_date = datetime.strptime(new_date,"%d-%m-%Y").strftime("%Y-%m-%d")
        elif re.search("[0-9]{2}-[0-9]{2}-[0-9]{4}",date_string):
            new_date = datetime.strptime(date_string,"%d-%m-%Y").strftime("%Y-%m-%d")
        else:
            raise AssertionError("Unrecognised date format")
    else:
        new_date=date_string

    return(new_date)

def get_dashboard_update_date(base_url,headers):
    # Get update date
    update_date_url =  base_url + DASHBOARD_UPDATE_DATE_FILE
    update_date_url_response = requests.get(update_date_url, headers=headers)
    update_date = datetime.strptime(update_date_url_response.text,"%m/%d/%Y %H:%M:%S").strftime("%Y-%m-%d")
    return(update_date)
    
def get_revised_data(base_url,headers,update_date):
    # Get update data
    url = base_url+DASHBOARD_DATA_FILE

    url_response = requests.get(url, headers=headers)
    df = pd.read_csv(io.StringIO(url_response.text))
    
    df['virus'] = [abbreviate_virus(v) for v in df['virus']]
    epiw =  df.apply(lambda x: Week(x['year'],x['week']),axis=1)
    df.insert(0,"epiweek",[int(str(w)) for w in epiw])
    df['epiweek'] = [int(str(w)) for w in df['epiweek']]
    df['province'] = [abbreviate_geo(g) for g in df['province']]
    df=df.rename(columns={'province':"geo_value",'date':'time_value',"detections":"positivetests"})
    df['time_value'] = [check_date_format(d) for d in df['time_value']]
    df['geo_type'] = [create_geo_types(g,"province") for g in df['geo_value']]
    df.insert(1,"issue",update_date)
    
    #df=df.drop(["weekorder","region","year","week"],axis=1)
    
    df = df.pivot(index=['epiweek','time_value','issue','geo_type','geo_value'],
                  columns="virus",values=['tests','percentpositive','positivetests'])
    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    df = df.rename(columns=lambda x: '_'.join(x.split('_')[1:]+x.split('_')[:1]))
    df.columns=[re.sub("positivetests", "positive_tests",col) for col in df.columns]
    df.columns=[re.sub("percentpositive", "pct_positive",col) for col in df.columns]
    df.columns=[re.sub(r' ','_',c) for c in df.columns]
    
    for k in range(len(df.columns)):
        if "pct_positive" in df.columns[k]:
            assert all([0 <= val <= 100 or math.isnan(val) for val in  df[df.columns[k]]]), "Percentage not from 0-100"
    
    return(df)
    
## TODO: the `start_year` arg is making calling this complicated. If we know that LAST_WEEK_OF_YEAR (really, of the season) is always 35, then we should be able to derive `start_year` from `update_date`.
def get_weekly_data(base_url,headers,update_date):
    # Get current week and year
    summary_url =  base_url + "RVD_SummaryText.csv"
    summary_url_response = requests.get(summary_url, headers=headers)
    summary_df = pd.read_csv(io.StringIO(summary_url_response.text))
    
    week_df = summary_df[(summary_df['Section'] == "summary") & (summary_df['Type']=="title")]
    week_string = week_df.iloc[0]['Text'].lower()
    current_week = int(re.search("week (.+?) ", week_string).group(1))
    current_year= int(re.search("20\d{2}", week_string).group(0))

    '''
    if current_week < FIRST_WEEK_OF_YEAR:
        current_year = start_year+1
    else:
        current_year = start_year
    '''
        
    current_epiweek= Week(current_year,current_week)
   
    # Get weekly data
    weekly_url = base_url + "RVD_CurrentWeekTable.csv"
    weekly_url_response = requests.get(weekly_url, headers=headers)
    weekly_url_response.encoding='UTF-8'
    df_weekly = pd.read_csv(io.StringIO(weekly_url_response.text))
    
    df_weekly = df_weekly.rename(columns=lambda x: '_'.join(x.split('_')[1:]+x.split('_')[:1]))
    df_weekly.insert(0,"epiweek",int(str(current_epiweek)))
    df_weekly.insert(1,"time_value",str(current_epiweek.enddate()))
    df_weekly.insert(2,"issue",update_date)
    df_weekly.columns=[abbreviate_virus(c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'test\b','tests',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'pos\b','positive_tests',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'flua_','flu_a',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'flub_','flu_b',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'bpositive','b_positive',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'apositive','a_positive',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r'flu_ah1_','flu_ah1pdm09_',c) for c in df_weekly.columns]
    df_weekly.columns=[re.sub(r' ','_',c) for c in df_weekly.columns]
    df_weekly=df_weekly.rename(columns={'reportinglaboratory':"geo_value"})
    df_weekly['geo_value'] = [abbreviate_geo(g) for g in df_weekly['geo_value']]
    df_weekly['geo_type'] = [create_geo_types(g,"lab") for g in df_weekly['geo_value']]
    
   # if df_weekly.columns.isin(["weekorder","date","week"]).all():
    #    df_weekly=df_weekly.drop(["weekorder","date","week"],axis=1)

    return(df_weekly.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value']))

def fetch_dashboard_data(url):
    """Get data from current or archived dashboard"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    update_date = get_dashboard_update_date(url, headers)

    weekly_data = get_weekly_data(url,headers,update_date)
    positive_data = get_revised_data(url,headers,update_date)

    ## TODO: how to "weekly" and "positive" correspond to the dict keys ("respiratory_detection", "positive", "count") from historical reports? Need to make sure keys used here are from the same set.
    return {
        "respiratory_detection": weekly_data, ## TODO: ?
        "positive": positive_data,
        # "count": None, # Dashboards don't contain this data.
    }
