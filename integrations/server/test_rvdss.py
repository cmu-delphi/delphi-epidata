# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class rvdssTest(DelphiTestBase):
    """Basic integration tests for rvdss endpoint."""

    def localSetUp(self):
        self.truncate_tables_list = ["rvdss"]

    def test_rvdss_repiratory_detections(self):
        """Basic integration test for rvdss endpoint"""
        self.cur.execute(
            "INSERT INTO `rvdss` (`epiweek`, `time_value`,`time_type`, `issue`, `geo_type`, `geo_value`, `sarscov2_tests`, `sarscov2_positive_tests`, `sarscov2_pct_positive`, `flu_tests`, `flu_positive_tests`, `flu_pct_positive`, `fluah1n1pdm09_positive_tests`, `fluah3_positive_tests`, `fluauns_positive_tests`, `flua_positive_tests`, `flua_tests`, `flua_pct_positive`, `flub_positive_tests`, `flub_tests`, `flub_pct_positive`, `rsv_tests`, `rsv_positive_tests`, `rsv_pct_positive`, `hpiv_tests`, `hpiv1_positive_tests`, `hpiv2_positive_tests`, `hpiv3_positive_tests`, `hpiv4_positive_tests`, `hpivother_positive_tests`, `hpiv_positive_tests`, `hpiv_pct_positive`, `adv_tests`, `adv_positive_tests`, `adv_pct_positive`, `hmpv_tests`, `hmpv_positive_tests`, `hmpv_pct_positive`, `evrv_tests`, `evrv_positive_tests`, `evrv_pct_positive`, `hcov_tests`, `hcov_positive_tests`, `hcov_pct_positive`, `year`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (201212,20120412,"week",20120417,'province','on',10.0,1.0,10.0,20.0, 10.0, 50.0, 1.0, 1.0, 1.0, 5.0, 20.0, 25.0, 4.0, 20.0, 20.0, 30.0, 3.0, 10.0, 40.0, 2.0, 2.0, 2.0, 1.0, 1.0, 8.0, 20.0, 40.0, 16.0, 40.0, 10.0, 2.0, 20.0, 1.0, 0.0, 0.0, 24.0, 3.0, 12.5, 2012),
        )
        self.cnx.commit()

        response = self.epidata_client.rvdss(geo_type="province", time_values = 201212,geo_value="on")
        self.assertEqual(
            response,
            {
                "epidata": [
                    { "geo_type":"province",
                      "geo_value":"on",
                      "time_type":"week",
                      "epiweek":201212,
                      "time_value":20120412,
                      "issue":20120417,
                      "year":2012,
                      "adv_pct_positive":40.0,
                      "adv_positive_tests":16.0,
                      "adv_tests":40.0,
                      "evrv_pct_positive":0.0,
                      "evrv_positive_tests":0.0,
                      "evrv_tests":1.0,
                      "flu_pct_positive":50.0,
                      "flu_positive_tests":10.0,
                      "flu_tests":20.0,
                      "flua_pct_positive":25.0,
                      "flua_positive_tests":5.0,
                      "flua_tests":20.0,
                      "fluah1n1pdm09_positive_tests":1.0,
                      "fluah3_positive_tests":1.0,
                      "fluauns_positive_tests":1.0,
                      "flub_pct_positive":20.0,
                      "flub_positive_tests":4.0,
                      "flub_tests":20.0,
                      "hcov_pct_positive":12.5,
                      "hcov_positive_tests":3.0,
                      "hcov_tests":24.0, 
                      "hmpv_pct_positive":20.0,
                      "hmpv_positive_tests":2.0,
                      "hmpv_tests":10.0,
                      "hpiv1_positive_tests":2.0,
                      "hpiv2_positive_tests":2.0,
                      "hpiv3_positive_tests":2.0,
                      "hpiv4_positive_tests":1.0,
                      "hpiv_pct_positive":20.0,
                      "hpiv_positive_tests":8.0,
                      "hpiv_tests":40.0,
                      "hpivother_positive_tests":1.0,
                      "rsv_pct_positive":10.0,
                      "rsv_positive_tests":3.0,
                      "rsv_tests":30.0,
                      "sarscov2_pct_positive":10.0,
                      "sarscov2_positive_tests":1.0,
                      "sarscov2_tests":10.0
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
