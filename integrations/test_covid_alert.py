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
        (0, 'sensor', 'county', '2020-04-14', '01234', 1.5, 2.5, -1, 3.5)
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
        'direction': -1,
        'sample_size': 3.5,
       }],
      'message': 'success',
    })

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-14', '11111', 10, 11, -1, 12),
        (0, 'sensor', 'county', '2020-04-14', '22222', 20, 21, 0, 22),
        (0, 'sensor', 'county', '2020-04-14', '33333', 30, 31, 1, NULL),
        (0, 'sensor', 'msa', '2020-04-14', '11111', 40, 41, -1, 42),
        (0, 'sensor', 'msa', '2020-04-14', '22222', 50, 51, 0, 52),
        (0, 'sensor', 'msa', '2020-04-14', '33333', 60, 61, 1, NULL)
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
          'direction': -1,
          'sample_size': 12,
        }, {
          'date': '2020-04-14',
          'geo_id': '22222',
          'raw': 20,
          'scaled': 21,
          'direction': 0,
          'sample_size': 22,
        }, {
          'date': '2020-04-14',
          'geo_id': '33333',
          'raw': 30,
          'scaled': 31,
          'direction': 1,
          'sample_size': None,
        },
       ],
      'message': 'success',
    })

  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-11', '01234', 10, 11, -1, 12),
        (0, 'sensor', 'county', '2020-04-12', '01234', 20, 21, 0, 22),
        (0, 'sensor', 'county', '2020-04-13', '01234', 30, 31, 1, NULL),
        (0, 'sensor', 'county', '2020-04-11', '11111', 40, 41, -1, 42),
        (0, 'sensor', 'county', '2020-04-12', '22222', 50, 51, 0, 52),
        (0, 'sensor', 'county', '2020-04-13', '33333', 60, 61, 1, NULL)
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
          'direction': -1,
          'sample_size': 12,
        }, {
          'date': '2020-04-12',
          'geo_id': '01234',
          'raw': 20,
          'scaled': 21,
          'direction': 0,
          'sample_size': 22,
        }, {
          'date': '2020-04-13',
          'geo_id': '01234',
          'raw': 30,
          'scaled': 31,
          'direction': 1,
          'sample_size': None,
        },
       ],
      'message': 'success',
    })

  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor', 'county', '2020-04-14', '01234', 0, 0, 0, 0)
    ''')
    self.cnx.commit()

    # fail to insert different dummy data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
      self.cur.execute('''
        insert into covid_alert values
          (0, 'sensor', 'county', '2020-04-14', '01234', 1, 1, 1, 1)
      ''')

  def test_metadata(self):
    """Fetch metadata over sensors, locations, and dates."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_alert values
        (0, 'sensor1', 'msa', '2020-04-01', 'a', 0, 0, 0, 0),
        (0, 'sensor1', 'msa', '2020-04-01', 'b', 0, 0, 0, 0),
        (0, 'sensor1', 'msa', '2020-04-02', 'c', 0, 0, 0, 0),
        (0, 'sensor1', 'msa', '2020-04-02', 'd', 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-01', 'd', 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-03', 'e', 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-03', 'd', 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-02', 'e', 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-01', 'a', 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-01', 'b', 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-02', 'c', 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-04', 'd', 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-11', 'e', 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-12', 'e', 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-13', 'e', 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-14', 'e', 0, 0, 0, 0)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={'source': 'covid_alert_meta'})
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'name': 'sensor1',
          'geo_type': 'hrr',
          'min_date': '2020-04-01',
          'max_date': '2020-04-03',
          'num_locations': 2,
        }, {
          'name': 'sensor1',
          'geo_type': 'msa',
          'min_date': '2020-04-01',
          'max_date': '2020-04-02',
          'num_locations': 4,
        }, {
          'name': 'sensor2',
          'geo_type': 'hrr',
          'min_date': '2020-04-11',
          'max_date': '2020-04-14',
          'num_locations': 1,
        }, {
          'name': 'sensor2',
          'geo_type': 'msa',
          'min_date': '2020-04-01',
          'max_date': '2020-04-04',
          'num_locations': 4,
        },
       ],
      'message': 'success',
    })
