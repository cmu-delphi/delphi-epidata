"""Integration tests for acquisition of COVID hospitalization."""

# standard library
from datetime import date
import unittest
from unittest.mock import patch

# third party
from freezegun import freeze_time
import pandas as pd

# first party
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database
from delphi.epidata.acquisition.covid_hosp.common.test_utils import CovidHospTestCase, UnitTestUtils
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.acquisition.covid_hosp.common.network import Network
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething

# py3tester coverage target (equivalent to `import *`)
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.update'


class AcquisitionTests(CovidHospTestCase):

  db_class = Database
  test_util_context = __file__

  @freeze_time("2021-03-16")
  def test_acquire_dataset(self):
    """Acquire a new dataset."""

    # make sure the data does not yet exist
    with self.subTest(name='no data yet'):
      response = Epidata.covid_hosp('MA', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], -2, response)

    # acquire sample data into local database
    # mock out network calls to external hosts
    with self.subTest(name='first acquisition'), \
         patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()) as mock_fetch_meta, \
         patch.object(Network, 'fetch_dataset', side_effect=[self.test_utils.load_sample_dataset("dataset0.csv"), # dataset for 3/13
                                                             self.test_utils.load_sample_dataset("dataset0.csv"), # first dataset for 3/15
                                                             self.test_utils.load_sample_dataset()] # second dataset for 3/15
                      ):
      acquired = Database().update_dataset()
      self.assertTrue(acquired)
      self.assertEqual(mock_fetch_meta.call_count, 1)

    # make sure the data now exists
    with self.subTest(name='initial data checks'):
      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
      row = response['epidata'][0]
      self.assertEqual(row['state'], 'WY')
      self.assertEqual(row['date'], 20201209)
      self.assertEqual(row['issue'], 20210315)
      self.assertEqual(row['critical_staffing_shortage_today_yes'], 8)
      self.assertEqual(row['total_patients_hospitalized_confirmed_influenza_covid_coverage'], 56)
      actual = row['inpatient_bed_covid_utilization']
      expected = 0.11729857819905214
      self.assertAlmostEqual(actual, expected)
      self.assertIsNone(row['critical_staffing_shortage_today_no'])

      # Expect len(row) to equal the amount of dynamic columns + one extra issue column
      self.assertEqual(len(row), len(list(CovidHospSomething().columns('state_daily'))) + 1)

    with self.subTest(name='all date batches acquired'):
      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101), issues=20210313)
      self.assertEqual(response['result'], 1)

    # re-acquisition of the same dataset should be a no-op
    with self.subTest(name='second acquisition'), \
         patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()), \
         patch.object(Network, 'fetch_dataset', return_value=self.test_utils.load_sample_dataset()):
      acquired = Database().update_dataset()
      self.assertFalse(acquired)

    # make sure the data still exists
    with self.subTest(name='final data checks'):
      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)


  @freeze_time("2021-03-16")
  def test_acquire_specific_issue(self):
    """Acquire a new dataset."""

    # make sure the data does not yet exist
    with self.subTest(name='no data yet'):
      response = Epidata.covid_hosp('MA', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], -2)

    # acquire sample data into local database
    # mock out network calls to external hosts
    with Database().connect() as db:
      pre_max_issue = db.get_max_issue()
    self.assertEqual(pre_max_issue, pd.Timestamp('1900-01-01 00:00:00'))
    with self.subTest(name='first acquisition'), \
         patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()), \
         patch.object(Network, 'fetch_dataset', side_effect=[self.test_utils.load_sample_dataset("dataset0.csv")]):
      acquired = Database().update_dataset(date(2021, 3, 12), date(2021, 3, 14))
      with Database().connect() as db:
        post_max_issue = db.get_max_issue()
      self.assertEqual(post_max_issue, pd.Timestamp('2021-03-13 00:00:00'))
      self.assertTrue(acquired)
