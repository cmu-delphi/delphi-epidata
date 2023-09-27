"""Integration tests for covidcast's batch deletions."""

# standard library
from collections import namedtuple
import unittest
from os import path

# first party
from delphi.epidata.common.covidcast_test_base import covidcast_rows_from_args, CovidcastTestBase

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.database'

Example = namedtuple("example", "given expected")

class DeleteBatch(CovidcastTestBase):
    """Tests batch deletions"""

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
        rows = covidcast_rows_from_args(
            time_value = [0] * 5 + [1] * 5 + [0],
            geo_value = ["d_nonlatest"] * 2 + ["d_latest"] * 3 + ["d_nonlatest"] * 2 + ["d_latest"] * 3 + ["d_justone"],
            issue = [1, 2] + [1, 2, 3] + [1, 2] + [1, 2, 3] + [1],
            sanitize_fields = True
        )

        self._db.insert_or_update_bulk(rows)

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
                f'select geo_value, issue from {self._db.latest_view} where time_value=0 order by geo_value',
                [('d_latest', 2),
                 ('d_nonlatest', 2)]
            )
        ]

        for ex in examples:
            cur.execute(ex.given)
            result = list(cur)
            self.assertEqual(result, ex.expected, ex.given)
