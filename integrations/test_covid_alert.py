"""Integration tests for the `covid_alert` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidAlertTests(unittest.TestCase):
  """Tests the `covid_alert` endpoint."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covid_alert` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covid_alert')
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
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-14', '01234',
          1.5, 2.5, 3, 4.5, 5.5, 6.5)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covid_alert',
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
        'raw': 1.5,
        'scaled': 2.5,
        'direction': 3,
        'sample_size': 4.5,
        'p_up': 5.5,
        'p_down': 6.5,
       }],
      'message': 'success',
    })

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-14', '11111',
          10, 11, 12, 13, 14, 15),
        (0, 'sensor', 'county', '2020-04-14', '22222',
          20, 21, 22, 23, 24, 25),
        (0, 'sensor', 'county', '2020-04-14', '33333',
          30, 31, 32, 33, 34, 35),
        (0, 'sensor', 'msa', '2020-04-14', '11111',
          40, 41, 42, 43, 44, 45),
        (0, 'sensor', 'msa', '2020-04-14', '22222',
          50, 51, 52, 53, 54, 55),
        (0, 'sensor', 'msa', '2020-04-14', '33333',
          60, 61, 62, 63, 64, 65)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covid_alert',
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
          'raw': 10,
          'scaled': 11,
          'direction': 12,
          'sample_size': 13,
          'p_up': 14,
          'p_down': 15,
        }, {
          'date': '2020-04-14',
          'geo_id': '22222',
          'raw': 20,
          'scaled': 21,
          'direction': 22,
          'sample_size': 23,
          'p_up': 24,
          'p_down': 25,
        }, {
          'date': '2020-04-14',
          'geo_id': '33333',
          'raw': 30,
          'scaled': 31,
          'direction': 32,
          'sample_size': 33,
          'p_up': 34,
          'p_down': 35,
        },
       ],
      'message': 'success',
    })

  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-11', '01234',
          10, 11, 12, 13, 14, 15),
        (0, 'sensor', 'county', '2020-04-12', '01234',
          20, 21, 22, 23, 24, 25),
        (0, 'sensor', 'county', '2020-04-13', '01234',
          30, 31, 32, 33, 34, 35),
        (0, 'sensor', 'county', '2020-04-11', '11111',
          40, 41, 42, 43, 44, 45),
        (0, 'sensor', 'county', '2020-04-12', '22222',
          50, 51, 52, 53, 54, 55),
        (0, 'sensor', 'county', '2020-04-13', '33333',
          60, 61, 62, 63, 64, 65)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covid_alert',
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
          'raw': 10,
          'scaled': 11,
          'direction': 12,
          'sample_size': 13,
          'p_up': 14,
          'p_down': 15,
        }, {
          'date': '2020-04-12',
          'geo_id': '01234',
          'raw': 20,
          'scaled': 21,
          'direction': 22,
          'sample_size': 23,
          'p_up': 24,
          'p_down': 25,
        }, {
          'date': '2020-04-13',
          'geo_id': '01234',
          'raw': 30,
          'scaled': 31,
          'direction': 32,
          'sample_size': 33,
          'p_up': 34,
          'p_down': 35,
        },
       ],
      'message': 'success',
    })

  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-14', '01234', 0, 0, 0, 0, 0, 0)
    ''')
    self.cnx.commit()

    # fail to insert different dummy data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
      self.cur.execute('''
        insert into covid_alert values
          (0, 'sensor', 'county', '2020-04-14', '01234', 1, 1, 1, 1, 1, 1)
      ''')

  def test_nullable_columns(self):
    """Missing values should be surfaced as null."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-14', '01234',
          NULL, NULL, NULL, NULL, NULL, NULL)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covid_alert',
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
        'raw': None,
        'scaled': None,
        'direction': None,
        'sample_size': None,
        'p_up': None,
        'p_down': None,
       }],
      'message': 'success',
    })
