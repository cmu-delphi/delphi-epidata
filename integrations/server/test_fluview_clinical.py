# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class FluviewClinicalTest(unittest.TestCase):
    """Basic integration tests for fluview_clinical endpint."""

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
        cur.execute("TRUNCATE TABLE fluview_clinical")

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
        """Basic integration test for fluview_clinical endpoint"""
        self.cur.execute(
            "INSERT INTO fluview_clinical(`release_date`, `issue`, `epiweek`, `region`, `lag`, `total_specimens`, `total_a`, `total_b`, `percent_positive`, `percent_a`, `percent_b`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("2018-10-10", "201839", "201640", "al", "103", "406", "4", "1", "1.32", "0.99", "0.25"),
        )
        self.cnx.commit()
        response = Epidata.fluview_clinical(epiweeks=201640, regions="al")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2018-10-10",
                        "region": "al",
                        "issue": 201839,
                        "epiweek": 201640,
                        "lag": 103,
                        "total_specimens": 406,
                        "total_a": 4,
                        "total_b": 1,
                        "percent_positive": 1.32,
                        "percent_a": 0.99,
                        "percent_b": 0.25,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
