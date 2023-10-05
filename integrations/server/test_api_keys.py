"""Integration tests for the API Keys"""
import requests

# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class APIKeysTets(DelphiTestBase):
    """Tests the API Keys behaviour"""

    def localSetUp(self):
        self.role_name = "cdc"

    def _make_request(self, endpoint: str, params: dict = {}, auth: tuple = None):
        url = f"{self.epidata_client.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params, auth=auth)
        return response

    def test_public_route(self):
        """Test public route"""
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("version").status_code)
        self.assertEqual(status_codes, {200})

    def test_no_multiples_data_source(self):
        """Test requests with no multiples and with provided `data_source` and `signal` as a separate query params."""
        params = {
            "data_source": "fb-survey",
            "signal": "smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {200})

    def test_no_multiples_source_signal(self):
        """Test requests with colon-delimited source-signal param presentation."""
        params = {
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {200})

    def test_multiples_allowed_signal_two_multiples(self):
        """Test requests with 2 multiples and allowed dashboard signal"""
        params = {
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {200})

    def test_multiples_non_allowed_signal(self):
        """Test requests with 2 multiples and non-allowed dashboard signal"""
        params = {
            "signal": "hospital-admissions:smoothed_adj_covid19_from_claims",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {200, 429})

    def test_multiples_mixed_allowed_signal_two_multiples(self):
        """Test requests with 2 multiples and mixed-allowed dashboard signal"""
        params = {
            "signal": "fb-survey:smoothed_wcli,hospital-admissions:smoothed_adj_covid19_from_claims",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {200, 429})

    def test_multiples_allowed_signal_three_multiples(self):
        """Test requests with 3 multiples and allowed dashboard signal"""
        params = {
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {401})

    def test_multiples_mixed_allowed_signal_three_multiples(self):
        """Test requests with 3 multiples and mixed-allowed dashboard signal"""
        params = {
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli1",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("covidcast", params=params).status_code)
        self.assertEqual(status_codes, {401})

    def test_multiples_mixed_allowed_signal_api_key(self):
        """Test requests with 3 multiples and mixed-allowed dashboard signal + valid API Key"""
        params = {
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli1",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(
                self._make_request("covidcast", params=params, auth=self.epidata_client.auth).status_code
            )
        self.assertEqual(status_codes, {200})

    def test_multiples_allowed_signal_api_key(self):
        """Test requests with 3 multiples and allowed dashboard signal + valid API Key"""
        params = {
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(
                self._make_request("covidcast", params=params, auth=self.epidata_client.auth).status_code
            )
        self.assertEqual(status_codes, {200})

    def test_no_multiples_allowed_signal_api_key(self):
        """Test requests with no multiples and allowed dashboard signal + valid API Key"""
        params = {
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(
                self._make_request("covidcast", params=params, auth=self.epidata_client.auth).status_code
            )
        self.assertEqual(status_codes, {200})

    def test_no_multiples_allowed_signal_bad_api_key(self):
        """Test requests with no multiples and allowed dashboard signal + bad API Key"""
        params = {
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(
                self._make_request(
                    "covidcast", params=params, auth=("bad_key", "bad_email")
                ).status_code
            )
        self.assertEqual(status_codes, {200})

    def test_restricted_endpoint_no_key(self):
        """Test restricted endpoint with no auth key"""
        params = {"regions": "1as", "epiweeks": "202020"}
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("cdc", params=params).status_code)
        self.assertEqual(status_codes, {401})

    def test_restricted_endpoint_invalid_key(self):
        """Test restricted endpoint with invalid auth key"""
        params = {
            "regions": "1as",
            "epiweeks": "202020",
            "auth": "invalid_key",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("cdc", params=params).status_code)
        self.assertEqual(status_codes, {401})

    def test_restricted_endpoint_no_roles_key(self):
        """Test restricted endpoint with no roles key"""
        params = {
            "regions": "1as",
            "epiweeks": "202020",
            "auth": "key",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("cdc", params=params).status_code)
        self.assertEqual(status_codes, {401})

    def test_restricted_endpoint_valid_roles_key(self):
        """Test restricted endpoint with valid auth key with required role"""
        params = {
            "regions": "1as",
            "epiweeks": "202020",
            "auth": "cdc_key",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request("cdc", params=params).status_code)
        self.assertEqual(status_codes, {200})
