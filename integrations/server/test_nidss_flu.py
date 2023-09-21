# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class NiddsFluTest(DelphiTestBase):
    """Basic integration tests for nids_flu endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["nidss_flu"]

    def test_nidss_flu(self):
        """Basic integration test for nidds_flu endpoint"""
        self.cur.execute(
            "INSERT INTO `nidss_flu`(`release_date`, `issue`, `epiweek`, `region`, `lag`, `visits`, `ili`) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            ("2015-09-05", "201530", "200111", "SomeRegion", "222", "333", "444"),
        )
        self.cnx.commit()
        response = self.epidata_client.nidss_flu(regions="SomeRegion", epiweeks="200111")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2015-09-05",
                        "region": "SomeRegion",
                        "issue": 201530,
                        "epiweek": 200111,
                        "lag": 222,
                        "visits": 333,
                        "ili": 444.0,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
