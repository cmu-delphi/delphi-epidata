"""Integration tests for delphi_epidata.py."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'


class DelphiEpidataPythonClientTests(unittest.TestCase):
  """Tests the Python client."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear relevant tables
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

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_covidcast(self):
    """Test that the covidcast endpoint returns expected data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0)
    ''')
    self.cnx.commit()

    # fetch data
    response = Epidata.covidcast(
        'src', 'sig', 'day', 'county', 20200414, '01234')

    # check result
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 1.5,
        'stderr': 2.5,
        'sample_size': 3.5,
        'direction': 4,
        'issue': 20200414,
        'lag': 0
       }],
      'message': 'success',
    })

  def test_covidcast_meta(self):
    """Test that the covidcast_meta endpoint returns expected data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0)
    ''')
    self.cnx.commit()

    # fetch data
    response = Epidata.covidcast_meta()

    # check result
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'data_source': 'src',
        'signal': 'sig',
        'time_type': 'day',
        'geo_type': 'county',
        'min_time': 20200414,
        'max_time': 20200414,
        'num_locations': 1,
        'min_value': 1.5,
        'max_value': 1.5,
        'mean_value': 1.5,
        'stdev_value': 0,
        'last_update': 123,
        'max_issue': 20200414,
        'min_lag': 0,
        'max_lag': 0
       }],
      'message': 'success',
    })
