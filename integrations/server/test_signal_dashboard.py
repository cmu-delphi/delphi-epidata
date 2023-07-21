# first party
from delphi.epidata.common.integration_test_base_class import BasicIntegrationTest


class SignalDashboardTest(BasicIntegrationTest):
    """Basic integration tests for signal_dashboard_coverage and signal_dashboard_status endpints."""

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

        params = {
            "endpoint": "signal_dashboard_coverage",
        }
        response = self.epidata._request(params=params)
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

        params = {
            "endpoint": "signal_dashboard_status",
        }
        response = self.epidata._request(params=params)
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
