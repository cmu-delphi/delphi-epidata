# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class SensorsTest(DelphiTestBase):
    """Basic integration tests for sensors endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["sensors"]
        self.role_name = "sensors"

    def test_sensors(self):
        """Basic integration test for sensors endpoint"""
        self.cur.execute(
            "INSERT INTO `sensors`(`name`, `epiweek`, `location`, `value`) VALUES(%s, %s, %s, %s)",
            ("sens1", "201111", "loc1", "222"),
        )
        self.cnx.commit()
        response = self.epidata_client.sensors(names="sens1", locations="loc1", epiweeks="201111", auth="sensors_key")
        self.assertEqual(
            response,
            {
                "epidata": [{"name": "sens1", "location": "loc1", "epiweek": 201111, "value": 222.0}],
                "result": 1,
                "message": "success",
            },
        )
