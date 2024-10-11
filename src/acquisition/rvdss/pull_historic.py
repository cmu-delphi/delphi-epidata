"""
Script to fetch historical data, before data reporting moved to the dashboard
format. This covers dates from the 2014-2015 season to the 2023-2024 season.

This script should not be run in production; it will not fetch newly-posted
data.
"""

from bs4 import BeautifulSoup
import requests
import regex as re
import pandas as pd
from epiweeks import Week
from datetime import datetime, timedelta
import math

from delphi.epidata.acquisition.rvdss.constants import (
        DASHBOARD_BASE_URLS_2023_2024_SEASON, HISTORIC_SEASON_URLS,
        ALTERNATIVE_SEASON_BASE_URL, SEASON_BASE_URL, LAST_WEEK_OF_YEAR,
        RESP_COUNTS_OUTPUT_FILE, POSITIVE_TESTS_OUTPUT_FILE
    )
from delphi.epidata.acquisition.rvdss.utils import (
        abbreviate_virus, abbreviate_geo, create_geo_types, check_date_format,
        get_revised_data, get_weekly_data
    )
 #%% Functions
 
 # Report Functions
def get_report_season_years(soup):
    """Get the start year of the season and the year the season ends """
    # Find the url in the page html and get the years included in the season
    canonical_url = str(soup.find_all('link',rel="canonical"))
    # The season range is in YYYY-YYYY format
    matches = re.search("20[0-9]{2}-20[0-9]{2}",canonical_url)

    if matches:
        season = matches.group(0)
    years=season.split("-")
    return(years)

def add_https_prefix(urls):
    """ Add https to urls, and changes any http to https"""
    for i in range(len(urls)):
        temp_url = urls[i]
  
        http_present = re.search("http:",temp_url)
        if not http_present:
            urls[i]=SEASON_BASE_URL+temp_url
        else:
            urls[i]=re.sub("http:","https:",temp_url)
    return(urls)

def construct_weekly_report_urls(soup):
    """ Construct links for each week in a season"""
    year= "-".join(get_report_season_years(soup))
    links=soup.find_all('a')
    alternative_url = ALTERNATIVE_SEASON_BASE_URL+year
    
    urls = [link.get("href") for link in links if "ending" in str(link) or 
            alternative_url in str(link)]
    
    report_links = add_https_prefix(urls)
    return(report_links)

def report_weeks(soup):
    """ Get a list of all the weeks in a season"""
    links=soup.find_all('a')
    full_weeks = [link.text for link in links if "Week" in str(link)]
    weeks= [int(re.search('Week (.+?) ', week).group(1)) for week in full_weeks]
    return(weeks)

def get_report_date(week,start_year,epi=False):
    """
    Get the end date of the current reporting/epiweek
    
    week - the epidemiological week number
    start_year - the year the season starts in
    epi - if True, return the date in cdc format (yearweek)
    
    """
    if week < LAST_WEEK_OF_YEAR: 
        year=int(start_year)+1
    else:
        year=int(start_year)
    
    epi_week =  Week(year, week)
    
    if not epi:
        report_date = str(epi_week.enddate())
    else:
        report_date =  str(epi_week)
        
    return(report_date)

def extract_captions_of_interest(soup):
    """
    finds all the table captions for the current week so tables can be identified 
    
    The captions from the 'summary' tag require less parsing, but sometimes they
    are missing. In that case, use the figure captions
    """
    captions = soup.findAll('summary')
    
    table_identifiers = ["respiratory","number","positive","abbreviation"]
    
    # For every caption, check if all of the table identifiers are missing. If they are,
    # this means the caption is noninformative (i.e just says Figure 1). If any of the captions are 
    # noninformative, use the figure captions as captions
    if sum([all(name not in cap.text.lower() for name in table_identifiers) for cap in captions]) != 0:
        figcaptions = soup.findAll('figcaption')     
        captions = captions + figcaptions
        
    remove_list=[]
    for i in range(len(captions)):
        caption = captions[i]
        
        matches = ["period","abbreviation","cumulative", "compared"] #skip historic comparisons and cumulative tables
        # remove any captions with a class or that are uninformative 
        if any(x in caption.text.lower() for x in matches) or caption.has_attr('class') or all(name not in caption.text.lower() for name in table_identifiers): 
            remove_list.append(caption)
    
    new_captions = [cap for cap in captions if cap not in remove_list]
    new_captions = list(set(new_captions))
    
    return(new_captions)

def get_modified_dates(soup,week_end_date):
    """
    Get the date the report page was modfified

    Reports include both posted dates and modified dates. Fairly often on
    historical data reports, posted date falls before the end of the week
    being reported on. Then the page is modified later, presumably with
    updated full-week data. Therefore, we use the modified date as the issue
    date for a given report.
    """
    meta_tags=soup.find_all("meta",title="W3CDTF")
    for tag in meta_tags:
        if tag.get("name", None) == "dcterms.modified" or tag.get("property", None) == "dcterms.modified":
            modified_date = tag.get("content", None)

    mod_date = datetime.strptime(modified_date, "%Y-%m-%d")
    week_date = datetime.strptime(week_end_date, "%Y-%m-%d")
    
    diff_days = (mod_date-week_date).days
    
    # Manually create a new modified date if the existing one is too long after the week.
    # Historically, we commonly see data reports being modified ~5 days after
    # the end of the week being reported on. In some cases, though, the
    # modified date falls a long time (up to a year) after the end of the
    # week being reported on. We expect that any changes made to the report
    # at that point were primarily wording, and not data, changes. So if the
    # modified date is NOT within 0-14 days after the end of the week, set
    # the issue date to be 5 days after the end of the week.
    if diff_days > 0 and diff_days < 14:
        new_modified_date = mod_date
    else:
        new_lag = timedelta(days=5)
        new_modified_date = week_date + new_lag
    
    new_modified_date_string = new_modified_date.strftime("%Y-%m-%d")
    
    return(new_modified_date_string)


def deduplicate_rows(table):
    """
    Sometimes tables have more than one row for the same week
    In that case, keep the row that has the highest canada tests
    (i.e drop the rows with the lower counts)
    """
    if table['week'].duplicated().any():
       duplicated_rows = table[table.duplicated('week',keep=False)]
       grouped = duplicated_rows.groupby("week")
       duplicates_drop = []
       
       for name, group in grouped:
           duplicates_drop.append(group['can tests'].idxmin())
    
       new_table = table.drop(duplicates_drop).reset_index(drop=True)
       
    else:
        new_table=table
    return(new_table)

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
    
    pat1 = "positive"
    pat2 = 'pos'
    combined_pat = '|'.join((pat1, pat2))
    
    pat3 = r"test\b"
    pat4 = 'tested'
    combined_pat2 = '|'.join((pat3, pat4))
    
    new_signal = re.sub(combined_pat, "positive_tests",signal)
    new_signal = re.sub(combined_pat2, "positive_tests",signal)
    new_signal = re.sub("total ", "",signal)
    return(new_signal)

def preprocess_table_columns(table):
    """ 
    Remove characters like . or * from columns
    Abbreviate the viruses in columns
    Change some naming of signals in columns (i.e order of hpiv and other)
    Change some naming of locations in columns (i.e at instead of atl)
    """
    table.columns = [re.sub("\xa0"," ", col) for col in table.columns] # \xa0 to space
    table.columns = [re.sub("(.*?)(\.\d+)", "\\1", c) for c in table.columns] # remove .# for duplicated columns
    table.columns =[re.sub("\.", "", s)for s in table.columns] #remove periods
    table.columns =[re.sub(r"\((all)\)", "", s)for s in table.columns] # remove (all) 
    table.columns =[re.sub(r"\s*\(|\)", "", s)for s in table.columns]
    table.columns = [re.sub(' +', ' ', col) for col in table.columns] # Make any muliple spaces into one space
    table.columns = [re.sub(r'\(|\)', '', col) for col in table.columns] # replace () for _
    table.columns = [re.sub(r'/', '_', col) for col in table.columns] # replace / with _
    
    table.columns = [re.sub(r"^at\b","atl ",t) for t in table.columns]
    table.columns = [re.sub("canada","can",t) for t in table.columns]
    
    table.columns =[re.sub(r"h1n1 2009 |h1n12009", "ah1n1pdm09", s)for s in table.columns]
    table.columns =[abbreviate_virus(col) for col in table.columns] # abbreviate viruses
    table.columns = [re.sub(r"flu a","flua",t) for t in table.columns]
    table.columns = [re.sub(r"flu b","flub",t) for t in table.columns]
    table.columns = [re.sub("flutest","flu test", col) for col in table.columns]
    table.columns = [re.sub(r"other hpiv","hpivother",t) for t in table.columns]
    
    return(table)

def create_detections_table(table,modified_date,week_number,week_end_date,start_year):
    lab_columns =[col for col in table.columns if 'reporting' in col][0]
    table=table.rename(columns={lab_columns:"geo_value"})
    table['geo_value']=table['geo_value'].str.lower()
    
    if start_year==2016 and week_number==3:
        table["geo_value"]=[re.sub("^province of$","alberta",c) for c in table["geo_value"]]  
    
    # make naming consistent
    table.columns=[make_signal_type_spelling_consistent(col) for col in table.columns]
    table.columns=[add_flu_prefix(col) for col in table.columns]
    matches=['test','geo_value']

    new_names = []
    for i in range(len(table.columns)):
        if not any(x in table.columns[i] for x in matches):
            new_names.append(table.columns[i]+ " positive_tests")
        else:
            new_names.append(table.columns[i])
    
    table.columns=new_names
    
    # remove any underscores or spaces from virus names
    table.columns=[re.sub(" positive","_positive",t) for t in table.columns]
    table.columns=[re.sub(" tests","_tests",t) for t in table.columns]
    table.columns=[re.sub(" ","",t) for t in table.columns]
    
    table['geo_value'] = [abbreviate_geo(g) for g in table['geo_value']]
    geo_types = [create_geo_types(g,"lab") for g in table['geo_value']]
    
    table = table.assign(**{'epiweek': get_report_date(week_number, start_year,epi=True), 
                    'time_value': week_end_date, 
                    'issue': modified_date,
                    'geo_type':geo_types})

    table.columns =[re.sub(" ","_",col) for col in table.columns]
    return(table)

def create_number_detections_table(table,modified_date,start_year):
    week_columns = table.columns.get_indexer(table.columns[~table.columns.str.contains('week')])
   
    for index in week_columns:
        new_name = abbreviate_virus(table.columns[index]) + " positive_tests"
        table.rename(columns={table.columns[index]: new_name}, inplace=True)
    
    if "week end" not in table.columns:
        week_ends = [get_report_date(week,start_year) for week in table["week"]]
        table.insert(1,"week end",week_ends)
    
    table = table.assign(**{'issue': modified_date, 
                    'geo_type': "nation", 
                    'geo_value': "ca"})

    table=table.rename(columns={'week end':"time_value"})
    table.columns =[re.sub(" ","_",col) for col in table.columns]
    table['time_value'] = [check_date_format(d) for d in table['time_value']]
    
    table=table.rename(columns={'week':"epiweek"})
    table['epiweek'] = [get_report_date(week, start_year,epi=True) for week in table['epiweek']]
    return(table)

def create_percent_positive_detection_table(table,modified_date,start_year, flu=False,overwrite_weeks=False):
    table = deduplicate_rows(table)
    table.columns=[re.sub(" *%", "_pct_positive",col) for col in table.columns]
    table.columns = [re.sub(' +', ' ',col) for col in table.columns]
    table.insert(2,"issue",modified_date)
    table=table.rename(columns={'week end':"time_value"})
    table['time_value'] = [check_date_format(d) for d in table['time_value']]

    # get the name of the virus for the table to append to column names
    virus_prefix=[]
    if flu:
        virus_prefix=['flua_pct_positive','flub_pct_positive']
        virus="flu"
        table.columns=[re.sub("a_pct","flua_pct",c) for c in table.columns]
        table.columns=[re.sub("b_pct","flub_pct",c) for c in table.columns]
    else:
        names=[]
        for j in range(len(table.columns)):
            old_name = table.columns[j]
            if "pct_positive" in table.columns[j]:
                virus_prefix=[table.columns[j]]
                virus=re.match("(.*?)_pct_positive",old_name).group(1)
                geo = table.columns[j-1].split(" ")[0]
                new_name = geo + " " + old_name
            else:
                new_name=old_name
            names.append(new_name)
        table.columns=names
    
    # Remake the weeks column from dates
    if overwrite_weeks:
        week_ends = [datetime.strptime(date_string, "%Y-%m-%d") for date_string in table['time_value']]
        table["week"] = [Week.fromdate(d).week for d in week_ends]
        
    # Change order of column names so tthey start with stubbnames
    table  = table.rename(columns=lambda x: ' '.join(x.split(' ')[::-1])) # 
    stubnames= virus_prefix+['tests']
    table= pd.wide_to_long(table, stubnames, i=['week','time_value','issue'], 
                           j='geo_value', sep=" ", suffix=r'\w+').reset_index()
 
    table.columns=[re.sub("tests",virus+"_tests",c) for c in table.columns]
    table.columns =[re.sub(" ","_",col) for col in table.columns]
    
    table=table.rename(columns={'week':"epiweek"})
    table['epiweek'] = [get_report_date(week, start_year,epi=True) for week in table['epiweek']]
    
    table['geo_value']= [abbreviate_geo(g) for g in table['geo_value']]
    geo_types = [create_geo_types(g,"lab") for g in table['geo_value']]
    table.insert(3,"geo_type",geo_types)
    
    # Calculate number of positive tests based on pct_positive and total tests
    if flu:
        table["flua_positive_tests"] = (table["flua_pct_positive"]/100)*table["flu_tests"]
        table["flub_positive_tests"] = (table["flub_pct_positive"]/100)*table["flu_tests"]

        table["flu_positive_tests"] =  table["flua_positive_tests"] +  table["flub_positive_tests"]
        table["flu_pct_positive"] =   (table["flu_positive_tests"]/table["flu_tests"])*100
    else:
        table[virus+"_positive_tests"] = (table[virus+"_pct_positive"]/100) *table[virus+"_tests"]
    
    table = table.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

    return(table)

def fetch_one_season_from_report(url):
    # From the url, go to the main landing page for a season
    # which contains all the links to each week in the season
    page=requests.get(url)
    soup=BeautifulSoup(page.text,'html.parser') 

    # get season, week numbers, urls and week ends
    season = get_report_season_years(soup)
    urls=construct_weekly_report_urls(soup)
    weeks= report_weeks(soup)
    end_dates = [get_report_date(week, season[0]) for week in weeks]
    
    # create tables to hold all the data for the season
    all_positive_tables=pd.DataFrame()
    all_number_tables=pd.DataFrame()
    all_respiratory_detection_tables=pd.DataFrame()
    
    for week_num in range(len(urls)):
        current_week = weeks[week_num]
        current_week_end = end_dates[week_num]
        
        # In the 2019-2020 season, the webpages for weeks 5 and 47 only have
        # the abbreviations table and the headers for the respiratory detections 
        # table, so they are effectively empty, and skipped
        if season[0] == '2019':
            if current_week == 5 or current_week == 47:
                continue

        # Get page for the current week
        temp_url=urls[week_num]
        temp_page=requests.get(temp_url)
        new_soup = BeautifulSoup(temp_page.text, 'html.parser')
        captions = extract_captions_of_interest(new_soup)
        modified_date = get_modified_dates(new_soup,current_week_end) 

        positive_tables=[]
        number_table_exists = False
        for i in range(len(captions)):
            caption=captions[i]
            tab = caption.find_next('table')
            
            # Remove footers from tables so the text isn't read in as a table row
            if tab.find('tfoot'):
                tab.tfoot.decompose()
            
            # In the positive adenovirus table in week 35 of the 2019-2020 season
            # The week number has been duplicated, which makes all the entries in the table 
            # are one column to the right of where they should be. To fix this the
            # entry in the table (which is the first "td" element in the html) is deleted
            if season[0] == '2019' and current_week == 35:
                if "Positive Adenovirus" in caption.text:
                    tab.select_one('td').decompose()
            
            # Replace commas with periods
            # Some "number of detections" tables have number with commas (i.e 1,000)
            # In this case the commas must be deleted, otherwise turn into periods
            # because some tables have commas instead of decimal points
            if "number" not in caption.text.lower():
                tab = re.sub(",",r".",str(tab))
            else:
                tab = re.sub(",","",str(tab))
            
            # Read table, coding all the abbreviations for missing data into NA
            # Also use dropna because removing footers causes the html to have an empty row
            na_values = ['N.A.','N.A', 'N.C.','N.R.','Not Available','Not Tested',"N.D.","-"]
            table =  pd.read_html(tab,na_values=na_values)[0].dropna(how="all")
            
            # Check for multiline headers
            # If there are any, combine them into a single line header
            if isinstance(table.columns, pd.MultiIndex):
                table.columns = [c[0] + " " + c[1] if c[0] != c[1] else c[0] for c in table.columns]
            
            # Make column names lowercase
            table.columns=table.columns.str.lower()
            
            # One-off edge cases where tables need to be manually adjusted because
            # they will cause errors otherwise
            if season[0] == '2017':
                if current_week == 35 and "entero" in caption.text.lower():
                    # The positive enterovirus table in week 35 of the 2017-2018 season has french
                    # in the headers,so the french needs to be removed
                    table.columns = ['week', 'week end', 'canada tests', 'entero/rhino%', 'at tests',
                       'entero/rhino%.1', 'qc tests', 'entero/rhino%.2', 'on tests',
                       'entero/rhino%.3', 'pr tests', 'entero/rhino%.4', 'bc tests',
                       'entero/rhino%.5']
                elif current_week == 35 and "adeno" in caption.text.lower():
                    # In week 35 of the 2017-2018, the positive adenovirus table has ">week end"
                    # instead of "week end", so remove > from the column
                    table = table.rename(columns={'>week end':"week end"})
                elif current_week == 47 and "rsv" in caption.text.lower():
                    #  In week 47 of the 2017-2018 season, a date is written as 201-11-25, 
                    #  instead of 2017-11-25
                    table.loc[table['week'] == 47, 'week end'] = "2017-11-25"
            elif season[0] == '2015' and current_week == 41:
                # In week 41 of the 2015-2016 season, a date written in m-d-y format not d-m-y
                table=table.replace("10-17-2015","17-10-2015",regex=True)
            elif season[0] == '2022' and current_week == 11 and "hmpv" in caption.text.lower():
                #  In week 11 of the 2022-2023 season, in the positive hmpv table,
                # a date is written as 022-09-03, instead of 2022-09-03
                 table.loc[table['week'] == 35, 'week end'] = "2022-09-03"
            
            # Rename columns
            table= preprocess_table_columns(table)
 
            # If "reporting laboratory" is one of the columns of the table, the table must be
            # the "Respiratory virus detections " table for a given week
            # this is the lab level table that has weekly positive tests for each virus, with no revisions
            # and each row represents a lab
            
            # If "number" is in the table caption, the table must be the
            # "Number of positive respiratory detections" table, for a given week
            # this is a national level table, reporting the number of detections for each virus,
            # this table has revisions, so each row is a week in the season, with weeks going from the
            # start of the season up to and including the current week
            
            # If "positive" is in the table caption, the table must be one of the
            # "Positive [virus] Tests (%)" table, for a given week
            # This is a region level table, reporting the total tests and percent positive tests  for each virus,
            # this table has revisions, so each row is a week in the season, with weeks going from the
            # start of the season up to and including the current week
            # The columns have the region information (i.e Pr tests, meaning this columns has the tests for the prairies)
            
            if "reporting laboratory" in str(table.columns):
               respiratory_detection_table = create_detections_table(table,modified_date,current_week,current_week_end,season[0]) 
               respiratory_detection_table = respiratory_detection_table.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
            elif "number" in caption.text.lower():
               number_table_exists = True
               number_detections_table = create_number_detections_table(table,modified_date,season[0])
               number_detections_table = number_detections_table.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
            elif "positive" in caption.text.lower():
               flu = " influenza" in caption.text.lower()
               
               # tables are missing week 53
               # In the 2014-2015 season the year ends at week 53 before starting at week 1 again.
               # weeks 53,2 and 3 skip week 53 in the positive detection tables, going from 52 to 1,
               # this means the week numbers following 52 are 1 larger then they should be
               # fix this by overwriting the week number columns 
             
               missing_week_53 = [53,2,3]
               if season[0]=="2014" and current_week in missing_week_53: 
                   overwrite_weeks=True
               else:
                   overwrite_weeks=False  
            
               pos_table = create_percent_positive_detection_table(table,modified_date,season[0],flu,overwrite_weeks)
                   
               # Check for percentages >100
               # One in 2014-2015 week 39, left in
               if season[0] != '2014' and current_week != 39:
                   for k in range(len(pos_table.columns)):
                       if "pct_positive" in pos_table.columns[k]:
                           assert all([0 <= val <= 100 or math.isnan(val) for val in  pos_table[pos_table.columns[k]]]), "Percentage not from 0-100"
               
               positive_tables.append(pos_table)

        # create path to save files
        path = "season_" + season[0]+"_"+season[1]
       
        # combine all the positive tables
        combined_positive_tables=pd.concat(positive_tables,axis=1)
    
        # Check if the indices are already in the season table
        # If not, add the weeks tables into the season table
        
        # check for deduplication pandas
        if not respiratory_detection_table.index.isin(all_respiratory_detection_tables.index).any():
            all_respiratory_detection_tables= pd.concat([all_respiratory_detection_tables,respiratory_detection_table])
            
        if not combined_positive_tables.index.isin(all_positive_tables.index).any():
            all_positive_tables=pd.concat([all_positive_tables,combined_positive_tables])
    
        if number_table_exists:
            if not number_detections_table.index.isin(all_number_tables.index).any():
                all_number_tables=pd.concat([all_number_tables,number_detections_table])

    return {
        "respiratory_detection": all_respiratory_detection_tables,
        "positive": all_positive_tables,
        "count": all_number_tables,
    }

def fetch_report_data():
    # Scrape each season.
    dict_list = [fetch_one_season_from_report(url) for url in HISTORIC_SEASON_URLS]

    return dict_list

def fetch_historical_dashboard_data():
    # Update the end of the 2023-2024 season with the dashboard data
    included_urls = fetch_archived_dashboard_urls()
    dict_list = [{} for url in included_urls]

    for i, base_url in enumerate(included_urls):
        # Get weekly dashboard data
        ## TODO: what to do with this "2023"? Need to parse the start year of the season from the URL
        ## TODO: how to "weekly" and "positive" correspond to the dict keys from historical reports?
        dict_list[i]["weekly"] = get_weekly_data(base_url,2023).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        dict_list[i]["positive"] = get_revised_data(base_url)

    return dict_list
