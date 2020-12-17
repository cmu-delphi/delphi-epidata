"""Integration tests for acquisition of COVID hospitalization facility."""

# standard library
import unittest
from unittest.mock import MagicMock

# first party
from delphi.epidata.acquisition.covid_hosp.common.database import Database
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.facility.update'


class AcquisitionTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # clear relevant tables
    with Database.connect() as db:
      with db.new_cursor() as cur:
        cur.execute('truncate table covid_hosp_facility')
        cur.execute('truncate table covid_hosp_meta')

  def test_acquire_dataset(self):
    """Acquire a new dataset."""

    # only mock out network calls to external hosts
    mock_network = MagicMock()
    mock_network.fetch_metadata.return_value = \
        self.test_utils.load_sample_metadata()
    mock_network.fetch_dataset.return_value = \
        self.test_utils.load_sample_dataset()

    # make sure the data does not yet exist
    with self.subTest(name='no data yet'):
      response = Epidata.covid_hosp_facility(
          '450822', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], -2)

    # acquire sample data into local database
    with self.subTest(name='first acquisition'):
      acquired = Update.run(network=mock_network)
      self.assertTrue(acquired)

    # make sure the data now exists
    with self.subTest(name='initial data checks'):
      response = Epidata.covid_hosp_facility(
          '450822', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
      row = response['epidata'][0]
      self.assertEqual(row['hospital_pk'], '450822')
      self.assertEqual(row['collection_week'], 20201030)
      self.assertEqual(row['publication_date'], 20201208)
      self.assertEqual(row['previous_day_total_ed_visits_7_day_sum'], 536)
      self.assertAlmostEqual(row['total_beds_7_day_avg'], 69.3)
      self.assertEqual(
          row['previous_day_admission_influenza_confirmed_7_day_sum'], -999999)

      # expect 94 fields per row (95 database columns, except `id`)
      self.assertEqual(len(row), 94)

    # re-acquisition of the same dataset should be a no-op
    with self.subTest(name='second acquisition'):
      acquired = Update.run(network=mock_network)
      self.assertFalse(acquired)

    # make sure the data still exists
    with self.subTest(name='final data checks'):
      response = Epidata.covid_hosp_facility(
          '450822', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
