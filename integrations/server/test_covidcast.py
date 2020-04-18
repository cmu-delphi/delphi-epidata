"""Integration tests for the `covidcast` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidcastTests(unittest.TestCase):
  """Tests the `covidcast` endpoint."""

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

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234', 1.5, 2.5, 3.5, 4)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 1.5,
        'stderr': 2.5,
        'sample_size': 3.5,
        'direction': 4,
       }],
      'message': 'success',
    })

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '11111', 10, 11, 12, 13),
        (0, 'src', 'sig', 'day', 'county', 20200414, '22222', 20, 21, 22, 23),
        (0, 'src', 'sig', 'day', 'county', 20200414, '33333', 30, 31, 32, 33),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '11111', 40, 41, 42, 43),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '22222', 50, 51, 52, 53),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '33333', 60, 61, 62, 634)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'time_value': 20200414,
          'geo_value': '11111',
          'value': 10,
          'stderr': 11,
          'sample_size': 12,
          'direction': 13,
        }, {
          'time_value': 20200414,
          'geo_value': '22222',
          'value': 20,
          'stderr': 21,
          'sample_size': 22,
          'direction': 23,
        }, {
          'time_value': 20200414,
          'geo_value': '33333',
          'value': 30,
          'stderr': 31,
          'sample_size': 32,
          'direction': 33,
        },
       ],
      'message': 'success',
    })

  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200411, '01234', 10, 11, 12, 13),
        (0, 'src', 'sig', 'day', 'county', 20200412, '01234', 20, 21, 22, 23),
        (0, 'src', 'sig', 'day', 'county', 20200413, '01234', 30, 31, 32, 33),
        (0, 'src', 'sig', 'day', 'county', 20200411, '11111', 40, 41, 42, 43),
        (0, 'src', 'sig', 'day', 'county', 20200412, '22222', 50, 51, 52, 53),
        (0, 'src', 'sig', 'day', 'county', 20200413, '33333', 60, 61, 62, 63)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '20200411-20200413',
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'time_value': 20200411,
          'geo_value': '01234',
          'value': 10,
          'stderr': 11,
          'sample_size': 12,
          'direction': 13,
        }, {
          'time_value': 20200412,
          'geo_value': '01234',
          'value': 20,
          'stderr': 21,
          'sample_size': 22,
          'direction': 23,
        }, {
          'time_value': 20200413,
          'geo_value': '01234',
          'value': 30,
          'stderr': 31,
          'sample_size': 32,
          'direction': 33,
        },
       ],
      'message': 'success',
    })

  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234', 0, 0, 0, 0)
    ''')
    self.cnx.commit()

    # fail to insert different dummy data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
      self.cur.execute('''
        insert into covidcast values
          (0, 'src', 'sig', 'day', 'county', 20200414, '01234', 1, 1, 1, 1)
      ''')

  def test_nullable_columns(self):
    """Missing values should be surfaced as null."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234', 0.123,
          NULL, NULL, NULL)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 0.123,
        'stderr': None,
        'sample_size': None,
        'direction': None,
       }],
      'message': 'success',
    })

  def test_temporal_partitioning(self):
    """Request a signal that's available at multiple temporal resolutions."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'hour', 'state', 2020041714, 'vi', 10, 11, 12, 13),
        (0, 'src', 'sig', 'day', 'state', 20200417, 'vi', 20, 21, 22, 23),
        (0, 'src', 'sig', 'week', 'state', 202016, 'vi', 30, 31, 32, 33),
        (0, 'src', 'sig', 'month', 'state', 202004, 'vi', 40, 41, 42, 43),
        (0, 'src', 'sig', 'year', 'state', 2020, 'vi', 50, 51, 52, 53)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'week',
      'geo_type': 'state',
      'time_values': '0-9999999999',
      'geo_value': 'vi',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 202016,
        'geo_value': 'vi',
        'value': 30,
        'stderr': 31,
        'sample_size': 32,
        'direction': 33,
       }],
      'message': 'success',
    })
