# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class GftTest(unittest.TestCase):
    """Basic integration tests for gft endpint."""

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
        cur.execute("TRUNCATE TABLE gft")

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

    def test_gft(self):
        """Basic integration test for gft endpoint"""
        self.cur.execute(
            "INSERT INTO gft(epiweek, location, num) VALUES(%s, %s, %s)",
            ("200340", "nat", "902"),
        )
        self.cnx.commit()
        response = Epidata.gft(locations="nat", epiweeks="200340")
        self.assertEqual(
            response,
            {"epidata": [{"location": "nat", "epiweek": 200340, "num": 902}], "result": 1, "message": "success"},
        )
