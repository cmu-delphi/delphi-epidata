# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class TwitterTest(unittest.TestCase):
    """Basic integration tests for twitter endpint."""

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
        cur.execute("TRUNCATE TABLE twitter")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("twitter_key", "twitter_email")')
        cur.execute('INSERT INTO user_role(name) VALUES("twitter") ON DUPLICATE KEY UPDATE name="twitter"')
        cur.execute(
            'INSERT INTO user_role_link(user_id, role_id) SELECT api_user.id, 1 FROM api_user WHERE api_key="twitter_key"'
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

    def test_twitter(self):
        """Basic integration test for twitter endpoint"""

        self.cur.execute(
            'INSERT INTO twitter(date, state, num, total) VALUES ("2015-07-29", "AK", "1", "223"), ("2020-07-29", "CT", "12", "778")', 
        )
        self.cnx.commit()
        response = Epidata.twitter(auth="twitter_key", locations="cen9", dates="20150701-20160101")
        self.assertEqual(
            response,
            {
                "epidata": [{"location": "cen9", "date": "2015-07-29", "num": 1, "total": 223, "percent": 0.4484}],
                "result": 1,
                "message": "success",
            },
        )
