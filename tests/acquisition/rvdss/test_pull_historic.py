"""Unit tests for rvdss/pull_historic.py."""

import pytest
import mock
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from epiweeks import Week
from datetime import datetime, timedelta
import math
import regex as re
from requests_file import FileAdapter
import requests

from delphi.epidata.acquisition.rvdss.pull_historic import (get_report_season_years, add_https_prefix, 
construct_weekly_report_urls, report_weeks, get_report_date, extract_captions_of_interest, get_modified_dates,
deduplicate_rows, drop_ah1_columns,preprocess_table_columns, create_detections_table, create_number_detections_table, 
create_percent_positive_detection_table, fetch_one_season_from_report, fetch_archived_dashboard_dates, 
fetch_report_data, fetch_historical_dashboard_data,fix_edge_cases)

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.rvdss.pull_historic"

TEST_DIR = Path(__file__).parent.parent.parent.parent
url = str(TEST_DIR) + "/testdata/acquisition/rvdss/week3_20162017.html"
with open(url) as page:
    soup = BeautifulSoup(page.read(),'html.parser')
    new_soup = BeautifulSoup(soup.text, 'html.parser')
    captions = extract_captions_of_interest(new_soup)

example_edge_case_tables=[
    pd.DataFrame(columns=["Week/Semaine", "Week End/Fin de la semaine", "Canada Tests", "Entero/entéro/rhino%", "At Tests",
    "Entero/entéro/rhino%","QC Tests", "Entero/entéro/rhino%", "ON Tests", "Entero/entéro/rhino%", "Pr Tests", 
    "Entero/entéro/rhino%", "BC/CB Tests", "Entero/entéro/rhino%"]), 
    pd.DataFrame(columns=[">week end","pos_tests"]),
    pd.DataFrame([{'week':47, 'week end':"201-11-25", 'canada tests':1, 'rsv%':1, 'at tests':1,
       'rsv%.1':1, 'qc tests':1, 'rsv%.2':1, 'on tests':1,
       'rsv%.3':1, 'pr tests':1, 'rsv%.4':1, 'bc tests':1,
       'rsv%.5':1}]),
    pd.DataFrame([{'week':41, 'week end':"10-17-2015", 'canada tests':1, 'rsv%':1, 'at tests':1,
       'rsv%.1':1, 'qc tests':1, 'rsv%.2':1, 'on tests':1,
       'rsv%.3':1, 'pr tests':1, 'rsv%.4':1, 'bc tests':1,
       'rsv%.5':1}]),
    pd.DataFrame([{'week':35, 'week end':"022-09-03", 'canada tests':1, 'hmpv%':1, 'at tests':1,
       'hmpv%.1':1, 'qc tests':1, 'hmpv%.2':1, 'on tests':1,
       'hmpv%.3':1, 'pr tests':1, 'hmpv%.4':1, 'bc tests':1,
       'hmpv%.5':1}]),
    pd.DataFrame(columns=["week end","pos_tests","percent_pos"])]

expected_edge_case_tables=[
    pd.DataFrame(columns=['week', 'week end', 'canada tests', 'entero/rhino%', 'at tests',
       'entero/rhino%.1', 'qc tests', 'entero/rhino%.2', 'on tests',
       'entero/rhino%.3', 'pr tests', 'entero/rhino%.4', 'bc tests',
       'entero/rhino%.5']), 
    pd.DataFrame(columns=["week end","pos_tests"]),
    pd.DataFrame([{'week':47, 'week end':"2017-11-25", 'canada tests':1, 'rsv%':1, 'at tests':1,
       'rsv%.1':1, 'qc tests':1, 'rsv%.2':1, 'on tests':1,
       'rsv%.3':1, 'pr tests':1, 'rsv%.4':1, 'bc tests':1,
       'rsv%.5':1}]),
    pd.DataFrame([{'week':41, 'week end':"17-10-2015", 'canada tests':1, 'rsv%':1, 'at tests':1,
       'rsv%.1':1, 'qc tests':1, 'rsv%.2':1, 'on tests':1,
       'rsv%.3':1, 'pr tests':1, 'rsv%.4':1, 'bc tests':1,
       'rsv%.5':1}]),
    pd.DataFrame([{'week':35, 'week end':"2022-09-03", 'canada tests':1, 'hmpv%':1, 'at tests':1,
       'hmpv%.1':1, 'qc tests':1, 'hmpv%.2':1, 'on tests':1,
       'hmpv%.3':1, 'pr tests':1, 'hmpv%.4':1, 'bc tests':1,
       'hmpv%.5':1}]),
    pd.DataFrame(columns=["week end","pos_tests","percent_pos"])]

example_edge_case_captions=[
    [t for t in captions if "Entero" in t.text][0],
    [t for t in captions if "Adeno" in t.text][0],
    [t for t in captions if "RSV" in t.text][0],
    [t for t in captions if "RSV" in t.text][0],
    [t for t in captions if "hMPV" in t.text][0],
    [t for t in captions if "hMPV" in t.text][0]]

example_edge_case_seasons=[["2017","2018"],["2017","2018"],["2017","2018"],
                           ["2015","2016"],["2022","2023"],["2021","2022"]]

example_edge_case_weeks=[35,35,47,41,11,10]

class TestPullHistoric():

    def test_syntax(self):
        """This no-op test ensures that syntax is valid."""
        pass
    
    def test_get_report_season_years(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/mainpage_20162017.html"
        
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert get_report_season_years(new_soup) == ['2016','2017']

    def test_add_https_prefix(self):
       assert add_https_prefix(["/random.html"]) == ["https://www.canada.ca/random.html"]
       assert add_https_prefix(["http://randomurl2.html"]) == ["https://randomurl2.html"]
       assert add_https_prefix(["https://randomurl3.html"]) == ["https://randomurl3.html"]
   
    def test_construct_weekly_report_urls(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
            
        url_alt = str(TEST_DIR) + "/testdata/acquisition/rvdss/mainpage_20162017.html"
        test_data_url_alt  = str(TEST_DIR) + "/testdata/acquisition/rvdss/test_urls_20162017.txt"
        
        with open(test_data_url_alt) as f:
            expected_urls_alt = [line.rstrip('\n') for line in f]
    
        with open(url_alt) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert set(construct_weekly_report_urls(new_soup)) == set(expected_urls_alt)

    def test_report_weeks(self):
        expected_weeks = list(range(35,0,-1)) + list(range(52,34,-1))
        
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/mainpage_20162017.html"
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert set(report_weeks(new_soup)) == set(expected_weeks)
        
    def test_get_report_date(self):
        assert get_report_date(35,2024,epi=True) == "202435" # first week of season
        assert get_report_date(34,2024,epi=True) == "202534" # last week of season
        assert get_report_date(50,2024,epi=False) == "2024-12-14" # normal week within season
        assert get_report_date(53,2020,epi=False) == "2021-01-02" # last week of year leap year
        assert get_report_date(53,2020,epi=True) == "202053"

    def test_extract_captions_of_interest(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/week3_20162017.html"
        
        test_data_url  = str(TEST_DIR) + "/testdata/acquisition/rvdss/test_captions_20162017.txt"
        with open(test_data_url) as f: 
            soup = BeautifulSoup(f.read(),'html.parser')
            expected_captions = soup.find_all("summary")
        
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert set(extract_captions_of_interest(new_soup)) == set(expected_captions)
        
    def test_get_modified_dates(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/week3_20162017.html"
        
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert get_modified_dates(new_soup,"2017-01-21") == "2017-01-25"
               
            # modify the meta modified date so it is to far after the week end
            mod_date = new_soup.find("meta", {"name":"dcterms.modified"})
            new_date = str(mod_date).replace("2017-01-25", "2017-02-25")
            modified_tag =  BeautifulSoup(new_date, "html.parser")
            mod_date.replace_with(modified_tag)
            assert get_modified_dates(new_soup,"2017-01-21") == "2017-01-26"

    def test_deduplicate_rows(self):
        duplicated_table = pd.DataFrame({
            "week":[35,36,36,37],
            "can tests":[10,20,30,40]
            })
        
        unduplicated_table = pd.DataFrame({
            "week":[35,36,37],
            "can tests":[10,30,40]
            })
        
        assert deduplicate_rows(duplicated_table).equals(unduplicated_table) # should remove the row with less can tests
        assert deduplicate_rows(unduplicated_table).equals(unduplicated_table) # unduplicated table should stay the same

    def test_drop_ah1_columns(self):
        ah1_table =  pd.DataFrame({
            "week":[35,36,36,37],
            "ah1 tests":[10,20,30,40]
            })
        
        h1n1_table =  pd.DataFrame({
            "week":[35,36,36,37],
            "h1n1 tests":[10,20,30,40]
            })
        
        ah1_h1n1_table =  pd.DataFrame({
            "week":[35,36,36,37],
            "ah1 tests":[10,20,30,40],
            "h1n1 tests":[1,2,3,4]
            })
        
        expected_table =  pd.DataFrame({
            "week":[35,36,36,37],
            "h1n1 tests":[1,2,3,4]
            })
        
        reg_table =  pd.DataFrame({
            "week":[35,36,36,37],
            "flu tests":[10,20,30,40],
            "rsv tests":[1,2,3,4]
            })
        
        assert drop_ah1_columns(ah1_table).equals(ah1_table) # if only ah1 column exists, keep it
        assert drop_ah1_columns(h1n1_table).equals(h1n1_table) # if only h1n1 column exists, keep it
        assert drop_ah1_columns(reg_table).equals(reg_table) # if neither ah1 and h1n1 columns exists, do nothing
        assert drop_ah1_columns(ah1_h1n1_table).equals(expected_table) # if both ah1 and h1n1 columns exists, drop ah1

    def test_create_detections_table(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent

        expected_data = pd.read_csv(str(TEST_DIR) + "/testdata/acquisition/rvdss/formatted_detections.csv")
        expected_data['epiweek'] = expected_data['epiweek'].astype(str)
        expected_data = expected_data.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        expected_data = expected_data.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

        #url = str(TEST_DIR) + "/testdata/acquisition/rvdss/week3_20162017.html"
        # with open(url) as page:
        #     soup = BeautifulSoup(page.read(),'html.parser')
        #     new_soup = BeautifulSoup(soup.text, 'html.parser')
        #     captions = extract_captions_of_interest(new_soup)
        caption=[t for t in captions if "Table 1" in t.text][0]
        tab = caption.find_next('table')
        tab.tfoot.decompose()
        tab = re.sub(",",r".",str(tab))
            
        na_values = ['N.A.','N.A', 'N.C.','N.R.','Not Available','Not Tested',"not available",
                     "not tested","N.D.","-",'Not tested','non testé']
        table =  pd.read_html(tab,na_values=na_values)[0].dropna(how="all")
        table.columns=table.columns.str.lower()
        table = drop_ah1_columns(table)
        table= preprocess_table_columns(table)
        
        modified_date = "2017-01-25"
        week_number = 3
        week_end_date = "2017-01-21"
        start_year = 2016
        
        detection_table = create_detections_table(table,modified_date,week_number,week_end_date,start_year)
        detection_table = detection_table.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        detection_table = detection_table.sort_values(by=['epiweek','time_value','issue','geo_type','geo_value'])
        
        assert expected_data.equals(detection_table)

    def test_create_number_detections_table(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent

        expected_data = pd.read_csv(str(TEST_DIR) + "/testdata/acquisition/rvdss/formatted_number_detections.csv")
        expected_data['epiweek'] = expected_data['epiweek'].astype(str)
        expected_data = expected_data.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        expected_data = expected_data.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])

        # url = str(TEST_DIR) + "/testdata/acquisition/rvdss/week3_20162017.html"
        # with open(url) as page:
        #     soup = BeautifulSoup(page.read(),'html.parser')
        #     new_soup = BeautifulSoup(soup.text, 'html.parser')
        #     captions = extract_captions_of_interest(new_soup)
        caption=[t for t in captions if "Number" in t.text][0]
        tab = caption.find_next('table')
        tab = re.sub(",","",str(tab))
                
        na_values = ['N.A.','N.A', 'N.C.','N.R.','Not Available','Not Tested',"not available",
                     "not tested","N.D.","-",'Not tested','non testé']
        table =  pd.read_html(tab,na_values=na_values)[0].dropna(how="all")
        table.columns=table.columns.str.lower()
        table = drop_ah1_columns(table)
        table= preprocess_table_columns(table)
        table_no_weekend = table.drop(columns=['week end'])
            
        modified_date = "2017-01-25"
        start_year = 2016
            
        number_table = create_number_detections_table(table,modified_date,start_year)
        number_table = number_table.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        number_table = number_table.sort_values(by=['epiweek','time_value','issue','geo_type','geo_value'])
            
        number_table_no_weekend =  create_number_detections_table(table_no_weekend,modified_date,start_year)
        number_table_no_weekend = number_table_no_weekend.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        number_table_no_weekend = number_table_no_weekend.sort_values(by=['epiweek','time_value','issue','geo_type','geo_value'])
            
        assert number_table.equals(expected_data)
        assert number_table_no_weekend.equals(expected_data)

    def test_create_percent_positive_detection_table(self):
        # set up expected output
        #flu data
        expected_fludata = pd.read_csv(str(TEST_DIR) + "/testdata/acquisition/rvdss/formatted_flu_positive_tests.csv")
        expected_fludata['epiweek'] = expected_fludata['epiweek'].astype(str)
        expected_fludata = expected_fludata.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        expected_fludata = expected_fludata.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        #rsv data
        expected_rsvdata = pd.read_csv(str(TEST_DIR) + "/testdata/acquisition/rvdss/formatted_rsv_positive_tests.csv")
        expected_rsvdata['epiweek'] = expected_rsvdata['epiweek'].astype(str)
        expected_rsvdata = expected_rsvdata.set_index(['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        expected_rsvdata = expected_rsvdata.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        
        # get tables from raw html and process before testing the function
        na_values = ['N.A.','N.A', 'N.C.','N.R.','Not Available','Not Tested',"not available",
                     "not tested","N.D.","-",'Not tested','non testé']
        flu_caption=[t for t in captions if "Influenza" in t.text][0]
        flu_tab = flu_caption.find_next('table')
        flu_tab = re.sub(",","",str(flu_tab))
                
        flu_table =  pd.read_html(flu_tab,na_values=na_values)[0].dropna(how="all")
        flu_table.columns=flu_table.columns.str.lower()
        flu_table = drop_ah1_columns(flu_table)
        flu_table= preprocess_table_columns(flu_table)
        
        rsv_caption=[t for t in captions if "RSV" in t.text][0]
        rsv_tab = rsv_caption.find_next('table')
        rsv_tab = re.sub(",","",str(rsv_tab))
                
        rsv_table =  pd.read_html(rsv_tab,na_values=na_values)[0].dropna(how="all")
        rsv_table.columns=rsv_table.columns.str.lower()
        rsv_table = drop_ah1_columns(rsv_table)
        rsv_table= preprocess_table_columns(rsv_table)
        
        rsv_table_overwrite_weeks= rsv_table.copy()
        rsv_table_overwrite_weeks= rsv_table_overwrite_weeks.replace({'week': {1: 4, 2:5, 3:6}})
        
        modified_date = "2017-01-25"
        start_year = 2016
        
        pos_flu_table = create_percent_positive_detection_table(flu_table,modified_date,start_year,True,False)
        pos_flu_table = pos_flu_table.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        
        pos_rsv_table = create_percent_positive_detection_table(rsv_table,modified_date,start_year,False,False)
        pos_rsv_table = pos_rsv_table.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        
        pos_rsv_overwrite_table = create_percent_positive_detection_table(rsv_table_overwrite_weeks,modified_date,start_year,False,True)
        pos_rsv_overwrite_table = pos_rsv_overwrite_table.sort_values(by=['epiweek', 'time_value', 'issue', 'geo_type', 'geo_value'])
        
        assert round(pos_flu_table,10).equals(round(expected_fludata,10))
        assert round(pos_rsv_table,10).equals(round(expected_rsvdata,10))
        assert round(pos_rsv_overwrite_table,10).equals(round(expected_rsvdata,10))
    
    def test_fix_edge_cases(self):
        for table, caption,season,week,expected in zip(example_edge_case_tables, example_edge_case_captions,
                                              example_edge_case_seasons,example_edge_case_weeks,
                                              expected_edge_case_tables):
            assert fix_edge_cases(table,season,caption,week).equals(expected)


    def test_fetch_one_season_from_report(self):
        pass
        
    @mock.patch("requests.get")
    def test_fetch_archived_dashboard_dates(self,mock_requests):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        expected_url = str(TEST_DIR) + "/testdata/acquisition/rvdss/ArchivedDates.txt"
        
        with open(expected_url) as f:
            expected_dates = [line.rstrip('\n') for line in f]
                
        s = requests.Session()
        s.mount('file://', FileAdapter())
        
        resp = s.get('file://'+ str(TEST_DIR) + "/testdata/acquisition/rvdss/ArchiveDates.json")
                     
        # Mocks
        mock_requests.return_value = resp
        
        url={}
        assert set(fetch_archived_dashboard_dates(url))==set(expected_dates)
        
    def test_fetch_report_data(self):
        pass

    def test_fetch_historical_dashboard_data(self):
        pass
        