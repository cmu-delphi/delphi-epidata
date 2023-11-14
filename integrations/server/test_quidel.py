# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class QuidelTest(DelphiTestBase):
    """Basic integration tests for quidel endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["quidel"]
        self.role_name = "quidel"

    def test_quidel(self):
        """Basic integration test for quidel endpoint"""
        self.cur.execute(
            "INSERT INTO `quidel`(`location`, `epiweek`, `value`, `num_rows`, `num_devices`) VALUES(%s, %s, %s, %s, %s)",
            ("loc1", "201111", "1", "0", "0"),
        )
        self.cnx.commit()
        response = self.epidata_client.quidel(locations="loc1", epiweeks="201111", auth="quidel_key")
        self.assertEqual(
            response,
            {"epidata": [{"location": "loc1", "epiweek": 201111, "value": 1.0}], "result": 1, "message": "success"},
        )
