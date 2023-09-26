# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class EcdcIliTest(DelphiTestBase):
    """Basic integration tests for edcd_ili endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["ecdc_ili"]

    def test_ecdc_ili(self):
        """Basic integration test for ecdc_ili endpoint"""
        self.cur.execute(
            "INSERT INTO `ecdc_ili`(`release_date`, `issue`, `epiweek`, `lag`, `region`, `incidence_rate`) VALUES(%s, %s, %s, %s, %s, %s)",
            ("2020-03-26", "202012", "201840", "76", "Armenia", "0"),
        )
        self.cnx.commit()
        response = self.epidata_client.ecdc_ili(regions="Armenia", epiweeks="201840")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2020-03-26",
                        "region": "Armenia",
                        "issue": 202012,
                        "epiweek": 201840,
                        "lag": 76,
                        "incidence_rate": 0.0,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
