from typing import Tuple
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal

from delphi.epidata.server.endpoints.covidcast_utils.correlation import CorrelationResult, lag_join, compute_correlations, compute_correlation, Correlation


def as_df(*tuples: Tuple[int, float]) -> pd.DataFrame:
    df = pd.DataFrame.from_records(tuples, columns=["time_value", "value"])
    df["time_value"] = pd.to_datetime(df["time_value"], format="%Y%m%d")
    return df.set_index("time_value")


def as_xy_df(*tuples: Tuple[float, float]) -> pd.DataFrame:
    return pd.DataFrame.from_records(tuples, columns=["x", "y"])


class UnitTests(unittest.TestCase):
    def test_lag_join(self):
        with self.subTest("all data"):
            x = as_df((20201010, 1), (20201011, 2), (20201012, 3))
            y = as_df((20201010, 11), (20201011, 12), (20201012, 13))
            with self.subTest("lag = 0"):
                # xxx
                # yyy
                self.assertEqual(lag_join(0, x, y).to_dict("records"), [dict(x=1, y=11), dict(x=2, y=12), dict(x=3, y=13)])
            with self.subTest("lag = 1"):
                # xxx
                #  yyy
                self.assertEqual(lag_join(1, x, y).to_dict("records"), [dict(x=2, y=11), dict(x=3, y=12)])
            with self.subTest("lag = -1"):
                #  xxx
                # yyy
                self.assertEqual(lag_join(-1, x, y).to_dict("records"), [dict(x=1, y=12), dict(x=2, y=13)])
        with self.subTest("missing entry"):
            x = as_df((20201010, 1), (20201011, 2), (20201012, 3), (20201013, 4))
            y = as_df((20201010, 11), (20201012, 13), (20201013, 14))
            with self.subTest("lag = 0"):
                # xxxx
                # y yy
                self.assertEqual(lag_join(0, x, y).to_dict("records"), [dict(x=1, y=11), dict(x=3, y=13), dict(x=4, y=14)])
            with self.subTest("lag = 1"):
                # xxxx
                #  y yy
                self.assertEqual(lag_join(1, x, y).to_dict("records"), [dict(x=2, y=11), dict(x=4, y=13)])
            with self.subTest("lag = -1"):
                #  xxxx
                # y yy
                self.assertEqual(lag_join(-1, x, y).to_dict("records"), [dict(x=2, y=13), dict(x=3, y=14)])

    def test_compute_correlation(self):
        with self.subTest("simple"):
            xy = as_xy_df((1, 11), (2, 12), (3, 13))
            self.assertEqual(compute_correlation(xy), Correlation(r2=1, intercept=10, slope=1, samples=3))
        with self.subTest("inverted"):
            xy = as_xy_df((1, 13), (2, 12), (3, 11))
            self.assertEqual(compute_correlation(xy), Correlation(r2=1, intercept=14, slope=-1, samples=3))
        with self.subTest("none"):
            xy = as_xy_df((1, 0), (2, 0), (3, 0))
            self.assertEqual(compute_correlation(xy), Correlation(r2=0, intercept=0, slope=0, samples=3))

    def test_compute_correlations(self):
        x = as_df((20201010, 1), (20201011, 2), (20201012, 3))
        y = as_df((20201010, 11), (20201011, 12), (20201012, 13))

        r = list(compute_correlations("gt", "gv", "so", "si", 2, x, y))
        self.assertEqual(len(r), 5)
        # lag 0
        self.assertEqual(r[2], CorrelationResult("gt", "gv", "so", "si", 0, r2=1, intercept=10, slope=1, samples=3))
