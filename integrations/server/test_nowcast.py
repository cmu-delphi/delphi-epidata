# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class NowcastTest(unittest.TestCase):
    """Basic integration tests for nowcast endpint."""

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
        cur.execute("TRUNCATE TABLE nowcasts")

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

    def test_nowcast(self):
        """Basic integration test for nowcast endpoint"""
        self.cur.execute(
            "INSERT INTO nowcasts(`epiweek`, `location`, `value`, `std`) VALUES(%s, %s, %s, %s)",
            ("201145", "nat", "12345", "0.01234"),
        )
        self.cnx.commit()
        response = Epidata.nowcast(locations="nat", epiweeks="201145")
        self.assertEqual(
            response,
            {
                "epidata": [{"location": "nat", "epiweek": 201145, "value": 12345.0, "std": 0.01234}],
                "result": 1,
                "message": "success",
            },
        )
