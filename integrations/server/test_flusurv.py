# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class FlusurvTest(DelphiTestBase):
    """Basic integration tests for flusurv endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["flusurv"]

    def test_flusurv(self):
        """Basic integration test for flusurv endpoint"""
        self.cur.execute(
            """
            INSERT INTO `flusurv`(
                `release_date`, `issue`, `epiweek`, `location`, `lag`,
                `rate_age_0`, `rate_age_1`, `rate_age_2`, `rate_age_3`, `rate_age_4`,
                `rate_overall`, `rate_age_5`, `rate_age_6`, `rate_age_7`,
                `rate_age_18t29`,
                `rate_age_30t39`,
                `rate_age_40t49`,
                `rate_age_5t11`,
                `rate_age_12t17`,
                `rate_age_lt18`,
                `rate_age_gte18`,
                `rate_age_1t4`,
                `rate_age_gte75`,
                `rate_age_0tlt1`,
                `rate_race_white`,
                `rate_race_black`,
                `rate_race_hisp`,
                `rate_race_asian`,
                `rate_race_natamer`,
                `rate_sex_male`,
                `rate_sex_female`,
                `rate_flu_a`,
                `rate_flu_b`
            ) VALUES(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                "2012-11-02", "201243", "201143", "CA", "52", "0", "0", "0", "0.151", "0", "0.029", "0", "0", "0",
                "2.54", "0", "1", "0", "0", "0", "0", "0", "0.68", "0.46", "1", "1", "0", "0", "0", "99", "0", "0", "22.2"
            ),
        )
        self.cnx.commit()
        response = self.epidata_client.flusurv(epiweeks=201143, locations="CA")
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
                        "rate_age_5": 0.0,
                        "rate_age_6": 0.0,
                        "rate_age_7": 0.0,
                        "rate_age_18t29": 2.54,
                        "rate_age_30t39": 0.0,
                        "rate_age_40t49": 1.0,
                        "rate_age_5t11": 0.0,
                        "rate_age_12t17": 0.0,
                        "rate_age_lt18": 0.0,
                        "rate_age_gte18": 0.0,
                        "rate_age_1t4": 0.0,
                        "rate_age_gte75": 0.68,
                        "rate_age_0tlt1": 0.46,
                        "rate_race_white": 1.0,
                        "rate_race_black": 1.0,
                        "rate_race_hisp": 0.0,
                        "rate_race_asian": 0.0,
                        "rate_race_natamer": 0.0,
                        "rate_sex_male": 99.0,
                        "rate_sex_female": 0.0,
                        "rate_flu_a": 0.0,
                        "rate_flu_b": 22.2,
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
