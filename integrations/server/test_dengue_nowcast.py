# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class DengueNowcastTest(unittest.TestCase):
    """Basic integration tests for dengue_nowcast endpint."""

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

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS `dengue_nowcasts` (
            `id` int NOT NULL AUTO_INCREMENT,
            `target` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
            `epiweek` int NOT NULL,
            `location` varchar(12) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
            `value` float NOT NULL,
            `std` float NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `entry` (`target`,`epiweek`,`location`),
            KEY `target` (`target`),
            KEY `epiweek` (`epiweek`),
            KEY `location` (`location`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
        """
        )

        cur.execute("DELETE FROM api_user")
        cur.execute("TRUNCATE TABLE dengue_nowcasts")

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

    def test_dengue_nowcasts(self):
        """Basic integration test for dengue_nowcasts endpoint"""
        self.cur.execute(
            "INSERT INTO dengue_nowcasts(target, epiweek, location, value, std) VALUES(%s, %s, %s, %s, %s)",
            ("num_dengue", "201409", "ar", "85263", "351456"),
        )
        self.cnx.commit()
        response = Epidata.dengue_nowcast(locations="ar", epiweeks=201409)
        self.assertEqual(
            response,
            {
                "epidata": [{"location": "ar", "epiweek": 201409, "value": 85263.0, "std": 351456.0}],
                "result": 1,
                "message": "success",
            },
        )
