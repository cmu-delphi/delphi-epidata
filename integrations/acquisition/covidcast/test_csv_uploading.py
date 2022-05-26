"""Integration tests for covidcast's CSV-to-database uploading."""

# standard library
from datetime import date
import os
import unittest
from unittest.mock import MagicMock

# third party
import mysql.connector
import pandas as pd
import numpy as np

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.csv_to_database import main
from delphi.epidata.acquisition.covidcast.dbjobs_runner import main as dbjobs_main
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.csv_to_database'


class CsvUploadingTests(unittest.TestCase):
  """Tests covidcast CSV uploading."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='covid')
    cur = cnx.cursor()

    # clear all tables
    cur.execute("truncate table signal_load")
    cur.execute("truncate table signal_history")
    cur.execute("truncate table signal_latest")
    cur.execute("truncate table geo_dim")
    cur.execute("truncate table signal_dim")
    # reset the `covidcast_meta_cache` table (it should always have one row)
    cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  @staticmethod
  def apply_lag(expected_epidata):
    expected_issue_day=date.today()
    expected_issue=expected_issue_day.strftime("%Y%m%d")
    for dct in expected_epidata:
      dct['issue'] = int(expected_issue)
      time_value_day = date(year=dct['time_value'] // 10000,
                            month=dct['time_value'] % 10000 // 100,
                            day= dct['time_value'] % 100)
      expected_lag = (expected_issue_day - time_value_day).days
      dct['lag'] = expected_lag
    return expected_epidata

  def verify_timestamps_and_defaults(self):
    self.cur.execute('''
select value_updated_timestamp from signal_history
UNION ALL
select value_updated_timestamp from signal_latest''')
    for (value_updated_timestamp,) in self.cur:
      self.assertGreater(value_updated_timestamp, 0)

  def test_uploading(self):
    """Scan, parse, upload, archive, serve, and fetch a covidcast signal."""

    # print full diff if something unexpected comes out
    self.maxDiff=None

    # make some fake data files
    data_dir = 'covid/data'
    source_receiving_dir = data_dir + '/receiving/src-name'
    log_file_directory = "/var/log/"
    os.makedirs(source_receiving_dir, exist_ok=True)
    os.makedirs(log_file_directory, exist_ok=True)
    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(
          log_file=log_file_directory +
          "output.log",
          data_dir=data_dir,
          specific_issue_date=False)
    uploader_column_rename = {"geo_id": "geo_value", "val": "value", "se": "stderr", "missing_val": "missing_value", "missing_se": "missing_stderr"}


    with self.subTest("Valid CSV with correct missing columns"):
      values = pd.DataFrame({
        "geo_id": ["ca", "fl", "tx"],
        "val": [1.0, 2.0, 3.0],
        "se": [0.1, 0.2, 0.3],
        "sample_size": [10.0, 20.0, 30.0],
        "missing_val": [Nans.NOT_MISSING] * 3,
        "missing_se": [Nans.NOT_MISSING] * 3,
        "missing_sample_size": [Nans.NOT_MISSING] * 3
      })
      signal_name = "test"
      values.to_csv(source_receiving_dir + f'/20200419_state_{signal_name}.csv', index=False)

      # upload CSVs
      main(args)
      dbjobs_main()
      response = Epidata.covidcast('src-name', signal_name, 'day', 'state', 20200419, '*')

      expected_values = pd.concat([values, pd.DataFrame({ "time_value": [20200419] * 3, "signal": [signal_name] * 3, "direction": [None] * 3})], axis=1).rename(columns=uploader_column_rename).to_dict(orient="records")
      expected_response = {'result': 1, 'epidata': self.apply_lag(expected_values), 'message': 'success'}

      self.assertEqual(response, expected_response)
      self.verify_timestamps_and_defaults()

      # Verify that files were archived
      path = data_dir + f'/archive/successful/src-name/20200419_state_test.csv.gz'
      self.assertIsNotNone(os.stat(path))

      self.tearDown()
      self.setUp()


    with self.subTest("Valid CSV with no missing columns should set intelligent defaults"):
      values = pd.DataFrame({
        "geo_id": ["ca", "fl", "tx"],
        "val": [None, 2.0, 3.0],
        "se": [0.1, None, 0.3],
        "sample_size": [10.0, 20.0, None]
      }, dtype=object)
      signal_name = "test_no_missing_cols"
      values.to_csv(source_receiving_dir + f'/20200419_state_{signal_name}.csv', index=False)

      # upload CSVs
      main(args)
      dbjobs_main()
      response = Epidata.covidcast('src-name', signal_name, 'day', 'state', 20200419, '*')

      expected_values = pd.concat([values, pd.DataFrame({
        "time_value": [20200419] * 3,
        "signal": [signal_name] * 3,
        "direction": [None] * 3,
        "missing_value": [Nans.OTHER] + [Nans.NOT_MISSING] * 2,
        "missing_stderr": [Nans.NOT_MISSING, Nans.OTHER, Nans.NOT_MISSING],
        "missing_sample_size": [Nans.NOT_MISSING] * 2 + [Nans.OTHER]
      })], axis=1).rename(columns=uploader_column_rename).to_dict(orient="records")
      expected_response = {'result': 1, 'epidata': self.apply_lag(expected_values), 'message': 'success'}

      self.assertEqual(response, expected_response)
      self.verify_timestamps_and_defaults()

      self.tearDown()
      self.setUp()


    with self.subTest("Invalid, missing with an inf value"):
      values = pd.DataFrame({
        "geo_id": ["tx"],
        "val": [np.inf],
        "se": [0.3],
        "sample_size": [None],
        "missing_value": [Nans.OTHER],
        "missing_stderr": [Nans.NOT_MISSING],
        "missing_sample_size": [Nans.NOT_MISSING]
      })
      signal_name = "test_with_inf"
      values.to_csv(source_receiving_dir + f'/20200419_state_{signal_name}.csv', index=False)

      # upload CSVs
      main(args)
      dbjobs_main()
      response = Epidata.covidcast('src-name', signal_name, 'day', 'state', 20200419, '*')

      expected_response = {'result': -2, 'message': 'no results'}

      self.assertEqual(response, expected_response)
      self.verify_timestamps_and_defaults()
      self.tearDown()
      self.setUp()


    with self.subTest("Valid, missing with incorrect missing codes, fixed by acquisition"):
      values = pd.DataFrame({
        "geo_id": ["tx"],
        "val": [None],
        "se": [0.3],
        "sample_size": [30.0],
        "missing_val": [Nans.NOT_MISSING],
        "missing_se": [Nans.NOT_MISSING],
        "missing_sample_size": [Nans.OTHER]
      }).replace({np.nan:None})
      signal_name = "test_incorrect_missing_codes"
      values.to_csv(source_receiving_dir + f'/20200419_state_{signal_name}.csv', index=False)

      # upload CSVs
      main(args)
      dbjobs_main()
      response = Epidata.covidcast('src-name', signal_name, 'day', 'state', 20200419, '*')

      expected_values_df = pd.concat([values, pd.DataFrame({
        "time_value": [20200419],
        "signal": [signal_name],
        "direction": [None]})], axis=1).rename(columns=uploader_column_rename)
      expected_values_df["missing_value"].iloc[0] = Nans.OTHER
      expected_values_df["missing_sample_size"].iloc[0] = Nans.NOT_MISSING
      expected_values = expected_values_df.to_dict(orient="records")
      expected_response = {'result': 1, 'epidata': self.apply_lag(expected_values), 'message': 'success'}

      self.assertEqual(response, expected_response)
      self.verify_timestamps_and_defaults()

      self.tearDown()
      self.setUp()


    with self.subTest("Invalid signal with a too-long name"):
      values = pd.DataFrame({
        "geo_id": ["pa"],
        "val": [100.0],
        "se": [5.4],
        "sample_size": [624.0],
        "missing_val": [Nans.NOT_MISSING],
        "missing_se": [Nans.NOT_MISSING],
        "missing_sample_size": [Nans.NOT_MISSING]
      })
      signal_name = "really_long_name_that_will_get_truncated_lorem_ipsum_dolor_sit_amet"
      values.to_csv(source_receiving_dir + f'/20200419_state_{signal_name}.csv', index=False)

      # upload CSVs
      main(args)
      dbjobs_main()
      response = Epidata.covidcast('src-name', signal_name, 'day', 'state', 20200419, '*')

      expected_response = {'result': -2, 'message': 'no results'}

      self.assertEqual(response, expected_response)
      self.verify_timestamps_and_defaults()

      self.tearDown()
      self.setUp()


    with self.subTest("Invalid file with a wrong header"):
      with open(source_receiving_dir + '/20200420_state_test.csv', 'w') as f:
        f.write('this,header,is,wrong\n')

      main(args)
      dbjobs_main()

      path = data_dir + '/archive/failed/src-name/20200420_state_test.csv'
      self.assertIsNotNone(os.stat(path))

      self.tearDown()
      self.setUp()


    with self.subTest("Invalid file with a wrong name"):
      with open(source_receiving_dir + '/hello.csv', 'w') as f:
        f.write('file name is wrong\n')

      main(args)
      dbjobs_main()

      path = data_dir + '/archive/failed/unknown/hello.csv'
      self.assertIsNotNone(os.stat(path))

      self.tearDown()
      self.setUp()
