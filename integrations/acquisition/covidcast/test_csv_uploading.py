"""Integration tests for covidcast's CSV-to-database uploading."""

# standard library
from datetime import date
import os
import unittest
from unittest.mock import MagicMock

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
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
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast')
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

  def test_uploading(self):
    """Scan, parse, upload, archive, serve, and fetch a covidcast signal."""

    # print full diff if something unexpected comes out
    self.maxDiff=None

    # make some fake data files
    data_dir = 'covid/data'
    source_receiving_dir = data_dir + '/receiving/src-name'
    os.makedirs(source_receiving_dir, exist_ok=True)

    # valid
    with open(source_receiving_dir + '/20200419_state_test.csv', 'w') as f:
      f.write('geo_id,val,se,sample_size\n')
      f.write('ca,1,0.1,10\n')
      f.write('tx,2,0.2,20\n')
      f.write('fl,3,0.3,30\n')

    # valid wip
    with open(source_receiving_dir + '/20200419_state_wip_prototype.csv', 'w') as f:
      f.write('geo_id,val,se,sample_size\n')
      f.write('me,10,0.01,100\n')
      f.write('nd,20,0.02,200\n')
      f.write('wa,30,0.03,300\n')

    # invalid
    with open(source_receiving_dir + '/20200420_state_test.csv', 'w') as f:
      f.write('this,header,is,wrong\n')

    # invalid
    with open(source_receiving_dir + '/hello.csv', 'w') as f:
      f.write('file name is wrong\n')

    # invalid
    with open(source_receiving_dir + '/20200419_state_wip_really_long_name_that_will_get_truncated.csv', 'w') as f:
      f.write('geo_id,val,se,sample_size\n')
      f.write('pa,100,5.4,624\n')

    # upload CSVs
    args = MagicMock(data_dir=data_dir)
    main(args)

    # request CSV data from the API
    response = Epidata.covidcast(
        'src-name', 'test', 'day', 'state', 20200419, '*')


    expected_issue_day=date.today()
    expected_issue=expected_issue_day.strftime("%Y%m%d")
    def apply_lag(expected_epidata):
      for dct in expected_epidata:
        dct['issue'] = int(expected_issue)
        time_value_day = date(year=dct['time_value'] // 10000,
                              month=dct['time_value'] % 10000 // 100,
                              day= dct['time_value'] % 100)
        expected_lag = (expected_issue_day - time_value_day).days
        dct['lag'] = expected_lag
      return expected_epidata
    
    # verify data matches the CSV
    # NB these are ordered by geo_value
    self.assertEqual(response, {
      'result': 1,
      'epidata': apply_lag([
        {
          'time_value': 20200419,
          'geo_value': 'ca',
          'value': 1,
          'stderr': 0.1,
          'sample_size': 10,
          'direction': None,
        },
        {
          'time_value': 20200419,
          'geo_value': 'fl',
          'value': 3,
          'stderr': 0.3,
          'sample_size': 30,
          'direction': None,
        },
        {
          'time_value': 20200419,
          'geo_value': 'tx',
          'value': 2,
          'stderr': 0.2,
          'sample_size': 20,
          'direction': None,
        },
    ]),
      'message': 'success',
    })

    # request CSV data from the API on WIP signal
    response = Epidata.covidcast(
      'src-name', 'wip_prototype', 'day', 'state', 20200419, '*')

    
    # verify data matches the CSV
    # NB these are ordered by geo_value
    self.assertEqual(response, {
      'result': 1,
      'epidata': apply_lag([
        {
          'time_value': 20200419,
          'geo_value': 'me',
          'value': 10,
          'stderr': 0.01,
          'sample_size': 100,
          'direction': None,
        },
        {
          'time_value': 20200419,
          'geo_value': 'nd',
          'value': 20,
          'stderr': 0.02,
          'sample_size': 200,
          'direction': None,
        },
        {
          'time_value': 20200419,
          'geo_value': 'wa',
          'value': 30,
          'stderr': 0.03,
          'sample_size': 300,
          'direction': None,
        },
       ]),
      'message': 'success',
    })

    # request CSV data from the API on the long-named signal
    response = Epidata.covidcast(
      'src-name', 'wip_really_long_name_that_will_g', 'day', 'state', 20200419, '*')

    # verify data matches the CSV
    # if the CSV failed correctly there should be no results
    self.assertEqual(response, {
      'result': -2,
      'message': 'no results',
    })

    # verify timestamps and default values are reasonable
    self.cur.execute('select timestamp1, timestamp2, direction from covidcast')
    for timestamp1, timestamp2, direction in self.cur:
      self.assertGreater(timestamp1, 0)
      self.assertEqual(timestamp2, 0)
      self.assertIsNone(direction)

    # verify that the CSVs were archived
    for sig in ["test","wip_prototype"]:
      path = data_dir + f'/archive/successful/src-name/20200419_state_{sig}.csv.gz'
      self.assertIsNotNone(os.stat(path))
    path = data_dir + '/archive/failed/src-name/20200420_state_test.csv'
    self.assertIsNotNone(os.stat(path))
    path = data_dir + '/archive/failed/unknown/hello.csv'
    self.assertIsNotNone(os.stat(path))
