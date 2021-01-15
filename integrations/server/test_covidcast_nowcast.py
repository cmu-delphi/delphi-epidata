"""Integration tests for the `covidcast_nowcast` endpoint."""

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
    cur.execute('truncate table covidcast_nowcast')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_query(self):
    """Query nowcasts using default and specified issue."""

    self.cur.execute(
      f'''insert into covidcast_nowcast values 
      (0, 'src', 'sig', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 3.5, 20200101, 2),
      (0, 'src', 'sig', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 2.5, 20200102, 2),
      (0, 'src', 'sig', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 1.5, 20200103, 2)''')

    self.cnx.commit()
    # make the request with specified issue date
    response = requests.get(BASE_URL, params={
      'source': 'covidcast_nowcast',
      'data_source': 'src',
      'signals': 'sig',
      'sensor_names': 'sensor',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200101,
      'geo_value': '01001',
      'issues': 20200101
    })
    response.raise_for_status()
    response = response.json()
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'signal': 'sig',
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 3.5,
        'issue': 20200101,
        'lag': 2,
       }],
      'message': 'success',
    })

    # make request without specific issue date
    response = requests.get(BASE_URL, params={
      'source': 'covidcast_nowcast',
      'data_source': 'src',
      'signals': 'sig',
      'sensor_names': 'sensor',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200101,
      'geo_value': '01001',
    })
    response.raise_for_status()
    response = response.json()

    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'signal': 'sig',
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 1.5,
        'issue': 20200103,
        'lag': 2,
       }],
      'message': 'success',
    })

    response = requests.get(BASE_URL, params={
      'source': 'covidcast_nowcast',
      'data_source': 'src',
      'signals': 'sig',
      'sensor_names': 'sensor',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200101,
      'geo_value': '01001',
      'as_of': 20200101
    })
    response.raise_for_status()
    response = response.json()

    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'signal': 'sig',
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 3.5,
        'issue': 20200101,
        'lag': 2,
       }],
      'message': 'success',
    })
