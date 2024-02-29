# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class SignalDashboardTest(DelphiTestBase):
    """Basic integration tests for signal_dashboard_coverage and signal_dashboard_status endpints."""

    # NOTE: In all other tests localSetUp() method was used. But it is not applicable for this test
    # due to order of commands, so thats why method reload + calling super was required.
    def setUp(self) -> None:
        """Perform per-test setup."""

        self.delete_from_tables_list = ["dashboard_signal_coverage", "dashboard_signal"]
        super().setUp()

        self.cur.execute(
            "INSERT INTO `dashboard_signal`(`id`, `name`, `source`, `covidcast_signal`, `enabled`, `latest_coverage_update`, `latest_status_update`) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            ("1", "Change", "chng", "smoothed_outpatient_covid", "1", "2021-10-02", "2021-11-27"),
        )
        self.cur.execute(
            "INSERT INTO `dashboard_signal_coverage`(`signal_id`, `date`, `geo_type`, `count`) VALUES(%s, %s, %s, %s)",
            ("1", "2021-10-02", "county", "2222"),
        )

        self.cnx.commit()

    def test_signal_dashboard_coverage(self):
        """Basic integration test for signal_dashboard_coverage endpoint"""
        
        response = self.epidata_client._request("signal_dashboard_coverage")
        self.assertEqual(
            response,
            {
                "epidata": {"Change": {"county": [{"count": 2222, "date": "2021-10-02"}]}},
                "message": "success",
                "result": 1,
            },
        )

    def test_signal_dashboard_status(self):
        """Basic integration test for signal_dashboard_status endpoint"""

        response = self.epidata_client._request("signal_dashboard_status")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {
                        "name": "Change",
                        "source": "chng",
                        "covidcast_signal": "smoothed_outpatient_covid",
                        "latest_issue": None,
                        "latest_time_value": None,
                        "coverage": {"county": [{"date": "2021-10-02", "count": 2222}]},
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
