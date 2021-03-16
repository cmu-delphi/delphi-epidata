"""Unit tests for update.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.update import Update
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.update'


class UpdateTests(unittest.TestCase):
  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

  def test_run(self):
    """Acquire a new dataset.

    This test is more involved than the other covid_hosp update tests because we
    need to make sure batches are being fetched properly.
    """

    mock_db = MagicMock(spec=Database)
    mock_db.contains_revision.return_value = False
    mock_db.get_max_issue.return_value = pd.Timestamp("2021/3/13")
    sample_dataset = self.test_utils.load_sample_dataset()
    with patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()) as mock_metadata, \
         patch.object(Database, 'connect', return_value=MagicMock()) as mock_connect, \
         patch.object(Network, 'fetch_dataset', return_value=sample_dataset) as mock_fetch:
      # extra level of indirection due to context manager
      mock_connect.return_value.__enter__.return_value = mock_db

      key_cols = ['state', 'reporting_cutoff_start']
      self.assertTrue('state' in sample_dataset.columns)
      self.assertTrue('reporting_cutoff_start' in sample_dataset.columns)
      result = Update.run()

      mock_metadata.assert_called_once()
      mock_connect.assert_called_once()
      mock_fetch.assert_called_with("https://test.csv")

      # don't care what the third argument is, so only test the first two:
      self.assertEqual(mock_db.insert_metadata.call_args.args[0], 20210315)
      self.assertEqual(mock_db.insert_metadata.call_args.args[1], "https://test.csv")

      # can't use assert_called_with to test data frame equality, so check args individually:
      self.assertEqual(mock_db.insert_dataset.call_args.args[0], 20210315)
      self.assertEqual(set(mock_db.insert_dataset.call_args.args[1].columns),
                       set(sample_dataset.columns))
      pd.testing.assert_frame_equal(
        mock_db.insert_dataset.call_args.args[1],
        sample_dataset[mock_db.insert_dataset.call_args.args[1].columns]
      )
      self.assertTrue(result)

  def test_merge(self):
    """Merging the set of updates in each batch is pretty tricky"""
    # Generate a set of synthetic updates with overlapping keys
    N = 10
    dfs = []
    for i in range(5):
        # knock out every 2nd key, then every 3rd, then every 4th, etc
        dfs.append(pd.DataFrame(dict(
            state=range(1, N, i+1),
            reporting_cutoff_start=range(N+1, 2*N, i+1),
            **{spec[0]: i+1 for spec in Database.ORDERED_CSV_COLUMNS[2:]}
        )))
    # add a data frame with unseen keys
    dfs.append(pd.DataFrame(dict(
      state=[-1],
      reporting_cutoff_start=[-1],
      **{spec[0]: -1 for spec in Database.ORDERED_CSV_COLUMNS[2:]}
    )))

    # now we need to know which data frame was used as the final value. the
    # above procedure is a prime number generator, so we can derive the result
    # mathematically:

    # for x in 1..N get the greatest number 5 or less that evenly divides x
    value_from = [[i for i in range(5, 0, -1) if x/i == x//i][0] for x in range(N-1)] + [-1]
    states = list(range(1, N)) + [-1]
    dates = list(range(N+1, 2*N)) + [-1]
    self.assertEqual(len(value_from), len(states))
    self.assertEqual(len(states), len(dates))

    expected = pd.DataFrame(dict(
        state=states,
        reporting_cutoff_start=dates,
        **{spec[0]: value_from for spec in Database.ORDERED_CSV_COLUMNS[2:]}
    )).astype({spec[0]: 'float64' for spec in Database.ORDERED_CSV_COLUMNS[2:]}
    )
    result = Update.merge_by_state_date(dfs)
    try:
      pd.testing.assert_frame_equal(result, expected)
    except:
      assert False, f"""
result:
{result}

expected:
{expected}
"""
