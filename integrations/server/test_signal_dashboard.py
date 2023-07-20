# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class SignalDashboardTest(unittest.TestCase):
    """Basic integration tests for signal_dashboard_coverage and signal_dashboard_status endpints."""

    @classmethod
    def setUpClass(cls) -> None:
        """Perform one-time setup."""

        # use local instance of the Epidata API
        Epidata.BASE_URL = "http://delphi_web_epidata/epidata/api.php"
        Epidata.auth = ("epidata", "key")

    def setUp(self) -> None:
        """Perform per-test setup."""

        # connect to the `epidata` database
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()

        cur.execute("DELETE FROM api_user")

        cur.execute("DELETE FROM dashboard_signal_coverage")
        cur.execute("DELETE FROM dashboard_signal")
        

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("key", "email")')

        cur.execute(
            "INSERT INTO dashboard_signal(id, name, source, covidcast_signal, enabled, latest_coverage_update, latest_status_update) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            ("1", "Change", "chng", "smoothed_outpatient_covid", "1", "2021-10-02", "2021-11-27"),
        )
        cur.execute(
            "INSERT INTO dashboard_signal_coverage(signal_id, date, geo_type, count) VALUES(%s, %s, %s, %s)",
            ("1", "2021-10-02", "county", "2222"),
        )

        cnx.commit()
        cur.close()

        self.cnx = cnx
        self.cur = cnx.cursor()

    @staticmethod
    def _clear_limits():
        limiter.storage.reset()

    def tearDown(self) -> None:
        """Perform per-test teardown."""
        self.cur.close()
        self.cnx.close()
        self._clear_limits()

    def test_signal_dashboard_coverage(self):
        """Basic integration test for signal_dashboard_coverage endpoint"""

        params = {
            "endpoint": "signal_dashboard_coverage",
        }
        response = Epidata._request(params=params)
        self.assertEqual(
            response,
            {
                "epidata": {"Change": {"county": [{"count": 2222, "date": "2021-10-02"}]}},
                "message": "success",
                "result": 1,
            },
        )

    def test_signal_dashboard_status(self):
        """Basic integration test for signal_dashboard_status endpoint"""

        params = {
            "endpoint": "signal_dashboard_status",
        }
        response = Epidata._request(params=params)
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "name": "Change",
                        "source": "chng",
                        "covidcast_signal": "smoothed_outpatient_covid",
                        "latest_issue": None,
                        "latest_time_value": None,
                        "coverage": {"county": [{"date": "2021-10-02", "count": 2222}]},
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
