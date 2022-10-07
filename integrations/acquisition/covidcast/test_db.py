from delphi_utils import Nans

from delphi.epidata.acquisition.covidcast.database import DBLoadStateException
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase


# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value

class TestTest(CovidcastBase):

    def _find_matches_for_row(self, row):
        # finds (if existing) row from both history and latest views that matches long-key of provided CovidcastRow
        cols = "source signal time_type time_value geo_type geo_value issue".split()
        results = {}
        cur = self._db._cursor
        for table in ['epimetric_latest_v', 'epimetric_full_v']:
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

    def test_insert_or_update_with_nonempty_load_table(self):
        # make rows
        a_row = CovidcastRow.make_default_row(time_value=20200202)
        another_row = CovidcastRow.make_default_row(time_value=20200203, issue=20200203)
        # insert one
        self._db.insert_or_update_bulk([a_row])
        # put something into the load table
        self._db._cursor.execute(f'''
            INSERT INTO {self._db.load_table}
            (source, `signal`, geo_type, geo_value, time_type, time_value, issue, `lag`, value_updated_timestamp)
            VALUES
            ('sr',   'si',     'gt',     'gv',      'tt',      3,          8,     5,     13)''')
        # ensure inserting the other row fails
        with self.assertRaises(DBLoadStateException):
            self._db.insert_or_update_bulk([another_row])
        # make sure the one row is still in there but the other is not
        nones = [None] * 2
        present_values = list(self._find_matches_for_row(a_row).values())
        self.assertNotEqual(present_values, nones)
        absent_values = list(self._find_matches_for_row(another_row).values())
        self.assertEqual(absent_values, nones)

    def test_id_sync(self):
        # the history and latest tables have a non-AUTOINCREMENT primary key id that is fed by the
        # AUTOINCREMENT pk id from the load table.  this test is intended to make sure that they
        # appropriately stay in sync with each other

        pk_column = 'epimetric_id'
        histor_view = 'epimetric_full_v'
        latest_view = 'epimetric_latest_v'

        # add a data point
        base_row = CovidcastRow.make_default_row()
        self._insert_rows([base_row])
        # ensure the primary keys match in the latest and history tables
        matches = self._find_matches_for_row(base_row)
        self.assertEqual(matches[latest_view][pk_column],
                         matches[histor_view][pk_column])
        # save old pk value
        old_pk_id = matches[latest_view][pk_column]

        # add a reissue for said data point
        next_row = CovidcastRow.make_default_row()
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
