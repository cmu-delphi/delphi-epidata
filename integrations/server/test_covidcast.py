"""Integration tests for the `covidcast` endpoint."""

# standard library
import json
import unittest

# third party
import mysql.connector
import requests

# first party
from delphi_utils import Nans
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'



class CovidcastTests(CovidcastBase):
  """Tests the `covidcast` endpoint."""

  def localSetUp(self):
    """Perform per-test setup."""
    self._db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

  def request_based_on_row(self, row, extract_response=lambda x: x.json(), **kwargs):
    params = self.params_from_row(row, endpoint='covidcast', **kwargs)
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    response = extract_response(response)

    expected = self.expected_from_row(row)

    return response, expected

  def _insert_placeholder_set_one(self):
    row, settings = self._make_placeholder_row()
    self._insert_rows([row])
    return row

  def _insert_placeholder_set_two(self):
    rows = [
      self._make_placeholder_row(geo_type='county', geo_value=str(i)*5, value=i*1., stderr=i*10., sample_size=i*100.)[0]
      for i in [1, 2, 3]
    ] + [
      # geo value intended to overlap with counties above
      self._make_placeholder_row(geo_type='msa', geo_value=str(i-3)*5, value=i*1., stderr=i*10., sample_size=i*100.)[0]
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows

  def _insert_placeholder_set_three(self):
    rows = [
      self._make_placeholder_row(geo_type='county', geo_value='11111', time_value=2000_01_01+i, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03, lag=2-i)[0]
      for i in [1, 2, 3]
    ] + [
      # time value intended to overlap with 11111 above, with disjoint geo values
      self._make_placeholder_row(geo_type='county', geo_value=str(i)*5, time_value=2000_01_01+i-3, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03, lag=5-i)[0]
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows

  def _insert_placeholder_set_four(self):
    rows = [
      self._make_placeholder_row(source='src1', signal=str(i)*5, value=i*1., stderr=i*10., sample_size=i*100.)[0]
      for i in [1, 2, 3]
    ] + [
      # signal intended to overlap with the signal above
      self._make_placeholder_row(source='src2', signal=str(i-3)*5, value=i*1., stderr=i*10., sample_size=i*100.)[0]
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows

  def _insert_placeholder_set_five(self):
    rows = [
      self._make_placeholder_row(time_value=2000_01_01, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03+i)[0]
      for i in [1, 2, 3]
    ] + [
      # issue intended to overlap with the issue above
      self._make_placeholder_row(time_value=2000_01_01+i-3, value=i*1., stderr=i*10., sample_size=i*100., issue=2000_01_03+i-3)[0]
      for i in [4, 5, 6]
    ]
    self._insert_rows(rows)
    return rows 

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # make the request
    response, expected = self.request_based_on_row(row)
    self.assertEqual(response, {
      'result': 1,
      'epidata': [expected],
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
    response, _ = self.request_based_on_row(
      row,
      extract_response=lambda resp: resp.text,
      **{'format':'csv'}
    )
    expected_response = (
      "geo_value,signal,time_value,direction,issue,lag,missing_value," +
      "missing_stderr,missing_sample_size,value,stderr,sample_size\n" +
      ",".join("" if x is None else str(x) for x in [
        row.geo_value,
        row.signal,
        row.time_value,
        row.direction,
        row.issue,
        row.lag,
        row.missing_value,
        row.missing_stderr,
        row.missing_sample_size,
        row.value,
        row.stderr,
        row.sample_size
      ]) + "\n"
    )

    # assert that the right data came back
    self.assertEqual(response, expected_response)

  def test_raw_json_format(self):
    """Test generate raw json data."""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # make the request
    response, expected = self.request_based_on_row(row, **{'format':'json'})

    # assert that the right data came back
    self.assertEqual(response, [expected])

  def test_fields(self):
    """Test fields parameter"""

    # insert placeholder data
    row = self._insert_placeholder_set_one()

    # limit fields
    response, expected = self.request_based_on_row(row, fields='time_value,geo_value')
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
    response, _ = self.request_based_on_row(row, fields='time_value,geo_value,doesnt_exist')

    # assert that the right data came back (only valid fields)
    self.assertEqual(response, expected_all)


    # limit exclude fields: exclude all except time_value and geo_value

    response, _ = self.request_based_on_row(row, fields=(
        '-value,-stderr,-sample_size,-direction,-issue,-lag,-signal,' +
        '-missing_value,-missing_stderr,-missing_sample_size'
    ))

    # assert that the right data came back
    self.assertEqual(response, expected_all)

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_two()
    expected_counties = [
      self.expected_from_row(r) for r in rows[:3]
    ]

    # make the request
    response, _ = self.request_based_on_row(rows[0], geo_value="*")

    self.maxDiff = None
    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected_counties,
      'message': 'success',
    })

  def test_time_values_wildcard(self):
    """Select all time_values with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_three()
    expected_time_values = [
      self.expected_from_row(r) for r in rows[:3]
    ]

    # make the request
    response, _ = self.request_based_on_row(rows[0], time_values="*")

    self.maxDiff = None
    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected_time_values,
      'message': 'success',
    })

  def test_issues_wildcard(self):
    """Select all issues with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_five()
    expected_issues = [
      self.expected_from_row(r) for r in rows[:3]
    ]

    # make the request
    response, _ = self.request_based_on_row(rows[0], issues="*")

    self.maxDiff = None
    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected_issues,
      'message': 'success',
    })

  def test_signal_wildcard(self):
    """Select all signals with a wildcard query."""

    # insert placeholder data
    rows = self._insert_placeholder_set_four()
    expected_signals = [
      self.expected_from_row(r) for r in rows[:3]
    ]

    # make the request
    response, _ = self.request_based_on_row(rows[0], signals="*")

    self.maxDiff = None
    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': expected_signals,
      'message': 'success',
    })

  def test_geo_value(self):
    """test different variants of geo types: single, *, multi."""

    # insert placeholder data
    rows = self._insert_placeholder_set_two()
    expected_counties = [
      self.expected_from_row(r) for r in rows[:3]
    ]

    def fetch(geo_value):
      # make the request
      response, _ = self.request_based_on_row(rows[0], geo_value=geo_value)

      return response

    # test fetch a specific region
    r = fetch('11111')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [expected_counties[0]])
    # test fetch a specific yet not existing region
    r = fetch('55555')
    self.assertEqual(r['message'], 'no results')
    # test fetch multiple regions
    r = fetch('11111,22222')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [expected_counties[0], expected_counties[1]])
    # test fetch multiple noncontiguous regions
    r = fetch('11111,33333')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [expected_counties[0], expected_counties[2]])
    # test fetch multiple regions but one is not existing
    r = fetch('11111,55555')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [expected_counties[0]])
    # test fetch empty region
    r = fetch('')
    self.assertEqual(r['message'], 'no results')

  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert placeholder data
    rows = self._insert_placeholder_set_three()
    expected_timeseries = [
      self.expected_from_row(r) for r in rows[:3]
    ]

    # make the request
    response, _ = self.request_based_on_row(rows[0], time_values='20000101-20000105')

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

    row, _ = self._make_placeholder_row(
      stderr=None, sample_size=None,
      missing_stderr=Nans.OTHER.value, missing_sample_size=Nans.OTHER.value
    )
    self._insert_rows([row])

    # make the request
    response, expected = self.request_based_on_row(row)
    expected.update(stderr=None, sample_size=None)

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
      self._make_placeholder_row(time_type=tt)[0]
      for tt in "hour day week month year".split()
    ]
    self._insert_rows(rows)

    # make the request
    response, expected = self.request_based_on_row(rows[1], time_values="0-99999999")

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [expected],
      'message': 'success',
    })

  def test_date_formats(self):
    """Request a signal using different time formats."""

    # insert placeholder data
    rows = self._insert_placeholder_set_three()

    # make the request
    response, expected = self.request_based_on_row(rows[0], time_values="20000102", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2)

    # make the request
    response, expected = self.request_based_on_row(rows[0], time_values="2000-01-02", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2)

    # make the request
    response, expected = self.request_based_on_row(rows[0], time_values="20000102,20000103", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 4)

    # make the request
    response, expected = self.request_based_on_row(rows[0], time_values="2000-01-02,2000-01-03", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 4)

    # make the request
    response, expected = self.request_based_on_row(rows[0], time_values="20000102-20000104", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 6)

    # make the request
    response, expected = self.request_based_on_row(rows[0], time_values="2000-01-02:2000-01-04", geo_value="*")

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 6)
