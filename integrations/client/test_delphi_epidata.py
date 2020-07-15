"""Integration tests for delphi_epidata.py."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_covidcast_meta_cache

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
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          456, 5.5, 1.2, 10.5, 789, 0, 20200415, 1),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          345, 6.5, 2.2, 11.5, 678, 0, 20200416, 2)
    ''')
    self.cnx.commit()

    # fetch data, without specifying issue or lag
    response_1 = Epidata.covidcast(
        'src', 'sig', 'day', 'county', 20200414, '01234')

    # check result
    self.assertEqual(response_1, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 6.5,
        'stderr': 2.2,
        'sample_size': 11.5,
        'direction': 0,
        'issue': 20200416,
        'lag': 2
       }],
      'message': 'success',
    })

    # fetch data, specifying as_of
    response_1a = Epidata.covidcast(
        'src', 'sig', 'day', 'county', 20200414, '01234',
      as_of=20200415)

    # check result
    self.assertEqual(response_1a, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 5.5,
        'stderr': 1.2,
        'sample_size': 10.5,
        'direction': 0,
        'issue': 20200415,
        'lag': 1
       }],
      'message': 'success',
    })

    # fetch data, specifying issue range, not lag
    response_2 = Epidata.covidcast(
        'src', 'sig', 'day', 'county', 20200414, '01234',
        issues=Epidata.range(20200414, 20200415))

    # check result
    self.assertDictEqual(response_2, {
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
        }, {
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 5.5,
            'stderr': 1.2,
            'sample_size': 10.5,
            'direction': 0,
            'issue': 20200415,
            'lag': 1
        }],
        'message': 'success',
    })

    # fetch data, specifying lag, not issue range
    response_3 = Epidata.covidcast(
        'src', 'sig', 'day', 'county', 20200414, '01234',
        lag=2)

    # check result
    self.assertDictEqual(response_3, {
        'result': 1,
        'epidata': [{
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 6.5,
            'stderr': 2.2,
            'sample_size': 11.5,
            'direction': 0,
            'issue': 20200416,
            'lag': 2
        }],
        'message': 'success',
    })

  def test_covidcast_meta(self):
    """Test that the covidcast_meta endpoint returns expected data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          345, 6.0, 2.2, 11.5, 678, 0, 20200416, 2),
        (0, 'src', 'sig', 'day', 'county', 20200415, '01234',
          345, 7.0, 2.0, 12.5, 678, 0, 20200416, 1)
    ''')
    self.cnx.commit()

    # cache it
    update_covidcast_meta_cache(args=None)

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
        'max_time': 20200415,
        'num_locations': 1,
        'min_value': 6.0,
        'max_value': 7.0,
        'mean_value': '6.5000000',
        'stdev_value': '0.5000000',
        'last_update': 345,
        'max_issue': 20200416,
        'min_lag': 1,
        'max_lag': 2
       }],
      'message': 'success',
    })
