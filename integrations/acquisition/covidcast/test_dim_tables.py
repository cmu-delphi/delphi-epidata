"""Integration tests for covidcast's dimension tables."""
# standard library
import unittest


# third party
import mysql.connector
# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
import delphi.operations.secrets as secrets

__test_target__ = 'delphi.epidata.acquisition.covidcast.database'

nmv = Nans.NOT_MISSING.value
class CovidcastDimensionTablesTests(unittest.TestCase):
    """Tests covidcast's dimension tables."""
    
    def setUp(self):
        """Perform per-test setup."""
        # connect to the `epidata` database
        cnx = mysql.connector.connect(
            user='user',
            password='pass',
            host='delphi_database_epidata',
            database='covid')
        cur = cnx.cursor()

        # clear all tables
        cur.execute("truncate table signal_load")
        cur.execute("truncate table signal_history")
        cur.execute("truncate table signal_latest")
        cur.execute("truncate table geo_dim")
        cur.execute("truncate table signal_dim")
        # reset the `covidcast_meta_cache` table (it should always have one row)
        cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')
        cnx.commit()
        cur.close()

        # make connection and cursor available to the Database object
        self._db = Database()
        self._db._connection = cnx
        self._db._cursor = cnx.cursor()

        # use the local instance of the Epidata API
        Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

        # use the local instance of the epidata database
        secrets.db.host = 'delphi_database_epidata'
        secrets.db.epi = ('user', 'pass')

        #Commonly used SQL commands:
        self.viewSignalLatest = f'SELECT * FROM {Database.latest_table}'
        self.viewSignalHistory = f'SELECT * FROM {Database.history_table}'
        self.viewSignalDim = f'SELECT `source`, `signal` FROM `signal_dim`'
        self.viewGeoDim = f'SELECT `geo_type`,`geo_value` FROM `geo_dim`'

    def tearDown(self):
        """Perform per-test teardown."""
        self._db._cursor.close()
        self._db._connection.close()

    # We want to test src_sig to make sure rows are added to *_dim only when needed
    #new src, sig (ensure that it is added into *_dim)
    #old src, sig (ensure that it is NOT added into *_dim)
    #new geo (added)
    #old geo (not added)
    def test_src_sig(self):
    #BASE CASES
        rows = [
        CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
        2, 2, 2, nmv, nmv, nmv, 20200414, 0),
        CovidcastRow('src', 'sig', 'day', 'county', 20200414, '11111',
        3, 3, 3, nmv, nmv, nmv, 20200414, 0)
        ]
        self._db.insert_or_update_batch(rows)
        self._db.run_dbjobs()
        self._db._cursor.execute(self.viewGeoDim)
        record = self._db._cursor.fetchall()
        self.geoDimRows = len(list(record))

        self._db._cursor.execute(self.viewSignalDim)
        record = self._db._cursor.fetchall()
        self.sigDimRows = len(list(record))

        self._db._cursor.execute(self.viewSignalLatest)
        record = self._db._cursor.fetchall()
        self.sigLatestRows = len(list(record))

        #test not added first
        with self.subTest(name='older src and sig not added into sig_dim'):
            oldSrcSig = [
                CovidcastRow('src', 'sig', 'day', 'state', 20211111, 'pa', #new src, new sig
                            99, 99, 99, nmv, nmv, nmv, 20211111, 1),
                CovidcastRow('src', 'sig', 'day', 'county', 20211111, '11111', #new src, new sig, same geo
                            99, 99, 99, nmv, nmv, nmv, 20211111, 1)
                ]  
            self._db.insert_or_update_batch(oldSrcSig)
            self._db.run_dbjobs()

            #testing src, sig 
            self._db._cursor.execute(self.viewSignalDim)
            record = self._db._cursor.fetchall()
            res = [('src','sig')] #output
            self.assertEqual(res , list(record))

            #ensure new entries are added in latest
            self._db._cursor.execute(self.viewSignalLatest)
            record = self._db._cursor.fetchall()
            self.sigLatestRows = len(list(record))
            self.assertEqual(len(list(record)), self.sigLatestRows) #2 original, 2 added (updated)
            
            #ensure nothing in geo
            self._db._cursor.execute(self.viewGeoDim)
            record = self._db._cursor.fetchall()
            self.assertEqual(len(list(record)),self.geoDimRows)

        with self.subTest(name='newer src and sig added in sig_dim'):
            newSrcSig = [
                CovidcastRow('new_src', 'sig', 'day', 'state', 20200414, 'pa', # new_src
                            2, 2, 2, nmv, nmv, nmv, 20200414, 0),
                CovidcastRow('src', 'new_sig', 'day', 'state', 20200414, 'pa', # new_sig
                            2, 2, 2, nmv, nmv, nmv, 20200414, 0)
            ]  
            self._db.insert_or_update_batch(newSrcSig)
            self._db.run_dbjobs()

            #testing src, sig
            self._db._cursor.execute(self.viewSignalDim)
            record = self._db._cursor.fetchall()
            self.sigDimRows = len(list(record))
            # res = [('src', 'sig'), ('new_src', 'sig'), ('src', 'new_sig')]
            res = [('new_src', 'sig'), ('src', 'new_sig'), ('src', 'sig')] # the sequence of adding changed
            self.assertEqual(res , (record))
            self.assertEqual(3, self.sigDimRows)
            #ensure nothing in geo
            self._db._cursor.execute(self.viewGeoDim)
            record = self._db._cursor.fetchall()
            self.assertEqual(len(list(record)),self.geoDimRows)

        with self.subTest(name='old geo not added in geo_dim'): 
            repeatedGeoValues = [                   #geo_type          #geo_value
                CovidcastRow('src', 'sig', 'day', 'state', 20200415, 'pa', # same geo_type, geo_value
                        2, 2, 2, nmv, nmv, nmv, 20200415, 0),
                CovidcastRow('src', 'sig', 'day', 'county', 20200415, '11111', # same geo_type, geo_value
                        3, 3, 3, nmv, nmv, nmv, 20200415, 0),
                ]  
            self._db.insert_or_update_batch(repeatedGeoValues)
            self._db.run_dbjobs()

            self._db._cursor.execute(self.viewGeoDim)
            record = self._db._cursor.fetchall()
            self.assertEqual(len(list(record)),self.geoDimRows) #self.geoDimRows unchanged

            self._db._cursor.execute(self.viewSignalLatest)
            record = self._db._cursor.fetchall()
            self.sigLatestRows = len(list(record)) #update
            self.assertEqual(8,self.sigLatestRows) #total entries = 2(initial) + 6(test)

        with self.subTest(name='newer geo added in geo_dim'): 
            newGeoValues = [                   #geo_type          #geo_value
                CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'nj', # everything same except, state = nj
                    2, 2, 2, nmv, nmv, nmv, 20200414, 0),
                CovidcastRow('src', 'sig', 'day', 'county', 20200414, '15217', # everything same except, county = al
                    3, 3, 3, nmv, nmv, nmv, 20200414, 0),
                CovidcastRow('src', 'sig', 'day', 'county', 20200414, '15451', # everything same except, county = nj
                    3, 3, 3, nmv, nmv, nmv, 20200414, 0)
                ]  
            self._db.insert_or_update_batch(newGeoValues)
            self._db.run_dbjobs()

            self._db._cursor.execute(f'SELECT `geo_type`,`geo_value` FROM `geo_dim`')
            record = self._db._cursor.fetchall()
            self.geoDimRows = len(list(record))
            self.assertEqual(5,self.geoDimRows) #2 + 3 new

            self._db._cursor.execute(self.viewSignalLatest)
            record = self._db._cursor.fetchall()
            self.sigLatestRows = len(list(record)) #update
            self.assertEqual(11,self.sigLatestRows) #total entries = 2(initial) + 6(test) + 3
        