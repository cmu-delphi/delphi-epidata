"""Integration tests for the `covid_hosp` endpoint."""

# standard library
import unittest

# first party
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets


class ServerTests(unittest.TestCase):
  """Tests the `covid_hosp` endpoint."""

  def setUp(self):
    """Perform per-test setup."""

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # clear relevant tables
    with Database.connect() as db:
      with db.new_cursor() as cur:
        cur.execute('truncate table covid_hosp_state_timeseries')
        cur.execute('truncate table covid_hosp_meta')

  def test_query_by_issue(self):
    """Query with and without specifying an issue."""

    # insert dummy data
    def insert_issue(cur, issue, value):
      so_many_nulls = ', '.join(['null'] * 57)
      cur.execute(f'''insert into covid_hosp_state_timeseries values (
        0, {issue}, 'PA', 20201118, {value}, {so_many_nulls}, 'T'
      )''')
    with Database.connect() as db:
      with db.new_cursor() as cur:
        # inserting out of order to test server-side order by
        insert_issue(cur, 20201201, 123)
        insert_issue(cur, 20201203, 789)
        insert_issue(cur, 20201202, 456)

    # request without issue (defaulting to latest issue)
    with self.subTest(name='no issue (latest)'):
      response = Epidata.covid_hosp('PA', 20201118)

      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
      self.assertEqual(response['epidata'][0]['issue'], 20201203)
      self.assertEqual(response['epidata'][0]['critical_staffing_shortage_today_yes'], 789)

    # request for specific issue
    with self.subTest(name='specific single issue'):
      response = Epidata.covid_hosp('PA', 20201118, issues=20201201)

      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
      self.assertEqual(response['epidata'][0]['issue'], 20201201)
      self.assertEqual(response['epidata'][0]['critical_staffing_shortage_today_yes'], 123)

    # request for multiple issues
    with self.subTest(name='specific multiple issues'):
      issues = Epidata.range(20201201, 20201231)
      response = Epidata.covid_hosp('PA', 20201118, issues=issues)

      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 3)
      rows = response['epidata']
      self.assertEqual(rows[0]['issue'], 20201201)
      self.assertEqual(rows[0]['critical_staffing_shortage_today_yes'], 123)
      self.assertEqual(rows[1]['issue'], 20201202)
      self.assertEqual(rows[1]['critical_staffing_shortage_today_yes'], 456)
      self.assertEqual(rows[2]['issue'], 20201203)
      self.assertEqual(rows[2]['critical_staffing_shortage_today_yes'], 789)
