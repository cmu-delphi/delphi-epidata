"""Integration tests for covidcast's batch deletions."""

# standard library
from collections import namedtuple
import unittest
from unittest.mock import patch
from os import path

# third party
import mysql.connector

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.database'

Example = namedtuple("example", "given expected")

def _request(params):
  """Request and parse epidata.

  We default to GET since it has better caching and logging
  capabilities, but fall back to POST if the request is too
  long and returns a 414.
  """
  params.update({'meta_key': 'meta_secret'})
  try:
    return Epidata._request_with_retry(params).json()
  except Exception as e:
    return {'result': 0, 'message': 'error: ' + str(e)}


@patch.object(Epidata, '_request', _request)
class DeleteBatch(unittest.TestCase):
    """Tests batch deletions"""


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

        # use the local instance of the epidata database
        secrets.db.host = 'delphi_database_epidata'
        secrets.db.epi = ('user', 'pass')

        # use the local instance of the Epidata API
        Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

        # will use secrets as set above
        from delphi.epidata.acquisition.covidcast.database import Database
        self.database = Database()
        self.database.connect()

    def tearDown(self):
        """Perform per-test teardown."""
        self.cur.close()
        self.cnx.close()

    @unittest.skip("Database user would require FILE privileges")
    def test_delete_from_file(self):
        self._test_delete_batch(path.join(path.dirname(__file__), "delete_batch.csv"))

    def test_delete_from_tuples(self):
        with open(path.join(path.dirname(__file__), "delete_batch.csv")) as f:
            rows=[]
            for line in f:
                rows.append(line.strip().split(","))
        rows = [r + ["day"] for r in rows[1:]]
        self._test_delete_batch(rows)

    def _test_delete_batch(self, cc_deletions):
        # load sample data
        rows = [
            # geo_value issue is_latest
            ["d_nonlatest", 1, 0],
            ["d_nonlatest", 2, 1],
            ["d_latest", 1, 0],
            ["d_latest", 2, 0],
            ["d_latest", 3, 1]
        ]
        for time_value in [0, 1]:
            self.cur.executemany(f'''
            INSERT INTO covidcast
            (`geo_value`, `issue`, `is_latest_issue`, `time_value`,
            `source`, `signal`, `time_type`, `geo_type`,
            value_updated_timestamp, direction_updated_timestamp, value, stderr, sample_size, lag, direction)
            VALUES
            (%s, %s, %s, {time_value},
            "src", "sig", "day", "geo",
            0, 0, 0, 0, 0, 0, 0)
            ''', rows)
        self.cnx.commit()

        # delete entries
        self.database.delete_batch(cc_deletions)

        # verify remaining data is still there
        self.cur.execute("select * from covidcast")
        result = list(self.cur)
        self.assertEqual(len(result), 2*len(rows)-2)

        examples = [
            # verify deletions are gone
            Example(
                'select * from covidcast where time_value=0 and geo_value="d_nonlatest" and issue=1',
                []
            ),
            Example(
                'select * from covidcast where time_value=0 and geo_value="d_latest" and issue=3',
                []
            ),
            # verify is_latest_issue flag was corrected
            Example(
                'select geo_value, issue from covidcast where time_value=0 and is_latest_issue=1',
                [('d_nonlatest', 2),
                 ('d_latest', 2)]
            )
        ]

        for ex in examples:
            self.cur.execute(ex.given)
            result = list(self.cur)
            self.assertEqual(result, ex.expected, ex.given)
