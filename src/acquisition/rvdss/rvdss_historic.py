from bs4 import BeautifulSoup
import requests
import regex as re
import pandas as pd
from epiweeks import Week
from datetime import datetime,timedelta
import math
import io

 #%% Functions
 
 # Report Functions
def get_report_season(soup):
    # Find the url in the page html and get the season
    canonical_url = str(soup.find_all('link',rel="canonical"))
    matches = re.search("20[0-9]{2}-20[0-9]{2}",canonical_url)

    if matches:
        season = matches.group(0)
    years=season.split("-")
    return(years)

def append_urls(urls):
    # Add https to the urls
    for i in range(len(urls)):
        temp_url = urls[i]
  
        http_present = re.search("http",temp_url)
        if not http_present:
            urls[i]="https://www.canada.ca"+temp_url
    return(urls)

def report_urls(soup):
    # Get links for individual weeks
    year= "-".join(get_report_season(soup))
    links=soup.find_all('a')
    alternative_url = "http://www.phac-aspc.gc.ca/bid-bmi/dsd-dsm/rvdi-divr/"+year
    
    urls = [link.get("href") for link in links if "ending" in str(link) or 
            alternative_url in str(link)]
    
    report_links = append_urls(urls)
    return(report_links)

def report_weeks(soup):
    links=soup.find_all('a')
    full_weeks = [link.text for link in links if "Week" in str(link)]
    weeks= [int(re.search('Week (.+?) ', week).group(1)) for week in full_weeks]
    return(weeks)

def get_report_date(week,start_year,epi=False):
    if week < 35: 
        year=int(start_year)+1
    else:
        year=int(start_year)
    
    epi_week =  Week(year, week)
    
    if epi==False:
        report_date = str(epi_week.enddate())
    else:
        report_date =  str(epi_week)
        
    return(report_date)

def abbreviate_virus(full_name):
    lowercase=full_name.lower()
    
    if any(name in lowercase for name in ["parainfluenza","para","piv"]):
        if "hpiv" not in lowercase:
            abbrev = re.sub("parainfluenza|para|piv","hpiv",lowercase)
        else:
            abbrev = lowercase
    elif any(name in lowercase for name in ["adenovirus","adeno"]):
        abbrev =  re.sub("adenovirus|adeno","adv",lowercase)
    elif "human metapneumovirus" in lowercase:
        abbrev =  re.sub("human metapneumovirus","hmpv",lowercase)
    elif any(name in lowercase for name in ["enterovirus/rhinovirus","rhinovirus","rhv","entero/rhino","rhino","ev/rv","evrv"]):
        abbrev = re.sub("enterovirus/rhinovirus|rhinovirus|rhv|entero/rhino|rhino|ev/rv|evrv","ev_rv",lowercase)
    elif any(name in lowercase for name in ["coronavirus","coron","coro"]):
        abbrev = re.sub("coronavirus|coron|coro","hcov",lowercase)
    elif "respiratory syncytial virus" in lowercase:
        abbrev = re.sub("respiratory syncytial virus","rsv",lowercase)
    elif "influenza" in lowercase:
        abbrev = re.sub("influenza","flu",lowercase)       
    elif "sarscov2" in lowercase:
        abbrev = re.sub("sarscov2","sars-cov-2",lowercase) 
    else:
        abbrev=lowercase
    return(abbrev)

def abbreviate_geo(full_name):
    lowercase=full_name.lower()
    
    if "newfoundland" in lowercase:
        abbrev =  "nl"
    elif "prince edward island" in lowercase:
        abbrev =  "pe"
    elif "nova scotia" in lowercase:
        abbrev =  "ns"
    elif "new brunswick" in lowercase:
        abbrev =  "nb"
    elif "nova scotia" in lowercase:
        abbrev =  "ns"     
    elif re.match('|'.join(("^québec$", "province of québec","quebec")),lowercase):
        abbrev = "qc"  
    elif re.match('|'.join(("^ontario$", "province of ontario")),lowercase):
        abbrev =  "on"
    elif "manitoba" in lowercase:
        abbrev =  "mb"
    elif "saskatchewan" in lowercase:
        abbrev =  "sk"
    elif "alberta" in lowercase:
        abbrev =  "ab"
    elif "british columbia" in lowercase:
        abbrev =  "bc"
    elif "yukon" in lowercase:
        abbrev =  "yk"
    elif "northwest territories" in lowercase:
        abbrev =  "nt"
    elif "nunavut" in lowercase:
        abbrev =  "nu"
    elif re.match("canada|can",lowercase):
        abbrev = "ca" 
    elif re.match(r"^at\b",lowercase):
        abbrev = "atlantic" 
    elif "pr" in lowercase:
        abbrev = "prairies" 
    elif "terr" in lowercase:
        abbrev = "territories" 
    else:
        abbrev=lowercase
    return(abbrev)
       

def get_table_captions(soup):
    captions = soup.findAll('summary')
    
    table_identifiers = ["respiratory","number","positive","abbreviation"]
    if sum([all(name not in cap.text.lower() for name in table_identifiers) for cap in captions]) != 0:
        figcaptions = soup.findAll('figcaption')     
        captions = captions + figcaptions
             
    remove_list=[]
    for i in range(len(captions)):
        caption = captions[i]
        
        matches = ["period","abbreviation","cumulative", "compared"] #skip historic comparisons and cumulative tables
        if any(x in caption.text.lower() for x in matches): 
            remove_list.append(caption)
        
        elif caption.has_attr('class'):
            remove_list.append(caption)
            
        elif all(name not in caption.text.lower() for name in table_identifiers):
            remove_list.append(caption)
    
    new_captions = [cap for cap in captions if cap not in remove_list]
    new_captions = list(set(new_captions))
    
    return(new_captions)

def get_modified_dates(soup,week_end_date):
    # get the date the report page was modfified
    meta_tags=soup.find_all("meta",title="W3CDTF")
    for tag in meta_tags:
        if tag.get("name", None) == "dcterms.modified" or tag.get("property", None) == "dcterms.modified":
            modified_date = tag.get("content", None)

    mod_date = datetime.strptime(modified_date, "%Y-%m-%d")
    week_date = datetime.strptime(week_end_date, "%Y-%m-%d")
    
    diff_days = (mod_date-week_date).days
    
    # manually create a new modified date if the existing one is too long after the week
    if diff_days > 0 and diff_days < 14:
        new_modified_date = mod_date
    else:
        new_lag = timedelta(days=5)
        new_modified_date = week_date + new_lag
    
    new_modified_date_string = new_modified_date.strftime("%Y-%m-%d")
    
    return(new_modified_date_string)

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

def check_duplicate_rows(table):
    if table['week'].duplicated().any():
       table.columns = [re.sub("canada","can",t) for t in table.columns]
       duplicated_rows = table[table.duplicated('week',keep=False)]
       grouped = duplicated_rows.groupby("week")
       duplicates_drop = []
       
       for name, group in grouped:
           duplicates_drop.append(group['can tests'].idxmin())
    
       new_table = table.drop(duplicates_drop).reset_index(drop=True)
       
    else:
        new_table=table
    return(new_table)

def create_geo_types(geo,default_geo):
    regions = ['atlantic','atl','province of québec','québec','qc','province of ontario','ontario','on',
               'prairies', 'pr', "british columbia", 'bc',"territories",'terr']
    nation = ["canada","can",'ca']
                    
    if geo in nation:
        geo_type="nation"
    elif geo in regions:
        geo_type="region"
    else:
        geo_type = default_geo
    return(geo_type)
    
def create_detections_table(table,modified_date,week_number,week_end_date,start_year):
    lab_columns =[col for col in table.columns if 'reporting' in col][0]
    table=table.rename(columns={lab_columns:"geo_value"})
    table['geo_value']=table['geo_value'].str.lower()
    
    pat1 = "positive"
    pat2 = 'pos'
    combined_pat = '|'.join((pat1, pat2))
    
    pat3 = r"test\b"
    pat4 = 'tested'
    combined_pat2 = '|'.join((pat3, pat4))
    
    pat5 =r"^ah3"
    pat6= r"^auns" 
    pat7= r"^ah1pdm09"
    pat8= r"^ah1n1pdm09"
    combined_pat3 = '|'.join((pat5, pat6,pat7,pat8))
    
    table.columns=[re.sub(combined_pat, "positive_tests",col) for col in table.columns] #making naming consistent
    table.columns=[re.sub(combined_pat2, "tests",col) for col in table.columns]
    table.columns=[re.sub(combined_pat3, r"flu_\g<0>",col) for col in table.columns] # add flu as a prefix 
    table.columns=[re.sub("total ", "",col) for col in table.columns]
    matches=['test','geo_value']
    new_names = []
    for i in range(len(table.columns)):
        if not any(x in table.columns[i] for x in matches):
            new_names.append(table.columns[i]+ " positive_tests")
        else:
            new_names.append(table.columns[i])
    
    table.columns=new_names
    table.columns=[re.sub("other hpiv", "hpiv other",col) for col in table.columns]
    table['geo_value'] = [re.sub("^québec$","province of québec",name) for name in table['geo_value']]
    table['geo_value'] = [re.sub("^ontario$","province of ontario",name) for name in table['geo_value']]
    
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
    table = check_duplicate_rows(table)
    table.columns=[re.sub(" *%", "_pct_positive",col) for col in table.columns]
    table.columns = [re.sub(' +', ' ',col) for col in table.columns]
    table.insert(2,"issue",modified_date)
    table=table.rename(columns={'week end':"time_value"})
    table['time_value'] = [check_date_format(d) for d in table['time_value']]

    # get the name of the virus for the table to append to column names
    virus_prefix=[]
    if flu:
        virus_prefix=['flu_a_pct_positive','flu_b_pct_positive']
        virus="flu"
        table.columns=[re.sub("a_pct","flu_a_pct",c) for c in table.columns]
        table.columns=[re.sub("b_pct","flu_b_pct",c) for c in table.columns]
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
    if overwrite_weeks==True:
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
    
    table = table.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

    return(table)

def get_season_reports(url):
    page=requests.get(url)
    soup=BeautifulSoup(page.text,'html.parser') 

    # get season, weeks, urls and week ends
    season = get_report_season(soup)
    urls=report_urls(soup)
    weeks= report_weeks(soup)
    end_dates = [get_report_date(week, season[0]) for week in weeks]
    
    # create tables to hold all the data for the season
    all_positive_tables=pd.DataFrame()
    all_number_tables=pd.DataFrame()
    all_respiratory_detection_table=pd.DataFrame()
    
    for week_num in range(len(urls)):
        current_week = weeks[week_num]
        current_week_end = end_dates[week_num]
        
        # Skip empty pages
        if season[0] == '2019':
            if current_week == 5:
                continue
            elif current_week == 47:
                continue
        
        # Get page for the current week
        temp_url=urls[week_num]
        temp_page=requests.get(temp_url)
        new_soup = BeautifulSoup(temp_page.text, 'html.parser')
        captions = get_table_captions(new_soup)
        modified_date = get_modified_dates(new_soup,current_week_end) 

        positive_tables=[]
        number_table_exists = False
        for i in range(len(captions)):
            caption=captions[i]
            tab = caption.find_next('table')
            
            # Remove footers from tables
            if tab.find('tfoot'):
                tab.tfoot.decompose()
            
            # Delete duplicate entry from week 35 of the 2019-2020 season
            if season[0] == '2019' and current_week == 35:
                if "Positive Adenovirus" in caption.text:
                    tab.select_one('td').decompose()
            
            # Replace commas with periods
            tab2 = re.sub(",",r".",str(tab))
            
            # Read table
            na_values = ['N.A.','N.A', 'N.C.','N.R.','Not Available','Not Tested',"N.D.","-"]
            table =  pd.read_html(tab2,na_values=na_values)[0].dropna(how="all")
            
            # Check for multiline headers
            if isinstance(table.columns, pd.MultiIndex):
                table.columns = [c[0] + " " + c[1] if c[0] != c[1] else c[0] for c in table.columns]
            
            # Make column names lowercase
            table.columns=table.columns.str.lower()
            
            if season[0] == '2017':
                if current_week == 35 and "entero" in caption.text.lower():
                    # Remove french from headers in week 35 for the entero table
                    table.columns = ['week', 'week end', 'canada tests', 'entero/rhino%', 'at tests',
                       'entero/rhino%.1', 'qc tests', 'entero/rhino%.2', 'on tests',
                       'entero/rhino%.3', 'pr tests', 'entero/rhino%.4', 'bc tests',
                       'entero/rhino%.5']
                elif current_week == 35 and "adeno" in caption.text.lower():
                    # Remove > from column name
                    table = table.rename(columns={'>week end':"week end"})
                elif current_week == 47 and "rsv" in caption.text.lower():
                    # fix date written as 201-11-25
                    table.loc[table['week'] == 47, 'week end'] = "2017-11-25"
            elif season[0] == '2015' and current_week == 41:
                # Fix date written m-d-y not d-m-y
                table=table.replace("10-17-2015","17-10-2015",regex=True)
            elif season[0] == '2022' and current_week == 11 and "hmpv" in caption.text.lower():
                # fix date written as 022-09-03
                 table.loc[table['week'] == 35, 'week end'] = "2022-09-03"
            
            # Rename columns
            table.columns = [re.sub("\xa0"," ", col) for col in table.columns] # \xa0 to space
            table.columns = [re.sub("flutest","flu test", col) for col in table.columns]
            table.columns = [re.sub("(.*?)(\.\d+)", "\\1", c) for c in table.columns] # remove .# for duplicated columns
            table.columns =[re.sub("\.", "", s)for s in table.columns] #remove periods
            table.columns =[re.sub(r"\((all)\)", "", s)for s in table.columns] # remove (all) 
            table.columns =[re.sub(r"\s*\(|\)", "", s)for s in table.columns] # remove (all) 
            table.columns =[re.sub(r"h1n1 2009 |h1n12009", "ah1n1pdm09", s)for s in table.columns] # remove (all) 
            table.columns =[abbreviate_virus(col) for col in table.columns] # abbreviate viruses
            table.columns = [re.sub(' +', ' ', col) for col in table.columns] # Make any muliple spaces into one space
            table.columns = [re.sub(r'\(|\)', '', col) for col in table.columns] # replace () for _
            table.columns = [re.sub(r'/', '_', col) for col in table.columns] # replace / with _
            table.columns = [re.sub(r"^at\b","atl ",t) for t in table.columns]
            
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
               if season[0]=="2014" and current_week==2:
                   overwrite_weeks=True
               elif season[0]=="2014" and current_week==3: 
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
        if respiratory_detection_table.index.isin(all_respiratory_detection_table.index).any() == False:
            all_respiratory_detection_table= pd.concat([all_respiratory_detection_table,respiratory_detection_table])
            
        if combined_positive_tables.index.isin(all_positive_tables.index).any() == False:
            all_positive_tables=pd.concat([all_positive_tables,combined_positive_tables])
    
        if number_table_exists == True:
            if number_detections_table.index.isin(all_number_tables.index).any() == False:
                all_number_tables=pd.concat([all_number_tables,number_detections_table])

    # write files to csvs
    all_respiratory_detection_table.to_csv(path+"/"+path+"_respiratory_detections.csv", index=True) 
    all_positive_tables.to_csv(path+"/"+path+"_positive_tests.csv", index=True)
    
    # Write the number of detections table to csv if it exists (i.e has rows)
    if len(all_number_tables) != 0:
        all_number_tables.to_csv(path+"/"+path+"_number_of_detections.csv", index=True) 

# Dashboard functions
def get_revised_data(base_url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    # Get update date
    update_date_url =  base_url + "RVD_UpdateDate.csv"
    update_date_url_response = requests.get(update_date_url, headers=headers)
    update_date = datetime.strptime(update_date_url_response.text,"%m/%d/%Y %H:%M:%S").strftime("%Y-%m-%d")
    
    # Get update data
    url = base_url+"RVD_WeeklyData.csv"

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
    
    df=df.drop(["weekorder","region","year","week"],axis=1)
    
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
    
def get_weekly_data(base_url,start_year):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    # Get update date
    update_date_url =  base_url + "RVD_UpdateDate.csv"
    update_date_url_response = requests.get(update_date_url, headers=headers)
    update_date = datetime.strptime(update_date_url_response.text,"%m/%d/%Y %H:%M:%S").strftime("%Y-%m-%d")

    # Get current week and year
    summary_url =  base_url + "RVD_SummaryText.csv"
    summary_url_response = requests.get(summary_url, headers=headers)
    summary_df = pd.read_csv(io.StringIO(summary_url_response.text))
    
    week_df = summary_df[(summary_df['Section'] == "summary") & (summary_df['Type']=="title")]
    week_string = week_df.iloc[0]['Text'].lower()
    current_week = int(re.search("week (.+?) ", week_string).group(1))

    if current_week < 34:
        current_year = start_year+1
    else:
        current_year = start_year
        
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
    
    #df_weekly=df_weekly.drop(["weekorder","date","week"],axis=1)

    return(df_weekly)

        
 #%% Scrape each season

urls = ["https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2013-2014.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2014-2015.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2015-2016.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2016-2017.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2017-2018.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2018-2019.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2019-2020.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2020-2021.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2021-2022.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2022-2023.html",
"https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada/2023-2024.html"]

[get_season_reports(url) for url in urls]


 #%% Update the end of the 2023-2024 season with the dashboard data
 
base_urls=["https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-06-20/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-06-27/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-07-04/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-07-11/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-07-18/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-08-01/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-08-08/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-08-15/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-08-22/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-08-29/",
"https://health-infobase.canada.ca/src/data/respiratory-virus-detections/archive/2024-09-05/"]

# Load old csvs
old_detection_data = pd.read_csv('season_2023_2024/season_2023_2024_respiratory_detections.csv').set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
old_positive_data = pd.read_csv('season_2023_2024/season_2023_2024_positive_tests.csv').set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

for base_url in base_urls:
    # Get weekly dashboard data
    weekly_data = get_weekly_data(base_url,2023).set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
    positive_data = get_revised_data(base_url)
    
    # Check if indices are already present in the old data
    # If not, add the new data
    if weekly_data.index.isin(old_detection_data.index).any() == False:
        old_detection_data= pd.concat([old_detection_data,weekly_data],axis=0)
    
    if positive_data.index.isin(old_positive_data.index).any() == False:
        old_positive_data= pd.concat([old_positive_data,positive_data],axis=0)
    
# Overwrite/update csvs
old_detection_data.to_csv('season_2023_2024/season_2023_2024_respiratory_detections.csv',index=True)
old_positive_data.to_csv('season_2023_2024/season_2023_2024_positive_tests.csv',index=True)

