"""Integration tests for the API Keys"""

# standard library
import unittest

# third party
import mysql.connector
import requests

# first party
from delphi.epidata.server._limiter import limiter

BASE_URL = "http://delphi_web_epidata/epidata/api.php"
AUTH = ("epidata", "key")


class APIKeysTets(unittest.TestCase):
    """Tests the API Keys behaviour"""

    def setUp(self):
        """Perform per-test setup."""

        # connect to the `epidata` database and clear the `api_user` table
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()

        # clear `api_user` table
        cur.execute("delete from api_user")
        cur.execute('insert into api_user(api_key, email) values("key", "email")')
        # insert cdc role api key
        cur.execute('insert into api_user(api_key, email) values("cdc_key", "cdc_email")')
        cur.execute('insert into user_role(name) values("cdc") on duplicate key update name="cdc"')
        cur.execute(
            'insert into user_role_link(user_id, role_id) select api_user.id, 1 from api_user where api_key="cdc_key"'
        )
        cnx.commit()
        cur.close()

        # make connection and cursor available to test cases
        self.cnx = cnx
        self.cur = cnx.cursor()

    @staticmethod
    def _clear_limits():
        limiter.storage.reset()

    def tearDown(self) -> None:
        self.cur.execute("delete from api_user")
        self.cur.execute("truncate table user_role")
        self.cur.execute("truncate table user_role_link")
        self.cnx.commit()
        self.cur.close()
        self.cnx.close()
        self._clear_limits()

    @staticmethod
    def _make_request(url: str, params: dict = {}, auth: tuple = None):
        response = requests.get(url, params=params, auth=auth)
        return response

    def test_public_route(self):
        """Test public route"""
        public_route = "http://delphi_web_epidata/epidata/version"
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(public_route).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_no_multiples_data_source(self):
        """Test requests with no multiples and with provided `data_source` and `signal` as a separate query params."""
        params = {
            "source": "covidcast",
            "data_source": "fb-survey",
            "signal": "smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_no_multiples_source_signal(self):
        """Test requests with colon-delimited source-signal param presentation."""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_multiples_allowed_signal(self):
        """Test requests with 2 multiples and allowed dashboard signal"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_multiples_non_allowed_signal(self):
        """Test requests with 2 multiples and non-allowed dashboard signal"""
        params = {
            "source": "covidcast",
            "signal": "hospital-admissions:smoothed_adj_covid19_from_claims",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 2)
        self.assertEqual(status_codes, {200, 429})

    def test_multiples_mixed_allowed_signal(self):
        """Test requests with 2 multiples and mixed-allowed dashboard signal"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli,hospital-admissions:smoothed_adj_covid19_from_claims",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 2)
        self.assertEqual(status_codes, {200, 429})

    def test_multiples_allowed_signal(self):
        """Test requests with 3 multiples and allowed dashboard signal"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 401)

    def test_multiples_mixed_allowed_signal(self):
        """Test requests with 3 multiples and mixed-allowed dashboard signal"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli1",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 401)

    def test_multiples_mixed_allowed_signal_api_key(self):
        """Test requests with 3 multiples and mixed-allowed dashboard signal + valid API Key"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli1",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params, auth=AUTH).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_multiples_allowed_signal_api_key(self):
        """Test requests with 3 multiples and allowed dashboard signal + valid API Key"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli,fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa,ny",
            "time_values": "20200406,20200407",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params, auth=AUTH).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_no_multiples_allowed_signal_api_key(self):
        """Test requests with no multiples and allowed dashboard signal + valid API Key"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params, auth=AUTH).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_no_multiples_allowed_signal_bad_api_key(self):
        """Test requests with no multiples and allowed dashboard signal + bad API Key"""
        params = {
            "source": "covidcast",
            "signal": "fb-survey:smoothed_wcli",
            "time_type": "day",
            "geo_type": "state",
            "geo_value": "pa",
            "time_values": "20200406",
        }
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params, auth=("bad_key", "bad_email")).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)

    def test_restricted_endpoint_no_key(self):
        """Test restricted endpoint with no auth key"""
        params = {"source": "cdc", "regions": "1as", "epiweeks": "202020"}
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 401)

    def test_restricted_endpoint_invalid_key(self):
        """Test restricted endpoint with invalid auth key"""
        params = {"source": "cdc", "regions": "1as", "epiweeks": "202020", "auth": "invalid_key"}
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 401)

    def test_restricted_endpoint_no_roles_key(self):
        """Test restricted endpoint with no roles key"""
        params = {"source": "cdc", "regions": "1as", "epiweeks": "202020", "auth": "key"}
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 401)

    def test_restricted_endpoint_valid_roles_key(self):
        """Test restricted endpoint with valid auth key with required role"""
        params = {"source": "cdc", "regions": "1as", "epiweeks": "202020", "auth": "cdc_key"}
        status_codes = set()
        for _ in range(10):
            status_codes.add(self._make_request(BASE_URL, params=params).status_code)
        self.assertEqual(len(status_codes), 1)
        self.assertEqual(next(iter(status_codes)), 200)
