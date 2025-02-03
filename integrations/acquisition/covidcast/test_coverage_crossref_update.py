"""Integration tests for the covidcast `geo_coverage` endpoint."""

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
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata' # NOSONAR


class CoverageCrossrefTests(CovidcastBase):
  """Tests coverage crossref updater."""

  def localSetUp(self):
    """Perform per-test setup."""
    self._db._cursor.execute('TRUNCATE TABLE `coverage_crossref`')

  @staticmethod
  def _make_request(params=None):
    if params is None:
        params = {'geo': 'state:*'}
    response = requests.get(f"{Epidata.BASE_URL}/covidcast/geo_coverage", params=params, auth=Epidata.auth)
    response.raise_for_status()
    return response.json()

  def test_caching(self):
    """Populate, query, cache, query, and verify the cache."""

    # insert dummy data
    self._db._cursor.execute('''
      INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`)
      VALUES
        (42, 'src', 'sig');
    ''')
    self._db._cursor.execute('''
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
    self._db.commit()

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

    # make sure the data was actually served
    self.assertEqual(results, {
      'result': 1,
      'epidata': [{'signal': 'sig', 'source': 'src'}],
      'message': 'success',
    })

    results = self._make_request(params = {'geo': 'hrr:*'})

    # make sure the tables are empty
    self.assertEqual(results, {
      'result': -2,
      'epidata': [],
      'message': 'no results',
    })

    results = self._make_request(params = {'geo': 'state:pa'})

    # make sure the data was actually served
    self.assertEqual(results, {
      'result': 1,
      'epidata': [{'signal': 'sig', 'source': 'src'}],
      'message': 'success',
    })
