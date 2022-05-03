"""Integration tests for the `covidcast` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests

# first party
from delphi_utils import Nans

# use the local instance of the Epidata API
BASE_URL = 'http://delphi_web_epidata/epidata/api.php'


class CovidcastTests(unittest.TestCase):
  """Tests the `covidcast` endpoint."""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='covid')
    cur = cnx.cursor()

    # clear all tables
    cur.execute("truncate table signal_load")
    cur.execute("truncate table signal_history")
    cur.execute("truncate table signal_latest")
    cur.execute("truncate table geo_dim")
    cur.execute("truncate table signal_dim")
    # reset the `covidcast_meta_cache` table (it should always have one row)
    cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def _insert_dummy_data_set_one(self):
    self.cur.execute(f'''  INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`) VALUES (42, 'src', 'sig');  ''')
    self.cur.execute(f'''  INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`) VALUES (96, 'county', '01234');  ''')
    self.cur.execute(f'''
      INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
        `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
      VALUES (0, 42, 96,
        'day', 20200414, 123, 1.5, 2.5, 3.5, 20200414, 0,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING});
    ''')

  def _insert_dummy_data_set_two(self):
    self.cur.execute(f'''  INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`) VALUES (42, 'src', 'sig');  ''')
    self.cur.execute(f'''
      INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`) VALUES
          (101, 'county', '11111'),
          (202, 'county', '22222'),
          (303, 'county', '33333'),
          (1001, 'msa',   '11111'),
          (2002, 'msa',   '22222'),
          (3003, 'msa',   '33333');  ''')
    self.cur.execute(f'''
      INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
        `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
      VALUES
          (1, 42, 101, 'day', 20200414, 123, 10, 11, 12, 20200414, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (2, 42, 202, 'day', 20200414, 123, 20, 21, 22, 20200414, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (3, 42, 303, 'day', 20200414, 123, 30, 31, 32, 20200414, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (4, 42, 1001, 'day', 20200414, 123, 40, 41, 42, 20200414, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (5, 42, 2002, 'day', 20200414, 123, 50, 51, 52, 20200414, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (6, 42, 3003, 'day', 20200414, 123, 60, 61, 62, 20200414, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING});  ''')

  def _insert_dummy_data_set_three(self):
    self.cur.execute(f'''  INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`) VALUES (42, 'src', 'sig');  ''')
    self.cur.execute(f'''
      INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`) VALUES
          (101, 'county', '11111'),
          (202, 'county', '22222'),
          (303, 'county', '33333'),
          (444, 'county', '01234');  ''')
    self.cur.execute(f'''
      INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
        `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
      VALUES
          (1, 42, 444, 'day', 20200411, 123, 10, 11, 12, 20200413, 2, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (2, 42, 444, 'day', 20200412, 123, 20, 21, 22, 20200413, 1, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (3, 42, 444, 'day', 20200413, 123, 30, 31, 32, 20200413, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (4, 42, 101, 'day', 20200411, 123, 40, 41, 42, 20200413, 2, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (5, 42, 202, 'day', 20200412, 123, 50, 51, 52, 20200413, 1, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
          (6, 42, 303, 'day', 20200413, 123, 60, 61, 62, 20200413, 0, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING});  ''')

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert dummy data
    self._insert_dummy_data_set_one()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 1.5,
        'stderr': 2.5,
        'sample_size': 3.5,
        'direction': None,
        'issue': 20200414,
        'lag': 0,
        'signal': 'sig',
        'missing_value': Nans.NOT_MISSING,
        'missing_stderr': Nans.NOT_MISSING,
        'missing_sample_size': Nans.NOT_MISSING
       }],
      'message': 'success',
    })

  # TODO enable test again when the gunicorn issue https://github.com/benoitc/gunicorn/issues/2487 is resolved
  # def test_uri_too_long(self):
  # def test_uri_too_long(self):
  #   """Test that a long request yields a 414 with GET but works with POST."""

  #   # insert dummy data
  #   self.cur.execute(f'''
  #    INSERT INTO
  #      `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`, 
  #      `time_value`, `geo_value`, `value_updated_timestamp`, 
  #      `value`, `stderr`, `sample_size`, `direction_updated_timestamp`, 
  #      `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
  #      `missing_stderr`,`missing_sample_size`) 
  #    VALUES
  #       (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
  #         123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1, False,
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

    # insert dummy data
    self._insert_dummy_data_set_one()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
      'format': 'csv'
    })
    response.raise_for_status()
    response = response.text
    expected_response = (
      "geo_value,signal,time_value,direction,issue,lag,missing_value," +
      "missing_stderr,missing_sample_size,value,stderr,sample_size\n" +
      "01234,sig,20200414,,20200414,0,0,0,0,1.5,2.5,3.5\n"
    )

    # assert that the right data came back
    self.assertEqual(response, expected_response)

  def test_raw_json_format(self):
    """Test generate raw json data."""

    # insert dummy data
    self._insert_dummy_data_set_one()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
      'format': 'json'
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, [{
      'time_value': 20200414,
      'geo_value': '01234',
      'value': 1.5,
      'stderr': 2.5,
      'sample_size': 3.5,
      'direction': None,
      'issue': 20200414,
      'lag': 0,
      'signal': 'sig',
      'missing_value': Nans.NOT_MISSING,
      'missing_stderr': Nans.NOT_MISSING,
      'missing_sample_size': Nans.NOT_MISSING
    }])

  def test_fields(self):
    """Test to limit fields field"""

    # insert dummy data
    self._insert_dummy_data_set_one()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 1.5,
        'stderr': 2.5,
        'sample_size': 3.5,
        'direction': None,
        'issue': 20200414,
        'lag': 0,
        'signal': 'sig',
        'missing_value': Nans.NOT_MISSING,
        'missing_stderr': Nans.NOT_MISSING,
        'missing_sample_size': Nans.NOT_MISSING
       }],
      'message': 'success',
    })

    # limit fields
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
      'fields': 'time_value,geo_value'
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234'
       }],
      'message': 'success',
    })

    # limit invalid values
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
      'fields': 'time_value,geo_value,dummy'
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234'
       }],
      'message': 'success',
    })


    # limit exclude fields
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
      'fields': (
        '-value,-stderr,-sample_size,-direction,-issue,-lag,-signal,' +
        '-missing_value,-missing_stderr,-missing_sample_size'
      )
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234'
       }],
      'message': 'success',
    })

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert dummy data
    self._insert_dummy_data_set_two()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'time_value': 20200414,
          'geo_value': '11111',
          'value': 10,
          'stderr': 11,
          'sample_size': 12,
          'direction': None,
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
          'direction': None,
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
          'direction': None,
          'issue': 20200414,
          'lag': 0,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
        },
       ],
      'message': 'success',
    })

  def test_geo_value(self):
    """test different variants of geo types: single, *, multi."""

    # insert dummy data
    self._insert_dummy_data_set_two()
    self.cnx.commit()

    def fetch(geo_value):
      # make the request
      params = {
        'endpoint': 'covidcast',
        'data_source': 'src',
        'signal': 'sig',
        'time_type': 'day',
        'geo_type': 'county',
        'time_values': 20200414,
      }
      if isinstance(geo_value, list):
        params['geo_values'] = ','.join(geo_value)
      else:
        params['geo_value'] = geo_value
      response = requests.get(BASE_URL, params=params)
      response.raise_for_status()
      response = response.json()

      return response

    counties = [{
      'time_value': 20200414,
      'geo_value': '11111',
      'value': 10,
      'stderr': 11,
      'sample_size': 12,
      'direction': None,
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
      'direction': None,
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
      'direction': None,
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


  def test_location_timeline(self):
    """Select a timeline for a particular location."""

    # insert dummy data
    self._insert_dummy_data_set_three()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '20200411-20200413',
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [
        {
          'time_value': 20200411,
          'geo_value': '01234',
          'value': 10,
          'stderr': 11,
          'sample_size': 12,
          'direction': None,
          'issue': 20200413,
          'lag': 2,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
        }, {
          'time_value': 20200412,
          'geo_value': '01234',
          'value': 20,
          'stderr': 21,
          'sample_size': 22,
          'direction': None,
          'issue': 20200413,
          'lag': 1,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
        }, {
          'time_value': 20200413,
          'geo_value': '01234',
          'value': 30,
          'stderr': 31,
          'sample_size': 32,
          'direction': None,
          'issue': 20200413,
          'lag': 0,
          'signal': 'sig',
          'missing_value': Nans.NOT_MISSING,
          'missing_stderr': Nans.NOT_MISSING,
          'missing_sample_size': Nans.NOT_MISSING
        },
       ],
      'message': 'success',
    })

  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert dummy data
    self._insert_dummy_data_set_one()
    self.cnx.commit()

    # fail to insert different dummy data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
          self.cur.execute(f'''
            INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
              `time_type`, `time_value`, `value_updated_timestamp`,
              `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
            VALUES (1, 42, 96,
              'day', 20200414, 123, 991.5, 992.5, 993.5, 20200414, 0,
              {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING});
          ''')

    # succeed to insert different dummy data under a different time_type
    self.cur.execute(f'''
            INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
              `time_type`, `time_value`, `value_updated_timestamp`,
              `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
            VALUES (2, 42, 96,
              'score', 20200414, 123, 991.5, 992.5, 993.5, 20200415, 1,
              {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING});
    ''')

  def test_nullable_columns(self):
    """Missing values should be surfaced as null."""

    # insert dummy data
    self.cur.execute(f'''  INSERT INTO `signal_dim` (`signal_key_id`, `source`, `signal`) VALUES (42, 'src', 'sig');  ''')
    self.cur.execute(f'''  INSERT INTO `geo_dim` (`geo_key_id`, `geo_type`, `geo_value`) VALUES (96, 'county', '01234');  ''')
    self.cur.execute(f'''
      INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
        `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
      VALUES (0, 42, 96,
        'day', 20200414, 123, 0.123, NULL, NULL, 20200414, 0,
          {Nans.NOT_MISSING}, {Nans.OTHER}, {Nans.OTHER});
    ''')
    self.cnx.commit()

    # TODO: should this show that even if numeric values go into the fields, that if they are marked w/ a MISSING reason, they show up as NULL anyway?

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200414,
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()
    expected_response = {
      'result': 1,
      'epidata': [{
        'time_value': 20200414,
        'geo_value': '01234',
        'value': 0.123,
        'stderr': None,
        'sample_size': None,
        'direction': None,
        'issue': 20200414,
        'lag': 0,
        'signal': 'sig',
        'missing_value': Nans.NOT_MISSING,
        'missing_stderr': Nans.OTHER,
        'missing_sample_size': Nans.OTHER
       }],
      'message': 'success',
    }

    # assert that the right data came back
    self.assertEqual(response, expected_response)

  def test_temporal_partitioning(self):
    """Request a signal that's available at multiple temporal resolutions."""

    # insert dummy data
    self._insert_dummy_data_set_one() # this creates a record w/ temporal type of 'day'
    self.cur.execute(f'''
      INSERT INTO `signal_latest` (`signal_data_id`, `signal_key_id`, `geo_key_id`,
        `time_type`, `time_value`, `value_updated_timestamp`,
        `value`, `stderr`, `sample_size`, `issue`, `lag`, `missing_value`, `missing_stderr`,`missing_sample_size`)
      VALUES 
        (1, 42, 96,
        'hour', 2020041423, 123, 15, 25, 35, 20200414, 0,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (2, 42, 96,
        'week', 202016, 123, 115, 125, 135, 202016, 0,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (3, 42, 96,
        'month', 202004, 123, 215, 225, 235, 20200414, 0,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING}),
        (4, 42, 96,
        'year', 2020, 123, 315, 325, 335, 20200414, 0,
          {Nans.NOT_MISSING}, {Nans.NOT_MISSING}, {Nans.NOT_MISSING});
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'week',
      'geo_type': 'county',
      'time_values': '0-9999999999',
      'geo_value': '01234',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 202016,
        'geo_value': '01234',
        'value': 115,
        'stderr': 125,
        'sample_size': 135,
        'direction': None,
        'issue': 202016,
        'lag': 0,
        'signal': 'sig',
        'missing_value': Nans.NOT_MISSING,
        'missing_stderr': Nans.NOT_MISSING,
        'missing_sample_size': Nans.NOT_MISSING
       }],
      'message': 'success',
    })

  def test_date_formats(self):
    """Request a signal using different time formats."""

    # insert dummy data
    self._insert_dummy_data_set_three()
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '20200411',
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2)

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '2020-04-11',
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 2)

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '20200411,20200412',
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 4)

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '2020-04-11,2020-04-12',
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 4)

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '20200411-20200413',
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 6)

    # make the request
    response = requests.get(BASE_URL, params={
      'endpoint': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': '2020-04-11:2020-04-13',
      'geo_value': '*',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(len(response['epidata']), 6)
