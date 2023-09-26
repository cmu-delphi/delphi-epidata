"""Integration tests for the `fluview` endpoint."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.common.delphi_test_base import DelphiTestBase


class FluviewTests(DelphiTestBase):
  """Tests the `fluview` endpoint."""

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
        10, 11, 12, 13, 14, 15)
    ''')
    self.cnx.commit()

    # make the request
    response = self.epidata_client.fluview('nat', 202020)

    # assert that the right data came back
    self.assertEqual(response, {
      'result': 1,
      'epidata': [{
         'release_date': '2020-04-07',
         'region': 'nat',
         'issue': 202021,
         'epiweek': 202020,
         'lag': 1,
         'num_ili': 2,
         'num_patients': 3,
         'num_providers': 4,
         'num_age_0': 10,
         'num_age_1': 11,
         'num_age_2': 12,
         'num_age_3': 13,
         'num_age_4': 14,
         'num_age_5': 15,
         'wili': 3.14159,
         'ili': 1.41421,
       }],
      'message': 'success',
    })
