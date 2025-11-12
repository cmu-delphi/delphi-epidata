# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class rvdssTest(DelphiTestBase):
    """Basic integration tests for rvdss endpoint."""

    def localSetUp(self):
        self.truncate_tables_list = ["rvdss_repiratory_detections",
                                     "rvdss_pct_positive",
                                     "rvdss_detections_counts"]

    def test_rvdss_repiratory_detections(self):
        """Basic integration test for rvdss_repiratory_detections endpoint"""
        self.cur.execute(
            "INSERT INTO `rvdss_repiratory_detections`(`epiweek`, `time_value`, `issue`, `geo_type`, `geo_value`, `sarscov2_tests`, `sarscov2_positive_tests`, `flu_tests`, `flu_positive_tests`, `fluah1n1pdm09_positive_tests`, `fluah3_positive_tests`, `fluauns_positive_tests`, `flua_positive_tests`, `flub_positive_tests`, `rsv_tests`, `rsv_positive_tests`, `hpiv_tests`, `hpiv1_positive_tests`, `hpiv2_positive_tests`, `hpiv3_positive_tests`, `hpiv4_positive_tests`, `hpivother_positive_tests`, `adv_tests`, `adv_positive_tests`, `hmpv_tests`, `hmpv_positive_tests`, `evrv_tests`, `evrv_positive_tests`, `hcov_tests`, `hcov_positive_tests`, `week`, `weekorder`, `year`) VALUES(%(epiweek)s, %(time_value)s, %(issue)s, %(geo_type)s, %(geo_value)s, %(sarscov2_tests)s, %(sarscov2_positive_tests)s, %(flu_tests)s, %(flu_positive_tests)s, %(fluah1n1pdm09_positive_tests)s, %(fluah3_positive_tests)s, %(fluauns_positive_tests)s, %(flua_positive_tests)s, %(flub_positive_tests)s, %(rsv_tests)s, %(rsv_positive_tests)s, %(hpiv_tests)s, %(hpiv1_positive_tests)s, %(hpiv2_positive_tests)s, %(hpiv3_positive_tests)s, %(hpiv4_positive_tests)s, %(hpivother_positive_tests)s, %(adv_tests)s, %(adv_positive_tests)s, %(hmpv_tests)s, %(hmpv_positive_tests)s, %(evrv_tests)s, %(evrv_positive_tests)s, %(hcov_tests)s, %(hcov_positive_tests)s, %(week)s, %(weekorder)s, %(year)s)",
            ("201212", "2012-04-12", "2012-04-17", "region","on", "10", "1", "9", "1", "0", "0", "2", "3", "1", "8", "2", "7", "1", "1", "1", "1","1", "6", "5", "100", "13", "92", "9", "167", "52", "12", "34", "2012"),
        )
        self.cnx.commit()
        response = self.epidata_client.rvdss_repiratory_detections(epiweeks=201212, geo_value="on")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {'epiweek':201212,
                     'time_value':"2012-04-12",
                     'issue':"2012-04-17",
                     'geo_type':"region",
                     'geo_value':"on",
                     'sarscov2_tests':10,
                     'sarscov2_positive_tests':1,
                     'flu_tests':9,
                     'flu_positive_tests':1,
                     'fluah1n1pdm09_positive_tests':0,
                     'fluah3_positive_tests':0,
                     'fluauns_positive_tests':2,
                     'flua_positive_tests':3,
                     'flub_positive_tests':1,
                     'rsv_tests':8,
                     'rsv_positive_tests':2,
                     'hpiv_tests':8,
                     'hpiv1_positive_tests':1,
                     'hpiv2_positive_tests':1,
                     'hpiv3_positive_tests':1,
                     'hpiv4_positive_tests':1,
                     'hpivother_positive_tests':1,
                     'adv_tests':6,
                     'adv_positive_tests':5,
                     'hmpv_tests':100,
                     'hmpv_positive_tests':13,
                     'evrv_tests':92,
                     'evrv_positive_tests':9,
                     'hcov_tests':167,
                     'hcov_positive_tests':52,
                     'week':12,
                     'weekorder':34,
                     'year':2012
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
        
    def test_rvdss_pct_positive(self):
        """Basic integration test for rvdss_pct_positive endpoint"""
        self.cur.execute(
            "INSERT INTO rvdss_pct_positive (`epiweek`, `time_value`, `issue`, `geo_type`, `geo_value`, `evrv_pct_positive`, `evrv_tests`, `evrv_positive_tests`, `hpiv_pct_positive`, `hpiv_tests`, `hpiv_positive_tests`, `adv_pct_positive`, `adv_tests`, `adv_positive_tests`,`hcov_pct_positive`, `hcov_tests`, `hcov_positive_tests`, `flua_pct_positive`, `flub_pct_positive`, `flu_tests`, `flua_positive_tests`, `flua_tests`, `flub_tests`, `flub_positive_tests`, `flu_positive_tests`, `flu_pct_positive`, `hmpv_pct_positive`, `hmpv_tests`, `hmpv_positive_tests`, `rsv_pct_positive`, `rsv_tests`, `rsv_positive_tests`, `sarscov2_pct_positive`, `sarscov2_tests`, `sarscov2_positive_tests`, `region`, `week`, `weekorder`, `year`) VALUES (%(epiweek)s, %(time_value)s, %(issue)s, %(geo_type)s, %(geo_value)s, %(evrv_pct_positive)s, %(evrv_tests)s, %(evrv_positive_tests)s, %(hpiv_pct_positive)s, %(hpiv_tests)s, %(hpiv_positive_tests)s, %(adv_pct_positive)s, %(adv_tests)s, %(hcov_pct_positive)s, %(hcov_tests)s, %(hcov_positive_tests)s, %(flua_pct_positive)s, %(flub_pct_positive)s, %(flu_tests)s, %(flua_positive_tests)s, %(flua_tests)s, %(flub_tests)s, %(flub_positive_tests)s, %(flu_positive_tests)s, %(flu_pct_positive)s, %(hmpv_pct_positive)s, %(hmpv_tests)s, %(hmpv_positive_tests)s, %(rsv_pct_positive)s, %(rsv_tests)s, %(rsv_positive_tests)s, %(sarscov2_pct_positive)s, %(sarscov2_tests)s, %(sarscov2_positive_tests)s, %(region)s, %(week)s, %(weekorder)s, %(year)s)",
            ("201212", "2012-04-12", "2012-04-17", "region","on","0.1","10","1","0.1","10","1","0.1","10","1","0.1","10","1","0.05","0.05","100", "10", "100","100", "10", "20", "0.1","0.1","10","1","0.1","10","1","0.1","10","1","on","12","34","2012")
        )
        self.cnx.commit()
        response = self.epidata_client.rvdss_pct_positive(epiweeks=201212, geo_value="on")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {'epiweek':201212,
                     'time_value':"2012-04-12",
                     'issue':"2012-04-17",
                     'geo_type':"region",
                     'geo_value':"on",
                     'evrv_pct_positive':0.1,
                     'evrv_tests':10,
                     'evrv_positive_tests':1,
                     'hpiv_pct_positive':0.1,
                     'hpiv_tests':10,
                     'hpiv_positive_tests':1,
                     'adv_pct_positive':0.1,
                     'adv_tests':10,
                     'adv_positive_tests':1,
                     'hcov_pct_positive':0.1,
                     'hcov_tests':10,
                     'hcov_positive_tests':1,
                     'flua_pct_positive':0.05,
                     'flub_pct_positive':0.05,
                     'flu_tests':100,
                     'flua_positive_tests':10,
                     'flua_tests':100,
                     'flub_tests':100,
                     'flub_positive_tests':10,
                     'flu_positive_tests':20,
                     'flu_pct_positive':0.1,
                     'hmpv_pct_positive':0.1,
                     'hmpv_tests':10,
                     'hmpv_positive_tests':1,
                     'rsv_pct_positive':0.1,
                     'rsv_tests':10,
                     'rsv_positive_tests':1,
                     'sarscov2_pct_positive':0.1,
                     'sarscov2_tests':10,
                     'sarscov2_positive_tests':1,
                     'region':"on",
                     'week':12,
                     'weekorder':34,
                     'year':2012
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
        
    def test_rvdss_detections_counts(self):
        """Basic integration test for rvdss_detections_counts endpoint"""
        self.cur.execute(
            "INSERT INTO rvdss_detections_counts (`epiweek`, `time_value`, `issue`, `geo_type`, `geo_value`, `hpiv_positive_tests`, `adv_positive_tests`, `hmpv_positive_tests`, `evrv_positive_tests`, `hcov_positive_tests`, `rsv_positive_tests`, `flu_positive_tests`) VALUES (%(epiweek)s, %(time_value)s, %(issue)s, %(geo_type)s, %(geo_value)s, %(hpiv_positive_tests)s, %(adv_positive_tests)s, %(hmpv_positive_tests)s, %(evrv_positive_tests)s, %(hcov_positive_tests)s, %(rsv_positive_tests)s, %(flu_positive_tests)s)",
            ("201212", "2012-04-12", "2012-04-17", "nation","ca", "10", "9", "8", "7", "6", "5", "4"),
        )
        self.cnx.commit()
        response = self.epidata_client.rvdss_detections_counts(epiweeks=201212, geo_value="ca")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {'epiweek':201212,
                     'time_value':"2012-04-12",
                     'issue':"2012-04-17",
                     'geo_type':"nation",
                     'geo_value':"ca",
                     'hpiv_positive_tests':10,
                     'adv_positive_tests':9,
                     'hmpv_positive_tests':8,
                     'evrv_positive_tests':7,
                     'hcov_positive_tests':6,
                     'rsv_positive_tests':5,
                     'flu_positive_tests':4
                    }
                ],
                "result": 1,
                "message": "success",
            },
        )
