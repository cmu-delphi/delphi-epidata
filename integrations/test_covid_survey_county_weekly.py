"""Integration tests for the `covid_survey_county_weekly` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidSurveyCountyWeeklyTests(unittest.TestCase):
  """Tests the `covid_survey_county_weekly` endpoint."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the
    # `covid_survey_county_weekly` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covid_survey_county_weekly')
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
      insert into covid_survey_county_weekly values
        (0, 202014, '42003', 1.5, 2.5, 3.5, 4.5, 5678.5)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covid_survey_county_weekly',
      'counties': '42003',
      'epiweeks': 202014,
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'epiweek': 202014,
        'county': '42003',
        'ili': 1.5,
        'ili_stdev': 2.5,
        'cli': 3.5,
        'cli_stdev': 4.5,
        'denominator': 5678.5,
       }],
      'message': 'success',
    })

  def test_county_range(self):
    """Select multiple counties using range of FIPS 6-4 codes (strings)."""

    # insert dummy data
    self.cur.execute('''
      insert into covid_survey_county_weekly values
        (0, 202014, '00100', 100, 101, 102, 103, 10104),
        (0, 202014, '00200', 200, 201, 202, 203, 10204),
        (0, 202014, '00300', 300, 301, 302, 303, 10304),
        (0, 202014, '00400', 400, 401, 402, 403, 10404)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covid_survey_county_weekly',
      'counties': '00111-00333',
      'epiweeks': 202014,
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'epiweek': 202014,
          'county': '00200',
          'ili': 200,
          'ili_stdev': 201,
          'cli': 202,
          'cli_stdev': 203,
          'denominator': 10204,
        }, {
          'epiweek': 202014,
          'county': '00300',
          'ili': 300,
          'ili_stdev': 301,
          'cli': 302,
          'cli_stdev': 303,
          'denominator': 10304,
        },
      ],
      'message': 'success',
    })

  def test_privacy_filtering(self):
    """Don't return rows with too small of a denominator."""

    # shared constants
    request_params = {
      'source': 'covid_survey_county_weekly',
      'counties': '42003',
      'epiweeks': 202014,
    }

    with self.subTest(name='filtered'):

      # insert dummy data
      self.cur.execute('''
        insert into covid_survey_county_weekly values
          (0, 202014, '42003', 1.5, 2.5, 3.5, 4.5, 99.5)
      ''')
      self.cnx.commit()

      # make the request
      response = requests.get(BASE_URL, params=request_params)
      response.raise_for_status()
      response = response.json()

      # assert that no data came back
      self.assertEqual(response, {
        'result': -2,
        'message': 'no results',
      })

    with self.subTest(name='unfiltered'):

      # amend the denominator
      self.cur.execute('''
        update covid_survey_county_weekly set denominator = 100.5
      ''')
      self.cnx.commit()

      # make the request
      response = requests.get(BASE_URL, params=request_params)
      response.raise_for_status()
      response = response.json()

      # assert that the right data came back
      self.assertEqual(response, {
        'result': 1,
        'epidata': [{
          'epiweek': 202014,
          'county': '42003',
          'ili': 1.5,
          'ili_stdev': 2.5,
          'cli': 3.5,
          'cli_stdev': 4.5,
          'denominator': 100.5,
         }],
        'message': 'success',
      })
