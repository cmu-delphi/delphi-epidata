"""Integration tests for delphi_epidata.py."""

# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'

class DelphiEpidataPythonClientNowcastTests(DelphiTestBase):
  """Tests the Python client."""

  def localSetUp(self):
    """Perform per-test setup."""
    self.truncate_tables_list = ["covidcast_nowcast"]

  def test_covidcast_nowcast(self):
    """Test that the covidcast_nowcast endpoint returns expected data."""

    # insert dummy data
    self.cur.execute('''insert into covidcast_nowcast values
      (0, 'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 3.5, 20200101, 2),
      (0, 'src', 'sig2', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 2.5, 20200101, 2),
      (0, 'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001', 12345678, 1.5, 20200102, 2)''')
    self.cnx.commit()

    # fetch data
    response = self.epidata_client.covidcast_nowcast(
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
    response = self.epidata_client.covidcast_nowcast(
      'src', 'sig1', 'sensor', 'day', 'county', 20200101, '01001',
      issues=self.epidata_client.range(20200101, 20200102))

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
    response = self.epidata_client.covidcast_nowcast(
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
    response = self.epidata_client.covidcast_nowcast(
      'src', 'sig1', 'sensor', 'day', 'county', 22222222, '01001')

    self.assertEqual(response, {'epidata': [], 'result': -2, 'message': 'no results'})
