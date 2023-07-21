# first party
from delphi.epidata.common.integration_test_base_class import BasicIntegrationTest


class GhtTest(BasicIntegrationTest):
    """Basic integration tests for ght endpint."""

    def setUp(self) -> None:
        """Perform per-test setup."""

        self.truncate_tables_list = ["ght"]
        self.role_name = "ght"
        super().setUp()

    def test_ght(self):
        """Basic integration test for ght endpoint"""
        self.cur.execute(
            "INSERT INTO `ght`(`query`, `location`, `epiweek`, `value`) VALUES(%s, %s, %s, %s)",
            ("/n/query", "US", "200101", "12345"),
        )
        self.cnx.commit()
        response = self.epidata.ght(locations="US", epiweeks="200101", query="/n/query", auth="ght_key")
        self.assertEqual(
            response,
            {"epidata": [{"location": "US", "epiweek": 200101, "value": 12345.0}], "result": 1, "message": "success"},
        )
