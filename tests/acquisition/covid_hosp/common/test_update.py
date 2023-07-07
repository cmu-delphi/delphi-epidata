"""Unit tests for update.py."""

# standard library
import unittest
from unittest.mock import patch
from unittest.mock import sentinel

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import UnitTestUtils

# Using state_daily as an example - the update files are identical across datasets
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.update'


class UpdateTests(unittest.TestCase):
  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = UnitTestUtils(__file__)

  def test_merge(self):
    """Merging the set of updates in each batch is pretty tricky"""
    # Generate a set of synthetic updates with overlapping keys
    db = Database()
    keys = list(db.columns_and_types.keys())
    N = 10
    dfs = []
    for i in range(5):
        # knock out every 2nd key, then every 3rd, then every 4th, etc
        dfs.append(pd.DataFrame(dict(
            state=range(1, N, i+1),
            reporting_cutoff_start=range(N+1, 2*N, i+1),
            **{spec[0]: i+1 for spec in keys[2:]}
        )))
    # add a data frame with unseen keys
    dfs.append(pd.DataFrame(dict(
      state=[-1],
      reporting_cutoff_start=[-1],
      **{spec[0]: -1 for spec in keys[2:]}
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
        **{spec[0]: value_from for spec in keys[2:]}
    )).astype({spec[0]: 'float64' for spec in keys[2:]}
    )
    result = Database().merge_by_key_cols(dfs, db.key_columns)
    try:
      pd.testing.assert_frame_equal(result, expected)
    except:
      assert False, f"""
result:
{result}

expected:
{expected}
"""
