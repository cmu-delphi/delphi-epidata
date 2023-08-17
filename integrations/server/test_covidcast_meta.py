"""Integration tests for the `covidcast_meta` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests

#first party
from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase, CovidcastTestRow
from delphi.epidata.maintenance.covidcast_meta_cache_updater import main as update_cache
import delphi.operations.secrets as secrets

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
AUTH = ('epidata', 'key')


class CovidcastMetaTests(CovidcastBase):
  """Tests the `covidcast_meta` endpoint."""

  src_sig_lookups = {
    ('src1', 'sig1'): 101,
    ('src1', 'sig2'): 102,
    ('src2', 'sig1'): 201,
    ('src2', 'sig2'): 202,
  }
  geo_lookups = {
    ('hrr', 'geo1'): 10001,
    ('hrr', 'geo2'): 10002,
    ('msa', 'geo1'): 20001,
    ('msa', 'geo2'): 20002,
  }

  template = '''
      INSERT INTO `epimetric_latest` (
        `epimetric_id`, `signal_key_id`, `geo_key_id`,
        `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`,
        `issue`, `lag`, `missing_value`,
        `missing_stderr`,`missing_sample_size`)
      VALUES
        (%d, %d, %d,
         "%s", %d, 123,
         %d, 0, 0,
         %d, 0, %d,
         %d, %d)
  '''

  def localSetUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
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
    # reset the `covidcast_meta_cache` table (it should always have one row)
    cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    cur.execute("TRUNCATE TABLE epidata.api_user")
    cur.execute("TRUNCATE TABLE epidata.user_role")
    cur.execute("TRUNCATE TABLE epidata.user_role_link")
    cur.execute("INSERT INTO epidata.api_user (api_key, email) VALUES ('quidel_key', 'quidel_email')")
    cur.execute("INSERT INTO epidata.user_role (name) VALUES ('quidel')")
    cur.execute(
      "INSERT INTO epidata.user_role_link (user_id, role_id) SELECT api_user.id, user_role.id FROM epidata.api_user JOIN epidata.user_role WHERE api_key='quidel_key' and user_role.name='quidel'"
    )
    cur.execute("insert into epidata.api_user (api_key, email) values ('key', 'email')")

    # populate dimension tables
    for (src,sig) in self.src_sig_lookups:
        cur.execute('''
            INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`)
            VALUES (%d, '%s', '%s'); ''' % ( self.src_sig_lookups[(src,sig)], src, sig ))
    for (gt,gv) in self.geo_lookups:
        cur.execute('''
            INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`)
            VALUES (%d, '%s', '%s'); ''' % ( self.geo_lookups[(gt,gv)], gt, gv ))

    cnx.commit()
    cur.close()

    # initialize counter for tables without non-autoincrement id
    self.id_counter = 666

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')


  def localTearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def insert_placeholder_data(self):
    expected = []
    for src in ('src1', 'src2'):
      for sig in ('sig1', 'sig2'):
        for tt in ('day', 'week'):
          for gt in ('hrr', 'msa'):
            expected.append({
              'data_source': src,
              'signal': sig,
              'time_type': tt,
              'geo_type': gt,
              'min_time': 1,
              'max_time': 2,
              'num_locations': 2,
              'min_value': 10,
              'max_value': 20,
              'mean_value': 15,
              'stdev_value': 5,
              'last_update': 123,
              'max_issue': 2,
              'min_lag': 0,
              'max_lag': 0,
            })
            for tv in (1, 2):
              for gv, v in zip(('geo1', 'geo2'), (10, 20)):
                self.cur.execute(self.template % (
                  self._get_id(),
                  self.src_sig_lookups[(src,sig)], self.geo_lookups[(gt,gv)],
                  tt, tv, v, tv, # re-use time value for issue
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.cnx.commit()
    update_cache(args=None)
    return expected

  def _get_id(self):
    self.id_counter += 1
    return self.id_counter
  
  @staticmethod
  def _fetch(auth=AUTH, **kwargs):
    params = kwargs.copy()
    params['endpoint'] = 'covidcast_meta'
    response = requests.get(BASE_URL, params=params, auth=auth)
    response.raise_for_status()
    return response.json()

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert placeholder data and accumulate expected results (in sort order)
    expected = self.insert_placeholder_data()

    # make the request
    response = self._fetch()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })

  def test_restricted_sources(self):
    # insert data from two different sources, one restricted/protected (quidel), one not
    self._insert_rows([
      CovidcastTestRow.make_default_row(source="quidel"),
      CovidcastTestRow.make_default_row(source="not-quidel")
    ])

    # generate metadata cache
    update_cache(args=None)

    # verify unauthenticated (no api key) or unauthorized (user w/o privilege) only see metadata for one source
    self.assertEqual(len(self._fetch(auth=None)['epidata']), 1)
    self.assertEqual(len(self._fetch(auth=AUTH)['epidata']), 1)

    # verify authorized user sees metadata for both sources
    qauth = ('epidata', 'quidel_key')
    self.assertEqual(len(self._fetch(auth=qauth)['epidata']), 2)

  def test_filter(self):
    """Test filtering options some sample data."""

    # insert placeholder data and accumulate expected results (in sort order)
    expected = self.insert_placeholder_data()

    res = self._fetch()
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), len(expected))

    # time types
    res = self._fetch(time_types='day')
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['time_type'] == 'day']))

    res = self._fetch(time_types='day,week')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), len(expected))

    res = self._fetch(time_types='sec')
    self.assertEqual(res['result'], -2)

    # geo types
    res = self._fetch(geo_types='hrr')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['geo_type'] == 'hrr']))

    res = self._fetch(geo_types='hrr,msa')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), len(expected))

    res = self._fetch(geo_types='state')
    self.assertEqual(res['result'], -2)

    # signals
    res = self._fetch(signals='src1:sig1')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['data_source'] == 'src1' and s['signal'] == 'sig1']))

    res = self._fetch(signals='src1')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['data_source'] == 'src1']))

    res = self._fetch(signals='src1:*')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['data_source'] == 'src1']))

    res = self._fetch(signals='src1:src4')
    self.assertEqual(res['result'], -2)

    res = self._fetch(signals='src1:*,src2:*')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), len(expected))

    # filter fields
    res = self._fetch(fields='data_source,min_time')
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), len(expected))
    self.assertTrue('data_source' in res['epidata'][0])
    self.assertTrue('min_time' in res['epidata'][0])
    self.assertFalse('max_time' in res['epidata'][0])
    self.assertFalse('signal' in res['epidata'][0])

    res = self._fetch(fields='xx')
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), len(expected))
    self.assertEqual(res['epidata'][0], {})

