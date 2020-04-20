"""Integration tests for covidcast's CSV-to-database uploading."""

# standard library
import os
import unittest
from unittest.mock import MagicMock

# third party
import mysql.connector
import requests

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

    # make some fake data files
    data_dir = 'covid/data'
    source_receiving_dir = data_dir + '/receiving/src-name'
    os.makedirs(source_receiving_dir, exist_ok=True)

    # valid
    with open(source_receiving_dir + '/20200419_state_test.csv', 'w') as f:
      f.write('geo_id,val,se,sample_size,direction\n')
      f.write('ca,1,0.1,10,1\n')
      f.write('tx,2,0.2,20,NA\n')
      f.write('fl,3,0.3,30,-1\n')

    # invalid
    with open(source_receiving_dir + '/20200420_state_test.csv', 'w') as f:
      f.write('this,header,is,wrong\n')

    # invalid
    with open(source_receiving_dir + '/hello.csv', 'w') as f:
      f.write('file name is wrong\n')

    # upload CSVs
    args = MagicMock(data_dir=data_dir, test=False)
    main(args)

    # request CSV data from the API
    response = Epidata.covidcast(
        'src-name', 'test', 'day', 'state', 20200419, '*')

    # verify data matches the CSV
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'time_value': 20200419,
          'geo_value': 'ca',
          'value': 1,
          'stderr': 0.1,
          'sample_size': 10,
          'direction': 1,
        },
        {
          'time_value': 20200419,
          'geo_value': 'fl',
          'value': 3,
          'stderr': 0.3,
          'sample_size': 30,
          'direction': -1,
        },
        {
          'time_value': 20200419,
          'geo_value': 'tx',
          'value': 2,
          'stderr': 0.2,
          'sample_size': 20,
          'direction': None,
        },
       ],
      'message': 'success',
    })

    # verify that the CSVs were archived
    path = data_dir + '/archive/successful/src-name/20200419_state_test.csv.gz'
    self.assertIsNotNone(os.stat(path))
    path = data_dir + '/archive/failed/src-name/20200420_state_test.csv'
    self.assertIsNotNone(os.stat(path))
    path = data_dir + '/archive/failed/unknown/hello.csv'
    self.assertIsNotNone(os.stat(path))
