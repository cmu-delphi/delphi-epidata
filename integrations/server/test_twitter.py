# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class TwitterTest(DelphiTestBase):
    """Basic integration tests for twitter endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["twitter"]
        self.role_name = "twitter"

    def test_twitter(self):
        """Basic integration test for twitter endpoint"""

        self.cur.execute(
            'INSERT INTO `twitter`(`date`, `state`, `num`, `total`) VALUES ("2015-07-29", "AK", "1", "223"), ("2020-07-29", "CT", "12", "778")',
        )
        self.cnx.commit()
        response = self.epidata_client.twitter(auth="twitter_key", locations="cen9", dates="20150701-20160101")
        self.assertEqual(
            response,
            {
                "epidata": [{"location": "cen9", "date": "2015-07-29", "num": 1, "total": 223, "percent": 0.4484}],
                "result": 1,
                "message": "success",
            },
        )
