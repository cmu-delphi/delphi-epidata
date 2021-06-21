"""Integration tests for delphi_epidata.py."""

# standard library
import unittest
from unittest.mock import patch, MagicMock
from json import JSONDecodeError

# third party
from aiohttp.client_exceptions import ClientResponseError
import mysql.connector
import pytest

# first party
from delphi_utils import Nans
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_covidcast_meta_cache
import delphi.operations.secrets as secrets

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'

def fake_epidata_endpoint(func):
  """This can be used as a decorator to enable a bogus Epidata endpoint to return 404 responses."""
  def wrapper(*args):
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/fake_api.php'
    func(*args)
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'
  return wrapper


class DelphiEpidataPythonClientTests(unittest.TestCase):
  """Tests the Python client."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear relevant tables
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast')
    cur.execute('truncate table covidcast_nowcast')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_covidcast(self):
    """Test that the covidcast endpoint returns expected data."""

    # insert dummy data
    self.cur.execute(f'''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 0, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig2', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          456, 5.5, 1.2, 10.5, 789, 0, 20200415, 1, 0, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          345, 6.5, 2.2, 11.5, 678, 0, 20200416, 2, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
    ''')
    self.cnx.commit()

    with self.subTest(name='request two signals'):
      # fetch data
      response = Epidata.covidcast(
          'src', ['sig', 'sig2'], 'day', 'county', 20200414, '01234')

      # check result
      self.assertEqual(response, {
        'result': 1,
        'epidata': [{
          'time_value': 20200414,
          'geo_value': '01234',
          'value': 6.5,
          'stderr': 2.2,
          'sample_size': 11.5,
          'direction': 0,
          'issue': 20200416,
          'lag': 2,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
        }, {
          'time_value': 20200414,
          'geo_value': '01234',
          'value': 1.5,
          'stderr': 2.5,
          'sample_size': 3.5,
          'direction': 4,
          'issue': 20200414,
          'lag': 0,
          'signal': 'sig2',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
        }],
        'message': 'success',
      })

    with self.subTest(name='request two signals with tree format'):
      # fetch data
      response = Epidata.covidcast(
          'src', ['sig', 'sig2'], 'day', 'county', 20200414, '01234',
          format='tree')

      # check result
      self.assertEqual(response, {
        'result': 1,
        'epidata': [{
          'sig': [{
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 6.5,
            'stderr': 2.2,
            'sample_size': 11.5,
            'direction': 0,
            'issue': 20200416,
            'lag': 2,
            'missing_value': Nans.NOT_MISSING,
            'missing_stderr': Nans.NOT_MISSING,
            'missing_sample_size': Nans.NOT_MISSING
          }],
          'sig2': [{
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 1.5,
            'stderr': 2.5,
            'sample_size': 3.5,
            'direction': 4,
            'issue': 20200414,
            'lag': 0,
            'missing_value': Nans.NOT_MISSING,
            'missing_stderr': Nans.NOT_MISSING,
            'missing_sample_size': Nans.NOT_MISSING
          }],
        }],
        'message': 'success',
      })

    with self.subTest(name='request most recent'):
      # fetch data, without specifying issue or lag
      response_1 = Epidata.covidcast(
          'src', 'sig', 'day', 'county', 20200414, '01234')

      # check result
      self.assertEqual(response_1, {
        'result': 1,
        'epidata': [{
          'time_value': 20200414,
          'geo_value': '01234',
          'value': 6.5,
          'stderr': 2.2,
          'sample_size': 11.5,
          'direction': 0,
          'issue': 20200416,
          'lag': 2,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
         }],
        'message': 'success',
      })

    with self.subTest(name='request as-of a date'):
      # fetch data, specifying as_of
      response_1a = Epidata.covidcast(
          'src', 'sig', 'day', 'county', 20200414, '01234',
          as_of=20200415)

      # check result
      self.assertEqual(response_1a, {
        'result': 1,
        'epidata': [{
          'time_value': 20200414,
          'geo_value': '01234',
          'value': 5.5,
          'stderr': 1.2,
          'sample_size': 10.5,
          'direction': 0,
          'issue': 20200415,
          'lag': 1,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
         }],
        'message': 'success',
      })

    with self.subTest(name='request a range of issues'):
      # fetch data, specifying issue range, not lag
      response_2 = Epidata.covidcast(
          'src', 'sig', 'day', 'county', 20200414, '01234',
          issues=Epidata.range(20200414, 20200415))

      # check result
      self.assertDictEqual(response_2, {
          'result': 1,
          'epidata': [{
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 1.5,
            'stderr': 2.5,
            'sample_size': 3.5,
            'direction': 4,
            'issue': 20200414,
            'lag': 0,
            'signal': 'sig',
            'missing_value': Nans.NOT_MISSING,
            'missing_stderr': Nans.NOT_MISSING,
            'missing_sample_size': Nans.NOT_MISSING
          }, {
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 5.5,
            'stderr': 1.2,
            'sample_size': 10.5,
            'direction': 0,
            'issue': 20200415,
            'lag': 1,
            'signal': 'sig',
            'missing_value': Nans.NOT_MISSING,
            'missing_stderr': Nans.NOT_MISSING,
            'missing_sample_size': Nans.NOT_MISSING
          }],
          'message': 'success',
      })

    with self.subTest(name='request at a given lag'):
      # fetch data, specifying lag, not issue range
      response_3 = Epidata.covidcast(
          'src', 'sig', 'day', 'county', 20200414, '01234',
          lag=2)

      # check result
      self.assertDictEqual(response_3, {
          'result': 1,
          'epidata': [{
            'time_value': 20200414,
            'geo_value': '01234',
            'value': 6.5,
            'stderr': 2.2,
            'sample_size': 11.5,
            'direction': 0,
            'issue': 20200416,
            'lag': 2,
            'signal': 'sig',
            'missing_value': Nans.NOT_MISSING,
            'missing_stderr': Nans.NOT_MISSING,
            'missing_sample_size': Nans.NOT_MISSING
          }],
          'message': 'success',
      })
    with self.subTest(name='long request'):
      # fetch data, without specifying issue or lag
      # TODO should also trigger a post but doesn't due to the 414 issue
      response_1 = Epidata.covidcast(
          'src', 'sig'*1000, 'day', 'county', 20200414, '01234')

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

    # insert dummy data
    self.cur.execute(f'''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, 'src', 'sig', 'day', 'county', 20200414, '11111',
          123, 10, 11, 12, 456, 13, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '22222',
          123, 20, 21, 22, 456, 23, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '33333',
          123, 30, 31, 32, 456, 33, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '11111',
          123, 40, 41, 42, 456, 43, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '22222',
          123, 50, 51, 52, 456, 53, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '33333',
          123, 60, 61, 62, 456, 634, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
    ''')
    self.cnx.commit()

    def fetch(geo_value):
      # make the request
      response = Epidata.covidcast(
        'src', 'sig', 'day', 'county', 20200414, geo_value)
      return response

    counties = [{
      'time_value': 20200414,
      'geo_value': '11111',
      'value': 10,
      'stderr': 11,
      'sample_size': 12,
      'direction': 13,
      'issue': 20200414,
      'lag': 0,
      'signal': 'sig',
      'missing_value': Nans.NOT_MISSING,
      'missing_stderr': Nans.NOT_MISSING,
      'missing_sample_size': Nans.NOT_MISSING
    }, {
      'time_value': 20200414,
      'geo_value': '22222',
      'value': 20,
      'stderr': 21,
      'sample_size': 22,
      'direction': 23,
      'issue': 20200414,
      'lag': 0,
      'signal': 'sig',
      'missing_value': Nans.NOT_MISSING,
      'missing_stderr': Nans.NOT_MISSING,
      'missing_sample_size': Nans.NOT_MISSING
    }, {
      'time_value': 20200414,
      'geo_value': '33333',
      'value': 30,
      'stderr': 31,
      'sample_size': 32,
      'direction': 33,
      'issue': 20200414,
      'lag': 0,
      'signal': 'sig',
      'missing_value': Nans.NOT_MISSING,
      'missing_stderr': Nans.NOT_MISSING,
      'missing_sample_size': Nans.NOT_MISSING
    }]

    # test fetch all
    r = fetch('*')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], counties)
    # test fetch a specific region
    r = fetch('11111')
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[0]])
    # test fetch a specific yet not existing region
    r = fetch('55555')
    self.assertEqual(r['message'], 'no results')
    # test fetch a multiple regions
    r = fetch(['11111', '22222'])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[0], counties[1]])
    # test fetch a multiple regions in another variant
    r = fetch(['11111', '33333'])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[0], counties[2]])
    # test fetch a multiple regions but one is not existing
    r = fetch(['11111', '55555'])
    self.assertEqual(r['message'], 'success')
    self.assertEqual(r['epidata'], [counties[0]])
    # test fetch a multiple regions but specify no region
    r = fetch([])
    self.assertEqual(r['message'], 'no results')

  def test_covidcast_meta(self):
    """Test that the covidcast_meta endpoint returns expected data."""

    # insert dummy data
    self.cur.execute(f'''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 0, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          345, 6.0, 2.2, 11.5, 678, 0, 20200416, 2, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          345, 6.0, 2.2, 11.5, 678, 0, 20200410, 2, 0, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200415, '01234',
          345, 7.0, 2.0, 12.5, 678, 0, 20200416, 1, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
    ''')
    self.cnx.commit()

    # cache it
    update_covidcast_meta_cache(args=None)

    # fetch data
    response = Epidata.covidcast_meta()

    # check result
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'data_source': 'src',
        'signal': 'sig',
        'time_type': 'day',
        'geo_type': 'county',
        'min_time': 20200414,
        'max_time': 20200415,
        'num_locations': 1,
        'min_value': 6.0,
        'max_value': 7.0,
        'mean_value': 6.5,
        'stdev_value': 0.5,
        'last_update': 345,
        'max_issue': 20200416,
        'min_issue': 20200410,
        'min_lag': 1,
        'max_lag': 2,
       }],
      'message': 'success',
    })


  def test_covidcast_nowcast(self):
    """Test that the covidcast_nowcast endpoint returns expected data."""

    # insert dummy data
    self.cur.execute(f'''insert into covidcast_nowcast values
      (0, 'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 3.5, 20200101, 2),
      (0, 'src', 'sig2', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 2.5, 20200101, 2),
      (0, 'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 1.5, 20200102, 2)''')
    self.cnx.commit()

    # fetch data
    response = Epidata.covidcast_nowcast(
      'src', ['sig1', 'sig2'], 'sensor', 'day', 'county', 20200101, '01001')

    # request two signals
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 1.5,
        'issue': 20200102,
        'lag': 2,
        'signal': 'sig1',
      }, {
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 2.5,
        'issue': 20200101,
        'lag': 2,
        'signal': 'sig2',
      }],
      'message': 'success',
    })

    # request range of issues
    response = Epidata.covidcast_nowcast(
      'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001',
      issues=Epidata.range(20200101, 20200102))

    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 3.5,
        'issue': 20200101,
        'lag': 2,
        'signal': 'sig1',
      }, {
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 1.5,
        'issue': 20200102,
        'lag': 2,
        'signal': 'sig1',
      }],
      'message': 'success',
    })

    # request as_of
    response = Epidata.covidcast_nowcast(
      'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001',
      as_of=20200101)

    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 3.5,
        'issue': 20200101,
        'lag': 2,
        'signal': 'sig1',
      }],
      'message': 'success',
    })

    # request unavailable data
    response = Epidata.covidcast_nowcast(
      'src', 'sig1', 'sensor', 'day', 'county', 22222222, '01001')

    self.assertEqual(response, {'result': -2, 'message': 'no results'})

  def test_async_epidata(self):
    # insert dummy data
    self.cur.execute(f'''
      INSERT INTO
        `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
	      `time_value`, `geo_value`, `value_updated_timestamp`, 
        `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
        `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
        `missing_stderr`,`missing_sample_size`) 
      VALUES
        (0, 'src', 'sig', 'day', 'county', 20200414, '11111',
          123, 10, 11, 12, 456, 13, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '22222',
          123, 20, 21, 22, 456, 23, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'county', 20200414, '33333',
          123, 30, 31, 32, 456, 33, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '11111',
          123, 40, 41, 42, 456, 43, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '22222',
          123, 50, 51, 52, 456, 53, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '33333',
          123, 60, 61, 62, 456, 634, 20200414, 0, 1, False,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING})
    ''')
    self.cnx.commit()
    test_output = Epidata.async_epidata([
      {
        'source': 'covidcast',
        'data_source': 'src',
        'signals': 'sig',
        'time_type': 'day',
        'geo_type': 'county',
        'geo_value': '11111',
        'time_values': '20200414'
      },
      {
        'source': 'covidcast',
        'data_source': 'src',
        'signals': 'sig',
        'time_type': 'day',
        'geo_type': 'county',
        'geo_value': '00000',
        'time_values': '20200414'
      }
    ]*12, batch_size=10)
    responses = [i[0] for i in test_output]
    # check response is same as standard covidcast call, using 24 calls to test batch sizing
    self.assertEqual(responses,
                     [Epidata.covidcast('src', 'sig', 'day', 'county', 20200414, '11111'),
                      Epidata.covidcast('src', 'sig', 'day', 'county', 20200414, '00000')]*12
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