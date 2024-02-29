# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class KcdcIliTest(DelphiTestBase):
    """Basic integration tests for kcdc_ili endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["kcdc_ili"]

    def test_kcdc_ili(self):
        """Basic integration test for kcdc_ili endpoint"""
        self.cur.execute(
            "INSERT INTO `kcdc_ili`(`release_date`, `issue`, `epiweek`, `lag`, `region`, `ili`) VALUES(%s, %s, %s, %s, %s, %s)",
            ("2020-03-27", "202013", "200432", "222", "REG", "0.25"),
        )
        self.cnx.commit()
        response = self.epidata_client.kcdc_ili(regions="REG", epiweeks="200432")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2020-03-27",
                        "region": "REG",
                        "issue": 202013,
                        "epiweek": 200432,
                        "lag": 222,
                        "ili": 0.25,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
