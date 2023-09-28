# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class GhtTest(DelphiTestBase):
    """Basic integration tests for ght endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["ght"]
        self.role_name = "ght"

    def test_ght(self):
        """Basic integration test for ght endpoint"""
        self.cur.execute(
            "INSERT INTO `ght`(`query`, `location`, `epiweek`, `value`) VALUES(%s, %s, %s, %s)",
            ("/n/query", "US", "200101", "12345"),
        )
        self.cnx.commit()
        ghtauth = ("epidata", "ght_key")
        response = self.epidata_client.ght(locations="US", epiweeks="200101", query="/n/query", auth=ghtauth)
        self.assertEqual(
            response,
            {"epidata": [{"location": "US", "epiweek": 200101, "value": 12345.0}], "result": 1, "message": "success"},
        )
