# standard library
import unittest

# third party
import json

# first party
from delphi.epidata.common.integration_test_base_class import BasicIntegrationTest


class DelphiTest(BasicIntegrationTest):
    """Basic integration tests for delphi endpint."""

    def setUp(self) -> None:
        self.truncate_tables_list = ["forecasts"]
        super().setUp()

    def test_delphi(self):
        """Basic integration test for delphi endpoint"""
        self.cur.execute(
            "INSERT INTO `forecasts` (`system`, `epiweek`, `json`) VALUES(%s, %s, %s)",
            (
                "eb",
                "201441",
                json.dumps(
                    {
                        "_version": "version",
                        "name": "name",
                        "season": "season",
                        "epiweek": "epiweek",
                        "year_weeks": 222,
                        "season_weeks": 111,
                        "ili_bins": "ili_bins_123",
                        "ili_bin_size": "ili_bin_size231",
                    }
                ),
            ),
        )
        self.cnx.commit()
        response = self.epidata.delphi(system="eb", epiweek=201441)
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "epiweek": 201441,
                        "forecast": {
                            "_version": "version",
                            "epiweek": "epiweek",
                            "ili_bin_size": "ili_bin_size231",
                            "ili_bins": "ili_bins_123",
                            "name": "name",
                            "season": "season",
                            "season_weeks": 111,
                            "year_weeks": 222,
                        },
                        "system": "eb",
                    }
                ],
                "message": "success",
                "result": 1,
            },
        )
