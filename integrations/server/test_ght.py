# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class GhtTest(unittest.TestCase):
    """Basic integration tests for gft endpint."""

    @classmethod
    def setUpClass(cls) -> None:
        """Perform one-time setup."""

        # use local instance of the Epidata API
        Epidata.BASE_URL = "http://delphi_web_epidata/epidata/api.php"

    def setUp(self) -> None:
        """Perform per-test setup."""

        # connect to the `epidata` database
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()

        cur.execute("DELETE FROM api_user")
        cur.execute("TRUNCATE TABLE user_role")
        cur.execute("TRUNCATE TABLE user_role_link")
        cur.execute("TRUNCATE TABLE ght")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("ght_key", "ght_email")')
        cur.execute('INSERT INTO user_role(name) VALUES("ght") ON DUPLICATE KEY UPDATE name="ght"')
        cur.execute(
            'INSERT INTO user_role_link(user_id, role_id) SELECT api_user.id, 1 FROM api_user WHERE api_key="ght_key"'
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

    def test_ght(self):
        """Basic integration test for ght endpoint"""
        self.cur.execute(
            "INSERT INTO ght(`query`, `location`, `epiweek`, `value`) VALUES(%s, %s, %s, %s)",
            ("/n/query", "US", "200101", "12345"),
        )
        self.cnx.commit()
        response = Epidata.ght(locations="US", epiweeks="200101", query="/n/query", auth="ght_key")
        self.assertEqual(
            response,
            {"epidata": [{"location": "US", "epiweek": 200101, "value": 12345.0}], "result": 1, "message": "success"},
        )
