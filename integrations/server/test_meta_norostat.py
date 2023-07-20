# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.server._limiter import limiter


class MetaNorostatTest(unittest.TestCase):
    """Basic integration tests for meta_norostat endpint."""

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
            CREATE TABLE IF NOT EXISTS `norostat_raw_datatable_version_list` (
            `release_date` date NOT NULL,
            `parse_time` datetime NOT NULL,
            PRIMARY KEY (`release_date`,`parse_time`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
            """
        )

        # cnx.commit()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS `norostat_point_version_list` (
            `release_date` date NOT NULL,
            `parse_time` datetime NOT NULL,
            PRIMARY KEY (`release_date`,`parse_time`),
            CONSTRAINT `norostat_point_version_list_ibfk_1` FOREIGN KEY (`release_date`, `parse_time`) REFERENCES `norostat_raw_datatable_version_list` (`release_date`, `parse_time`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
            """
        )

        # cnx.commit()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS `norostat_raw_datatable_location_pool` (
            `location_id` int NOT NULL AUTO_INCREMENT,
            `location` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
            PRIMARY KEY (`location_id`),
            UNIQUE KEY `location` (`location`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
            """
        )

        # cnx.commit()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS `norostat_point_diffs` (
            `release_date` date NOT NULL,
            `parse_time` datetime NOT NULL,
            `location_id` int NOT NULL,
            `epiweek` int NOT NULL,
            `new_value` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
            PRIMARY KEY (`release_date`,`parse_time`,`location_id`,`epiweek`),
            UNIQUE KEY `location_id` (`location_id`,`epiweek`,`release_date`,`parse_time`,`new_value`),
            CONSTRAINT `norostat_point_diffs_ibfk_1` FOREIGN KEY (`release_date`, `parse_time`) REFERENCES `norostat_point_version_list` (`release_date`, `parse_time`),
            CONSTRAINT `norostat_point_diffs_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `norostat_raw_datatable_location_pool` (`location_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;    
            """
        )

        cur.execute("DELETE FROM api_user")
        cur.execute("TRUNCATE TABLE user_role")
        cur.execute("TRUNCATE TABLE user_role_link")
        cur.execute("DELETE FROM norostat_point_diffs")
        cur.execute("DELETE FROM norostat_point_version_list")
        cur.execute("DELETE FROM norostat_raw_datatable_location_pool")
        cur.execute("DELETE FROM norostat_raw_datatable_version_list")

        cur.execute('INSERT INTO api_user(api_key, email) VALUES("norostat_key", "norostat_email")')
        cur.execute('INSERT INTO user_role(name) VALUES("norostat") ON DUPLICATE KEY UPDATE name="norostat"')
        cur.execute(
            'INSERT INTO user_role_link(user_id, role_id) SELECT api_user.id, 1 FROM api_user WHERE api_key="norostat_key"'
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

    def test_meta_norostat(self):
        """Basic integration test for meta_norostat endpoint"""

        self.cur.execute(
            "INSERT INTO norostat_raw_datatable_version_list(release_date, parse_time) VALUES (%s, %s)",
            ("2014-10-22", "2048-12-08 15:22:51"),
        )
        self.cur.execute(
            'INSERT INTO norostat_raw_datatable_location_pool(`location`) VALUES ("Minnesota, Ohio, Oregon, Tennessee, and Wisconsin")'
        )
        self.cnx.commit()
        response = Epidata.meta_norostat(auth="norostat_key")
        self.assertEqual(
            response,
            {
                "epidata": {
                    "locations": [{"location": "Minnesota, Ohio, Oregon, Tennessee, and Wisconsin"}],
                    "releases": [{"release_date": "2014-10-22"}],
                },
                "message": "success",
                "result": 1,
            },
        )
