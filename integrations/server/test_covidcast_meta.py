"""Integration tests for the `covidcast_meta` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests

#first party
from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_cache

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidcastMetaTests(unittest.TestCase):
  """Tests the `covidcast_meta` endpoint."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    # clear the datapoint and data_reference tables
    cur.execute('SET foreign_key_checks = 0')
    cur.execute('truncate table datapoint')
    cur.execute('truncate table data_reference')
    cur.execute('SET foreign_key_checks = 1') 
    
    cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = ""')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert dummy data and accumulate expected results (in sort order)
    template = '''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, "%s", "%s", "%s", "%s", %d, "%s", 123,
        %d, 0, 0, 456, 0, %d, 0, 1, %d, %d, %d, %d)
    '''
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
                self.cur.execute(template % (
                  src, sig, tt, gt, tv, gv, v, tv, False,
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.cnx.commit()
    update_cache(args=None)

    # make the request
    response = requests.get(BASE_URL, params={'endpoint': 'covidcast_meta'})
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })


  def test_filter(self):
    """Test filtering options some sample data."""

    # insert dummy data and accumulate expected results (in sort order)
    template = '''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, "%s", "%s", "%s", "%s", %d, "%s", 123,
        %d, 0, 0, 456, 0, %d, 0, 1, %d, %d, %d, %d)
    '''
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
                self.cur.execute(template % (
                  src, sig, tt, gt, tv, gv, v, tv, False,
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.cnx.commit()
    update_cache(args=None)

    def fetch(**kwargs):
      # make the request
      params = kwargs.copy()
      params['endpoint'] = 'covidcast_meta'
      response = requests.get(BASE_URL, params=params)
      response.raise_for_status()
      return response.json()

    res = fetch()
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), len(expected))

    # time types
    res = fetch(time_types='day')
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['time_type'] == 'day']))

    res = fetch(time_types='day,week')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), len(expected))

    res = fetch(time_types='sec')
    self.assertEqual(res['result'], -2)

    # geo types
    res = fetch(geo_types='hrr')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['geo_type'] == 'hrr']))

    res = fetch(geo_types='hrr,msa')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), len(expected))

    res = fetch(geo_types='state')
    self.assertEqual(res['result'], -2)

    # signals
    res = fetch(signals='src1:sig1')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['data_source'] == 'src1' and s['signal'] == 'sig1']))

    res = fetch(signals='src1')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['data_source'] == 'src1']))

    res = fetch(signals='src1:*')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), sum([1 for s in expected if s['data_source'] == 'src1']))

    res = fetch(signals='src1:src4')
    self.assertEqual(res['result'], -2)

    res = fetch(signals='src1:*,src2:*')
    self.assertEqual(res['result'], 1)
    self.assertTrue(isinstance(res['epidata'], list))
    self.assertEqual(len(res['epidata']), len(expected))

    # filter fields
    res = fetch(fields='data_source,min_time')
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), len(expected))
    self.assertTrue('data_source' in res['epidata'][0])
    self.assertTrue('min_time' in res['epidata'][0])
    self.assertFalse('max_time' in res['epidata'][0])
    self.assertFalse('signal' in res['epidata'][0])

    res = fetch(fields='xx')
    self.assertEqual(res['result'], 1)
    self.assertEqual(len(res['epidata']), len(expected))
    self.assertEqual(res['epidata'][0], {})


  def test_suppress_work_in_progress(self):
    """Don't surface signals that are a work-in-progress."""

    # insert dummy data and accumulate expected results (in sort order)
    template = '''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, "%s", "%s", "%s", "%s", %d, "%s", 123,
        %d, 0, 0, 456, 0, %d, 0, 1, %d, %d, %d, %d)
    '''
    expected = []
    for src in ('src1', 'src2'):
      for sig in ('sig1', 'sig2', 'wip_sig3'):
        for tt in ('day', 'week'):
          for gt in ('hrr', 'msa'):

            if sig == 'wip_sig3':
              is_wip = True
            else:
              is_wip = False
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
                self.cur.execute(template % (
                  src, sig, tt, gt, tv, gv, v, tv, is_wip,
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.cnx.commit()
    update_cache(args=None)

    # make the request
    response = requests.get(BASE_URL, params={'endpoint': 'covidcast_meta'})
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })
