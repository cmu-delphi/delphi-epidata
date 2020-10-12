"""Integration tests for the `covidcast` endpoint."""

# standard library
import unittest

# third party
import mysql.connector
import requests


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
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
        'direction': 4,
        'issue': 20200414,
        'lag': 0,
        'signal': 'sig',
       }],
      'message': 'success',
    })


  def test_csv_format(self):
    """Test generate csv data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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

    # assert that the right data came back
    self.assertEqual(response,
"""geo_value,signal,time_value,direction,issue,lag,value,stderr,sample_size
01234,sig,20200414,4,20200414,0,1.5,2.5,3.5
""")

  def test_raw_json_format(self):
    """Test generate raw json data."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
      'direction': 4,
      'issue': 20200414,
      'lag': 0,
      'signal': 'sig',
    }])

  def test_fields(self):
    """Test to limit fields field"""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 1.5, 2.5, 3.5, 456, 4, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
        'direction': 4,
        'issue': 20200414,
        'lag': 0,
        'signal': 'sig'
       }],
      'message': 'success',
    })

    # limit fields
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
      'source': 'covidcast',
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

  def test_location_wildcard(self):
    """Select all locations with a wildcard query."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '11111',
          123, 10, 11, 12, 456, 13, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200414, '22222',
          123, 20, 21, 22, 456, 23, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200414, '33333',
          123, 30, 31, 32, 456, 33, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '11111',
          123, 40, 41, 42, 456, 43, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '22222',
          123, 50, 51, 52, 456, 53, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '33333',
          123, 60, 61, 62, 456, 634, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
          'direction': 13,
          'issue': 20200414,
          'lag': 0,
          'signal': 'sig',
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
        },
       ],
      'message': 'success',
    })

  def test_geo_value(self):
    """test different variants of geo types: single, *, multi."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '11111',
          123, 10, 11, 12, 456, 13, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200414, '22222',
          123, 20, 21, 22, 456, 23, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200414, '33333',
          123, 30, 31, 32, 456, 33, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '11111',
          123, 40, 41, 42, 456, 43, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '22222',
          123, 50, 51, 52, 456, 53, 20200414, 0, 1, False),
        (0, 'src', 'sig', 'day', 'msa', 20200414, '33333',
          123, 60, 61, 62, 456, 634, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    def fetch(geo_value):
      # make the request
      params = {
        'source': 'covidcast',
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
      'direction': 13,
      'issue': 20200414,
      'lag': 0,
      'signal': 'sig',
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
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200411, '01234',
          123, 10, 11, 12, 456, 13, 20200413, 2, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200412, '01234',
          123, 20, 21, 22, 456, 23, 20200413, 1, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200413, '01234',
          123, 30, 31, 32, 456, 33, 20200413, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200411, '11111',
          123, 40, 41, 42, 456, 43, 20200413, 2, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200412, '22222',
          123, 50, 51, 52, 456, 53, 20200413, 1, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200413, '33333',
          123, 60, 61, 62, 456, 63, 20200413, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
          'direction': 13,
          'issue': 20200413,
          'lag': 2,
          'signal': 'sig',
        }, {
          'time_value': 20200412,
          'geo_value': '01234',
          'value': 20,
          'stderr': 21,
          'sample_size': 22,
          'direction': 23,
          'issue': 20200413,
          'lag': 1,
          'signal': 'sig',
        }, {
          'time_value': 20200413,
          'geo_value': '01234',
          'value': 30,
          'stderr': 31,
          'sample_size': 32,
          'direction': 33,
          'issue': 20200413,
          'lag': 0,
          'signal': 'sig',
        },
       ],
      'message': 'success',
    })

  def test_unique_key_constraint(self):
    """Don't allow a row with a key collision to be inserted."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          0, 0, 0, 0, 0, 0, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # fail to insert different dummy data under the same key
    with self.assertRaises(mysql.connector.errors.IntegrityError):
      self.cur.execute('''
        insert into covidcast values
          (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
            1, 1, 1, 1, 1, 1, 20200414, 0, 1, False)
      ''')

    # succeed to insert different dummy data under a different issue
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          1, 1, 1, 1, 1, 1, 20200415, 1, 1, False)
    ''')

  def test_nullable_columns(self):
    """Missing values should be surfaced as null."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'county', 20200414, '01234',
          123, 0.123, NULL, NULL, 456, NULL, 20200414, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
        'value': 0.123,
        'stderr': None,
        'sample_size': None,
        'direction': None,
        'issue': 20200414,
        'lag': 0,
        'signal': 'sig',
       }],
      'message': 'success',
    })

  def test_temporal_partitioning(self):
    """Request a signal that's available at multiple temporal resolutions."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'hour', 'state', 2020041714, 'vi',
          123, 10, 11, 12, 456, 13, 2020041714, 0, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200417, 'vi',
          123, 20, 21, 22, 456, 23, 20200417, 00, 1, False),
        (0, 'src', 'sig', 'week', 'state', 202016, 'vi',
          123, 30, 31, 32, 456, 33, 202016, 0, 1, False),
        (0, 'src', 'sig', 'month', 'state', 202004, 'vi',
          123, 40, 41, 42, 456, 43, 202004, 0, 1, False),
        (0, 'src', 'sig', 'year', 'state', 2020, 'vi',
          123, 50, 51, 52, 456, 53, 2020, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
      'data_source': 'src',
      'signal': 'sig',
      'time_type': 'week',
      'geo_type': 'state',
      'time_values': '0-9999999999',
      'geo_value': 'vi',
    })
    response.raise_for_status()
    response = response.json()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'time_value': 202016,
        'geo_value': 'vi',
        'value': 30,
        'stderr': 31,
        'sample_size': 32,
        'direction': 33,
        'issue': 202016,
        'lag': 0,
        'signal': 'sig',
       }],
      'message': 'success',
    })

  def test_date_formats(self):
    """Request a signal using different time formats."""

    # insert dummy data
    self.cur.execute('''
      insert into covidcast values
      (0, 'src', 'sig', 'day', 'county', 20200411, '01234',
          123, 10, 11, 12, 456, 13, 20200413, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200412, '01234',
          123, 20, 21, 22, 456, 23, 20200413, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200413, '01234',
          123, 30, 31, 32, 456, 33, 20200413, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200411, '11111',
          123, 40, 41, 42, 456, 43, 20200413, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200412, '22222',
          123, 50, 51, 52, 456, 53, 20200413, 0, 1, False),
        (0, 'src', 'sig', 'day', 'county', 20200413, '33333',
          123, 60, 61, 62, 456, 63, 20200413, 0, 1, False)
    ''')
    self.cnx.commit()

    # make the request
    response = requests.get(BASE_URL, params={
      'source': 'covidcast',
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
      'source': 'covidcast',
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
      'source': 'covidcast',
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
      'source': 'covidcast',
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
      'source': 'covidcast',
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
      'source': 'covidcast',
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