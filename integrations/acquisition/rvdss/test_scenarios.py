"""Integration tests for acquisition of rvdss data."""
# standard library
import unittest
from unittest.mock import MagicMock

# first party
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.rvdss.database import update
import delphi.operations.secrets as secrets

# third party
import mysql.connector

# py3tester coverage target (equivalent to `import *`)
# __test_target__ = 'delphi.epidata.acquisition.covid_hosp.facility.update'

NEWLINE="\n"

class AcquisitionTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    # self.test_utils = UnitTestUtils(__file__)

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata'
    Epidata.auth = ('epidata', 'key')

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # clear relevant tables
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata")
    cur = cnx.cursor()
    
    cur.execute('truncate table rvdss_repiratory_detections')
    cur.execute('truncate table rvdss_pct_positive')
    cur.execute('truncate table rvdss_detections_counts')
    cur.execute('delete from api_user')
    cur.execute('insert into api_user(api_key, email) values ("key", "emai")')

  def test_rvdss_repiratory_detections(self):
    # make sure the data does not yet exist
    with self.subTest(name='no data yet'):
      response = Epidata.rvdss_repiratory_detections(
          '450822', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], -2, response)

    # acquire sample data into local database
    with self.subTest(name='first acquisition'):
      acquired = Update.run(network=mock_network)
      self.assertTrue(acquired)

    # make sure the data now exists
    with self.subTest(name='initial data checks'):
      expected_spotchecks = {
        "hospital_pk": "450822",
        "collection_week": 20201030,
        "publication_date": 20210315,
        "previous_day_total_ed_visits_7_day_sum": 536,
        "total_personnel_covid_vaccinated_doses_all_7_day_sum": 18,
        "total_beds_7_day_avg": 69.3,
        "previous_day_admission_influenza_confirmed_7_day_sum": -999999
      }
      response = Epidata.covid_hosp_facility(
          '450822', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 2)
      row = response['epidata'][0]
      for k,v in expected_spotchecks.items():
        self.assertTrue(
          k in row,
          f"no '{k}' in row:\n{NEWLINE.join(sorted(row.keys()))}"
        )
        if isinstance(v, float):
          self.assertAlmostEqual(row[k], v, f"row[{k}] is {row[k]} not {v}")
        else:
          self.assertEqual(row[k], v, f"row[{k}] is {row[k]} not {v}")

      # expect 113 fields per row (114 database columns, except `id`)
      self.assertEqual(len(row), 113)

    # re-acquisition of the same dataset should be a no-op
    with self.subTest(name='second acquisition'):
      acquired = Update.run(network=mock_network)
      self.assertFalse(acquired)

    # make sure the data still exists
    with self.subTest(name='final data checks'):
      response = Epidata.covid_hosp_facility(
          '450822', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 2)

 