"""Integration tests for covidcast's metadata caching."""

# standard library
import json
import unittest

# third party
import MySQLdb
import requests

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets
import delphi.epidata.acquisition.covidcast.database as live
from delphi.epidata.maintenance.covidcast_meta_cache_updater import main

# py3tester coverage target (equivalent to `import *`)
__test_target__ = (
  'delphi.epidata.acquisition.covidcast.'
  'covidcast_meta_cache_updater'
)

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata'


class CovidcastMetaCacheTests(unittest.TestCase):
  """Tests covidcast metadata caching."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database
    cnx = MySQLdb.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='covid')
    cur = cnx.cursor()

    # clear all tables
    cur.execute("truncate table epimetric_load")
    cur.execute("truncate table epimetric_full")
    cur.execute("truncate table epimetric_latest")
    cur.execute("truncate table geo_dim")
    cur.execute("truncate table signal_dim")
    # reset the `covidcast_meta_cache` table (it should always have one row)
    cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    epidata_cnx = MySQLdb.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    epidata_cur = epidata_cnx.cursor()

    epidata_cur.execute("DELETE FROM `api_user`")
    epidata_cur.execute('INSERT INTO `api_user`(`api_key`, `email`) VALUES("key", "email")')
    epidata_cnx.commit()
    epidata_cur.close()
    epidata_cnx.close()

    # use the local instance of the Epidata API
    Epidata.BASE_URL = BASE_URL
    Epidata.auth = ('epidata', 'key')

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  @staticmethod
  def _make_request():
    params = {'cached': 'true'}
    response = requests.get(f"{Epidata.BASE_URL}/covidcast_meta", params=params, auth=Epidata.auth)
    response.raise_for_status()
    return response.json()

  def test_caching(self):
    """Populate, query, cache, query, and verify the cache."""

    # insert dummy data
    self.cur.execute(f'''
      INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`)
      VALUES
        (42, 'src', 'sig');
    ''')
    self.cur.execute(f'''
      INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`)
      VALUES
        (96, 'state', 'pa'), 
        (97, 'state', 'wa');
    ''')
    self.cur.execute(f'''
      INSERT INTO
        `epimetric_latest` (`epimetric_id`, `signal_key_id`, `geo_key_id`, `time_type`,
	      `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`,
        `issue`, `lag`, `missing_value`,
        `missing_stderr`,`missing_sample_size`)
      VALUES
        (15, 42, 96, 'day', 20200422,
          123, 1, 2, 3, 20200422, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (16, 42, 97, 'day', 20200422,
          789, 1, 2, 3, 20200423, 1, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
    ''')
    self.cnx.commit()

    # make sure the live utility is serving something sensible
    cvc_database = live.Database()
    cvc_database.connect()
    epidata1 = cvc_database.compute_covidcast_meta()
    cvc_database.disconnect(False)
    self.assertEqual(len(epidata1),1)
    self.assertEqual(epidata1, [
      {
        'data_source': 'src',
        'signal': 'sig',
        'time_type': 'day',
        'geo_type': 'state',
        'min_time': 20200422,
        'max_time': 20200422,
        'num_locations': 2,
        'last_update': 789,
        'min_value': 1,
        'max_value': 1,
        'mean_value': 1,
        'stdev_value': 0,
        'max_issue': 20200423,
        'min_lag': 0,
        'max_lag': 1,
      }
    ])
    epidata1={'result':1, 'message':'success', 'epidata':epidata1}

    # make sure the API covidcast_meta is still blank, since it only serves
    # the cached version and we haven't cached anything yet
    epidata2 = Epidata.covidcast_meta()
    self.assertEqual(epidata2['result'], -2, json.dumps(epidata2))

    # update the cache
    args = None
    main(args)

    # fetch the cached version
    epidata3 = Epidata.covidcast_meta()

    # cached version should now equal live version
    self.assertEqual(epidata1, epidata3)

    # insert dummy data timestamped as of now
    self.cur.execute('''
      update covidcast_meta_cache set
        timestamp = UNIX_TIMESTAMP(NOW()),
        epidata = '[{"hello": "world"}]'
    ''')
    self.cnx.commit()

    # fetch the cached version (manually)
    epidata4 = self._make_request()

    # make sure the cache was actually served
    self.assertEqual(epidata4, {
      'result': 1,
      'epidata': [{
        'hello': 'world',
      }],
      'message': 'success',
    })

    # insert dummy data timestamped as 2 hours old
    self.cur.execute('''
      update covidcast_meta_cache set
        timestamp = UNIX_TIMESTAMP(NOW()) - 3600 * 2,
        epidata = '[{"hello": "world"}]'
    ''')
    self.cnx.commit()

    # fetch the cached version (manually)
    epidata5 = self._make_request()

    # make sure the cache was returned anyhow
    self.assertEqual(epidata4, epidata5)
