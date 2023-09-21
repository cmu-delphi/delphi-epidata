# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class NorostatTest(DelphiTestBase):
    """Basic integration tests for norostat endpint."""

    def localSetUp(self):
        create_norostat_point_diffs = """
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

        self.create_tables_list = [create_norostat_point_diffs]
        self.delete_from_tables_list = [
            "norostat_point_diffs",
            "norostat_point_version_list",
            "norostat_raw_datatable_location_pool",
            "norostat_raw_datatable_version_list",
        ]
        self.role_name = "norostat"

    def test_norostat(self):
        """Basic integration test for norostat endpoint"""
        self.cur.execute(
            'INSERT INTO `norostat_raw_datatable_version_list`(`release_date`, `parse_time`) VALUES ("2023-07-19", "2023-07-10 15:24:51")'
        )
        self.cur.execute(
            'INSERT INTO `norostat_raw_datatable_location_pool`(`location_id`, `location`) VALUES("1", "SomeTestLocation")'
        )
        self.cur.execute(
            'INSERT INTO `norostat_point_version_list`(`release_date`, `parse_time`) VALUES("2023-07-19", "2023-07-10 15:24:51")'
        )
        self.cur.execute(
            'INSERT INTO `norostat_point_diffs`(`release_date`, `parse_time`, `location_id`, `epiweek`, `new_value`) VALUES("2023-07-19", "2023-07-10 15:24:51", "1", "202329", 10)'
        )
        self.cnx.commit()
        response = self.epidata_client.norostat(auth="norostat_key", location="SomeTestLocation", epiweeks="202329")
        self.assertEqual(
            response,
            {
                "epidata": [{"release_date": "2023-07-19", "epiweek": 202329, "value": 10}],
                "result": 1,
                "message": "success",
            },
        )
        return True
