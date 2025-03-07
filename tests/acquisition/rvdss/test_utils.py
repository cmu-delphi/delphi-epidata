"""Unit tests for rvdss/utils.py."""

import pytest
import mock
import requests
from requests_file import FileAdapter
from pathlib import Path
import pandas as pd

from delphi.epidata.acquisition.rvdss.utils import (abbreviate_virus, abbreviate_geo, create_geo_types, check_date_format,
get_dashboard_update_date, check_most_recent_update_date, preprocess_table_columns, add_flu_prefix, 
make_signal_type_spelling_consistent, get_positive_data, get_detections_data, fetch_dashboard_data) 

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.rvdss.utils"

example_unprocessed_data = [
    pd.DataFrame({'Reporting\xa0Laboratories':1},index=[0]),
    pd.DataFrame({'lab':1,'lab.2':2},index=[0]),
    pd.DataFrame({'Reporting.lab':1},index=[0]),
    pd.DataFrame({'flucounts (all)':2},index=[0]),
    pd.DataFrame({'fluah1 (2009)':2},index=[0]),
    pd.DataFrame({'flucounts       s':2},index=[0]),
    pd.DataFrame({'lab/tech':3},index=[0]),
    
    pd.DataFrame({'at counts':1},index=[0]),
    pd.DataFrame({'canada counts':2},index=[0]),
    pd.DataFrame({'cb counts':3},index=[0]),
    
    pd.DataFrame({'h1n1 2009 ':3},index=[0]),
    pd.DataFrame({'h1n12009 counts':3},index=[0]), 
    pd.DataFrame({'a_h1 counts':3},index=[0]),
    pd.DataFrame({'ah1 counts':3},index=[0]),
    pd.DataFrame({'a_uns counts':3},index=[0]),
    pd.DataFrame({'a_h3 counts':3},index=[0]),
    
    pd.DataFrame({'parainfluenza a':4,'piv b':4, "para c":4},index=[0]),
    pd.DataFrame({'adeno a':4, 'adeno b':4},index=[0]),
    pd.DataFrame({'human metapneumovirus a':4},index=[0]),
    pd.DataFrame({'enterovirus_rhinovirus a':4,'rhinovirus b':4, "rhv c":4,"entero_rhino d":4,"rhino e":4, "ev_rv f":4},index=[0]),
    pd.DataFrame({'coronavirus a':4,'coron b':4, "coro c":4},index=[0]),
    pd.DataFrame({'respiratory syncytial virus a':4},index=[0]),
    pd.DataFrame({'influenza counts':4},index=[0]),
    pd.DataFrame({'sars-cov-2 counts':4},index=[0]),
    
    pd.DataFrame({"flu a":5,"flu b":5},index=[0]),
    pd.DataFrame({"flutest p":5},index=[0]),
    pd.DataFrame({"other hpiv a":5, "other_hpiv count b":5},index=[0]),
    
    
    pd.DataFrame({"flu apositive":6,"flu bpositive":6},index=[0]),
    pd.DataFrame({"hpiv_1 counts":6,"hpiv_2 counts":6,"hpiv_3 counts":6,"hpiv_4 counts":6},index=[0]),
    
    pd.DataFrame({"num positive tests":7},index=[0]),
    pd.DataFrame({"num positive a":7,"num pos b":7},index=[0]),
    pd.DataFrame({"num test a":7,"num tested b":7},index=[0]),
    pd.DataFrame({"virus% a":7,"virus % b":7},index=[0]),
    pd.DataFrame({"total counts":7},index=[0])
]

expected_processed_data = [
    pd.DataFrame({'reporting laboratories':1},index=[0]),
    pd.DataFrame({'lab':1,'lab2':2},index=[0]).rename(columns={"lab":"lab","lab2":"lab"}),
    pd.DataFrame({'reportinglab':1},index=[0]),
    pd.DataFrame({'flucounts ':2},index=[0]),
    pd.DataFrame({'fluah12009':2},index=[0]),
    pd.DataFrame({'flucounts s':2},index=[0]),
    pd.DataFrame({'lab_tech':3},index=[0]),
    
    pd.DataFrame({'atl counts':1},index=[0]),
    pd.DataFrame({'can counts':2},index=[0]),
    pd.DataFrame({'bc counts':3},index=[0]),
    
    pd.DataFrame({'ah1n1pdm09':3},index=[0]),
    pd.DataFrame({'ah1n1pdm09 counts':3},index=[0]), 
    pd.DataFrame({'ah1n1pdm09 counts':3},index=[0]),
    pd.DataFrame({'ah1n1pdm09 counts':3},index=[0]),
    pd.DataFrame({'auns counts':3},index=[0]),
    pd.DataFrame({'ah3 counts':3},index=[0]),
    
    pd.DataFrame({'hpiv a':4,'hpiv b':4, "hpiv c":4},index=[0]),
    pd.DataFrame({'adv a':4, 'adv b':4},index=[0]),
    pd.DataFrame({'hmpv a':4},index=[0]),
    pd.DataFrame({'evrv a':4,'evrv b':4, "evrv c":4,"evrv d":4,"evrv e":4, "evrv f":4},index=[0]),
    pd.DataFrame({'hcov a':4,'hcov b':4, "hcov c":4},index=[0]),
    pd.DataFrame({'rsv a':4},index=[0]),
    pd.DataFrame({'flu counts':4},index=[0]),
    pd.DataFrame({'sarscov2 counts':4},index=[0]),
    
    pd.DataFrame({"flua":5,"flub":5},index=[0]),
    pd.DataFrame({"flu tests p":5},index=[0]),
    pd.DataFrame({"hpivother a":5, "hpivother count b":5},index=[0]),
    
    pd.DataFrame({"flua_positive_tests":6,"flub_positive_tests":6},index=[0]),
    pd.DataFrame({"hpiv1 counts":6,"hpiv2 counts":6,"hpiv3 counts":6,"hpiv4 counts":6},index=[0]),
    
    pd.DataFrame({"num positive_tests":7},index=[0]),
    pd.DataFrame({"num positive_tests a":7,"num positive_tests b":7},index=[0]),
    pd.DataFrame({"num tests a":7,"num tests b":7},index=[0]),
    pd.DataFrame({"virus_pct_positive a":7,"virus_pct_positive b":7},index=[0]),
    pd.DataFrame({"counts":7},index=[0])
]

class TestUtils:
    def test_syntax(self):
        """This no-op test ensures that syntax is valid."""
        pass

    def test_abbreviate_virus(self):
        assert abbreviate_virus("influenza") == "flu" # normal case
        assert abbreviate_virus("flu") == "flu" # already abbreviated
        assert abbreviate_virus("parainfluenza") == "hpiv" 
        assert abbreviate_virus("banana") == "banana" #non geos should remain as is

    def test_abbreviate_geo(self):
        assert abbreviate_geo("british columbia") == "bc"
        assert abbreviate_geo("québec") == "qc" # recognise accents in provinces
        assert abbreviate_geo("Région Nord-Est") == "région nord est" # remove dashes, make lowercase
        assert abbreviate_geo("P.H.O.L. - Sault Ste. Marie") == "phol sault ste marie"
        assert abbreviate_geo("random lab") == "random lab" #unknown geos remain unchanged     
        # only province names on their own should be abbreviated, not as part of a larger name
        assert abbreviate_geo("british columbia lab") == "british columbia lab"
        
    def test_create_geo_types(self):
        assert create_geo_types("canada","lab") == "nation"
        assert create_geo_types("bc","lab") == "region"
        assert create_geo_types("random lab","lab") == "lab"
        assert create_geo_types("Canada","province") == "nation"
        
    def test_check_date_format(self):
        assert check_date_format("2015-09-05") == "2015-09-05"
        assert check_date_format("01/10/2020") == "2020-10-01" # change d/m/Y to Y-m-d
        assert check_date_format("02-11-2013") == "2013-11-02" # change d-m-Y to Y-m-d
        with pytest.raises(AssertionError):
            check_date_format("02-2005-10") # Invalid date format raises error
    
    @mock.patch("requests.get")
    def test_get_dashboard_update_date(self, mock_requests):
        # Set up fake data.
        headers={}
        url = "testurl.ca"
        
        s = requests.Session()
        s.mount('file://', FileAdapter())

        TEST_DIR = Path(__file__).parent
        resp = s.get('file://'+ str(TEST_DIR) + "/RVD_UpdateDate.csv") 
        
        # Mocks
        mock_requests.return_value = resp
        assert get_dashboard_update_date(url, headers) == "2025-02-20"
        
    def test_check_most_recent_update_date(self):
        TEST_DIR = Path(__file__).parent
        path = str(TEST_DIR) + "/example_update_dates.txt"
        
        assert check_most_recent_update_date("2025-02-14",path) == True #date is in the file
        assert check_most_recent_update_date("2025-03-20",path) == False #date is not in the file
        
    def test_preprocess_table_columns(self):
        for example, expected in zip(example_unprocessed_data, expected_processed_data):
            assert preprocess_table_columns(example).equals(expected)
    
    def test_add_flu_prefix(self):
        assert add_flu_prefix("ah3_pos") == "fluah3_pos"
        assert add_flu_prefix("auns") == "fluauns"
        assert add_flu_prefix("ah1pdm09 tests") == "fluah1pdm09 tests"
        assert add_flu_prefix("ah1n1pdm09") == "fluah1n1pdm09"
        assert add_flu_prefix("fluah1n1pdm09") == "fluah1n1pdm09" #if prefix exists, do nothing
        assert add_flu_prefix("random string") == "random string" #if no prefix, it should do nothing
        
    def test_make_signal_type_spelling_consistent(self):
        assert make_signal_type_spelling_consistent("positive tests") == "positive_tests"
        assert make_signal_type_spelling_consistent("flu pos") == "flu positive_tests"
        assert make_signal_type_spelling_consistent("rsv tested") == "rsv tests"
        assert make_signal_type_spelling_consistent("covid total tested") == "covid tests"
        assert make_signal_type_spelling_consistent("flua%") == "flua_pct_positive"
        
    
    def test_get_positive_data(self):
        pass
        
    def test_get_detections_data(self):
        pass
    
    def test_fetch_dashboard_data(self):
        pass