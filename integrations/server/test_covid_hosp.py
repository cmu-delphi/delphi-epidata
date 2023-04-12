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
        cur.execute('truncate table covid_hosp_state_daily')
        cur.execute('truncate table covid_hosp_state_timeseries')
        cur.execute('truncate table covid_hosp_meta')


  def insert_timeseries(self, cur, issue, value):
    so_many_nulls = ', '.join(['null'] * 114)
    cur.execute(f'''insert into covid_hosp_state_timeseries values (
      0, {issue}, 'PA', 20201118, {value}, {so_many_nulls}
    )''')

  def insert_daily(self, cur, issue, value):
    so_many_nulls = ', '.join(['null'] * 114)
    cur.execute(f'''insert into covid_hosp_state_daily values (
      0, {issue}, 'PA', 20201118, {value}, {so_many_nulls}
    )''')

  def test_query_by_issue(self):
    """Query with and without specifying an issue."""

    with Database.connect() as db:
      with db.new_cursor() as cur:
        # inserting out of order to test server-side order by
        # also inserting two for 20201201 to test tiebreaker.
        self.insert_timeseries(cur, 20201201, 123)
        self.insert_daily(cur, 20201201, 321)
        self.insert_timeseries(cur, 20201203, 789)
        self.insert_timeseries(cur, 20201202, 456)

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
      self.assertEqual(response['epidata'][0]['critical_staffing_shortage_today_yes'], 321)

    # request for multiple issues
    with self.subTest(name='specific multiple issues'):
      issues = Epidata.range(20201201, 20201231)
      response = Epidata.covid_hosp('PA', 20201118, issues=issues)

      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 3)
      rows = response['epidata']
      # tiebreaker
      self.assertEqual(rows[0]['issue'], 20201201)
      self.assertEqual(rows[0]['critical_staffing_shortage_today_yes'], 321)
      # server-side order by
      self.assertEqual(rows[1]['issue'], 20201202)
      self.assertEqual(rows[1]['critical_staffing_shortage_today_yes'], 456)
      self.assertEqual(rows[2]['issue'], 20201203)
      self.assertEqual(rows[2]['critical_staffing_shortage_today_yes'], 789)


  def test_query_by_as_of(self):
    with Database.connect() as db:
      with db.new_cursor() as cur:
        self.insert_timeseries(cur, 20201101, 0)
        self.insert_daily(cur, 20201102, 1)
        self.insert_daily(cur, 20201103, 2)
        self.insert_timeseries(cur, 20201103, 3)
        self.insert_timeseries(cur, 20201104, 4)

    with self.subTest(name='as_of with multiple issues'):
      response = Epidata.covid_hosp('PA', 20201118, as_of=20201103)
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
      self.assertEqual(response['epidata'][0]['issue'], 20201103)
      self.assertEqual(response['epidata'][0]['critical_staffing_shortage_today_yes'], 2)
