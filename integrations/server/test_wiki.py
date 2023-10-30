# first party
from delphi.epidata.common.integration_test_base_class import DelphiTestBase


class WikiTest(DelphiTestBase):
    """Basic integration tests for wiki endpint."""

    def localSetUp(self):
        self.truncate_tables_list = ["wiki", "wiki_meta"]

    def test_wiki(self):
        """Basic integration test for wiki endpoint"""

        self.cur.execute(
            'INSERT INTO `wiki`(`datetime`, `article`, `count`, `language`) VALUES ("2007-12-09 18:00:00", "amantadine", "3", "en"), ("2008-12-09 18:00:00", "test", "5", "en")',
        )
        self.cur.execute(
            'INSERT INTO `wiki_meta`(`datetime`, `date`, `epiweek`, `total`, `language`) VALUES ("2007-12-09 18:00:00", "2007-12-09", "200750", "969214", "en"), ("2008-12-09 18:00:00", "2008-12-09", "200750", "123321", "en")'
        )
        self.cnx.commit()
        response = self.epidata_client.wiki(articles="test", epiweeks="200701-200801")
        self.assertEqual(
            response,
            {
                "epidata": [
                    {"article": "test", "count": 5, "total": 123321, "hour": -1, "epiweek": 200750, "value": 40.544595}
                ],
                "result": 1,
                "message": "success",
            },
        )
