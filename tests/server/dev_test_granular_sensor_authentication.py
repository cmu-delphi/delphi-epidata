"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest

# first party
import delphi.epidata.server.simulate_api_response as sim_api
import delphi.operations.secrets as secrets

# py3tester coverage target
__test_target__ = 'delphi.epidata.server.simulate_api_response'



class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_twtr_auth_blocked_on_self_plus_open_plus_other_closed_plus_bogus_plus_repeat_sensors(self):
    """Test that TWTR key doesn't authenticate request for TWTR data + open data + other closed data + nonexistent sensor data + repeated sensor names:"""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.twtr_sensor,
        'names': 'ght,ghtj,gft,arch,sar3,arch,epic,twtr,quid,wiki,does_not_exist,does_not_exist,does_not_exist2,twtr,ght',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'unauthenticated/nonexistent sensor(s): ght,ghtj,gft,quid,wiki,does_not_exist,does_not_exist,does_not_exist2,ght')
    self.assertEqual(response['result'], -1)

  def test_no_auth_blocked_on_empty_sensor(self):
    """Test that a request with zero auth for zero sensors is blocked."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        # no auth
        'names': '',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'no sensor names provided')
    self.assertEqual(response['result'], -1)

  def test_no_auth_blocked_on_closed_ght_sensor(self):
    """Test that providing no auth token doesn't authenticate request for GHT sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        # no auth
        'names': 'ght',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'unauthenticated/nonexistent sensor(s): ght')
    self.assertEqual(response['result'], -1)

  def test_bogus_auth_blocked_on_closed_ght_sensor(self):
    """Test that providing a bogus auth token doesn't authenticate request for GHT sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': 'bogusauth',
        'names': 'ght',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'unauthenticated/nonexistent sensor(s): ght')
    self.assertEqual(response['result'], -1)

  def test_no_auth_succeeds_on_open_sar3_sensor(self):
    """Test that providing no auth token succeeds in retrieving a single open sensor (SAR3)."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        # no auth
        'names': 'sar3',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1) # no auth failure

  def test_no_auth_succeeds_on_open_sar3_arch_epic_sensor(self):
    """Test that providing no auth token succeeds in retrieving multiple open sensors."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        # no auth
        'names': 'sar3,arch,epic',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1) # no auth failure

  def test_bogus_auth_succeeds_on_open_sar3_sensor(self):
    """Test that even a bogus auth token succeeds in retrieving an open sensor (SAR3)."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': 'bogus',
        'names': 'sar3',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1) # no auth failure

  def test_no_auth_blocked_on_open_arch_epic_closed_quid_sensor(self):
    """Test that not providing an auth token doesn't authenticate a mix of open and closed sensors."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        # no auth
        'names': 'arch,epic,quid',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'unauthenticated/nonexistent sensor(s): quid')
    self.assertEqual(response['result'], -1)

  def test_two_auth_blocked_even_on_open_arch_sensor(self):
    """Test that providing two auth tokens is blocked before considering openness/closedness of sensors."""
    # NOTE: This tests the global auth check limit and the direct limit on the number of auth tokens. If these are changed later, this check should be changed to test the new global auth check limit, and more tests should be added to test the granular auth check limits.
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': 'auth1,auth2',
        'names': 'arch',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'currently, only a single auth token is allowed to be presented at a time; please issue a separate query for each sensor name using only the corresponding token')
    self.assertEqual(response['result'], -1)

  def test_two_auth_blocked_on_closed_ghtj_sensor(self):
    """Test that providing two auth tokens is blocked before considering openness/closedness of sensors."""
    # NOTE: This tests the global auth check limit and the direct limit on the number of auth tokens. If these are changed later, this check should be changed to test the new global auth check limit, and more tests should be added to test the granular auth check limits.
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': 'auth1,auth2',
        'names': 'ghtj',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'currently, only a single auth token is allowed to be presented at a time; please issue a separate query for each sensor name using only the corresponding token')
    self.assertEqual(response['result'], -1)

  def test_bogus_auth_blocked_on_31_sensors(self):
    """Test that providing a bogus auth token does not allow us to request more than 30 sensors, using 31."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': 'auth1',
        'names': ','*30,
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'too many sensors requested and/or auth tokens presented; please divide sensors into batches and/or use only the tokens needed for the sensors requested')
    self.assertEqual(response['result'], -1)

  def test_bogus_auth_blocked_on_61_sensors(self):
    """Test that providing a bogus auth token does not allow us to request more than 30 sensors, using 61."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': 'auth1',
        'names': ','*60,
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'too many sensors requested and/or auth tokens presented; please divide sensors into batches and/or use only the tokens needed for the sensors requested')
    self.assertEqual(response['result'], -1)

  def test_twtr_auth_blocked_on_31_twtr_sensors(self):
    """Test that providing a valid granular auth token does not succeed when we request too many sensors."""
    # NOTE: This tests the granular auth check limits. If the global auth check limit is changed later, this testing should be more extensive.
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.twtr_sensor,
        'names': 'twtr,'*30+'twtr',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'too many sensors requested and/or auth tokens presented; please divide sensors into batches and/or use only the tokens needed for the sensors requested')
    self.assertEqual(response['result'], -1)

  def test_twtr_auth_succeeds_on_twtr_sensor(self):
    """Test that the TWTR auth token authenticates a request for (a single copy of) the TWTR sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.twtr_sensor,
        'names': 'twtr',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)

  def test_gft_auth_succeeds_on_gft_sensor(self):
    """Test that the GFT auth token authenticates a request for the GFT sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.gft_sensor,
        'names': 'gft',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)

  def test_ght_auth_succeeds_on_ght_sensors(self):
    """Test that the GHT auth token authenticates a request for the GHT sensors."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.ght_sensors,
        'names': 'ght,ghtj',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)

  def test_cdc_auth_succeeds_on_cdc_sensor(self):
    """Test that the CDC auth token authenticates a request for the CDC sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.cdc_sensor,
        'names': 'cdc',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)

  def test_wiki_auth_succeeds_on_wiki_sensor(self):
    """Test that the WIKI auth token authenticates a request for the WIKI sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.wiki_sensor,
        'names': 'wiki',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)

  def test_quid_auth_succeeds_on_quid_sensor(self):
    """Test that the QUID auth token authenticates a request for the QUID sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.quid_sensor,
        'names': 'quid',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)

  def test_quid_auth_blocked_on_cdc_sensor(self):
    """Test that the QUIDEL auth token doesn't authenticate a request for the CDC sensor."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensor_subsets.quid_sensor,
        'names': 'cdc',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertEqual(response['message'], 'unauthenticated/nonexistent sensor(s): cdc')
    self.assertEqual(response['result'], -1)

  def test_global_auth_succeeds_on_open_closed_sensors(self):
    """Test that the global sensor auth token authenticates a request for open and closed sensors."""
    response = sim_api.extract_response_json(sim_api.dangerously_simulate_api_response({
        'source': 'sensors',
        'auth': secrets.api.sensors,
        'names': 'sar3,arch,ghtj,ght,epic,ght,quidel,cdc,wiki',
        'locations': 'nat',
        'epiweeks': '201410',
    }))
    self.assertNotEqual(response['result'], -1)
