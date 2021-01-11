"""Integration tests for covidcast's CSV-to-database uploading."""

# standard library
from datetime import date
import os
import unittest
from unittest.mock import patch
from functools import partialmethod
from datetime import date

# third party
import mysql.connector
import epiweeks as epi


# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast_nowcast.load_sensors import main
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast_nowcast.load_sensors'

FIXED_ISSUE_IMPORTER = partialmethod(CsvImporter.find_csv_files,
                                     issue=(date(2020, 4, 21), epi.Week.fromdate(date(2020, 4, 21)))
                                     )


class CsvUploadingTests(unittest.TestCase):
  """Tests covidcast nowcast CSV uploading."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast_nowcast')
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

  @patch('delphi.epidata.acquisition.covidcast_nowcast.load_sensors.CsvImporter.find_csv_files',
         new=FIXED_ISSUE_IMPORTER)
  def test_uploading(self):
    """Scan, parse, upload, archive, serve, and fetch a covidcast_nowcast signal."""

    # print full diff if something unexpected comes out
    self.maxDiff=None

    receiving_dir = '/common/covidcast_nowcast/receiving/src/'
    success_dir = '/common/covidcast_nowcast/archive/successful/src/'
    failed_dir = '/common/covidcast_nowcast/archive/failed/src/'
    os.makedirs(receiving_dir, exist_ok=True)
    os.makedirs(success_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    # valid
    with open(receiving_dir + '20200419_state_test.csv', 'w') as f:
      f.write('geo_value,value\n')
      f.write('ca,1\n')

    # invalid filename
    with open(receiving_dir + 'hello.csv', 'w') as f:
      f.write('file name is wrong\n')

    # upload CSVs
    main()

    # check files moved correctly
    self.assertTrue(
      os.path.isfile(success_dir + '20200419_state_test.csv')
    )
    self.assertTrue(
      os.path.isfile(failed_dir + 'hello.csv')
    )
    with self.assertRaises(Exception):
      # no data, will cause pandas to raise error
      with open(receiving_dir + '20200419_state_empty.csv', 'w') as f:
        f.write('')
      main()
    self.assertTrue(
      os.path.isfile(failed_dir + '20200419_state_empty.csv')
    )

    # check data uploaded
    response = Epidata.covidcast_nowcast(
      'src', 'test', 'day', 'state', 20200419, 'ca')
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200419,
        'geo_value': 'ca',
        'value': 1,
        'issue': 20200421,
        'lag': 2,
        'signal': 'test',
      }],
      'message': 'success',
    })
