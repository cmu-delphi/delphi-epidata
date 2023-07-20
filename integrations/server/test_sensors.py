# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class SensorsTest(unittest.TestCase):
    """Basic integration tests for sensors endpint."""

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
        cur.execute("TRUNCATE TABLE sensors")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("sensors_key", "sensors_email")')
        cur.execute('INSERT INTO user_role(name) VALUES("sensors") ON DUPLICATE KEY UPDATE name="sensors"')
        cur.execute(
            'INSERT INTO user_role_link(user_id, role_id) SELECT api_user.id, 1 FROM api_user WHERE api_key="sensors_key"'
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

    def test_gft(self):
        """Basic integration test for sensors endpoint"""
        self.cur.execute(
            "INSERT INTO sensors(name, epiweek, location, value) VALUES(%s, %s, %s, %s)",
            ("sens1", "201111", "loc1", "222"),
        )
        self.cnx.commit()
        response = Epidata.sensors(names="sens1", locations="loc1", epiweeks="201111", auth="sensors_key")
        self.assertEqual(
            response,
            {
                "epidata": [{"name": "sens1", "location": "loc1", "epiweek": 201111, "value": 222.0}],
                "result": 1,
                "message": "success",
            },
        )
