"""Integration tests for internal analytics."""

# standard library
import unittest

# third party
import mysql.connector
import requests


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class ApiAnalyticsTests(unittest.TestCase):
  """Tests internal analytics not specific to any particular endpoint."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `api_analytics` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table api_analytics')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_analytics_update(self):
    """Update internal analytics for requests to the API."""

    make_request = lambda src: requests.get(BASE_URL, params={'source': src})

    # make some requests
    for _ in range(1):
      make_request('source1')
    for _ in range(5):
      make_request('source2')
    for _ in range(19):
      make_request('source3')

    # verify that analytics are available
    self.cur.execute('''
      select source, count(1)
      from api_analytics
      group by source
      order by source
    ''')
    values = [row for row in self.cur]
    self.assertEqual(values, [
      ('source1', 1),
      ('source2', 5),
      ('source3', 19),
    ])
