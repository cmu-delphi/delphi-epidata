"""Integration tests for covidcast's is_latest_issue boolean."""
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
class CovidcastLatestIssueTests(unittest.TestCase):

  """Tests covidcast is_latest_issue caching."""

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

  def tearDown(self):
    """Perform per-test teardown."""
    self._db._cursor.close()
    self._db._connection.close()

  def test_signal_latest(self):

    rows = [
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
                   1.5, 2.5, 3.5, nmv, nmv, nmv, 20200414, 0)
    ]
    self._db.insert_or_update_batch(rows)
    self._db.run_dbjobs()
    self._db._cursor.execute(self.viewSignalHistory)
    self.totalRows = len(list(self._db._cursor.fetchall()))

    #sanity check for adding dummy data
    sql = f'SELECT `issue` FROM {Database.latest_table} where `time_value` = 20200414'
    self._db._cursor.execute(sql)
    record = self._db._cursor.fetchall()
    self.assertEqual(record[0][0], 20200414)
    self.assertEqual(len(record), 1) #check 1 entry present

    #when uploading data patches (data in signal load has < issue than data in signal_latest)
      #INSERT OLDER issue (does not end up in latest table)
      #INSERT NEWER issue (ends up in latest table)
    #when signal_load is older than signal_latest, we patch old data (i.e changed some old entries)
    newRow = [
    CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
                  4.4, 4.4, 4.4, nmv, nmv, nmv, 20200416, 2)] #should show up
    self._db.insert_or_update_batch(newRow)
    self._db.run_dbjobs()
    
    #check newer issue in signal_latest
    sql = f'SELECT `issue` FROM {Database.latest_table} where `time_value` = 20200414 '
    self._db._cursor.execute(sql)
    record = self._db._cursor.fetchall()
    self.assertEqual(record[0][0], 20200416) #new data added
    self.assertEqual(len(record), 1) #check 1 entry present

    updateRow = [
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
                  6.5, 2.2, 11.5, nmv, nmv, nmv, 20200414, 2)]  #should not showup
    self._db.insert_or_update_batch(updateRow)
    self._db.run_dbjobs()
    
    #check newer issue in signal_latest
    sql = f'SELECT `issue` FROM {Database.latest_table} where `time_value` = 20200414  '
    self._db._cursor.execute(sql)
    record2 = self._db._cursor.fetchall()
    self.assertEqual(record, record2) #same as previous as is_latest did not change

    #dynamic check for signal_history's list of issue
    self._db._cursor.execute(f'SELECT `issue` FROM {Database.history_table}')
    record3 = self._db._cursor.fetchall()
    self.totalRows = len(list(record3)) #updating totalRows
    self.assertEqual(2,self.totalRows) #ensure len(record3) = 2
    self.assertEqual(20200416,max(record3)[0]) #max of the outputs is 20200416 , extracting from tuple
    
    #check older issue not inside latest, empty field
    sql = f'SELECT * FROM {Database.latest_table} where `time_value` = 20200414 and `issue` = 20200414 '
    self._db._cursor.execute(sql)
    emptyRecord = list(self._db._cursor.fetchall())
    empty = []
    self.assertEqual(empty, emptyRecord)
  
  @unittest.skip("Having different (time_value,issue) pairs in one call to db pipeline does not happen in practice")
  def test_diff_timevalue_issue(self):
    rows = [
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', #updating old issue, should be seen in latest
                17, 17, 17, nmv, nmv, nmv, 20200417, 3),
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', # updating previous entry
                2, 2, 3, nmv, nmv, nmv, 20200416, 2)
    ]
    self._db.insert_or_update_batch(rows) 
    self._db.run_dbjobs()
    self._db._cursor.execute(f'SELECT `issue` FROM {Database.latest_table} ')
    record = self._db._cursor.fetchall()  
    self.assertEqual(record[0][0], 20200417) #20200416 != 20200417