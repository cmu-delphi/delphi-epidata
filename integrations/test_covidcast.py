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
        (0, 'sensor', 'county', '2020-04-14', '01234', 1.5, 2.5, 3.5, 4, 5.5)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'name': 'sensor',
      'geo_type': 'county',
      'dates': 20200414,
      'geo_id': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'date': '2020-04-14',
        'geo_id': '01234',
        'value': 1.5,
        'stderr': 2.5,
        'sample_size': 3.5,
        'direction': 4,
        'prob': 5.5,
       }],
      'message': 'success',
    })

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'sensor', 'county', '2020-04-14', '11111', 10, 11, 12, 13, 14),
        (0, 'sensor', 'county', '2020-04-14', '22222', 20, 21, 22, 23, 24),
        (0, 'sensor', 'county', '2020-04-14', '33333', 30, 31, 32, 33, 34),
        (0, 'sensor', 'msa', '2020-04-14', '11111', 40, 41, 42, 43, 44),
        (0, 'sensor', 'msa', '2020-04-14', '22222', 50, 51, 52, 53, 54),
        (0, 'sensor', 'msa', '2020-04-14', '33333', 60, 61, 62, 63, 64)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'name': 'sensor',
      'geo_type': 'county',
      'dates': 20200414,
      'geo_id': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'date': '2020-04-14',
          'geo_id': '11111',
          'value': 10,
          'stderr': 11,
          'sample_size': 12,
          'direction': 13,
          'prob': 14,
        }, {
          'date': '2020-04-14',
          'geo_id': '22222',
          'value': 20,
          'stderr': 21,
          'sample_size': 22,
          'direction': 23,
          'prob': 24,
        }, {
          'date': '2020-04-14',
          'geo_id': '33333',
          'value': 30,
          'stderr': 31,
          'sample_size': 32,
          'direction': 33,
          'prob': 34,
        },
       ],
      'message': 'success',
    })

  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'sensor', 'county', '2020-04-11', '01234', 10, 11, 12, 13, 14),
        (0, 'sensor', 'county', '2020-04-12', '01234', 20, 21, 22, 23, 24),
        (0, 'sensor', 'county', '2020-04-13', '01234', 30, 31, 32, 33, 34),
        (0, 'sensor', 'county', '2020-04-11', '11111', 40, 41, 42, 43, 44),
        (0, 'sensor', 'county', '2020-04-12', '22222', 50, 51, 52, 53, 54),
        (0, 'sensor', 'county', '2020-04-13', '33333', 60, 61, 62, 63, 64)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'name': 'sensor',
      'geo_type': 'county',
      'dates': '20200411-20200413',
      'geo_id': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'date': '2020-04-11',
          'geo_id': '01234',
          'value': 10,
          'stderr': 11,
          'sample_size': 12,
          'direction': 13,
          'prob': 14,
        }, {
          'date': '2020-04-12',
          'geo_id': '01234',
          'value': 20,
          'stderr': 21,
          'sample_size': 22,
          'direction': 23,
          'prob': 24,
        }, {
          'date': '2020-04-13',
          'geo_id': '01234',
          'value': 30,
          'stderr': 31,
          'sample_size': 32,
          'direction': 33,
          'prob': 34,
        },
       ],
      'message': 'success',
    })

  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'sensor', 'county', '2020-04-14', '01234', 0, 0, 0, 0, 0)
    ''')
    self.cnx.commit()

    # fail to insert different dummy data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
      self.cur.execute('''
        insert into covidcast values
          (0, 'sensor', 'county', '2020-04-14', '01234', 1, 1, 1, 1, 1)
      ''')

  def test_nullable_columns(self):
    """Missing values should be surfaced as null."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'sensor', 'county', '2020-04-14', '01234', 0.123,
          NULL, NULL, NULL, NULL)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'name': 'sensor',
      'geo_type': 'county',
      'dates': 20200414,
      'geo_id': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'date': '2020-04-14',
        'geo_id': '01234',
        'value': 0.123,
        'stderr': None,
        'sample_size': None,
        'direction': None,
        'prob': None,
       }],
      'message': 'success',
    })
