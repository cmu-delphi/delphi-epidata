# standard library
import unittest

# third party
import mysql.connector
import json

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class DelphiTest(unittest.TestCase):
    """Basic integration tests for delphi endpint."""

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
        cur.execute("TRUNCATE TABLE forecasts")

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

    def test_delphi(self):
        """Basic integration test for delphi endpoint"""
        self.cur.execute(
            "INSERT INTO forecasts (`system`, `epiweek`, `json`) VALUES(%s, %s, %s)",
            (
                "eb",
                "201441",
                json.dumps(
                    {
                        "_version": "version",
                        "name": "name",
                        "season": "season",
                        "epiweek": "epiweek",
                        "year_weeks": 222,
                        "season_weeks": 111,
                        "ili_bins": "ili_bins_123",
                        "ili_bin_size": "ili_bin_size231",
                    }
                ),
            ),
        )
        self.cnx.commit()
        response = Epidata.delphi(system="eb", epiweek=201441)
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "epiweek": 201441,
                        "forecast": {
                            "_version": "version",
                            "epiweek": "epiweek",
                            "ili_bin_size": "ili_bin_size231",
                            "ili_bins": "ili_bins_123",
                            "name": "name",
                            "season": "season",
                            "season_weeks": 111,
                            "year_weeks": 222,
                        },
                        "system": "eb",
                    }
                ],
                "message": "success",
                "result": 1,
            },
        )
