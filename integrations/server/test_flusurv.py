# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class FlusurvTest(unittest.TestCase):
    """Basic integration tests for flusurv endpint."""

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
        cur.execute("TRUNCATE TABLE flusurv")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("key", "email")')

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

    def test_ecdc_ili(self):
        """Basic integration test for flusurv endpoint"""
        self.cur.execute(
            "INSERT INTO flusurv(`release_date`, `issue`, `epiweek`, `location`, `lag`, `rate_age_0`, `rate_age_1`, `rate_age_2`, `rate_age_3`, `rate_age_4`, `rate_overall`, `rate_age_5`, `rate_age_6`, `rate_age_7`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("2012-11-02", "201243", "201143", "CA", "52", "0", "0", "0", "0.151", "0", "0.029", "0", "0", "0"),
        )
        self.cnx.commit()
        response = Epidata.flusurv(epiweeks=201143, locations="CA")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2012-11-02",
                        "location": "CA",
                        "issue": 201243,
                        "epiweek": 201143,
                        "lag": 52,
                        "rate_age_0": 0.0,
                        "rate_age_1": 0.0,
                        "rate_age_2": 0.0,
                        "rate_age_3": 0.151,
                        "rate_age_4": 0.0,
                        "rate_overall": 0.029,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
