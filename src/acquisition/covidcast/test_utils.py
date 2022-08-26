import unittest

from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
import delphi.operations.secrets as secrets

# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value

class CovidcastBase(unittest.TestCase):
    def setUp(self):
        # use the local test instance of the database
        secrets.db.host = 'delphi_database_epidata'
        secrets.db.epi = ('user', 'pass')

        self._db = Database()
        self._db.connect()

        # empty all of the data tables
        for table in "signal_load  signal_latest  signal_history  geo_dim  signal_dim".split():
            self._db._cursor.execute(f"TRUNCATE TABLE {table};")
        self.localSetUp()
        self._db._connection.commit()

    def localSetUp(self):
        # stub; override in subclasses to perform custom setup. 
        # runs after tables have been truncated but before database changes have been committed
        pass

    def tearDown(self):
        # close and destroy conenction to the database
        self._db.disconnect(False)
        del self._db

    DEFAULT_TIME_VALUE=2000_01_01
    DEFAULT_ISSUE=2000_01_01
    def _make_placeholder_row(self, **kwargs):
        settings = {
            'source': 'src',
            'signal': 'sig',
            'geo_type': 'state',
            'geo_value': 'pa',
            'time_type': 'day',
            'time_value': self.DEFAULT_TIME_VALUE,
            'value': 0.0,
            'stderr': 1.0,
            'sample_size': 2.0,
            'missing_value': nmv,
            'missing_stderr': nmv,
            'missing_sample_size': nmv,
            'issue': self.DEFAULT_ISSUE,
            'lag': 0
        }
        settings.update(kwargs)
        return (CovidcastRow(**settings), settings)

    def _insert_rows(self, rows):
        # inserts rows into the database using the full acquisition process, including 'dbjobs' load into history & latest tables
        n = self._db.insert_or_update_bulk(rows)
        print(f"{n} rows added to load table & dispatched to v4 schema")
        self._db._connection.commit() # NOTE: this isnt expressly needed for our test cases, but would be if using external access (like through client lib) to ensure changes are visible outside of this db session

    def params_from_row(self, row, **kwargs):
        ret = {
            'data_source': row.source,
            'signals': row.signal,
            'time_type': row.time_type,
            'geo_type': row.geo_type,
            'time_values': row.time_value,
            'geo_value': row.geo_value,
        }
        ret.update(kwargs)
        return ret

    DEFAULT_MINUS=['time_type', 'geo_type', 'source']
    def expected_from_row(self, row, minus=DEFAULT_MINUS):
        expected = dict(vars(row))
        # remove columns commonly excluded from output
        # nb may need to add source or *_type back in for multiplexed queries
        for key in ['id', 'direction_updated_timestamp'] + minus:
            del expected[key]
        return expected

