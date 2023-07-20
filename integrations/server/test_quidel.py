# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class QuidelTest(unittest.TestCase):
    """Basic integration tests for quidel endpint."""

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
        cur.execute("TRUNCATE TABLE quidel")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("quidel_key", "quidel_email")')
        cur.execute('INSERT INTO user_role(name) VALUES("quidel") ON DUPLICATE KEY UPDATE name="quidel"')
        cur.execute(
            'INSERT INTO user_role_link(user_id, role_id) SELECT api_user.id, 1 FROM api_user WHERE api_key="quidel_key"'
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

    def test_quidel(self):
        """Basic integration test for quidel endpoint"""
        self.cur.execute(
            "INSERT INTO quidel(location, epiweek, value, num_rows, num_devices) VALUES(%s, %s, %s, %s, %s)",
            ("loc1", "201111", "1", "0", "0"),
        )
        self.cnx.commit()
        response = Epidata.quidel(locations="loc1", epiweeks="201111", auth="quidel_key")
        self.assertEqual(
            response,
            {"epidata": [{"location": "loc1", "epiweek": 201111, "value": 1.0}], "result": 1, "message": "success"},
        )
