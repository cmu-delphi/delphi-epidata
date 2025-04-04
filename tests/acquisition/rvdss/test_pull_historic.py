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

from delphi.epidata.acquisition.rvdss.pull_historic import (get_report_season_years, add_https_prefix, 
construct_weekly_report_urls, report_weeks, get_report_date, extract_captions_of_interest, get_modified_dates,
deduplicate_rows, drop_ah1_columns, create_detections_table, create_number_detections_table, 
create_percent_positive_detection_table, fetch_one_season_from_report, fetch_archived_dashboard_dates, 
fetch_report_data, fetch_historical_dashboard_data)

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.rvdss.pull_historic"


class TestPullHistoric():

    def test_syntax(self):
        """This no-op test ensures that syntax is valid."""
        pass
    
    def test_get_report_season_years(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/main_page_20192020.html"
        
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert get_report_season_years(new_soup) == ['2019','2020']

    def test_add_https_prefix(self):
       assert add_https_prefix(["/random.html"]) == ["https://www.canada.ca/random.html"]
       assert add_https_prefix(["http://randomurl2.html"]) == ["https://randomurl2.html"]
       assert add_https_prefix(["https://randomurl3.html"]) == ["https://randomurl3.html"]
   
    def test_construct_weekly_report_urls(self):
        TEST_DIR = Path(__file__).parent.parent.parent.parent
        
        # test regular urls
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/main_page_20192020.html"
        test_data_url  = str(TEST_DIR) + "/testdata/acquisition/rvdss/test_urls_20192020.txt"
        
        with open(test_data_url) as f:
            expected_urls = [line.rstrip('\n') for line in f]
    
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert set(construct_weekly_report_urls(new_soup)) == set(expected_urls)
            
        # test alternative urls
        url_alt = str(TEST_DIR) + "/testdata/acquisition/rvdss/main_page_20162017.html"
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
        url = str(TEST_DIR) + "/testdata/acquisition/rvdss/main_page_20192020.html"
        with open(url) as page:
            soup = BeautifulSoup(page.read(),'html.parser')
            new_soup = BeautifulSoup(soup.text, 'html.parser')
            assert set(report_weeks(new_soup)) == set(expected_weeks)
        

    def test_get_report_date(self):
        pass

    def test_extract_captions_of_interest(self):
        pass
        
    def test_get_modified_dates(self):
        pass

    def test_deduplicate_rows(self):
        pass

    def test_drop_ah1_columns(self):
        pass

    def test_create_detections_table(self):
        pass

    def test_create_number_detections_table(self):
        pass

    def test_create_percent_positive_detection_table(self):
        pass

    def test_fetch_one_season_from_report(self):
        pass
        
    def test_fetch_archived_dashboard_dates(self):
        pass

    def test_fetch_report_data(self):
        pass

    def test_fetch_historical_dashboard_data(self):
        pass
        