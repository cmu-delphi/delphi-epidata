"""Integration tests for acquisition of rvdss data."""
# standard library
import unittest
from unittest.mock import MagicMock, patch
from copy import copy

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.rvdss.database import update, rvdss_cols, get_num_rows
import delphi.operations.secrets as secrets
from delphi_utils import get_structured_logger

# third party
import mysql.connector 
from mysql.connector.errors import IntegrityError
import pandas as pd
import numpy as np
from pathlib import Path
import pdb

# py3tester coverage target (equivalent to `import *`)
# __test_target__ = 'delphi.epidata.acquisition.covid_hosp.facility.update'

NEWLINE="\n"

class AcquisitionTests(unittest.TestCase):
  logger = get_structured_logger()

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    # self.test_utils = UnitTestUtils(__file__)

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata'
    Epidata.auth = ('epidata', 'key')

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # clear relevant tables
    epidata_cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    epidata_cur = epidata_cnx.cursor()

    epidata_cur.execute('truncate table rvdss')
    epidata_cur.execute('DELETE from api_user')
    epidata_cur.execute('INSERT INTO api_user(api_key, email) VALUES ("key", "email")')
    epidata_cnx.commit()
    epidata_cur.close()
    #epidata_cnx.close()

    # make connection and cursor available to test cases
    self.cnx = epidata_cnx
    self.cur = epidata_cnx.cursor()

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  @patch("mysql.connector.connect")
  def test_rvdss_repiratory_detections(self, mock_sql):
    connection_mock = MagicMock()

    TEST_DIR = Path(__file__).parent.parent.parent.parent
    detection_data = pd.read_csv(str(TEST_DIR) + "/testdata/acquisition/rvdss/RVD_CurrentWeekTable_Formatted.csv")
    detection_data['time_type'] = "week"

    # get the index of the subset of data we want to use
    subset_index = detection_data[(detection_data['geo_value'].isin(['nl', 'nb'])) & 
                   (detection_data['time_value'].isin([20240831, 20240907]))].index
    
    
    # change issue so the data has more than one
    detection_data.loc[subset_index,"issue"] = 20250227
    
    # take a small subset just for testing insertion
    detection_subset = detection_data.loc[subset_index]
    
    # get the expected response when calling the API
    # the dataframe needs to add the missing columns and replace nan with None
    # since that is what is returned from the API
    df = detection_subset.reindex(rvdss_cols,axis=1)
    df = df.replace({np.nan: None}).sort_values(by=["epiweek","geo_value"])
    df = df.to_dict(orient = "records")
    
    expected_response = {"epidata": df,
        "result": 1,
        "message": "success",
    }
    
    # get another subset of the data not in the subset to test more calling options
    detection_subset2 = detection_data[(detection_data['geo_value'].isin(['nu', 'nt'])) & (detection_data['time_value'].isin([20240831, 20240907])) ]
    
    df2 = detection_subset2.reindex(rvdss_cols,axis=1)
    df2 = df2.replace({np.nan: None}).sort_values(by=["epiweek","geo_value"])
    df2 = df2.to_dict(orient = "records")
    
    expected_response2 = {"epidata": df2,
        "result": 1,
        "message": "success",
    }
    
    # get another subset of the data for a single geo_value with multiple issues
    subset_index2 = detection_data[(detection_data['geo_value'].isin(['ouest du québec'])) & 
                   (detection_data['time_value'].isin([20240831, 20240907]))].index
    
    detection_data.loc[subset_index2,"issue"] = [20250220,20250227]
    detection_data.loc[subset_index2,"epiweek"] = [202435,202435]
    detection_data.loc[subset_index2,"time_value"] = [20240831,20240831]

    detection_subset3 = detection_data.loc[subset_index2]
    df3 = detection_subset3.reindex(rvdss_cols,axis=1)
    df3 = df3.replace({np.nan: None}).sort_values(by=["epiweek","geo_value"])
    df3 = df3.to_dict(orient = "records")
    
    expected_response3 = {"epidata": df3,
        "result": 1,
        "message": "success",
    }
    
    # expected response when asking for all provinces
    provincial_subset = pd.concat([detection_subset,detection_subset2])
    provincial_subset = provincial_subset.sort_values(by=['epiweek','geo_value'])
    df4 = provincial_subset.reindex(rvdss_cols,axis=1)
    df4 = df4.replace({np.nan: None}).sort_values(by=["epiweek","geo_value"])
    df4 = df4.to_dict(orient = "records")
    
    expected_response4 = {"epidata": df4,
        "result": 1,
        "message": "success",
    }
    
    # make sure the data does not yet exist
    with self.subTest(name='no data yet'):
      response = Epidata.rvdss(geo_type='province',
                               time_values= [202435, 202436],
                               geo_value = ['nl','nb'])
      self.assertEqual(response['result'], -2, response)

    # acquire sample data into local database
    with self.subTest(name='first acquisition'):
        # When the MagicMock connection's `cursor()` method is called, return
        # a real cursor made from the current open connection `cnx`.
        connection_mock.cursor.return_value = self.cnx.cursor()
        # Commit via the current open connection `cnx`, from which the cursor
        # is derived
        connection_mock.commit = self.cnx.commit
        mock_sql.return_value = connection_mock

        update(detection_subset, self.logger)

        response = Epidata.rvdss(geo_type='province',
                                 time_values= [202435, 202436],
                                 geo_value = ['nl','nb'])
        
        self.assertEqual(response,expected_response)
        
    with self.subTest(name='duplicate aquisition'):
        # The main run function checks if the update has already been fetched/updated
        # so it should never run twice, and duplocate aquisitions should never 
        # occur. Running the update twice will result in an error
        
        # When the MagicMock connection's `cursor()` method is called, return
        # a real cursor made from the current open connection `cnx`.
        connection_mock.cursor.return_value = self.cnx.cursor()
        # Commit via the current open connection `cnx`, from which the cursor
        # is derived
        connection_mock.commit = self.cnx.commit
        mock_sql.return_value = connection_mock

        with self.assertRaises(mysql.connector.errors.IntegrityError):
            update(detection_subset, self.logger)

    # Request with exact column order
    with self.subTest(name='exact column order'):
        rvdss_cols_subset = [col for col in detection_subset2.columns if col in rvdss_cols]
        ordered_cols = [col for col in rvdss_cols if col in rvdss_cols_subset] 
        ordered_df = detection_subset2[ordered_cols]
        
        connection_mock.cursor.return_value = self.cnx.cursor()
        connection_mock.commit = self.cnx.commit
        mock_sql.return_value = connection_mock
        
        update(ordered_df, self.logger)
        
        response = Epidata.rvdss(geo_type='province',
                                 time_values= [202435, 202436],
                                 geo_value = ['nt','nu'])
                
        self.assertEqual(response,expected_response2)
        
        
    # request by issue
    with self.subTest(name='issue request'):
        response = Epidata.rvdss(geo_type='province',
                                 time_values= [202435, 202436],
                                 geo_value = ['nl','nb'],
                                 issues = 20250227)
        
        self.assertEqual(response,expected_response)
                            
        
    # check requesting lists vs single values
    with self.subTest(name='duplicate aquisition'):
        # * with geo_value, single geo_type, time_value, issue
        connection_mock.cursor.return_value = self.cnx.cursor()
        connection_mock.commit = self.cnx.commit
        mock_sql.return_value = connection_mock
        
        update(detection_subset3, self.logger)
        
        response = Epidata.rvdss(geo_type='province',
                                 time_values= [202435, 202436],
                                 geo_value = "*",
                                 issues = 20250227)
        
        response2 = Epidata.rvdss(geo_type='province',
                                 time_values= "*",
                                 geo_value = ['nl','nb'],
                                 issues = 20250227)
        
        response3 = Epidata.rvdss(geo_type='lab',
                                 time_values= 202435,
                                 geo_value = 'ouest du québec',
                                 issues = [20250220,20250227])
        
        
        response4 = Epidata.rvdss(geo_type='lab',
                                 time_values= 202435,
                                 geo_value = 'ouest du québec',
                                 issues = "*")
        
        response5 = Epidata.rvdss(geo_type='province',
                                 time_values= '*',
                                 geo_value = '*',
                                 issues = "*")
        
        self.assertEqual(response,expected_response)
        self.assertEqual(response2,expected_response)
        self.assertEqual(response3,expected_response3)
        self.assertEqual(response4,expected_response3)
        self.assertEqual(response5,expected_response4)
        

