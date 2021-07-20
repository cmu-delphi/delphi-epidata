"""Integration tests for covidcast's direction updating."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.fill_is_latest_issue import main
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.fill_is_latest_issue'


class FillIsLatestIssueTests(unittest.TestCase):
  """Tests filling is_latest_issue column"""

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
    cur.execute("truncate table api_user")
    cur.execute('insert into api_user(api_key, email, roles) values("key", "test@test.com", "")')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
    Epidata.auth = ('epidata', 'key')

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def _test_fill_is_latest_issue(self, clbp, use_filter):
    """Update rows having a stale `direction` field and serve the results."""

    # NOTE: column order is:
    # (id, source, signal, time_type, geo_type, time_value, geo_value,
    # value_updated_timestamp, value, stderr, sample_size, direction_updated_timestamp,
    # direction, issue, lag, is_latest_issue, is_wip, missing_value, missing_stderr, missing_sample_size)

    self.cur.execute(f'''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 5, 5, 5, NULL, 20200228, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 0, 0, 0, NULL, 20200229, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 0, 0, 0, NULL, 20200301, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 9, 9, 9, NULL, 20200229, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 0, 0, 0, NULL, 20200303, 2, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 5, 5, 5, NULL, 20200302, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 9, 8, 7, NULL, 20200301, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ny',
          123, 2, 5, 5, 5, NULL, 20200228, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ny',
          123, 2, 0, 0, 0, NULL, 20200229, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ny',
          123, 6, 0, 0, 0, NULL, 20200301, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ny',
          123, 6, 9, 9, 9, NULL, 20200229, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ny',
          123, 5, 0, 0, 0, NULL, 20200303, 2, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ny',
          123, 5, 5, 5, 5, NULL, 20200302, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ny',
          123, 5, 9, 8, 7, NULL, 20200301, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
    ''')
    self.cnx.commit()

    # NOTE: 'ny' values are identical to the 'ca' values, but with the `geo_value` changed

    if use_filter:
      # ignores ny
      fc = "`geo_value` = 'ca'"
    else:
      # wildcard ; does not filter
      fc = "TRUE"

    # fill is_latest_issue
    main(FILTER_CONDITION=fc, CLEAR_LATEST_BY_PARTITION=clbp)

    self.cur.execute('''select * from covidcast''')
    result = list(self.cur)
    expected = [
        (1, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2.0, 5.0, 5.0, 5, None, 20200228, 0, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (2, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2.0, 0.0, 0.0, 0, None, 20200229, 1, bytearray(b'1'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (3, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6.0, 0.0, 0.0, 0, None, 20200301, 1, bytearray(b'1'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (4, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6.0, 9.0, 9.0, 9, None, 20200229, 0, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (5, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5.0, 0.0, 0.0, 0, None, 20200303, 2, bytearray(b'1'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (6, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5.0, 5.0, 5.0, 5, None, 20200302, 1, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (7, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5.0, 9.0, 8.0, 7, None, 20200301, 0, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (8, 'src', 'sig', 'day', 'state', 20200228, 'ny',
          123, 2.0, 5.0, 5.0, 5, None, 20200228, 0, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (9, 'src', 'sig', 'day', 'state', 20200228, 'ny',
          123, 2.0, 0.0, 0.0, 0, None, 20200229, 1, bytearray(b'1'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (10, 'src', 'sig', 'day', 'state', 20200229, 'ny',
          123, 6.0, 0.0, 0.0, 0, None, 20200301, 1, bytearray(b'1'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (11, 'src', 'sig', 'day', 'state', 20200229, 'ny',
          123, 6.0, 9.0, 9.0, 9, None, 20200229, 0, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (12, 'src', 'sig', 'day', 'state', 20200301, 'ny',
          123, 5.0, 0.0, 0.0, 0, None, 20200303, 2, bytearray(b'1'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (13, 'src', 'sig', 'day', 'state', 20200301, 'ny',
          123, 5.0, 5.0, 5.0, 5, None, 20200302, 1, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING),
        (14, 'src', 'sig', 'day', 'state', 20200301, 'ny',
          123, 5.0, 9.0, 8.0, 7, None, 20200301, 0, bytearray(b'0'), bytearray(b'0'),
          Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING)
    ]

    if use_filter:
      # revert ny is_latest values
      for i in range(7, 14):
        x = list(expected[i])
        x[-5] = bytearray(b'1')
        expected[i] = tuple(x)

    self.assertEqual(result, expected)

  def test_fill_is_latest_issue_by_partition(self):
    self._test_fill_is_latest_issue(True, False)

  def test_fill_is_latest_issue_not_by_partition(self):
    self._test_fill_is_latest_issue(False, False)

  def test_fill_is_latest_issue_by_partition_w_filter(self):
    self._test_fill_is_latest_issue(True, True)

  def test_fill_is_latest_issue_not_by_partition_w_filter(self):
    self._test_fill_is_latest_issue(False, True)
