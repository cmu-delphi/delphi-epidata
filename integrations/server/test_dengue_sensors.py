# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class DengueSensorsTest(DelphiTestBase):
    """Basic integration tests for dengue_sensors endpint."""

    def localSetUp(self):
        create_dengue_sensors = """
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
        self.create_tables_list = [create_dengue_sensors]
        self.truncate_tables_list = ["dengue_sensors"]
        self.role_name = "sensors"

    def test_dengue_sensors(self):
        """Basic integration test for dengue_sensors endpoint"""
        self.cur.execute(
            "INSERT INTO `dengue_sensors`(`target`, `name`, `epiweek`, `location`, `value`) VALUES(%s, %s, %s, %s, %s)",
            ("num_dengue", "ght", "201432", "ag", "1234"),
        )
        self.cnx.commit()
        response = self.epidata_client.dengue_sensors(auth="sensors_key", names="ght", locations="ag", epiweeks="201432")
        self.assertEqual(
            response,
            {
                "epidata": [{"name": "ght", "location": "ag", "epiweek": 201432, "value": 1234.0}],
                "result": 1,
                "message": "success",
            },
        )
