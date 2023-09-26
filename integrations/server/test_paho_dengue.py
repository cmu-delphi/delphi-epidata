# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class PahoDengueTest(DelphiTestBase):
    """Basic integration tests for paho_dengue endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["paho_dengue"]

    def test_paho_dengue(self):
        """Basic integration test for paho_dengue endpoint"""
        self.cur.execute(
            "INSERT INTO `paho_dengue`(`release_date`, `issue`, `epiweek`, `lag`, `region`, `total_pop`, `serotype`, `num_dengue`, `incidence_rate`, `num_severe`, `num_deaths`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("2018-12-01", "201848", "201454", "204", "AG", "91", "DEN 1,4", "37", "40.66", "0", "0"),
        )
        self.cnx.commit()
        response = self.epidata_client.paho_dengue(regions="AG", epiweeks="201454")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2018-12-01",
                        "region": "AG",
                        "serotype": "DEN 1,4",
                        "issue": 201848,
                        "epiweek": 201454,
                        "lag": 204,
                        "total_pop": 91,
                        "num_dengue": 37,
                        "num_severe": 0,
                        "num_deaths": 0,
                        "incidence_rate": 40.66,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
