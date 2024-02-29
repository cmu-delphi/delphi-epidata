# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class NowcastTest(DelphiTestBase):
    """Basic integration tests for nowcast endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["nowcasts"]

    def test_nowcast(self):
        """Basic integration test for nowcast endpoint"""
        self.cur.execute(
            "INSERT INTO `nowcasts`(`epiweek`, `location`, `value`, `std`) VALUES(%s, %s, %s, %s)",
            ("201145", "nat", "12345", "0.01234"),
        )
        self.cnx.commit()
        response = self.epidata_client.nowcast(locations="nat", epiweeks="201145")
        self.assertEqual(
            response,
            {
                "epidata": [{"location": "nat", "epiweek": 201145, "value": 12345.0, "std": 0.01234}],
                "result": 1,
                "message": "success",
            },
        )
