# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class GftTest(DelphiTestBase):
    """Basic integration tests for gft endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["gft"]

    def test_gft(self):
        """Basic integration test for gft endpoint"""
        self.cur.execute(
            "INSERT INTO `gft`(`epiweek`, `location`, `num`) VALUES(%s, %s, %s)",
            ("200340", "nat", "902"),
        )
        self.cnx.commit()
        response = self.epidata_client.gft(locations="nat", epiweeks="200340")
        self.assertEqual(
            response,
            {"epidata": [{"location": "nat", "epiweek": 200340, "num": 902}], "result": 1, "message": "success"},
        )
