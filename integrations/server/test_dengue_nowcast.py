# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class DengueNowcastTest(DelphiTestBase):
    """Basic integration tests for dengue_nowcast endpint."""

    def localSetUp(self):
        create_dengue_nowcasts = """
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
        self.create_tables_list = [create_dengue_nowcasts]
        self.truncate_tables_list = ["dengue_nowcasts"]

    def test_dengue_nowcasts(self):
        """Basic integration test for dengue_nowcasts endpoint"""
        self.cur.execute(
            "INSERT INTO dengue_nowcasts(target, epiweek, location, value, std) VALUES(%s, %s, %s, %s, %s)",
            ("num_dengue", "201409", "ar", "85263", "351456"),
        )
        self.cnx.commit()
        response = self.epidata_client.dengue_nowcast(locations="ar", epiweeks=201409)
        self.assertEqual(
            response,
            {
                "epidata": [{"location": "ar", "epiweek": 201409, "value": 85263.0, "std": 351456.0}],
                "result": 1,
                "message": "success",
            },
        )
