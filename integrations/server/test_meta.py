# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class MetaTest(unittest.TestCase):
    """Basic integration tests for meta endpint."""

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
        cur.execute("TRUNCATE TABLE fluview")
        cur.execute("TRUNCATE TABLE wiki")
        cur.execute("TRUNCATE TABLE wiki_meta")
        cur.execute("TRUNCATE TABLE twitter")

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

    def test_meta(self):
        """Basic integration test for meta endpoint"""
        response = Epidata.meta()
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "delphi": [],
                        "fluview": [{"latest_issue": None, "latest_update": None, "table_rows": 0}],
                        "twitter": [],
                        "wiki": [{"latest_update": None, "table_rows": 0}],
                    }
                ],
                "message": "success",
                "result": 1,
            },
        )
