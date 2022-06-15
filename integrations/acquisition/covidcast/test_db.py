import unittest

from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
import delphi.operations.secrets as secrets

# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value

class TestTest(unittest.TestCase):

    def setUp(self):
        # use the local test instance of the database
        secrets.db.host = 'delphi_database_epidata'
        secrets.db.epi = ('user', 'pass')

        self._db = Database()
        self._db.connect()

        # empty all of the data tables
        for table in "signal_load  signal_latest  signal_history  geo_dim  signal_dim".split():
            self._db._cursor.execute(f"TRUNCATE TABLE {table}")

    def tearDown(self):
        # close and destroy conenction to the database
        self._db.disconnect(False)
        del self._db

    def _make_dummy_row(self):
        return CovidcastRow('src', 'sig', 'day', 'state', 2022_02_22, 'pa', 2, 22, 222, nmv,nmv,nmv, 2022_02_22, 0)
        #             cols:                               ^ timeval         v  se  ssz               ^issue      ^lag

    def _insert_rows(self, rows):
        # inserts rows into the database using the full acquisition process, including 'dbjobs' load into history & latest tables
        self._db.insert_or_update_bulk(rows)
        self._db.run_dbjobs()
        ###db._connection.commit()  # NOTE: this isnt needed here, but would be if using external access (like through client lib)

    def _find_matches_for_row(self, row):
        # finds (if existing) row from both history and latest views that matches long-key of provided CovidcastRow
        cols = "source signal time_type time_value geo_type geo_value issue".split()
        results = {}
        cur = self._db._cursor
        for table in ['signal_latest_v', 'signal_history_v']:
            q = f"SELECT * FROM {table} WHERE "
            # NOTE: repr() puts str values in single quotes but simply 'string-ifies' numerics;
            #       getattr() accesses members by string of their name
            q += " AND ".join([f" `{c}` = {repr(getattr(row,c))} " for c in cols])
            q += " LIMIT 1;"
            cur.execute(q)
            res = cur.fetchone()
            if res:
                results[table] = dict(zip(cur.column_names, res))
            else:
                results[table] = None
        return results

    def test_id_sync(self):
        # the history and latest tables have a non-AUTOINCREMENT primary key id that is fed by the
        # AUTOINCREMENT pk id from the load table.  this test is intended to make sure that they
        # appropriately stay in sync with each other

        pk_column = 'signal_data_id'
        histor_view = 'signal_history_v'
        latest_view = 'signal_latest_v'

        # add a data point
        base_row = self._make_dummy_row()
        self._insert_rows([base_row])
        # ensure the primary keys match in the latest and history tables
        matches = self._find_matches_for_row(base_row)
        self.assertEqual(matches[latest_view][pk_column],
                         matches[histor_view][pk_column])
        # save old pk value
        old_pk_id = matches[latest_view][pk_column]

        # add a reissue for said data point
        next_row = self._make_dummy_row()
        next_row.issue += 1
        self._insert_rows([next_row])
        # ensure the new keys also match
        matches = self._find_matches_for_row(next_row)
        self.assertEqual(matches[latest_view][pk_column],
                         matches[histor_view][pk_column])
        # check new ids were used
        new_pk_id = matches[latest_view][pk_column]
        self.assertNotEqual(old_pk_id, new_pk_id)

        # verify old issue is no longer in latest table
        self.assertIsNone(self._find_matches_for_row(base_row)[latest_view])
