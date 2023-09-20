# first party
from delphi.epidata.common.integration_test_base_class import BasicIntegrationTest


class MetaTest(BasicIntegrationTest):
    """Basic integration tests for meta endpint."""

    def setUp(self) -> None:
        self.truncate_tables_list = ["forecasts", "fluview", "wiki", "wiki_meta", "twitter"]
        super().setUp()

    def test_meta(self):
        """Basic integration test for meta endpoint"""
        response = self.epidata.meta()
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "delphi": [],
                        "fluview": [{"latest_issue": None, "latest_update": None, "table_rows": 0}],
                        "twitter": [],
                        "wiki": [{"latest_update": None, "table_rows": 0}],
                    }
                ],
                "message": "success",
                "result": 1,
            },
        )
