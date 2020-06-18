"""Integration tests for covidcast's metadata caching."""

# standard library
import unittest

# third party
import mysql.connector
import requests

# first party
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = (
  'delphi.epidata.acquisition.covidcast.'
  'covidcast_meta_cache_updater'
)

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidcastMetaCacheTests(unittest.TestCase):
  """Tests covidcast metadata caching."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()

    # clear the `covidcast` table
    cur.execute('truncate table covidcast')
    # reset the `covidcast_meta_cache` table (it should always have one row)
    cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = ""')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = BASE_URL

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_caching(self):
    """Populate, query, cache, query, and verify the cache."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'state', 20200422, 'pa',
          123, 1, 2, 3, 456, 1, 20200422, 0),
        (0, 'src', 'sig', 'day', 'state', 20200422, 'wa',
          789, 1, 2, 3, 456, 1, 20200423, 1)
    ''')
    self.cur.execute('''
      insert into covidcast values
        (100, 'src', 'wip_sig', 'day', 'state', 20200422, 'pa',
          456, 4, 5, 6, 789, -1, 20200422, 0)
    ''')

    self.cnx.commit()

    # make sure covidcast_meta is serving something sensible
    epidata1 = Epidata.covidcast_meta()
    self.assertEqual(epidata1['result'], 1)
    self.assertEqual(epidata1['epidata'], [
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
        'max_lag': 1
      }
    ])

    # fetch the cached version (manually)
    params = {'source': 'covidcast_meta', 'cached': 'true'}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    epidata2 = response.json()

    # API should fallback to live version
    self.assertEqual(epidata1, epidata2)

    # update the cache
    args = None
    main(args)

    # fetch the cached version (manually)
    params = {'source': 'covidcast_meta', 'cached': 'true'}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    epidata3 = response.json()

    # cached version should equal live version
    self.assertEqual(epidata1, epidata3)

    # insert dummy data timestamped as of now
    self.cur.execute('''
      update covidcast_meta_cache set
        timestamp = UNIX_TIMESTAMP(NOW()),
        epidata = '[{"hello": "world"}]'
    ''')
    self.cnx.commit()

    # fetch the cached version (manually)
    params = {'source': 'covidcast_meta', 'cached': 'true'}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    epidata4 = response.json()

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
    params = {'source': 'covidcast_meta', 'cached': 'true'}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    epidata5 = response.json()

    # make sure the cache was bypassed
    self.assertEqual(epidata1, epidata5)
