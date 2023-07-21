# first party
from delphi.epidata.common.integration_test_base_class import BasicIntegrationTest


class FluviewClinicalTest(BasicIntegrationTest):
    """Basic integration tests for fluview_clinical endpint."""

    def setUp(self) -> None:
        """Perform per-test setup."""

        self.truncate_tables_list = ["fluview_clinical"]
        super().setUp()

    def test_fluview_clinical(self):
        """Basic integration test for fluview_clinical endpoint"""
        self.cur.execute(
            "INSERT INTO `fluview_clinical`(`release_date`, `issue`, `epiweek`, `region`, `lag`, `total_specimens`, `total_a`, `total_b`, `percent_positive`, `percent_a`, `percent_b`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("2018-10-10", "201839", "201640", "al", "103", "406", "4", "1", "1.32", "0.99", "0.25"),
        )
        self.cnx.commit()
        response = self.epidata.fluview_clinical(epiweeks=201640, regions="al")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2018-10-10",
                        "region": "al",
                        "issue": 201839,
                        "epiweek": 201640,
                        "lag": 103,
                        "total_specimens": 406,
                        "total_a": 4,
                        "total_b": 1,
                        "percent_positive": 1.32,
                        "percent_a": 0.99,
                        "percent_b": 0.25,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
