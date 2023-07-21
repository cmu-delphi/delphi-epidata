# first party
from delphi.epidata.common.integration_test_base_class import BasicIntegrationTest


class FlusurvTest(BasicIntegrationTest):
    """Basic integration tests for flusurv endpint."""

    def setUp(self) -> None:
        """Perform per-test setup."""

        self.truncate_tables_list = ["flusurv"]
        super().setUp()

    def test_flusurv(self):
        """Basic integration test for flusurv endpoint"""
        self.cur.execute(
            "INSERT INTO `flusurv`(`release_date`, `issue`, `epiweek`, `location`, `lag`, `rate_age_0`, `rate_age_1`, `rate_age_2`, `rate_age_3`, `rate_age_4`, `rate_overall`, `rate_age_5`, `rate_age_6`, `rate_age_7`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            ("2012-11-02", "201243", "201143", "CA", "52", "0", "0", "0", "0.151", "0", "0.029", "0", "0", "0"),
        )
        self.cnx.commit()
        response = self.epidata.flusurv(epiweeks=201143, locations="CA")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "release_date": "2012-11-02",
                        "location": "CA",
                        "issue": 201243,
                        "epiweek": 201143,
                        "lag": 52,
                        "rate_age_0": 0.0,
                        "rate_age_1": 0.0,
                        "rate_age_2": 0.0,
                        "rate_age_3": 0.151,
                        "rate_age_4": 0.0,
                        "rate_overall": 0.029,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
