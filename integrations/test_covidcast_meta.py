"""Integration tests for the `covidcast_meta` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidcastMetaTests(unittest.TestCase):
  """Tests the `covidcast_meta` endpoint."""

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
        (0, 'sensor1', 'msa', '2020-04-01', 'a', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'msa', '2020-04-01', 'b', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'msa', '2020-04-02', 'c', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'msa', '2020-04-02', 'd', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-01', 'd', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-03', 'e', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-03', 'd', 0, 0, 0, 0, 0),
        (0, 'sensor1', 'hrr', '2020-04-02', 'e', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-01', 'a', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-01', 'b', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-02', 'c', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'msa', '2020-04-04', 'd', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-11', 'e', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-12', 'e', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-13', 'e', 0, 0, 0, 0, 0),
        (0, 'sensor2', 'hrr', '2020-04-14', 'e', 0, 0, 0, 0, 0)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={'source': 'covidcast_meta'})
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
