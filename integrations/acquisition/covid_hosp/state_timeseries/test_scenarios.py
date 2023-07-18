"""Integration tests for acquisition of COVID hospitalization."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

# first party
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database
from delphi.epidata.acquisition.covid_hosp.common.network import Network
from delphi.epidata.acquisition.covid_hosp.common.test_utils import CovidHospTestCase, UnitTestUtils
from delphi.epidata.client.delphi_epidata import Epidata
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething

# third party
from freezegun import freeze_time

# py3tester coverage target (equivalent to `import *`)
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_timeseries.update'


class AcquisitionTests(CovidHospTestCase):

  db_class = Database
  test_util_context = __file__
  # TODO: no need for the following after covid_hosp table split is merged
  # (in https://github.com/cmu-delphi/delphi-epidata/pull/1126)
  extra_tables_used = ['covid_hosp_state_daily']

  @freeze_time("2021-03-17")
  def test_acquire_dataset(self):
    """Acquire a new dataset."""

    # make sure the data does not yet exist
    with self.subTest(name='no data yet'):
      response = Epidata.covid_hosp('MA', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], -2)

    # acquire sample data into local database
    with self.subTest(name='first acquisition'), \
         patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()), \
         patch.object(Network, 'fetch_dataset', return_value=self.test_utils.load_sample_dataset()):
      acquired = Database().update_dataset()
      self.assertTrue(acquired)

    # make sure the data now exists
    with self.subTest(name='initial data checks'):
      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101))
      self.assertEqual(response['result'], 1)
      self.assertEqual(len(response['epidata']), 1)
      row = response['epidata'][0]
      self.assertEqual(row['state'], 'WY')
      self.assertEqual(row['date'], 20200826)
      self.assertEqual(row['issue'], 20210315)
      self.assertEqual(row['critical_staffing_shortage_today_yes'], 2)
      self.assertEqual(row['total_patients_hospitalized_confirmed_influenza_covid_coverage'], 56)
      actual = row['inpatient_bed_covid_utilization']
      expected = 0.011946591707659873
      self.assertAlmostEqual(actual, expected)
      self.assertIsNone(row['critical_staffing_shortage_today_no'])

      # Expect len(row) to equal the amount of dynamic columns + one extra issue column
      self.assertEqual(len(row), len(list(CovidHospSomething().columns('state_timeseries'))) + 1)

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

    # acquire new data into local database
    with self.subTest(name='updated acquisition'), \
         patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata("metadata2.csv")), \
         patch.object(Network, 'fetch_dataset', return_value=self.test_utils.load_sample_dataset("dataset2.csv")):
      # acquire new data with 3/16 issue date
      acquired = Database().update_dataset()
      self.assertTrue(acquired)

    with self.subTest(name='as_of checks'):

      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101))
      self.assertEqual(len(response['epidata']), 2)
      row = response['epidata'][1]
      self.assertEqual(row['date'], 20200827)

      # previous data should have 3/15 issue date
      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101), as_of=20210315)
      self.assertEqual(len(response['epidata']), 1)
      row = response['epidata'][0]
      self.assertEqual(row['date'], 20200826)

      # no data before 3/15
      response = Epidata.covid_hosp('WY', Epidata.range(20200101, 20210101), as_of=20210314)
      self.assertEqual(response['result'], -2)
