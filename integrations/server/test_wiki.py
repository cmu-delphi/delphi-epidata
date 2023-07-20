# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class WikiTest(unittest.TestCase):
    """Basic integration tests for wiki endpint."""

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
        cur.execute("TRUNCATE TABLE wiki")
        cur.execute("TRUNCATE TABLE wiki_meta")

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

    def test_wiki(self):
        """Basic integration test for wiki endpoint"""

        self.cur.execute(
            'INSERT INTO wiki(datetime, article, count, language) VALUES ("2007-12-09 18:00:00", "amantadine", "3", "en"), ("2008-12-09 18:00:00", "test", "5", "en")',
        )
        self.cur.execute(
            'INSERT INTO wiki_meta(datetime, date, epiweek, total, language) VALUES ("2007-12-09 18:00:00", "2007-12-09", "200750", "969214", "en"), ("2008-12-09 18:00:00", "2008-12-09", "200750", "123321", "en")'
        )
        self.cnx.commit()
        response = Epidata.wiki(articles="test", epiweeks="200701-200801")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {"article": "test", "count": 5, "total": 123321, "hour": -1, "epiweek": 200750, "value": 40.544595}
                ],
                "result": 1,
                "message": "success",
            },
        )
