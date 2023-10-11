"""Integration tests for the `covidcast_nowcast` endpoint."""

from delphi.epidata.common.covidcast_test_base import CovidcastTestBase


class CovidcastTests(CovidcastTestBase):
  """Tests the `covidcast` endpoint."""

  def localSetUp(self):
    """Perform per-test setup."""
    self.truncate_tables_list = ["covidcast_nowcast"]

  def test_query(self):
    """Query nowcasts using default and specified issue."""

    self.cur.execute(
      f'''insert into covidcast_nowcast values 
      (0, 'src', 'sig', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 3.5, 20200101, 2),
      (0, 'src', 'sig', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 2.5, 20200102, 2),
      (0, 'src', 'sig', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 1.5, 20200103, 2)''')

    self.cnx.commit()
    # make the request with specified issue date
    params={
      'data_source': 'src',
      'signals': 'sig',
      'sensor_names': 'sensor',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200101,
      'geo_value': '01001',
      'issues': 20200101
    }
    response = self._make_request(endpoint="covidcast_nowcast", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'signal': 'sig',
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 3.5,
        'issue': 20200101,
        'lag': 2,
       }],
      'message': 'success',
    })

    # make request without specific issue date
    params={
      'data_source': 'src',
      'signals': 'sig',
      'sensor_names': 'sensor',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200101,
      'geo_value': '01001',
    }
    response = self._make_request(endpoint="covidcast_nowcast", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)

    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'signal': 'sig',
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 1.5,
        'issue': 20200103,
        'lag': 2,
       }],
      'message': 'success',
    })

    params={
      'data_source': 'src',
      'signals': 'sig',
      'sensor_names': 'sensor',
      'time_type': 'day',
      'geo_type': 'county',
      'time_values': 20200101,
      'geo_value': '01001',
      'as_of': 20200101
    }
    response = self._make_request(endpoint="covidcast_nowcast", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)

    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
        'signal': 'sig',
        'time_value': 20200101,
        'geo_value': '01001',
        'value': 3.5,
        'issue': 20200101,
        'lag': 2,
       }],
      'message': 'success',
    })
