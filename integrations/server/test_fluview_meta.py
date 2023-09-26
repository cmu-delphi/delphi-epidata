"""Integration tests for the `fluview_meta` endpoint."""

# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class FluviewMetaTests(DelphiTestBase):
  """Tests the `fluview_meta` endpoint."""

  def localSetUp(self):
    """Perform per-test setup."""
    self.truncate_tables_list = ["fluview"]

  def test_round_trip(self):
    """Make a simple round-trip with some sample data."""

    # insert dummy data
    self.cur.execute('''
      INSERT INTO 
        `fluview` (`id`, `release_date`, `issue`, `epiweek`, `region`, 
        `lag`, `num_ili`, `num_patients`, `num_providers`, `wili`, `ili`, 
        `num_age_0`, `num_age_1`, `num_age_2`, `num_age_3`, `num_age_4`, `num_age_5`)
      VALUES
        (0, "2020-04-07", 202021, 202020, "nat", 1, 2, 3, 4, 3.14159, 1.41421,
          10, 11, 12, 13, 14, 15),
        (0, "2020-04-28", 202022, 202022, "hhs1", 5, 6, 7, 8, 1.11111, 2.22222,
          20, 21, 22, 23, 24, 25)
    ''')
    self.cnx.commit()

    # make the request
    response = self.epidata_client.fluview_meta()

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
         'latest_update': '2020-04-28',
         'latest_issue': 202022,
         'table_rows': 2,
       }],
      'message': 'success',
    })
