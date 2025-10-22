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
            (201212,20120412,"week",20120417,'province','on',10,1,10,20, 10, 50, 1, 1, 1, 5, 20, 25, 4, 20, 20, 30, 3, 10, 40, 2, 2, 2, 1, 1, 8, 20, 40, 16, 40, 10, 2, 20, 1, 0, 0, 24, 3, 12.5, 2012),
        )
        self.cnx.commit()

        response = self.epidata_client.rvdss(geo_type="province", time_values = 201212,geo_value="on")
        self.assertEqual(
            response,
            {
                "epidata": [
                    { "epiweek":201212,
                      "time_value":20120412,
                      "time_type":"week",
                      "issue":20120417,
                      "geo_type":"province",
                      "geo_value":"on",
                      "sarscov2_tests":10,
                      "sarscov2_positive_tests":1,
                      "sarscov2_pct_positive":10,
                      "flu_tests":20,
                      "flu_positive_tests":10,
                      "flu_pct_positive":50,
                      "fluah1n1pdm09_positive_tests":1,
                      "fluah3_positive_tests":1,
                      "fluauns_positive_tests":1,
                      "flua_positive_tests":5,
                      "flua_tests":20,
                      "flua_pct_positive":25,
                      "flub_positive_tests":4,
                      "flub_tests":20,
                      "flub_pct_positive":25,
                      "rsv_tests":30,
                      "rsv_positive_tests":3,
                      "rsv_pct_positive":10,
                      "hpiv_tests":40,
                      "hpiv1_positive_tests":2,
                      "hpiv2_positive_tests":2,
                      "hpiv3_positive_tests":2,
                      "hpiv4_positive_tests":1,
                      "hpivother_positive_tests":1,
                      "hpiv_positive_tests":8,
                      "hpiv_pct_positive":20,
                      "adv_tests":40,
                      "adv_positive_tests":16,
                      "adv_pct_positive":40,
                      "hmpv_tests":10,
                      "hmpv_positive_tests":2,
                      "hmpv_pct_positive":20,
                      "evrv_tests":1,
                      "evrv_positive_tests":0,
                      "evrv_pct_positive":0,
                      "hcov_tests":24,
                      "hcov_positive_tests":3,
                      "hcov_pct_positive":12.5,
                      "year":2012
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
