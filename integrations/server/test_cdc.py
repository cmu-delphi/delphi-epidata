# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class CdcTest(DelphiTestBase):
    """Basic integration tests for cdc endpint."""

    def localSetUp(self) -> None:
        self.truncate_tables_list = ["cdc_extract"]
        self.role_name = "cdc"

    def test_cdc(self):
        """Basic integration test for cdc endpoint"""
        self.cur.execute(
            "INSERT INTO `cdc_extract`(`epiweek`, `state`, `num1`, `num2`, `num3`, `num4`, `num5`, `num6`, `num7`, `num8`, `total`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("201102", "AK", "16", "35", "51", "96", "30", "748", "243", "433", "65"),
        )
        self.cnx.commit()
        response = self.epidata_client.cdc(auth="cdc_key", epiweeks=201102, locations="cen9")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "location": "cen9",
                        "epiweek": 201102,
                        "num1": 16,
                        "num2": 35,
                        "num3": 51,
                        "num4": 96,
                        "num5": 30,
                        "num6": 748,
                        "num7": 243,
                        "num8": 433,
                        "total": 65,
                        "value": None,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
