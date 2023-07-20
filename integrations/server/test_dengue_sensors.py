# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class DengueSensorsTest(unittest.TestCase):
    """Basic integration tests for dengue_sensors endpint."""

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

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS `dengue_sensors` (
            `id` int NOT NULL AUTO_INCREMENT,
            `target` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
            `name` varchar(8) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
            `epiweek` int NOT NULL,
            `location` varchar(12) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
            `value` float NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `entry` (`target`,`name`,`epiweek`,`location`),
            KEY `sensor` (`target`,`name`),
            KEY `epiweek` (`epiweek`),
            KEY `location` (`location`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
        """
        )

        cur.execute("TRUNCATE TABLE dengue_sensors")

        cur.execute("DELETE FROM api_user")
        cur.execute("TRUNCATE TABLE user_role")
        cur.execute("TRUNCATE TABLE user_role_link")

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

    def test_dengue_sensors(self):
        """Basic integration test for dengue_sensors endpoint"""
        self.cur.execute(
            "INSERT INTO dengue_sensors(target, name, epiweek, location, value) VALUES(%s, %s, %s, %s, %s)",
            ("num_dengue", "ght", "201432", "ag", "1234"),
        )
        self.cnx.commit()
        response = Epidata.dengue_sensors(auth="sensors_key", names="ght", locations="ag", epiweeks="201432")
        self.assertEqual(
            response,
            {
                "epidata": [{"name": "ght", "location": "ag", "epiweek": 201432, "value": 1234.0}],
                "result": 1,
                "message": "success",
            },
        )
