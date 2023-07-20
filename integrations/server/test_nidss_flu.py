# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class NiddsFluTest(unittest.TestCase):
    """Basic integration tests for nids_flu endpint."""

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
        cur.execute("TRUNCATE TABLE nidss_flu")

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

    def test_nidss_flu(self):
        """Basic integration test for nidds_flu endpoint"""
        self.cur.execute(
            "INSERT INTO nidss_flu(`release_date`, `issue`, `epiweek`, `region`, `lag`, `visits`, `ili`) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            ("2015-09-05", "201530", "200111", "SomeRegion", "222", "333", "444"),
        )
        self.cnx.commit()
        response = Epidata.nidss_flu(regions="SomeRegion", epiweeks="200111")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2015-09-05",
                        "region": "SomeRegion",
                        "issue": 201530,
                        "epiweek": 200111,
                        "lag": 222,
                        "visits": 333,
                        "ili": 444.0,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
