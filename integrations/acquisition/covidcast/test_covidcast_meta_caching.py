"""Integration tests for covidcast's metadata caching."""

# standard library
import json

# first party
from delphi_utils import Nans
from delphi.epidata.common.covidcast_test_base import CovidcastTestBase
from delphi.epidata.maintenance.covidcast_meta_cache_updater import main

# py3tester coverage target (equivalent to `import *`)
__test_target__ = (
  'delphi.epidata.acquisition.covidcast.'
  'covidcast_meta_cache_updater'
)


class CovidcastMetaCacheTests(CovidcastTestBase):
  """Tests covidcast metadata caching."""

  def test_caching(self):
    """Populate, query, cache, query, and verify the cache."""

    # insert dummy data
    self._db._cursor.execute(f'''
      INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`)
      VALUES
        (42, 'src', 'sig');
    ''')
    self._db._cursor.execute(f'''
      INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`)
      VALUES
        (96, 'state', 'pa'), 
        (97, 'state', 'wa');
    ''')
    self._db._cursor.execute(f'''
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
    self._db._connection.commit()

    # make sure the live utility is serving something sensible
    epidata1 = self._db.compute_covidcast_meta()
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
    epidata2 = self.epidata_client.covidcast_meta()
    self.assertEqual(epidata2['result'], -2, json.dumps(epidata2))

    # update the cache
    args = None
    main(args)

    # fetch the cached version
    epidata3 = self.epidata_client.covidcast_meta()

    # cached version should now equal live version
    self.assertEqual(epidata1, epidata3)

    # insert dummy data timestamped as of now
    self._db._cursor.execute('''
      update covidcast_meta_cache set
        timestamp = UNIX_TIMESTAMP(NOW()),
        epidata = '[{"hello": "world"}]'
    ''')
    self._db._connection.commit()

    # fetch the cached version (manually)
    epidata4 = self._make_request(endpoint="covidcast_meta", json=True, params={'cached': 'true'}, auth=self.epidata_client.auth, raise_for_status=True)

    # make sure the cache was actually served
    self.assertEqual(epidata4, {
      'result': 1,
      'epidata': [{
        'hello': 'world',
      }],
      'message': 'success',
    })

    # insert dummy data timestamped as 2 hours old
    self._db._cursor.execute('''
      update covidcast_meta_cache set
        timestamp = UNIX_TIMESTAMP(NOW()) - 3600 * 2,
        epidata = '[{"hello": "world"}]'
    ''')
    self._db._connection.commit()

    # fetch the cached version (manually)
    epidata5 = self._make_request(endpoint="covidcast_meta", json=True, params={'cached': 'true'}, auth=self.epidata_client.auth, raise_for_status=True)

    # make sure the cache was returned anyhow
    self.assertEqual(epidata4, epidata5)
