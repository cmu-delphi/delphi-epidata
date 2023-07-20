# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class EcdcIliTest(unittest.TestCase):
    """Basic integration tests for edcd_ili endpint."""

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
        cur.execute("TRUNCATE TABLE ecdc_ili")

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
        """Basic integration test for ecdc_ili endpoint"""
        self.cur.execute(
            "INSERT INTO ecdc_ili(`release_date`, `issue`, `epiweek`, `lag`, `region`, `incidence_rate`) VALUES(%s, %s, %s, %s, %s, %s)",
            ("2020-03-26", "202012", "201840", "76", "Armenia", "0"),
        )
        self.cnx.commit()
        response = Epidata.ecdc_ili(regions="Armenia", epiweeks="201840")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2020-03-26",
                        "region": "Armenia",
                        "issue": 202012,
                        "epiweek": 201840,
                        "lag": 76,
                        "incidence_rate": 0.0,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
