"""Integration tests for covidcast's is_latest_issue boolean."""
# standard library
import unittest
import time
from unittest.mock import patch, MagicMock
from json import JSONDecodeError
import numpy as np
from math import ceil

from queue import Queue, Empty
import threading
from multiprocessing import cpu_count


# third party
from aiohttp.client_exceptions import ClientResponseError
import mysql.connector
import pytest
from prettytable import PrettyTable, from_db_cursor
    
# first party
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_covidcast_meta_cache
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
#  
__test_target__ = 'delphi.epidata.acquisition.covidcast.database'


nmv = Nans.NOT_MISSING.value
class CovidcastLatestIssueTests(unittest.TestCase):
  """Tests covidcast is_latest_issue caching."""

  maxDiff = None #access full output of differences for debugging

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

  def tearDown(self):
    """Perform per-test teardown."""
    self._db._cursor.close()
    self._db._connection.close()


  def test_signal_latest(self):
    rows = [
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
                   1.5, 2.5, 3.5, nmv, nmv, nmv, 20200414, 0),
      CovidcastRow('src', 'sig', 'day', 'state', 20200415, 'wa', 
                   3, 2, 1, nmv, nmv, nmv, 20200415, 0)
    ]
    self._db.insert_or_update_bulk(rows)
    self._db.run_dbjobs()
    #preview
    self._db._cursor.execute('''SELECT * FROM `signal_history`''')
    self.totalRows = len(list(self._db._cursor.fetchall()))
    self._db._cursor.execute('''SELECT * FROM `signal_latest`''')
    record = self._db._cursor.fetchall()
    x = PrettyTable()
    x.field_names = ['signal_data_id',
    'signal_key_id',
    'geo_key_id',
    'demog_key_id' ,
    'issue' ,
    'data_as_of_dt',
    'time_type',
    'time_value' ,
    'reference_dt' ,
    'value' ,
    'stderr' ,
    'sample_size',
    'lag' ,
    'value_updated_timestamp' ,
    'computation_as_of_dt']
    print("SIGNAL_LATEST TABLE")
    for row in record:
      x.add_row(list(row)[:len(x.field_names)])
    print(x)
    print("Finish with 1st Set of Data")

    #sanity check for adding dummy data
    sql = '''SELECT `issue` FROM `signal_latest` where `time_value` = 20200414'''
    self._db._cursor.execute(sql)
    record = self._db._cursor.fetchall()
    self.assertEqual(record[0][0], 20200414)

    #when uploading data patches (data in signal load has < issue than data in signal_latest)
      #INSERT OLDER issue (does not end up in latest table)
      #INSERT NEWER issue (ends up in latest table)
    #when signal_load is older than signal_latest, we patch old data (i.e changed some old entries)
    newRow = [
    CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
                  4.4, 4.4, 4.4, nmv, nmv, nmv, 20200416, 2)] #should show up
    self._db.insert_or_update_bulk(newRow)
    self._db.run_dbjobs()
    
    #check newer issue in signal_latest
    sql = '''SELECT `issue` FROM `signal_latest` where `time_value` = 20200414 '''
    self._db._cursor.execute(sql)
    record = self._db._cursor.fetchall()
    self.assertEqual(record[0][0], 20200416) #new data added

    updateRow = [
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', 
                  6.5, 2.2, 11.5, nmv, nmv, nmv, 20200414, 2)]  #should not showup
    self._db.insert_or_update_bulk(updateRow)
    self._db.run_dbjobs()
    
    #check newer issue in signal_latest
    sql = '''SELECT `issue` FROM `signal_latest` where `time_value` = 20200414  '''
    self._db._cursor.execute(sql)
    record2 = self._db._cursor.fetchall()
    self.assertEqual(record, record2) #same as previous as is_latest did not change

    #dynamic check
    sql2 = '''SELECT `issue` FROM `signal_history` where `time_value` '''
    self._db._cursor.execute(sql2)
    record3 = self._db._cursor.fetchall()
    self.assertEqual(3,self.totalRows + 1) #ensure 3 added (1 of which refreshed)
    self.assertEqual(20200416,max(list(record3))[0]) #max of the outputs is 20200416 , extracting from tuple
    
    #check older issue not inside latest, empty field
    sql = '''SELECT * FROM `signal_latest` where `time_value` = 20200414 and `issue` = 20200415 '''
    self._db._cursor.execute(sql)
    emptyRecord = list(self._db._cursor.fetchall())
    empty = []
    self.assertEqual(empty, emptyRecord)
      
  # make sure rows are added to *_dim only when needed
    #new src, sig (ensure that it is added into *_dim)
    #old src, sig (ensure that it is NOT added into *_dim)
    #new geo (added)
    #old geo (not added)
  def test_src_sig(self):
    #BASE CASES
    rows = [
      # CovidcastRow('src', 'sig', 'day', 'county', 20200416, 'wa', #not seen
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', # 
      2, 2, 2, nmv, nmv, nmv, 20200414, 0),
      CovidcastRow('src', 'sig', 'day', 'county', 20200414, 'ca', # updating previous entry
      3, 3, 3, nmv, nmv, nmv, 20200414, 0)
    ]
    self._db.insert_or_update_bulk(rows)
    self._db.run_dbjobs()
    #setting baseline variables
    self._db._cursor.execute('''SELECT * FROM `geo_dim`''')
    record = self._db._cursor.fetchall()
    self.geoDimRows = len(list(record))

    self._db._cursor.execute('''SELECT * FROM `signal_dim`''')
    record = self._db._cursor.fetchall()
    self.sigDimRows = len(list(record))

    self._db._cursor.execute('''SELECT * FROM `signal_latest`''')
    record = self._db._cursor.fetchall()
    self.sigLatestRows = len(list(record))

    #test not added first
    with self.subTest(name='older src and sig not added into sig_dim'):
      oldSrcSig = [
        CovidcastRow('src', 'sig', 'day', 'state', 20211111, 'pa', #new src, new sig
                    99, 99, 99, nmv, nmv, nmv, 20211111, 1),
        CovidcastRow('src', 'sig', 'day', 'county', 20211111, 'ca', #new src, new sig
                    99, 99, 99, nmv, nmv, nmv, 20211111, 1)
          ]  
      self._db.insert_or_update_bulk(oldSrcSig)
      self._db.run_dbjobs()

      #testing src, sig
      self._db._cursor.execute('''SELECT `source`, `signal` FROM `signal_dim`''')
      record = self._db._cursor.fetchall()
      res = [('src','sig')] #output
      self.assertEqual(res , list(record))

      #ensure new entries are added 
      sql = '''SELECT * FROM `signal_latest`'''
      self._db._cursor.execute(sql)
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)), self.sigLatestRows + 2) #2 original, 2 added
      
      #ensure nothing in geo
      self._db._cursor.execute('''SELECT * FROM `geo_dim`''')
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)),self.geoDimRows)

    with self.subTest(name='newer src and sig added in sig_dim'):
      newSrcSig = [
        CovidcastRow('new_src', 'sig', 'day', 'state', 20200414, 'pa', # new_src
                    2, 2, 2, nmv, nmv, nmv, 20200414, 0),
        CovidcastRow('src', 'new_sig', 'day', 'state', 20200414, 'pa', # new_sig
                      2, 2, 2, nmv, nmv, nmv, 20200414, 0)
      ]  
      self._db.insert_or_update_bulk(newSrcSig)
      self._db.run_dbjobs()

      #testing src, sig
      self._db._cursor.execute('''SELECT `source`, `signal` FROM `signal_dim`''')
      record = self._db._cursor.fetchall()
      res = [('src', 'sig'), ('new_src', 'sig'), ('src', 'new_sig')]
      self.assertEqual(res , (record))
      #ensure nothing in geo
      self._db._cursor.execute('''SELECT * FROM `geo_dim`''')
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)),self.geoDimRows)

    with self.subTest(name='old geo not added in geo_dim'): 
      repeatedGeoValues = [                   #geo_type          #geo_value
          CovidcastRow('src', 'sig', 'day', 'state', 20200415, 'pa', # same geo_type, geo_value
                2, 2, 2, nmv, nmv, nmv, 20200415, 0),
          CovidcastRow('src', 'sig', 'day', 'county', 20200415, 'ca', # same geo_type, geo_value
                3, 3, 3, nmv, nmv, nmv, 20200415, 0),
          ]  
      self._db.insert_or_update_bulk(repeatedGeoValues)
      self._db.run_dbjobs()

      self._db._cursor.execute('''SELECT `geo_type`,`geo_value` FROM `geo_dim`''')
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)),self.geoDimRows) #geoDimRows unchanged


      self._db._cursor.execute('''SELECT * FROM `signal_latest`''')
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)),self.sigLatestRows + 6) #total entries = 2(initial) + 6(test)

    with self.subTest(name='newer geo added in geo_dim'): 
      newGeoValues = [                   #geo_type          #geo_value
        CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'nj', # everything same except, state = nj
            2, 2, 2, nmv, nmv, nmv, 20200414, 0),
        CovidcastRow('src', 'sig', 'day', 'county', 20200414, 'al', # everything same except, county = al
              3, 3, 3, nmv, nmv, nmv, 20200414, 0),
        CovidcastRow('src', 'sig', 'day', 'county', 20200414, 'nj', # everything same except, county = nj
              3, 3, 3, nmv, nmv, nmv, 20200414, 0)
          ]  
      self._db.insert_or_update_bulk(newGeoValues)
      self._db.run_dbjobs()

      self._db._cursor.execute('''SELECT `geo_type`,`geo_value` FROM `geo_dim`''')
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)),self.geoDimRows + 3) #2 + 3 new

      self._db._cursor.execute('''SELECT * FROM `signal_latest`''')
      record = self._db._cursor.fetchall()
      self.assertEqual(len(list(record)),self.sigLatestRows + 6 + 3) #total entries = 2(initial) + 6(test)

  @unittest.skip("helper function")
  def view_table(table_name):
    #TODO: abstract into function
    y = PrettyTable()
    y.field_names = ['signal_data_id',
    'signal_key_id',
    'geo_key_id',
    'demog_key_id' ,
    'issue' ,
    'data_as_of_dt',
    'time_type',
    'time_value' ,
    'reference_dt' ,
    'value' ,
    'stderr' ,
    'sample_size',
    'lag' ,
    'value_updated_timestamp' ,
    'computation_as_of_dt']
   
    print('\n')
    self._db._cursor.execute('''SELECT * FROM `signal_latest`''')
    record = self._db._cursor.fetchall()
    print(record)
    # assert(len(record) == )
    for row in record:
      y.add_row(list(row)[:len(y.field_names)])
    print(y)
    print("signal_latest updated")
    # self._db._cursor.execute('''SELECT * FROM `signal_dim`''')
    # record = self._db._cursor.fetchall()
    # print(record)
    # self._db._cursor.execute('''SELECT * FROM `geo_dim`''')
    # record = self._db._cursor.fetchall()
    # print(record)
    
    # sig_hist = PrettyTable()
    # sig_hist.field_names = [('signal_data_id',), ('signal_key_id',), ('geo_key_id',), ('demog_key_id',), ('issue',), ('data_as_of_dt',), ('time_type',), ('time_value',), ('reference_dt',), ('value',), ('stderr',), ('sample_size',), ('lag',), ('value_updated_timestamp',), ('computation_as_of_dt',), ('is_latest_issue',), ('missing_value',), ('missing_stderr',), ('missing_sample_size',), ('legacy_id',)]
    
    # sig_load = PrettyTable()
    # sig_load.field_names = [('signal_data_id',), ('signal_key_id',), ('geo_key_id',), ('demog_key_id',), ('issue',), ('data_as_of_dt',), ('source',), ('signal',), ('geo_type',), ('geo_value',), ('time_type',), ('time_value',), ('reference_dt',), ('value',), ('stderr',), ('sample_size',), ('lag',), ('value_updated_timestamp',), ('computation_as_of_dt',), ('is_latest_issue',), ('missing_value',), ('missing_stderr',), ('missing_sample_size',), ('legacy_id',), ('compressed_signal_key',), ('compressed_geo_key',), ('compressed_demog_key',), ('process_status',)]
    
    #when uploading data patches (data in signal load has < issue than data in signal_latest)
    #when signal_load is older than signal_latest, we patch old data (i.e changed some old entries)
    pass

  @unittest.skip("Having different (time_value,issue) pairs in one call to db pipeline does not happen in practice")
  def test_diff_timevalue_issue(self):
    rows = [
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', #updating old issue, should be seen in latest
                17, 17, 17, nmv, nmv, nmv, 20200417, 3),
      CovidcastRow('src', 'sig', 'day', 'state', 20200414, 'pa', # updating previous entry
                2, 2, 3, nmv, nmv, nmv, 20200416, 2)
    ]
    self._db.insert_or_update_bulk(rows) 
    self._db.run_dbjobs()
    self._db._cursor.execute('''SELECT `issue` FROM `signal_latest` ''')
    record = self._db._cursor.fetchall()
    print(record[0][0])
    self.assertEqual(record[0][0], 20200417) #20200416 != 20200417