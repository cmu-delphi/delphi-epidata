"""Integration tests for delphi_epidata.py."""

# standard library
import time
from json import JSONDecodeError
from unittest.mock import MagicMock, patch
import unittest

# first party
import pytest
from aiohttp.client_exceptions import ClientResponseError

# third party
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_covidcast_meta_cache
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase
from delphi.epidata.client.delphi_epidata import Epidata
from delphi_utils import Nans


# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'
# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value
IGNORE_FIELDS = ["id", "direction_updated_timestamp", "value_updated_timestamp", "source", "time_type", "geo_type"]

def fake_epidata_endpoint(func):
  """This can be used as a decorator to enable a bogus Epidata endpoint to return 404 responses."""
  def wrapper(*args):
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/fake_api.php'
    func(*args)
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
  return wrapper

class DelphiEpidataPythonClientTests(CovidcastBase):
  """Tests the Python client."""

  def localSetUp(self):
    """Perform per-test setup."""

    # reset the `covidcast_meta_cache` table (it should always have one row)
    self._db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

  @unittest.skip
  def test_covidcast(self):
    """Test that the covidcast endpoint returns expected data."""

    # insert placeholder data: three issues of one signal, one issue of another
    rows = [
      CovidcastRow(issue=20200202 + i, value=i, lag=i)
      for i in range(3)
    ]
    row_latest_issue = rows[-1]
    rows.append(
      CovidcastRow(signal="sig2")
    )
    self._insert_rows(rows)

    with self.subTest(name='request two signals'):
      # fetch data
      response = Epidata.covidcast(
        **self.params_from_row(rows[0], signals=[rows[0].signal, rows[-1].signal])
      )

      expected = [
        row_latest_issue.as_dict(ignore_fields=IGNORE_FIELDS),
        rows[-1].as_dict(ignore_fields=IGNORE_FIELDS)
      ]

      self.assertEqual(response['epidata'], expected)
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
          row_latest_issue.as_dict(ignore_fields=IGNORE_FIELDS + ['signal']),
        ],
        rows[-1].signal: [
          rows[-1].as_dict(ignore_fields=IGNORE_FIELDS + ['signal']),
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

      expected = [row_latest_issue.as_dict(ignore_fields=IGNORE_FIELDS)]

      # check result
      self.assertEqual(response_1, {
        'result': 1,
        'epidata': expected,
        'message': 'success',
      })

    with self.subTest(name='request as-of a date'):
      # fetch data, specifying as_of
      response_1a = Epidata.covidcast(
        **self.params_from_row(rows[0], as_of=rows[1].issue)
      )

      expected = [rows[1].as_dict(ignore_fields=IGNORE_FIELDS)]

      # check result
      self.maxDiff=None
      self.assertEqual(response_1a, {
        'result': 1,
        'epidata': expected,
        'message': 'success',
      })

    with self.subTest(name='request a range of issues'):
      # fetch data, specifying issue range, not lag
      response_2 = Epidata.covidcast(
        **self.params_from_row(rows[0], issues=Epidata.range(rows[0].issue, rows[1].issue))
      )

      expected = [
        rows[0].as_dict(ignore_fields=IGNORE_FIELDS),
        rows[1].as_dict(ignore_fields=IGNORE_FIELDS)
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

      expected = [row_latest_issue.as_dict(ignore_fields=IGNORE_FIELDS)]

      # check result
      self.assertDictEqual(response_3, {
          'result': 1,
          'epidata': expected,
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
      CovidcastRow(geo_type="county", geo_value=str(i)*5, value=i)
      for i in range(N)
    ] + [
      CovidcastRow(geo_type="msa", geo_value=str(i)*5, value=i*10)
      for i in range(N)
    ]
    self._insert_rows(rows)

    counties = [
      rows[i].as_dict(ignore_fields=IGNORE_FIELDS) for i in range(N)
    ]

    def fetch(geo):
      return Epidata.covidcast(
        **self.params_from_row(rows[0], geo_value=geo)
      )

    # test fetch all
    request = fetch('*')
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], counties)
    # test fetch a specific region
    request = fetch('11111')
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[1]])
    # test fetch a specific yet not existing region
    request = fetch('55555')
    self.assertEqual(request['message'], 'no results')
    # test fetch a multiple regions
    request = fetch(['11111', '22222'])
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[1], counties[2]])
    # test fetch a multiple regions in another variant
    request = fetch(['00000', '22222'])
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[0], counties[2]])
    # test fetch a multiple regions but one is not existing
    request = fetch(['11111', '55555'])
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[1]])
    # test fetch a multiple regions but specify no region
    request = fetch([])
    self.assertEqual(request['message'], 'no results')

  def test_covidcast_meta(self):
    """Test that the covidcast_meta endpoint returns expected data."""

    # insert placeholder data: three dates, three issues. values are:
    # 1st issue: 0 10 20
    # 2nd issue: 1 11 21
    # 3rd issue: 2 12 22
    rows = [
      CovidcastRow(time_value=2020_02_02 + t, issue=2020_02_02 + i, value=t*10 + i)
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
      min_time=2020_02_02,
      max_time=2020_02_02 + 2,
      num_locations=1,
      min_value=2.,
      mean_value=12.,
      max_value=22.,
      stdev_value=8.1649658, # population stdev, not sample, which is 10.
      max_issue=2020_02_02 + 2,
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
      CovidcastRow(geo_type="county", geo_value=str(i)*5, value=i)
      for i in range(N)
    ] + [
      CovidcastRow(geo_type="msa", geo_value=str(i)*5, value=i*10)
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
