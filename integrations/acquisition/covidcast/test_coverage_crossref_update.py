"""Integration tests for covidcast's metadata caching."""

# standard library
import json
import unittest

# third party
import mysql.connector
import requests

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets
import delphi.epidata.acquisition.covidcast.database as live
from delphi.epidata.maintenance.coverage_crossref_updater import main

# py3tester coverage target (equivalent to `import *`)
__test_target__ = (
  'delphi.epidata.acquisition.covidcast.'
  'coverage_crossref_updater'
)

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata'


class CoverageCrossrefTests(unittest.TestCase):
  """Tests coverage crossref updater."""

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
    cur.execute("truncate table epimetric_load")
    cur.execute("truncate table epimetric_full")
    cur.execute("truncate table epimetric_latest")
    cur.execute("truncate table geo_dim")
    cur.execute("truncate table signal_dim")
    cur.execute("truncate table coverage_crossref")
    cur.execute("truncate table coverage_crossref_load")
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    epidata_cnx = mysql.connector.connect(
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
    params = {'geo': 'state:*'}
    response = requests.get(f"{Epidata.BASE_URL}/covidcast/geo_coverage", params=params, auth=Epidata.auth)
    response.raise_for_status()
    return response.json()

  def test_caching(self):
    """Populate, query, cache, query, and verify the cache."""

    # insert dummy data
    self.cur.execute('''
      INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`)
      VALUES
        (42, 'src', 'sig');
    ''')
    self.cur.execute('''
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

    results = self._make_request()
    
    # make sure the tables are empty
    self.assertEqual(results, {
      'result': -2,
      'epidata': [],
      'message': 'no results',
    })

    # update the coverage crossref table
    main()

    results = self._make_request()

    # make sure the cache was actually served
    self.assertEqual(results, {
      'result': 1,
      'epidata': [{'signal': 'sig', 'source': 'src'},
                  {'signal': 'sig', 'source': 'src'}],
      'message': 'success',
    })
