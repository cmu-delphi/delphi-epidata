"""Integration tests for delphi_epidata.py."""

# standard library
import time
import json
from json import JSONDecodeError
from unittest.mock import MagicMock, patch

# first party
import pytest
from aiohttp.client_exceptions import ClientResponseError

# third party
import delphi.operations.secrets as secrets
from delphi.epidata.maintenance.covidcast_meta_cache_updater import main as update_covidcast_meta_cache
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase, CovidcastTestRow, FIPS, MSA
from delphi.epidata.client.delphi_epidata import Epidata
from delphi_utils import Nans

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'
# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value

def fake_epidata_endpoint(func):
  """This can be used as a decorator to enable a bogus Epidata endpoint to return 404 responses."""
  def wrapper(*args):
    Epidata.BASE_URL = 'http://delphi_web_epidata/fake_epidata'
    func(*args)
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata'
  return wrapper

class DelphiEpidataPythonClientTests(CovidcastBase):
  """Tests the Python client."""

  def localSetUp(self):
    """Perform per-test setup."""

    # reset the `covidcast_meta_cache` table (it should always have one row)
    self._db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata'
    Epidata.auth = ('epidata', 'key')
    Epidata.debug = False
    Epidata.sandbox = False

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

  @pytest.fixture(autouse=True)
  def capsys(self, capsys):
    """Hook capsys (stdout and stderr) into this test class."""

    self.capsys = capsys

  def test_covidcast(self):
    """Test that the covidcast endpoint returns expected data."""

    # insert placeholder data: three issues of one signal, one issue of another
    rows = [
      CovidcastTestRow.make_default_row(issue=2020_02_02 + i, value=i, lag=i)
      for i in range(3)
    ]
    row_latest_issue = rows[-1]
    rows.append(CovidcastTestRow.make_default_row(signal="sig2"))
    self._insert_rows(rows)

    with self.subTest(name='request two signals'):
      # fetch data
      response = Epidata.covidcast(
        **self.params_from_row(rows[0], signals=[rows[0].signal, rows[-1].signal])
      )

      expected = [
        row_latest_issue.as_api_row_dict(),
        rows[-1].as_api_row_dict()
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
          row_latest_issue.as_api_row_dict(ignore_fields=['signal']),
        ],
        rows[-1].signal: [
          rows[-1].as_api_row_dict(ignore_fields=['signal']),
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

      expected = [row_latest_issue.as_api_row_dict()]

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

      expected = [rows[1].as_api_row_dict()]

      # check result
      self.maxDiff=None
      self.assertEqual(response_1a, {
        'result': 1,
        'epidata': expected,
        'message': 'success',
      })

    with self.subTest(name='bad as-of date'):
      # fetch data, specifying as_of
      as_of_response = Epidata.covidcast(
        **self.params_from_row(rows[0], as_of="20230101-20230102")
      )
      self.assertEqual(as_of_response, {"epidata": [], "message": "not a valid date: 20230101-20230102", "result": -1})


    with self.subTest(name='request a range of issues'):
      # fetch data, specifying issue range, not lag
      response_2 = Epidata.covidcast(
        **self.params_from_row(rows[0], issues=Epidata.range(rows[0].issue, rows[1].issue))
      )

      expected = [
        rows[0].as_api_row_dict(),
        rows[1].as_api_row_dict()
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

      expected = [row_latest_issue.as_api_row_dict()]

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
      self.assertEqual(response_1, {'epidata': [], 'message': 'no results', 'result': -2})

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
      response = Epidata._request("")
      self.assertEqual(get.call_count, 2)
      self.assertEqual(response, mock_response.json())

    with self.subTest(name='test retry'):
      get.reset_mock()
      mock_response = MagicMock()
      mock_response.status_code = 200
      get.side_effect = [JSONDecodeError('Expecting value', "",  0),
                         JSONDecodeError('Expecting value', "",  0),
                         mock_response]
      response = Epidata._request("")
      self.assertEqual(get.call_count, 2)  # 2 from previous test + 2 from this one
      self.assertEqual(response,
                       {'result': 0, 'message': 'error: Expecting value: line 1 column 1 (char 0)'}
                       )

  @patch('requests.post')
  @patch('requests.get')
  def test_debug(self, get, post):
    """Test that in debug mode request params are correctly logged."""
    class MockResponse:
      def __init__(self, content, status_code):
          self.content = content
          self.status_code = status_code
      def raise_for_status(self): pass

    Epidata.debug = True

    try:
      with self.subTest(name='test multiple GET'):
        get.reset_mock()
        get.return_value = MockResponse(b'{"key": "value"}', 200)
        Epidata._request_with_retry("test_endpoint1", params={"key1": "value1"})
        Epidata._request_with_retry("test_endpoint2", params={"key2": "value2"})

        captured = self.capsys.readouterr()
        output = captured.err.splitlines()
        self.assertEqual(len(output), 4) # [request, response, request, response]
        self.assertIn("Sending GET request", output[0])
        self.assertIn("\'url\': \'http://delphi_web_epidata/epidata/test_endpoint1/\'", output[0])
        self.assertIn("\'params\': {\'key1\': \'value1\'}", output[0])
        self.assertIn("Received response", output[1])
        self.assertIn("\'status_code\': 200", output[1])
        self.assertIn("\'len\': 16", output[1])
        self.assertIn("Sending GET request", output[2])
        self.assertIn("\'url\': \'http://delphi_web_epidata/epidata/test_endpoint2/\'", output[2])
        self.assertIn("\'params\': {\'key2\': \'value2\'}", output[2])
        self.assertIn("Received response", output[3])
        self.assertIn("\'status_code\': 200", output[3])
        self.assertIn("\'len\': 16", output[3])

      with self.subTest(name='test GET and POST'):
        get.reset_mock()
        get.return_value = MockResponse(b'{"key": "value"}', 414)
        post.reset_mock()
        post.return_value = MockResponse(b'{"key": "value"}', 200)
        Epidata._request_with_retry("test_endpoint3", params={"key3": "value3"})

        captured = self.capsys.readouterr()
        output = captured.err.splitlines()
        self.assertEqual(len(output), 3) # [request, retry, response]
        self.assertIn("Sending GET request", output[0])
        self.assertIn("\'url\': \'http://delphi_web_epidata/epidata/test_endpoint3/\'", output[0])
        self.assertIn("\'params\': {\'key3\': \'value3\'}", output[0])
        self.assertIn("Received 414 response, retrying as POST request", output[1])
        self.assertIn("\'url\': \'http://delphi_web_epidata/epidata/test_endpoint3/\'", output[1])
        self.assertIn("\'params\': {\'key3\': \'value3\'}", output[1])
        self.assertIn("Received response", output[2])
        self.assertIn("\'status_code\': 200", output[2])
        self.assertIn("\'len\': 16", output[2])
    finally: # make sure this global is always reset
      Epidata.debug = False

  @patch('requests.post')
  @patch('requests.get')
  def test_sandbox(self, get, post):
    """Test that in debug + sandbox mode request params are correctly logged, but no queries are sent."""
    Epidata.debug = True
    Epidata.sandbox = True
    try:
      Epidata.covidcast('src', 'sig', 'day', 'county', 20200414, '01234')
      captured = self.capsys.readouterr()
      output = captured.err.splitlines()
      self.assertEqual(len(output), 1)
      self.assertIn("Sending GET request", output[0])
      self.assertIn("\'url\': \'http://delphi_web_epidata/epidata/covidcast/\'", output[0])
      get.assert_not_called()
      post.assert_not_called()
    finally: # make sure these globals are always reset
      Epidata.debug = False
      Epidata.sandbox = False

  @patch('requests.get')
  def test_version_check(self, get):
    """Test that the _version_check() function correctly logs a version discrepancy."""
    class MockJson:
      def __init__(self, content, status_code):
          self.content = content
          self.status_code = status_code
      def raise_for_status(self): pass
      def json(self): return json.loads(self.content)
    get.reset_mock()
    get.return_value = MockJson(b'{"info": {"version": "0.0.1"}}', 200)
    Epidata._version_check()
    captured = self.capsys.readouterr()
    output = captured.err.splitlines()
    self.assertEqual(len(output), 1)
    self.assertIn("Client version not up to date", output[0])
    self.assertIn("\'latest_version\': \'0.0.1\'", output[0])

  @patch('delphi.epidata.client.delphi_epidata.Epidata._version_check')
  def test_version_check_once(self, version_check):
    """Test that the _version_check() function is only called once on initial module import."""
    from delphi.epidata.client.delphi_epidata import Epidata
    version_check.assert_not_called()

  def test_geo_value(self):
    """test different variants of geo types: single, *, multi."""

    # insert placeholder data: three counties, three MSAs
    N = 3
    rows = [
      CovidcastTestRow.make_default_row(geo_type="county", geo_value=FIPS[i], value=i)
      for i in range(N)
    ] + [
      CovidcastTestRow.make_default_row(geo_type="msa", geo_value=MSA[i], value=i*10)
      for i in range(N)
    ]
    self._insert_rows(rows)

    counties = [
      rows[i].as_api_row_dict() for i in range(N)
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
    request = fetch([FIPS[0]])
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[0]])
    # test fetch a specific yet not existing region
    request = fetch('55555')
    self.assertEqual(request['message'], 'Invalid geo_value(s) 55555 for the requested geo_type county')
    # test fetch a multiple regions
    request = fetch([FIPS[0], FIPS[1]])
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[0], counties[1]])
    # test fetch a multiple regions in another variant
    request = fetch([FIPS[0], FIPS[2]])
    self.assertEqual(request['message'], 'success')
    self.assertEqual(request['epidata'], [counties[0], counties[2]])
    # test fetch a multiple regions but one is not existing
    request = fetch([FIPS[0], '55555'])
    self.assertEqual(request['message'], 'Invalid geo_value(s) 55555 for the requested geo_type county')
    # test fetch a multiple regions but specify no region
    request = fetch([])
    self.assertEqual(request['message'], 'geo_value is empty for the requested geo_type county!')
    # test fetch a region with no results
    request = fetch([FIPS[3]])
    self.assertEqual(request['message'], 'no results')

  def test_covidcast_meta(self):
    """Test that the covidcast_meta endpoint returns expected data."""

    DEFAULT_TIME_VALUE = 2020_02_02
    DEFAULT_ISSUE = 2020_02_02

    # insert placeholder data: three dates, three issues. values are:
    # 1st issue: 0 10 20
    # 2nd issue: 1 11 21
    # 3rd issue: 2 12 22
    rows = [
      CovidcastTestRow.make_default_row(
        time_value=DEFAULT_TIME_VALUE + t,
        issue=DEFAULT_ISSUE + i,
        value=t*10 + i
      )
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
      min_time=DEFAULT_TIME_VALUE,
      max_time=DEFAULT_TIME_VALUE + 2,
      num_locations=1,
      min_value=2.,
      mean_value=12.,
      max_value=22.,
      stdev_value=8.1649658, # population stdev, not sample, which is 10.
      max_issue=DEFAULT_ISSUE + 2,
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
      CovidcastTestRow.make_default_row(geo_type="county", geo_value=FIPS[i-1], value=i)
      for i in range(N)
    ] + [
      CovidcastTestRow.make_default_row(geo_type="msa", geo_value=MSA[i-1], value=i*10)
      for i in range(N)
    ]
    self._insert_rows(rows)

    test_output = Epidata.async_epidata([
      self.params_from_row(rows[0], source='covidcast'),
      self.params_from_row(rows[1], source='covidcast')
    ]*12, batch_size=10)
    responses = [i[0]["epidata"] for i in test_output]
    # check response is same as standard covidcast call (minus fields omitted by the api.php endpoint),
    # using 24 calls to test batch sizing
    ignore_fields = CovidcastTestRow._api_row_compatibility_ignore_fields
    self.assertEqual(
      responses,
      [
        [{k: row[k] for k in row.keys() - ignore_fields} for row in Epidata.covidcast(**self.params_from_row(rows[0]))["epidata"]],
        [{k: row[k] for k in row.keys() - ignore_fields} for row in Epidata.covidcast(**self.params_from_row(rows[1]))["epidata"]],
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
