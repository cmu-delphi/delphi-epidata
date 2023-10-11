# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class MetaTest(DelphiTestBase):
    """Basic integration tests for meta endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["forecasts", "fluview", "wiki", "wiki_meta", "twitter"]

    def test_meta(self):
        """Basic integration test for meta endpoint"""
        response = self.epidata_client.meta()
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
