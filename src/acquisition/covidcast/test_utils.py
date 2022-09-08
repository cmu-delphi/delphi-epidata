from typing import Sequence
import unittest

from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.database import Database
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
        for table in "epimetric_load  epimetric_latest  epimetric_full  geo_dim  signal_dim".split():
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

    def _insert_rows(self, rows: Sequence[CovidcastRow]):
        # inserts rows into the database using the full acquisition process, including 'dbjobs' load into history & latest tables
        n = self._db.insert_or_update_bulk(rows)
        print(f"{n} rows added to load table & dispatched to v4 schema")
        self._db._connection.commit() # NOTE: this isnt expressly needed for our test cases, but would be if using external access (like through client lib) to ensure changes are visible outside of this db session

    def params_from_row(self, row: CovidcastRow, **kwargs):
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
