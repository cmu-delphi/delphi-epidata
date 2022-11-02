"""Integration tests for delphi_epidata.py."""

# standard library
import unittest
import time
from unittest.mock import patch, MagicMock
from json import JSONDecodeError

# third party
from aiohttp.client_exceptions import ClientResponseError
import mysql.connector
import pytest

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_covidcast_meta_cache
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase
import delphi.operations.secrets as secrets

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'
AUTH = ('epidata', 'key')

def fake_epidata_endpoint(func):
  """This can be used as a decorator to enable a bogus Epidata endpoint to return 404 responses."""
  def wrapper(*args):
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/fake_api.php'
    func(*args)
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
    Epidata.auth = AUTH
  return wrapper

# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value

class DelphiEpidataPythonClientTests(CovidcastBase):
  """Tests the Python client."""

  def localSetUp(self):
    """Perform per-test setup."""

    # reset the `covidcast_meta_cache` table (it should always have one row)
    self._db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
    Epidata.auth = AUTH

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

  def test_covidcast(self):
    """Test that the covidcast endpoint returns expected data."""

    # insert placeholder data: three issues of one signal, one issue of another
    rows = [
      self._make_placeholder_row(issue=self.DEFAULT_ISSUE + i, value=i, lag=i)[0]
      for i in range(3)
    ]
    row_latest_issue = rows[-1]
    rows.append(
      self._make_placeholder_row(signal="sig2")[0]
    )
    self._insert_rows(rows)

    with self.subTest(name='request two signals'):
      # fetch data
      response = Epidata.covidcast(
        **self.params_from_row(rows[0], signals=[rows[0].signal, rows[-1].signal])
      )

      expected = [
        self.expected_from_row(row_latest_issue),
        self.expected_from_row(rows[-1])
      ]

      # check result
      self.assertEqual(response, {
        'result': 1,
        'epidata': expected,
        'message': 'success',
      })

    with self.subTest(name='request two signals with tree format'):
      # fetch data
      response = Epidata.covidcast(
        **self.params_from_row(rows[0], signals=[rows[0].signal, rows[-1].signal], format='tree')
      )

      expected = [{
        rows[0].signal: [
          self.expected_from_row(row_latest_issue, self.DEFAULT_MINUS + ['signal']),
        ],
        rows[-1].signal: [
          self.expected_from_row(rows[-1], self.DEFAULT_MINUS + ['signal']),
        ],
      }]

      # check result
      self.assertEqual(response, {
        'result': 1,
        'epidata': expected,
        'message': 'success',
      })

    with self.subTest(name='request most recent'):
      # fetch data, without specifying issue or lag
      response_1 = Epidata.covidcast(
        **self.params_from_row(rows[0])
      )

      expected = self.expected_from_row(row_latest_issue)

      # check result
      self.assertEqual(response_1, {
        'result': 1,
        'epidata': [expected],
        'message': 'success',
      })

    with self.subTest(name='request as-of a date'):
      # fetch data, specifying as_of
      response_1a = Epidata.covidcast(
        **self.params_from_row(rows[0], as_of=rows[1].issue)
      )

      expected = self.expected_from_row(rows[1])

      # check result
      self.maxDiff=None
      self.assertEqual(response_1a, {
        'result': 1,
        'epidata': [expected],
        'message': 'success',
      })

    with self.subTest(name='request a range of issues'):
      # fetch data, specifying issue range, not lag
      response_2 = Epidata.covidcast(
        **self.params_from_row(rows[0], issues=Epidata.range(rows[0].issue, rows[1].issue))
      )

      expected = [
        self.expected_from_row(rows[0]),
        self.expected_from_row(rows[1])
      ]

      # check result
      self.assertDictEqual(response_2, {
          'result': 1,
          'epidata': expected,
          'message': 'success',
      })

    with self.subTest(name='request at a given lag'):
      # fetch data, specifying lag, not issue range
      response_3 = Epidata.covidcast(
        **self.params_from_row(rows[0], lag=2)
      )

      expected = self.expected_from_row(row_latest_issue)

      # check result
      self.assertDictEqual(response_3, {
          'result': 1,
          'epidata': [expected],
          'message': 'success',
      })
    with self.subTest(name='long request'):
      # fetch data, without specifying issue or lag
      # TODO should also trigger a post but doesn't due to the 414 issue
      response_1 = Epidata.covidcast(
        **self.params_from_row(rows[0], signals='sig'*1000)
      )

      # check result
      self.assertEqual(response_1, {'message': 'no results', 'result': -2})

  @patch('requests.post')
  @patch('requests.get')
  def test_request_method(self, get, post):
    """Test that a GET request is default and POST is used if a 414 is returned."""
    with self.subTest(name='get request'):
      Epidata.covidcast('src', 'sig', 'day', 'county', 20200414, '01234')
      get.assert_called_once()
      post.assert_not_called()
    with self.subTest(name='post request'):
      get.reset_mock()
      mock_response = MagicMock()
      mock_response.status_code = 414
      get.return_value = mock_response
      Epidata.covidcast('src', 'sig', 'day', 'county', 20200414, '01234')
      get.assert_called_once()
      post.assert_called_once()

  @patch('requests.get')
  def test_retry_request(self, get):
    """Test that a GET request is default and POST is used if a 414 is returned."""
    with self.subTest(name='test successful retry'):
      mock_response = MagicMock()
      mock_response.status_code = 200
      get.side_effect = [JSONDecodeError('Expecting value', "",  0), mock_response]
      response = Epidata._request(None)
      self.assertEqual(get.call_count, 2)
      self.assertEqual(response, mock_response.json())

    with self.subTest(name='test retry'):
      get.reset_mock()
      mock_response = MagicMock()
      mock_response.status_code = 200
      get.side_effect = [JSONDecodeError('Expecting value', "",  0),
                         JSONDecodeError('Expecting value', "",  0),
                         mock_response]
      response = Epidata._request(None)
      self.assertEqual(get.call_count, 2)  # 2 from previous test + 2 from this one
      self.assertEqual(response,
                       {'result': 0, 'message': 'error: Expecting value: line 1 column 1 (char 0)'}
                       )

  def test_geo_value(self):
    """test different variants of geo types: single, *, multi."""

    # insert placeholder data: three counties, three MSAs
    N = 3
    rows = [
      self._make_placeholder_row(geo_type="county", geo_value=str(i)*5, value=i)[0]
      for i in range(N)
    ] + [
      self._make_placeholder_row(geo_type="msa", geo_value=str(i)*5, value=i*10)[0]
      for i in range(N)
    ]
    self._insert_rows(rows)

    counties = [
      self.expected_from_row(rows[i]) for i in range(N)
    ]

    def fetch(geo):
      return Epidata.covidcast(
        **self.params_from_row(rows[0], geo_value=geo)
      )

    # test fetch all
    r = fetch('*')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], counties)
    # test fetch a specific region
    r = fetch('11111')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[1]])
    # test fetch a specific yet not existing region
    r = fetch('55555')
    self.assertEqual(r['message'], 'no results')
    # test fetch a multiple regions
    r = fetch(['11111', '22222'])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[1], counties[2]])
    # test fetch a multiple regions in another variant
    r = fetch(['00000', '22222'])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[0], counties[2]])
    # test fetch a multiple regions but one is not existing
    r = fetch(['11111', '55555'])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[1]])
    # test fetch a multiple regions but specify no region
    r = fetch([])
    self.assertEqual(r['message'], 'no results')

  def test_covidcast_meta(self):
    """Test that the covidcast_meta endpoint returns expected data."""

    # insert placeholder data: three dates, three issues. values are:
    # 1st issue: 0 10 20
    # 2nd issue: 1 11 21
    # 3rd issue: 2 12 22
    rows = [
      self._make_placeholder_row(time_value=self.DEFAULT_TIME_VALUE + t, issue=self.DEFAULT_ISSUE + i, value=t*10 + i)[0]
      for i in range(3) for t in range(3)
    ]
    self._insert_rows(rows)

    # cache it
    update_covidcast_meta_cache(args=None)

    # fetch data
    response = Epidata.covidcast_meta()

    # make sure "last updated" time is recent:
    updated_time = response['epidata'][0]['last_update']
    t_diff = time.time() - updated_time
    self.assertGreater(t_diff, 0) # else it was in the future
    self.assertLess(t_diff, 5) # 5s should be long enough to pull the metadata, right??
    # remove "last updated" time so our comparison below works:
    del response['epidata'][0]['last_update']

    expected = dict(
      data_source=rows[0].source,
      signal=rows[0].signal,
      time_type=rows[0].time_type,
      geo_type=rows[0].geo_type,
      min_time=self.DEFAULT_TIME_VALUE,
      max_time=self.DEFAULT_TIME_VALUE + 2,
      num_locations=1,
      min_value=2.,
      mean_value=12.,
      max_value=22.,
      stdev_value=8.1649658, # population stdev, not sample, which is 10.
      max_issue=self.DEFAULT_ISSUE + 2,
      min_lag=0,
      max_lag=0, # we didn't set lag when inputting data
    )
    # check result
    self.maxDiff=None
    self.assertEqual(response, {
      'result': 1,
      'epidata': [expected],
      'message': 'success',
    })

  def test_async_epidata(self):
    # insert placeholder data: three counties, three MSAs
    N = 3
    rows = [
      self._make_placeholder_row(geo_type="county", geo_value=str(i)*5, value=i)[0]
      for i in range(N)
    ] + [
      self._make_placeholder_row(geo_type="msa", geo_value=str(i)*5, value=i*10)[0]
      for i in range(N)
    ]
    self._insert_rows(rows)

    test_output = Epidata.async_epidata([
      self.params_from_row(rows[0], source='covidcast'),
      self.params_from_row(rows[1], source='covidcast')
    ]*12, batch_size=10)
    responses = [i[0] for i in test_output]
    # check response is same as standard covidcast call, using 24 calls to test batch sizing
    self.assertEqual(
      responses,
      [
        Epidata.covidcast(**self.params_from_row(rows[0])),
        Epidata.covidcast(**self.params_from_row(rows[1])),
      ]*12
    )

  @fake_epidata_endpoint
  def test_async_epidata_fail(self):
    with pytest.raises(ClientResponseError, match="404, message='NOT FOUND'"):
      Epidata.async_epidata([
        {
          'source': 'covidcast',
          'data_source': 'src',
          'signals': 'sig',
          'time_type': 'day',
          'geo_type': 'county',
          'geo_value': '11111',
          'time_values': '20200414'
        }
      ])
