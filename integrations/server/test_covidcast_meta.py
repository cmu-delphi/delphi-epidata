"""Integration tests for the `covidcast_meta` endpoint."""

# standard library
from datetime import date
from itertools import chain
from typing import Iterable, Optional

# third party
import numpy as np
import pandas as pd
import pytest
import requests

# first party
import delphi.operations.secrets as secrets
from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_cache
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.database_meta import DatabaseMeta
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase


# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


def _dicts_equal(d1: dict, d2: dict, ignore_keys: Optional[list] = None, rel: Optional[float] = None, abs: Optional[float] = None) -> bool:
    """Compare dictionary values using floating point comparison for numeric values."""
    assert set(d1.keys()) == set(d2.keys()), "Dictionary keys should be the same."
    return all(d1.get(key) == pytest.approx(d2.get(key), rel=rel, abs=abs, nan_ok=True) for key in d1.keys() if (ignore_keys and key not in ignore_keys))


class TestCovidcastMeta(CovidcastBase):
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

    # connect to the `epidata` database
    self.db = DatabaseMeta(base_url="http://delphi_web_epidata/epidata")
    self.db.connect(user="user", password="pass", host="delphi_database_epidata", database="covid")

    # TODO: Switch when delphi_epidata client is released.
    self.db.delphi_epidata = False

    # populate dimension tables
    for (src,sig) in self.src_sig_lookups:
        self.db._cursor.execute('''
            INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`)
            VALUES (%d, '%s', '%s'); ''' % ( self.src_sig_lookups[(src,sig)], src, sig ))
    for (gt,gv) in self.geo_lookups:
        self.db._cursor.execute('''
            INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`)
            VALUES (%d, '%s', '%s'); ''' % ( self.geo_lookups[(gt,gv)], gt, gv ))

    self.db._connection.commit()

    # initialize counter for tables without non-autoincrement id
    self.id_counter = 666

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

  def localTearDown(self):
    """Perform per-test teardown."""
    self.db._cursor.close()
    self.db._connection.close()

  def _insert_rows(self, rows: Iterable[CovidcastRow]):
      self.db.insert_or_update_bulk(list(rows))
      self.db.run_dbjobs()
      self.db._connection.commit()
      return rows

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
                self.db._cursor.execute(self.template % (
                  self._get_id(),
                  self.src_sig_lookups[(src,sig)], self.geo_lookups[(gt,gv)],
                  tt, tv, v, tv, # re-use time value for issue
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.db._connection.commit()
    update_cache(args=None)
    return expected

  def _get_id(self):
    self.id_counter += 1
    return self.id_counter

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert placeholder data and accumulate expected results (in sort order)
    expected = self.insert_placeholder_data()

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

    # insert placeholder data and accumulate expected results (in sort order)
    expected = self.insert_placeholder_data()

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

  def test_meta_values(self):
    """This is an A/B test between the old meta compute approach and the new one which relies on an API call for JIT signals.

    It relies on synthetic data.
    """

    def get_rows_gen(df: pd.DataFrame, filter_nans: bool = False) -> Iterable[CovidcastRow]:
      for row in df.itertuples(index=False):
        row_dict = row._asdict()
        if not filter_nans or (filter_nans and not any(map(pd.isna, row_dict.values()))):
          yield CovidcastRow(**row_dict)

    start_date = date(2022, 4, 1)
    end_date = date(2022, 6, 1)
    n = (end_date - start_date).days + 1

    # TODO: Build a more complex synthetic dataset here.
    # fmt: off
    cumulative_df = pd.DataFrame(
      {
        "source": ["jhu-csse"] * n + ["usa-facts"] * n,
        "signal": ["confirmed_cumulative_num"] * n + ["confirmed_cumulative_num"] * (n // 2 - 1) +  [np.nan] + ["confirmed_cumulative_num"] * (n // 2),
        "time_value": chain(pd.date_range(start_date, end_date), pd.date_range(start_date, end_date)),
        "issue": chain(pd.date_range(start_date, end_date), pd.date_range(start_date, end_date)),
        "value": chain(range(n), range(n))
      }
    )
    incidence_df = (
      cumulative_df.set_index(["source", "time_value"])
        .groupby("source")
        .apply(lambda df: df.assign(
          signal="confirmed_incidence_num",
          value=df.value.diff(),
          issue=[max(window) if window.size >= 2 else np.nan for window in df.issue.rolling(2)]
        )
      )
    ).reset_index()
    smoothed_incidence_df = (
      cumulative_df.set_index(["source", "time_value"])
        .groupby("source")
        .apply(lambda df: df.assign(
          signal="confirmed_7dav_incidence_num",
          value=df.value.rolling(7).mean().diff(),
          issue=[max(window) if window.size >= 7 else np.nan for window in df.issue.rolling(7)]
        )
      )
    ).reset_index()
    # fmt: on

    self._insert_rows(get_rows_gen(cumulative_df, filter_nans=True))
    self._insert_rows(get_rows_gen(incidence_df, filter_nans=True))
    self._insert_rows(get_rows_gen(smoothed_incidence_df, filter_nans=True))

    meta_values = self.db.compute_covidcast_meta(jit=False)
    meta_values2 = self.db.compute_covidcast_meta(jit=True)

    out = [_dicts_equal(x, y, ignore_keys=["max_lag"]) for x, y in zip(meta_values, meta_values2)]

    assert all(out)
