"""Unit tests for rvdss/pull_historic.py."""

import pytest
import mock

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
        pass

    def test_add_https_prefix(self):
       # assert add_https_prefix(["/random.html"]) == "https://www.canada.ca/random.html"
       # assert add_https_prefix(["http://randomurl2.html"]) == "https://randomurl2.html"
       # assert add_https_prefix(["https://randomurl3.html"]) == "https://randomurl3.html"
       pass
   
    def test_construct_weekly_report_urls(self):
        pass

    def test_report_weeks(self):
        pass

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
        