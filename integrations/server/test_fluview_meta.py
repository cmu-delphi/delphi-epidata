"""Integration tests for the `fluview_meta` endpoint."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata


class FluviewMetaTests(unittest.TestCase):
  """Tests the `fluview_meta` endpoint."""

  @classmethod
  def setUpClass(cls):
    """Perform one-time setup."""

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
    Epidata.auth = ('epidata', 'key')

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `fluview` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table fluview')
    cur.execute("truncate table api_user")
    cur.execute('insert into api_user(api_key, email, roles) values("key", "test@test.com", "")')
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
      INSERT INTO 
        `fluview` (`id`, `release_date`, `issue`, `epiweek`, `region`, 
        `lag`, `num_ili`, `num_patients`, `num_providers`, `wili`, `ili`, 
        `num_age_0`, `num_age_1`, `num_age_2`, `num_age_3`, `num_age_4`, `num_age_5`)
      VALUES
        (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421,
          10, 11, 12, 13, 14, 15),
        (0, "2020-04-28", 202022, 202022, "hhs1", 5, 6, 7, 8, 1.11111, 2.22222,
          20, 21, 22, 23, 24, 25)
    ''')
    self.cnx.commit()

    # make the request
    response = Epidata.fluview_meta()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
         'latest_update': '2020-04-28',
         'latest_issue': 202022,
         'table_rows': 2,
       }],
      'message': 'success',
    })
