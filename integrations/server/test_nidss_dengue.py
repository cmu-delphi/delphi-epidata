# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class NiddsDengueTest(DelphiTestBase):
    """Basic integration tests for nids_dengue endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["nidss_dengue"]

    def test_nidss_dengue(self):
        """Basic integration test for nidds_dengue endpoint"""
        self.cur.execute(
            "INSERT INTO `nidss_dengue`(`epiweek`, `location`, `region`, `count`) VALUES(%s, %s, %s, %s)",
            ("200340", "SomeCity", "Central", "0"),
        )
        self.cnx.commit()
        response = self.epidata_client.nidss_dengue(locations="SomeCity", epiweeks="200340")
        self.assertEqual(
            response,
            {"epidata": [{"location": "SomeCity", "epiweek": 200340, "count": 0}], "result": 1, "message": "success"},
        )
