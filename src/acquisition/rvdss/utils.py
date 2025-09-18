import requests
import pandas as pd
import io
import regex as re
from epiweeks import Week
from datetime import datetime
import math
from unidecode import unidecode
import string
import numpy as np

from delphi.epidata.acquisition.rvdss.constants import (
        VIRUSES, GEOS, REGIONS, NATION,PROVINCES,
        DASHBOARD_DATA_FILE
    )

 #%% Functions
def abbreviate_virus(full_name):
    """Abbreviate viruses and make them lowercase """
    
    lowercase=full_name.lower()
    keys = (re.escape(k) for k in VIRUSES.keys())
    pattern = re.compile(r'\b(' + '|'.join(keys) + r')\b')
    result = pattern.sub(lambda x: VIRUSES[x.group()], lowercase)
    return(result)

def abbreviate_geo(full_name):
    """Abbreviate provincial geo_values and make spelling consistent (i.e. removing extra spaces)"""
    lowercase=full_name.lower()
    lowercase = re.sub("province of ","",lowercase)
    lowercase=re.sub(r"\.|\*","",lowercase)
    lowercase=re.sub("/territoires","",lowercase)
    lowercase=re.sub("^cana$","can",lowercase)
    lowercase =lowercase.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation),'.'+"'"))
    lowercase=re.sub("kidshospital","kids hospital",lowercase)
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
    lowercase_geo = geo.lower()
    if lowercase_geo in NATION:
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
    update_date_url =  base_url + "RVD_UpdateDate.csv"
    update_date_url_response = requests.get(update_date_url, headers=headers)
    
    pattern1= re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    pattern2= re.compile("[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}")
    
    if pattern1.match(update_date_url_response.text):
        update_date = datetime.strptime(update_date_url_response.text,"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    elif pattern2.match(update_date_url_response.text):
        update_date = datetime.strptime(update_date_url_response.text,"%m/%d/%Y %H:%M:%S").strftime("%Y-%m-%d")
    
    return(update_date)

def check_most_recent_update_date(date,date_file):
    with open(date_file) as file:
        current_date = date
        contents = file.read()

    already_updated = current_date in contents
    return(already_updated)

def preprocess_table_columns(table):
    """
    Remove characters like . or * from columns
    Abbreviate the viruses in columns
    Change some naming of signals in columns (i.e order of hpiv and other)
    Change some naming of locations in columns (i.e at instead of atl)
    """
    table.columns = [re.sub("\xa0"," ", col) for col in table.columns] # \xa0 to space
    table.columns = [re.sub(r"(.*?)(\.\d+)", "\\1", c) for c in table.columns] # remove .# for duplicated columns
    table.columns =[re.sub(r"\.", "", s)for s in table.columns] #remove periods
    table.columns =[re.sub(r"\((all)\)", "", s)for s in table.columns] # remove (all)
    table.columns =[re.sub(r"\s*\(|\)", "", s)for s in table.columns] # remove ( )
    table.columns = [re.sub(' +', ' ', col) for col in table.columns] # Make any muliple spaces into one space
    table.columns = [re.sub(r'\(|\)', '', col) for col in table.columns]
    table.columns = [re.sub(r'/', '_', col) for col in table.columns] # replace / with _

    table.columns = [re.sub(r"^at\b","atl",t) for t in table.columns]
    table.columns = [re.sub("canada","can",t) for t in table.columns]
    table.columns = [re.sub(r"\bcb\b","bc",t) for t in table.columns]

    table.columns =[re.sub(r"h1n1 2009 |h1n12009|a_h1|ah1\b|ah1pdm09", "ah1n1pdm09", s)for s in table.columns]
    table.columns =[re.sub(r"a_uns", "auns", s)for s in table.columns]
    table.columns =[re.sub(r"a_h3", "ah3", s)for s in table.columns]

    table.columns =[abbreviate_virus(col) for col in table.columns] # abbreviate viruses
    table.columns = [re.sub(r"flu a","flua",t) for t in table.columns]
    table.columns = [re.sub(r"flu b","flub",t) for t in table.columns]
    table.columns = [re.sub(r"flutest\b","flu test", col) for col in table.columns]
    table.columns = [re.sub(r"other hpiv|other_hpiv|hpiv_other","hpivother",t) for t in table.columns]

    table.columns=[re.sub(r'bpositive','b_positive',c) for c in table.columns]
    table.columns=[re.sub(r'apositive','a_positive',c) for c in table.columns]
    table.columns=[re.sub(r'hpiv_1','hpiv1',c) for c in table.columns]
    table.columns=[re.sub(r'hpiv_2','hpiv2',c) for c in table.columns]
    table.columns=[re.sub(r'hpiv_3','hpiv3',c) for c in table.columns]
    table.columns=[re.sub(r'hpiv_4','hpiv4',c) for c in table.columns]

    table.columns=[make_signal_type_spelling_consistent(col) for col in table.columns]
    return(table)

def add_flu_prefix(flu_subtype):
    """ Add the prefix `flu` when only the subtype is reported """

    pat1 =r"^ah3"
    pat2= r"^auns"
    pat3= r"^ah1pdm09"
    pat4= r"^ah1n1pdm09"
    combined_pat = '|'.join((pat1, pat2,pat3,pat4))

    full_fluname = re.sub(combined_pat, r"flu\g<0>",flu_subtype)
    return(full_fluname)

def make_signal_type_spelling_consistent(signal):
    """
    Make the signal type (i.e. percent positive, number tests, total tests) have consistent spelling
    Also remove total from signal names
    """

    pat1 = r"positive\b"
    pat2 = r'pos\b'
    combined_pat = '|'.join((pat1, pat2))

    pat3 = r"test\b"
    pat4 = 'tested'
    combined_pat2 = '|'.join((pat3, pat4))

    new_signal = re.sub("positive tests", "positive_tests",signal)
    new_signal = re.sub(combined_pat, "positive_tests",new_signal)
    new_signal = re.sub(combined_pat2, "tests",new_signal)
    new_signal =re.sub(" *%", "_pct_positive",new_signal)
    new_signal = re.sub("total ", "",new_signal)
    return(new_signal)

def get_positive_data(base_url,headers,update_date):
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
    df['region'] = [abbreviate_geo(g) for g in df['region']]
    
    #df=df.drop(["weekorder","region","year","week"],axis=1)

    df = df.pivot(index=['epiweek','time_value','issue','geo_type','geo_value','region','week','weekorder','year'],
                  columns="virus",values=['tests','percentpositive','positivetests'])

    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    df = df.rename(columns=lambda x: '_'.join(x.split('_')[1:]+x.split('_')[:1]))
    df.columns = [re.sub(r'/', '', col) for col in df.columns] # replace / with _
    df.columns = [re.sub(r"flu a","flua",t) for t in df.columns]
    df.columns = [re.sub(r"flu b","flub",t) for t in df.columns]
    df.columns=[re.sub("positivetests", "positive_tests",col) for col in df.columns]
    df.columns=[re.sub("percentpositive", "pct_positive",col) for col in df.columns]
    df.columns=[re.sub(r' ','_',c) for c in df.columns]

    for k in range(len(df.columns)):
        if "pct_positive" in df.columns[k]:
            assert all([0 <= val <= 100 or math.isnan(val) for val in  df[df.columns[k]]]), "Percentage not from 0-100"

    df = df.reset_index()
    return(df.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'],verify_integrity=True))

def get_detections_data(base_url,headers,update_date):
    # Get weekly data
    detections_url = base_url + "RVD_CurrentWeekTable.csv"
    detections_url_response = requests.get(detections_url, headers=headers)
    detections_url_response.encoding='UTF-8'
    df_detections = pd.read_csv(io.StringIO(detections_url_response.text))
    
    if ("date" in df_detections.columns):
        df_detections["year"] = [int(re.search(r"20\d{2}", w).group(0)) for w in  df_detections["date"]] 
        ew = df_detections.apply(lambda x: Week(x['year'],x['week']),axis=1)
        df_detections.insert(0,"epiweek",[int(str(w)) for w in ew])
        df_detections['epiweek'] = [int(str(w)) for w in df_detections['epiweek']]
    else:
        #Get current week and year
        summary_url =  base_url + "RVD_SummaryText.csv"
        summary_url_response = requests.get(summary_url, headers=headers)
        summary_df = pd.read_csv(io.StringIO(summary_url_response.text))
        week_df = summary_df[(summary_df['Section'] == "summary") & (summary_df['Type']=="title")]
        week_string = week_df.iloc[0]['Text'].lower()
        current_week = int(re.search("week (.+?) ", week_string).group(1))
        current_year= int(re.search(r"20\d{2}", week_string).group(0))
        current_epiweek= Week(current_year,current_week)
        df_detections['epiweek'] = int(str(current_epiweek))
        df_detections['date'] = current_epiweek.enddate()


    # swap order of names from a_b to b_a
    df_detections = df_detections.rename(columns=lambda x: '_'.join(x.split('_')[1:]+x.split('_')[:1]))
    df_detections.insert(2,"issue",update_date)
    df_detections=preprocess_table_columns(df_detections)
    df_detections.columns=[re.sub(r' ','_',c) for c in df_detections.columns]
    
    df_detections=df_detections.rename(columns={'reportinglaboratory':"geo_value",'date':"time_value"})
    df_detections['geo_value'] = [abbreviate_geo(g) for g in df_detections['geo_value']]
    df_detections['geo_type'] = [create_geo_types(g,"lab") for g in df_detections['geo_value']]

    return(df_detections.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'],verify_integrity=True))

def expand_detections_columns(new_data):
    # add extra columns - percent positivities
    if "adv_positive_tests" in new_data.columns and "adv_tests" in new_data.columns:
        new_data["adv_pct_positive"] =  np.divide(new_data["adv_positive_tests"], new_data["adv_tests"], 
                      out=np.zeros_like(new_data["adv_positive_tests"],dtype=float), 
                      where=new_data["adv_tests"]!=0)*100
        
    if "evrv_positive_tests" in new_data.columns and "evrv_tests" in new_data.columns:
        new_data["evrv_pct_positive"] =  np.divide(new_data["evrv_positive_tests"], new_data["evrv_tests"], 
                      out=np.zeros_like(new_data["evrv_positive_tests"],dtype=float), 
                      where=new_data["evrv_tests"]!=0)*100
    
    if "flu_positive_tests" in new_data.columns and "flu_tests" in new_data.columns:
        new_data["flu_pct_positive"] =  np.divide(new_data["flu_positive_tests"], new_data["flu_tests"], 
                      out=np.zeros_like(new_data["flu_positive_tests"],dtype=float), 
                      where=new_data["flu_tests"]!=0)*100
        
    if "sarscov2_positive_tests" in new_data.columns and "sarscov2_tests" in new_data.columns:
        new_data["sarscov2_pct_positive"] =  np.divide(new_data["sarscov2_positive_tests"], new_data["sarscov2_tests"], 
                      out=np.zeros_like(new_data["sarscov2_positive_tests"],dtype=float), 
                      where=new_data["sarscov2_tests"]!=0)*100
    
    if "flua_positive_tests" in new_data.columns and "flub_positive_tests" in new_data.columns:
        new_data["flua_tests"] =  new_data["flu_tests"]
        new_data["flub_tests"] =  new_data["flu_tests"]
        
        new_data["flua_pct_positive"] =  np.divide(new_data["flua_positive_tests"], new_data["flu_tests"], 
                      out=np.zeros_like(new_data["flua_positive_tests"],dtype=float), 
                      where=new_data["flu_tests"]!=0)*100
        
        new_data["flub_pct_positive"] =  new_data["flub_positive_tests"]/new_data["flu_tests"]*100
        new_data["flub_pct_positive"] =  np.divide(new_data["flub_positive_tests"], new_data["flu_tests"], 
                      out=np.zeros_like(new_data["flub_positive_tests"],dtype=float), 
                      where=new_data["flu_tests"]!=0)*100
        
    if "hcov_positive_tests" in new_data.columns and "hcov_tests" in new_data.columns:
        new_data["hcov_pct_positive"] =  np.divide(new_data["hcov_positive_tests"], new_data["hcov_tests"], 
                      out=np.zeros_like(new_data["hcov_positive_tests"],dtype=float), 
                      where=new_data["hcov_tests"]!=0)*100
   
    if "hmpv_positive_tests" in new_data.columns and "hmpv_tests" in new_data.columns: 
       new_data["hmpv_pct_positive"] =  np.divide(new_data["hmpv_positive_tests"], new_data["hmpv_tests"], 
                     out=np.zeros_like(new_data["hmpv_positive_tests"],dtype=float), 
                     where=new_data["hmpv_tests"]!=0)*100
   
    if "rsv_positive_tests" in new_data.columns and "rsv_tests" in new_data.columns:
        new_data["rsv_pct_positive"] =  np.divide(new_data["rsv_positive_tests"], new_data["rsv_tests"], 
                      out=np.zeros_like(new_data["rsv_positive_tests"],dtype=float), 
                      where=new_data["rsv_tests"]!=0)*100
    
    if "hpiv1_positive_tests" in new_data.columns and "hpiv_tests" in new_data.columns:
        new_data["hpiv_positive_tests"] =  new_data["hpiv1_positive_tests"] + new_data["hpiv2_positive_tests"]+ new_data["hpiv3_positive_tests"]+new_data["hpiv4_positive_tests"]+new_data["hpivother_positive_tests"]
    
        new_data["hpiv_pct_positive"] =  np.divide(new_data["hpiv_positive_tests"], new_data["hpiv_tests"], 
                      out=np.zeros_like(new_data["hpiv_positive_tests"],dtype=float), 
                      where=new_data["hpiv_tests"]!=0)*100
        
    return(new_data.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value']))

def duplicate_provincial_detections(data):
    dat = data.copy(deep=True)
    dat = dat.reset_index()
    
    # provincial data
    dat.loc[dat['geo_value'].isin(PROVINCES),'geo_type'] = "province" 
    provincial_detections = dat.loc[dat['geo_value'].isin(PROVINCES)]
    
    if not provincial_detections.empty:
        #provincial_detections['geo_type']="province"
        
        provincial_detections = provincial_detections.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        new_data = pd.concat([data,provincial_detections])  
    else:
        new_data = dat.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
    
    return(new_data)

def combine_tables(data_dict):
    if(set(data_dict.keys()) == set({"positive","respiratory_detection"})):
        positive=data_dict["positive"] 
        detections=data_dict["respiratory_detection"]
        
        positive["epiweek"] = pd.to_numeric(positive["epiweek"],downcast="integer")
        positive["time_value"] = pd.to_datetime(positive["time_value"])
        positive["issue"] = pd.to_datetime(positive["issue"])

        detections["epiweek"] = pd.to_numeric(detections["epiweek"],downcast="integer")
        detections["time_value"] = pd.to_datetime(detections["time_value"])
        detections["issue"] = pd.to_datetime(detections["issue"])

        detections = expand_detections_columns(detections)
        positive = positive.drop(['geo_type'], axis=1)
        positive['geo_type'] = [create_geo_types(g,'lab') for g in positive['geo_value']]
        positive=positive.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        
        positive = positive.fillna(np.nan)
        detections = detections.fillna(np.nan)
        
        t = detections.merge(positive, how='outer', left_index=True,right_index=True)
        cols = set(positive.columns.to_list()+detections.columns.to_list())

        for col in cols:
            colx = col + "_x"
            coly = col + "_y"
            
            if colx in t.columns and coly in t.columns:
                t[col] = np.where(np.isnan(t[colx]), t[coly], t[colx])
                t = t.drop([colx, coly],axis=1)
                
        table = duplicate_provincial_detections(t)
    else:
        raise ValueError("Unexpected dictonary keys")
        
    return(table)
        
def fetch_archived_dashboard_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    update_date = get_dashboard_update_date(url, headers)
    detections_data = get_detections_data(url,headers,update_date)
    positive_data = get_positive_data(url,headers,update_date)

    return {
        "respiratory_detection": detections_data,
        "positive": positive_data,
        # "count": None, # Dashboards don't contain this data.
    }

def fetch_current_dashboard_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    update_date = get_dashboard_update_date(url, headers)
    detections_data = get_detections_data(url,headers,update_date)
    return(detections_data)
