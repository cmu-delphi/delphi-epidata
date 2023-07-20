# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class PahoDengueTest(unittest.TestCase):
    """Basic integration tests for paho_dengue endpint."""

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
        cur.execute("TRUNCATE TABLE paho_dengue")

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

    def test_paho_dengue(self):
        """Basic integration test for paho_dengue endpoint"""
        self.cur.execute(
            "INSERT INTO paho_dengue(`release_date`, `issue`, `epiweek`, `lag`, `region`, `total_pop`, `serotype`, `num_dengue`, `incidence_rate`, `num_severe`, `num_deaths`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("2018-12-01", "201848", "201454", "204", "AG", "91", "DEN 1,4", "37", "40.66", "0", "0"),
        )
        self.cnx.commit()
        response = Epidata.paho_dengue(regions="AG", epiweeks="201454")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2018-12-01",
                        "region": "AG",
                        "serotype": "DEN 1,4",
                        "issue": 201848,
                        "epiweek": 201454,
                        "lag": 204,
                        "total_pop": 91,
                        "num_dengue": 37,
                        "num_severe": 0,
                        "num_deaths": 0,
                        "incidence_rate": 40.66,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
