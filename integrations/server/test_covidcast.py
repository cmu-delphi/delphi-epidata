"""Integration tests for the `covidcast` endpoint."""

# standard library
from typing import Callable
import unittest

# third party
import mysql.connector
import requests

# first party
from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase, CovidcastTestRow, FIPS, MSA
from delphi.epidata.client.delphi_epidata import Epidata

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

class CovidcastTests(CovidcastBase):
  """Tests the `covidcast` endpoint."""

  def localSetUp(self):
    """Perform per-test setup."""
    self._db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

  def request_based_on_row(self, row: CovidcastTestRow, **kwargs):
    params = self.params_from_row(row, endpoint='covidcast', **kwargs)
    Epidata.BASE_URL = BASE_URL
    response = Epidata.covidcast(**params) 

    return response

  def _insert_placeholder_set_one(self):
    row = CovidcastTestRow.make_default_row()
    self._insert_rows([row])
    return row

  def _insert_placeholder_set_two(self):
    rows = [
      CovidcastTestRow.make_default_row(geo_type='msa', geo_value=MSA[i-1], value=i*1., stderr=i*10., sample_size=i*100.)
      for i in [1, 2, 3]
    ] + [
      CovidcastTestRow.make_default_row(geo_type='fips', geo_value=FIPS[i-4], value=i*1., stderr=i*10., sample_size=i*100.)
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows

  def _insert_placeholder_set_three(self):
    rows = [
      CovidcastTestRow.make_default_row(time_value=2000_01_01+i, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03, lag=2-i)
      for i in [1, 2, 3]
    ] + [
      # time value intended to overlap with the time values above, with disjoint geo values
      CovidcastTestRow.make_default_row(geo_value=MSA[i-3], time_value=2000_01_01+i-3, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03, lag=5-i)
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows

  def _insert_placeholder_set_four(self):
    rows = [
      CovidcastTestRow.make_default_row(source='src1', signal=str(i)*5, value=i*1., stderr=i*10., sample_size=i*100.)
      for i in [1, 2, 3]
    ] + [
      # signal intended to overlap with the signal above
      CovidcastTestRow.make_default_row(source='src2', signal=str(i-3)*5, value=i*1., stderr=i*10., sample_size=i*100.)
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows

  def _insert_placeholder_set_five(self):
    rows = [
      CovidcastTestRow.make_default_row(time_value=2000_01_01, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03+i)
      for i in [1, 2, 3]
    ] + [
      # different time_values, same issues
      CovidcastTestRow.make_default_row(time_value=2000_01_01+i-3, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03+i-3)
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows 
  
  def _insert_placeholder_set_six(self):
    rows = [
      CovidcastTestRow.make_default_row(time_value=2000_01_01+i, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03)
      for i in [1, 2, 3, 4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows 

  def _insert_placeholder_set_seven(self):
    rows = [
      CovidcastTestRow.make_default_row(time_value=2000_01_01, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03+i)
      for i in [1, 2, 3, 4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows 

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # make the request
    response = self.request_based_on_row(row)

    expected = [row.as_api_compatibility_row_dict()]

    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })

  # TODO enable test again when the gunicorn issue https://github.com/benoitc/gunicorn/issues/2487 is resolved
  # def test_uri_too_long(self):
  # def test_uri_too_long(self):
  #   """Test that a long request yields a 414 with GET but works with POST."""

  #   # insert placeholder data
  #   self.cur.execute(f'''
  #    INSERT INTO
  #      `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
  #      `time_value`, `geo_value`, `value_updated_timestamp`, 
  #      `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
  #      `direction`, `issue`, `lag`, `is_latest_issue`, `missing_value`,
  #      `missing_stderr`,`missing_sample_size`) 
  #    VALUES
  #       (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
  #         123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1,
  #         {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
  #   ''')
  #   self.cnx.commit()

  #   # make the request with GET
  #   response = requests.get(BASE_URL, {
  #     'endpoint': 'covidcast',
  #     'data_source': 'src'*10000,
  #     'signal': 'sig',
  #     'time_type': 'day',
  #     'geo_type': 'county',
  #     'time_values': 20200414,
  #     'geo_value': '01234',
  #   })
  #   self.assertEqual(response.status_code, 414)

  #   # make request with POST
  #   response = requests.post(BASE_URL, {
  #     'endpoint': 'covidcast',
  #     'data_source': 'src'*10000,
  #     'signal': 'sig',
  #     'time_type': 'day',
  #     'geo_type': 'county',
  #     'time_values': 20200414,
  #     'geo_value': '01234',
  #   })

  #   self.assertEqual(response.status_code, 200)

  def test_csv_format(self):
    """Test generate csv data."""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # make the request
    # NB 'format' is a Python reserved word
    response = self.request_based_on_row(
      row,
      **{'format':'csv'}
    )

    # This is a hardcoded mess because of api.php.
    column_order = [
      "geo_value", "signal", "time_value", "direction", "issue", "lag", "missing_value",
      "missing_stderr", "missing_sample_size", "value", "stderr", "sample_size"
    ]
    expected = (
      row.as_api_compatibility_row_df()
         .assign(direction = None)
         .to_csv(columns=column_order, index=False)
    )
    
    # assert that the right data came back
    self.assertEqual(response, expected)

  def test_raw_json_format(self):
    """Test generate raw json data."""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # make the request
    response = self.request_based_on_row(row, **{'format':'json'})

    expected = [row.as_api_compatibility_row_dict()]

    # assert that the right data came back
    self.assertEqual(response, expected)

  def test_fields(self):
    """Test fields parameter"""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # limit fields
    response = self.request_based_on_row(row, **{"fields":"time_value,geo_value"})

    expected = row.as_api_compatibility_row_dict()
    expected_all = {
      'result': 1,
      'epidata': [{
        k: expected[k] for k in ['time_value', 'geo_value']
       }],
      'message': 'success',
    }

    # assert that the right data came back
    self.assertEqual(response, expected_all)

    # limit using invalid fields
    response = self.request_based_on_row(row, fields='time_value,geo_value,doesnt_exist')

    # assert that the right data came back (only valid fields)
    self.assertEqual(response, expected_all)


    # limit exclude fields: exclude all except time_value and geo_value
    response = self.request_based_on_row(row, fields=(
        '-value,-stderr,-sample_size,-direction,-issue,-lag,-signal,' +
        '-missing_value,-missing_stderr,-missing_sample_size'
    ))

    # assert that the right data came back
    self.assertEqual(response, expected_all)

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_two()
    expected = [row.as_api_compatibility_row_dict() for row in rows[:3]]
    # make the request
    response = self.request_based_on_row(rows[0], geo_value="*")

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })

  def test_time_values_wildcard(self):
    """Select all time_values with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_three()
    expected = [row.as_api_compatibility_row_dict() for row in rows[:3]]

    # make the request
    response = self.request_based_on_row(rows[0], time_values="*")

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })

  def test_time_values_inequality(self):
    """Select all time_values with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_six()
    expected = [row.as_api_compatibility_row_dict() for row in rows[:6]]

    def fetch(time_value):
      # make the request
      response = self.request_based_on_row(rows[0], time_values=time_value)
      return response
    self.maxDiff = None
    # test fetch time_value with <
    r = fetch('<20000104')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:2])
    # test fetch time_value with <=
    r = fetch('<=20000104')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:3])
    # test fetch time_value with >
    r = fetch('>20000104')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[3:6])
    # test fetch time_value with >=
    r = fetch('>=20000104')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[2:6])
    # test fetch multiple inequalities
    r = fetch('<20000104,>20000104')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:2] + expected[3:6])
    # test overlapped inequalities, pick the more extreme one
    r = fetch('<20000104,<20000105')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:3])
    # test fetch inequalities that has no results
    r = fetch('>20000107')
    self.assertEqual(r['message'], 'no results')
    # test fetch empty time_value
    r = fetch('')
    self.assertEqual(r['message'], 'missing parameter: need [time_type, time_values]')
    # test fetch invalid time_value
    r = fetch('>')
    self.assertEqual(r['message'], 'missing parameter: date after the inequality operator')
    # test if extra operators provided
    r = fetch('>>')
    self.assertEqual(r['message'], 'not a valid date: >')
    r = fetch('>>20000103')
    self.assertEqual(r['message'], 'not a valid date: >20000103')
    # test invalid operator
    r = fetch('#')
    self.assertEqual(r['message'], 'not a valid date: #')

  def test_issues_wildcard(self):
    """Select all issues with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_five()
    expected = [row.as_api_compatibility_row_dict() for row in rows[:3]]

    # make the request
    response = self.request_based_on_row(rows[0], issues="*")

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })

  def test_issues_inequality(self):
    """Select all time_values with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_seven()
    expected = [row.as_api_compatibility_row_dict() for row in rows[:6]]

    def fetch(issue):
      # make the request
      response = self.request_based_on_row(rows[0], issues=issue)
      return response

    # test fetch issues with <
    r = fetch('<20000106')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:2])
    # test fetch issues with <=
    r = fetch('<=20000106')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:3])
    # test fetch issues with >
    r = fetch('>20000106')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[3:])
    # test fetch issues with >=
    r = fetch('>=20000106')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[2:])
    # test fetch multiple inequalities
    r = fetch('<20000106,>20000106')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[:2] + expected[3:])
    # test overlapped inequalities, pick the more extreme one
    r = fetch('>20000107,>20000106')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[3:])
    # test fetch inequalities that has no results
    r = fetch('>20000109')
    self.assertEqual(r['message'], 'no results')
    # test fetch empty issues
    r = fetch('')
    self.assertEqual(r['message'], 'not a valid date: (empty)')
    # test fetch invalid issues
    r = fetch('>')
    self.assertEqual(r['message'], 'missing parameter: date after the inequality operator')
    # test if extra operators provided
    r = fetch('<>')
    self.assertEqual(r['message'], 'not a valid date: >')
    r = fetch('><20000106')
    self.assertEqual(r['message'], 'not a valid date: <20000106')
    # test invalid operator
    r = fetch('@')
    self.assertEqual(r['message'], 'not a valid date: @')

  def test_signal_wildcard(self):
    """Select all signals with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_four()
    expected_signals = [row.as_api_compatibility_row_dict() for row in rows[:3]]

    # make the request
    response = self.request_based_on_row(rows[0], signals="*")

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected_signals,
      'message': 'success',
    })

  def test_geo_value(self):
    """test whether geo values are valid for specific geo types"""

    # insert placeholder data
    rows = self._insert_placeholder_set_two()
    expected = [row.as_api_compatibility_row_dict() for row in rows[:3]]

    def fetch(geo_value):
      # make the request
      response = self.request_based_on_row(rows[0], geo_value=geo_value)

      return response

    # test fetch a specific region
    r = fetch(MSA[0])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[0:1])
    # test fetch a specific yet not existing region
    r = fetch('11111')
    self.assertEqual(r['message'], 'Invalid geo_value(s) 11111 for the requested geo_type msa')
    # test fetch multiple regions
    r = fetch(f'{MSA[0]},{MSA[1]}')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], expected[0:2])
    # test fetch multiple noncontiguous regions
    r = fetch(f'{MSA[0]},{MSA[2]}')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [expected[0], expected[2]])
    # test fetch multiple regions but one is not existing
    r = fetch(f'{MSA[0]},11111')
    self.assertEqual(r['message'], 'Invalid geo_value(s) 11111 for the requested geo_type msa')
    # test fetch empty region
    r = fetch('')
    self.assertEqual(r['message'], 'geo_value is empty for the requested geo_type msa!')
    # test a region that has no results
    r = fetch(MSA[3])
    self.assertEqual(r['message'], 'no results')

  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert placeholder data
    rows = self._insert_placeholder_set_three()
    expected_timeseries = [row.as_api_compatibility_row_dict() for row in rows[:3]]

    # make the request
    response = self.request_based_on_row(rows[0], time_values='20000101-20000105')

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected_timeseries,
      'message': 'success',
    })

  @unittest.skip("v4 now uses ON DUPLICATE KEY UPDATE which prevents this key collision. Consider moving this test to a database integration test which runs SQL without the ON DUPLICATE KEY UPDATE clause to verify constraints are set correctly.")
  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # fail to insert different placeholder data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
      self._insert_placeholder_set_one()

    # succeed to insert different placeholder data under a different time_type
    self._insert_placeholder_set_one(time_type='week')

  def test_nullable_columns(self):
    """Missing values should be surfaced as null."""

    row = CovidcastTestRow.make_default_row(
      stderr=None, sample_size=None,
      missing_stderr=Nans.OTHER.value, missing_sample_size=Nans.OTHER.value
    )
    self._insert_rows([row])

    # make the request
    response = self.request_based_on_row(row)
    expected = row.as_api_compatibility_row_dict()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [expected],
      'message': 'success',
    })

  def test_temporal_partitioning(self):
    """Request a signal that's available at multiple temporal resolutions."""

    # insert placeholder data
    rows = [
      CovidcastTestRow.make_default_row(time_type=tt)
      for tt in "hour day week month year".split()
    ]
    self._insert_rows(rows)

    # make the request
    response = self.request_based_on_row(rows[1], time_values="*")
    expected = [rows[1].as_api_compatibility_row_dict()]

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected,
      'message': 'success',
    })

  def test_date_formats(self):
    """Request a signal using different time formats."""

    # insert placeholder data
    rows = self._insert_placeholder_set_three()

    # make the request
    response = self.request_based_on_row(rows[0], time_values="20000102", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2)

    # make the request
    response = self.request_based_on_row(rows[0], time_values="2000-01-02", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2)

    # make the request
    response = self.request_based_on_row(rows[0], time_values="20000102,20000103", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2 * 2)

    # make the request
    response = self.request_based_on_row(rows[0], time_values="2000-01-02,2000-01-03", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2 * 2)

    # make the request
    response = self.request_based_on_row(rows[0], time_values="20000102-20000104", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2 * 3)

    # make the request
    response = self.request_based_on_row(rows[0], time_values="2000-01-02:2000-01-04", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2 * 3)
