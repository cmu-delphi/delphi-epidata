"""Integration tests for the `covidcast_meta` endpoint."""

# standard library
import unittest
from datetime import date, datetime
from numbers import Number
from typing import Iterable, Optional, Union

# third party
import numpy as np
import pandas as pd
import requests

# first party
from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_cache
from delphi.epidata.acquisition.covidcast.database import CovidcastRow
from delphi.epidata.acquisition.covidcast.database_meta import DatabaseMeta
import delphi.operations.secrets as secrets

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


def _df_to_covidcastrows(df: pd.DataFrame) -> Iterable[CovidcastRow]:
  """Iterates over the rows of a dataframe.

  The dataframe is expected to have many columns, see below for which.
  """
  for x in df.iterrows():
    _, row = x
    yield CovidcastRow(
      source=row.data_source,
      signal=row.signal,
      time_type="day",
      geo_type=row.geo_type,
      time_value=datetime.strptime(row.time_value, "%Y-%m-%d"),
      geo_value=row.geo_value,
      value=row.value,
      stderr=row.stderr if not np.isnan(row.stderr) else None,
      sample_size=row.sample_size if not np.isnan(row.sample_size) else None,
      missing_value=row.missing_value,
      missing_stderr=row.missing_stderr,
      missing_sample_size=row.missing_sample_size,
      issue=datetime.strptime(row.issue, "%Y-%m-%d"),
      lag=row.lag,
    )


def _almost_equal(v1: Optional[Union[Number, str]], v2: Optional[Union[Number, str]], atol: float = 1e-08) -> bool:
  if v1 is None and v2 is None:
    return True
  elif (v1 is None and v2 is not None) or (v1 is not None and v2 is None):
    return False
  else:
    return np.allclose(v1, v2, atol=atol) if isinstance(v1, Number) and isinstance(v2, Number) else v1 == v2


def _dicts_equal(d1: dict, d2: dict, ignore_keys: Optional[list] = None, atol: float = 1e-08) -> bool:
  """Compare dictionary values using floating point comparison for numeric values."""
  assert set(d1.keys()) == set(d2.keys())
  return all(_almost_equal(d1.get(key), d2.get(key), atol=atol) for key in d1.keys() if (ignore_keys and key not in ignore_keys))


class CovidcastMetaTests(unittest.TestCase):
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
      INSERT INTO
        `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
	      `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`,
        `issue`, `lag`, `missing_value`,
        `missing_stderr`,`missing_sample_size`)
      VALUES
        (%d, %d, %d, "%s", %d, 123,
        %d, 0, 0, %d, 0, %d, %d, %d)
  '''

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database
    self.db = DatabaseMeta(base_url="http://delphi_web_epidata/epidata")
    self.db.connect(user="user", password="pass", host="delphi_database_epidata", database="covid")

    # TODO: Switch when delphi_epidata client is released.
    self.db.delphi_epidata = False

    # clear all tables
    self.db._cursor.execute("truncate table signal_load")
    self.db._cursor.execute("truncate table signal_history")
    self.db._cursor.execute("truncate table signal_latest")
    self.db._cursor.execute("truncate table geo_dim")
    self.db._cursor.execute("truncate table signal_dim")
    self.db._connection.commit()
    # reset the `covidcast_meta_cache` table (it should always have one row)
    self.db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    # populate dimension tables for convenience
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


  def tearDown(self):
    """Perform per-test teardown."""
    self.db._cursor.close()
    self.db._connection.close()

  def _get_id(self):
    self.id_counter += 1
    return self.id_counter

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert dummy data and accumulate expected results (in sort order)
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
                  self.src_sig_lookups[(src,sig)], self.geo_lookups[(gt,gv)], tt, tv, v, tv,
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.db._connection.commit()
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
                  self.src_sig_lookups[(src,sig)], self.geo_lookups[(gt,gv)], tt, tv, v, tv,
                  Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING
                ))
    self.db._connection.commit()
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

  def _insert_rows(self, rows: Iterable[CovidcastRow]):
    self.db.insert_or_update_bulk(list(rows))
    self.db.run_dbjobs()
    self.db._connection.commit()
    return rows

  def _insert_csv(self, filename: str):
    self._insert_rows(_df_to_covidcastrows(pd.read_csv(filename)))

  def test_meta_values(self):
    """This test provides a framework for A/B testing between the old meta compute approach and the new one which relies on an API call for JIT signals.
    
    Uses a piece of the real data from the API to compare the results.

    test-jhu-data-small.csv was generated with 

    >>> start_day = date(2020, 1, 20)
    >>> end_day = date(2020, 5, 1)
    >>> df = pd.concat([ 
        covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027")
    ])
    >>> df.to_csv("test-jhu-data-small.csv")

    test-jhu-data-smaller.csv was generated with (just a start_day difference, to match with 7dav)

    >>> end_day = date(2020, 5, 1)
    >>> df = pd.concat([ 
        covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=date(2020, 2, 13), end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=date(2020, 2, 13), end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=date(2020, 2, 14), end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=date(2020, 2, 14), end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=date(2020, 2, 20), end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
        covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=date(2020, 2, 20), end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027")
    ])
    >>> df.to_csv("test-jhu-data-smaller.csv")
    """
    test_data_filename = "repos/delphi/delphi-epidata/testdata/acquisition/covidcast/test-jhu-data-smaller.csv"
    self._insert_csv(test_data_filename)

    meta_values = self.db.compute_covidcast_meta(jit=False)
    meta_values2 = self.db.compute_covidcast_meta(jit=True, parallel=False)

    # This doesn't work because they are not exactly equal.
    # assert meta_values == meta_values2
    # 1. We have a difference in the min_lag, because JIT computes the lag differently.
    # 2. We have a numerical difference, because the existing indicators don't seem to compute smooth-diffed entries correctly (see below).

    df1 = pd.read_csv(test_data_filename).query("signal == 'confirmed_cumulative_num' & geo_value == 'ca' & '2020-02-10' <= time_value <= '2020-02-26'")
    df2 = pd.read_csv(test_data_filename).query("signal == 'confirmed_7dav_incidence_num' & geo_value == 'ca' & '2020-02-10' <= time_value <= '2020-02-26'")
    df = pd.merge(
      df1.assign(smooth_diffed = df1.value.diff().rolling(7).mean())[["time_value", "smooth_diffed"]],
      df2[["time_value", "value"]],
      on = "time_value"
    )
    # This SHOULD be zero, but it's not.
    assert df.smooth_diffed.sub(df.value).abs().sum() > 0

    # Ignore these issues, we have a match on this dataset.
    out = [_dicts_equal(x, y, ignore_keys=["min_lag"], atol=1.5) for x, y in zip(meta_values, meta_values2)]
    assert all(out)

    # TODO: The parallelized version of the code is not written yet, but should be simple once we're confident in the non-parallel version.
    # meta_values3 = self.db.compute_covidcast_meta(jit=True, parallel=True)
    # assert meta_values == meta_values3

  def test_meta_values2(self):
    """This is an A/B test between the old meta compute approach and the new one which relies on an API call for JIT signals.

    It relies on synthetic data that attempts to be as realistic and as general as possible.
    """

    def get_rows_gen(df: pd.DataFrame, filter_nans: bool = False) -> Iterable[CovidcastRow]:
      for args in df.itertuples(index=False):
        if not filter_nans or (filter_nans and not any(map(pd.isna, args._asdict().values()))):
          yield CovidcastRow(**args._asdict())

    start_date = date(2022, 4, 1)
    end_date = date(2022, 6, 1)
    n = (end_date - start_date).days + 1

    # TODO: Build a more complex synthetic dataset here.
    cumulative_df = pd.DataFrame(
      {
        "source": ["jhu-csse"] * n,
        "signal": ["confirmed_cumulative_num"] * n,
        "time_value": pd.date_range(start_date, end_date),
        "issue": pd.date_range(start_date, end_date),
        "value": list(range(n)),
      }
    )
    incidence_df = cumulative_df.assign(
      signal="confirmed_incidence_num", value=cumulative_df.value.diff(), issue=[max(window) if window.size >= 2 else np.nan for window in cumulative_df.issue.rolling(2)]
    )
    smoothed_incidence_df = incidence_df.assign(
      signal="confirmed_7dav_incidence_num", value=incidence_df.value.rolling(7).mean(), issue=[max(window) if window.size >= 7 else np.nan for window in incidence_df.issue.rolling(7)]
    )

    self._insert_rows(get_rows_gen(cumulative_df, filter_nans=True))
    self._insert_rows(get_rows_gen(incidence_df, filter_nans=True))
    self._insert_rows(get_rows_gen(smoothed_incidence_df, filter_nans=True))

    meta_values = self.db.compute_covidcast_meta(jit=False)
    meta_values2 = self.db.compute_covidcast_meta(jit=True, parallel=False)

    out = [_dicts_equal(x, y, ignore_keys=["max_lag"]) for x, y in zip(meta_values, meta_values2)]

    assert meta_values == meta_values2
