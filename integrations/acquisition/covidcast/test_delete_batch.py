"""Integration tests for covidcast's batch deletions."""

# standard library
from collections import namedtuple
import unittest
from os import path

# first party
import delphi.operations.secrets as secrets

from ....src.acquisition.covidcast.database import Database, CovidcastRow

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.database'

Example = namedtuple("example", "given expected")

class DeleteBatch(unittest.TestCase):
    """Tests batch deletions"""


    def setUp(self):
        """Perform per-test setup."""

        # use the local instance of the epidata database
        secrets.db.host = 'delphi_database_epidata'
        secrets.db.epi = ('user', 'pass')

        # will use secrets as set above
        self._db = Database()
        self._db.connect()

        for table in "signal_load  signal_latest  signal_history  geo_dim  signal_dim".split():
            self._db._cursor.execute(f"TRUNCATE TABLE {table}")


    def tearDown(self):
        """Perform per-test teardown."""
        self._db.disconnect(False)
        del self._db

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
        rows = []
        for time_value in [0, 1]:
            rows += [
                # varying numeric column here (2nd to last) is `issue`
                CovidcastRow('src', 'sig', 'day', 'geo', time_value, "d_nonlatest", 0,0,0,0,0,0, 1, 0),
                CovidcastRow('src', 'sig', 'day', 'geo', time_value, "d_nonlatest", 0,0,0,0,0,0, 2, 0),
                CovidcastRow('src', 'sig', 'day', 'geo', time_value, "d_latest", 0,0,0,0,0,0, 1, 0),
                CovidcastRow('src', 'sig', 'day', 'geo', time_value, "d_latest", 0,0,0,0,0,0, 2, 0),
                CovidcastRow('src', 'sig', 'day', 'geo', time_value, "d_latest",  0,0,0,0,0,0, 3, 0)
            ]
        rows.append(CovidcastRow('src', 'sig', 'day', 'geo', 0, "d_justone",  0,0,0,0,0,0, 1, 0))
        self._db.insert_or_update_bulk(rows)
        self._db.run_dbjobs()

        # delete entries
        self._db.delete_batch(cc_deletions)

        cur = self._db._cursor

        # verify remaining data is still there
        cur.execute(f"select * from {self._db.history_view}")
        result = list(cur)
        self.assertEqual(len(result), len(rows)-3)

        examples = [
            # verify deletions are gone
            Example(
                f'select * from {self._db.history_view} where time_value=0 and geo_value="d_nonlatest" and issue=1',
                []
            ),
            Example(
                f'select * from {self._db.history_view} where time_value=0 and geo_value="d_latest" and issue=3',
                []
            ),
            Example(
                f'select * from {self._db.history_view} where geo_value="d_justone"',
                []
            ),
            # verify latest issue was corrected
            Example(
                f'select geo_value, issue from {self._db.latest_view} where time_value=0',
                [('d_nonlatest', 2),
                 ('d_latest', 2)]
            )
        ]

        for ex in examples:
            cur.execute(ex.given)
            result = list(cur)
            self.assertEqual(result, ex.expected, ex.given)
