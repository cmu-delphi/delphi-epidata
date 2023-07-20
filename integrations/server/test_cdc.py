# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class CdcTest(unittest.TestCase):
    """Basic integration tests for cdc endpint."""

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
        cur.execute("TRUNCATE TABLE cdc_extract")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("cdc_key", "cdc_email")')
        cur.execute('INSERT INTO user_role(name) VALUES("cdc") ON DUPLICATE KEY UPDATE name="cdc"')
        cur.execute(
            'INSERT INTO user_role_link(user_id, role_id) SELECT api_user.id, 1 FROM api_user WHERE api_key="cdc_key"'
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

    def test_cdc(self):
        """Basic integration test for cdc endpoint"""
        self.cur.execute(
            "INSERT INTO cdc_extract(epiweek, state, num1, num2, num3, num4, num5, num6, num7, num8, total) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("201102", "AK", "16", "35", "51", "96", "30", "748", "243", "433", "65"),
        )
        self.cnx.commit()
        response = Epidata.cdc(auth="cdc_key", epiweeks=201102, locations="cen9")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "location": "cen9",
                        "epiweek": 201102,
                        "num1": 16,
                        "num2": 35,
                        "num3": 51,
                        "num4": 96,
                        "num5": 30,
                        "num6": 748,
                        "num7": 243,
                        "num8": 433,
                        "total": 65,
                        "value": None,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
