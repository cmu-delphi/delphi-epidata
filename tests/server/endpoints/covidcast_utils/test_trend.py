from typing import Tuple
import unittest

from delphi.epidata.server.endpoints.covidcast_utils.trend import compute_trend_value, compute_trend_class, TrendEnum, compute_trend, Trend, compute_trends


class UnitTests(unittest.TestCase):
    def test_compute_trend_value(self):
        with self.subTest("same"):
            self.assertEqual(compute_trend_value(0, 0, 0), 0.0)
            self.assertEqual(compute_trend_value(5, 5, 0), 0.0)
            self.assertEqual(compute_trend_value(5, 5, 2), 0.0)

        with self.subTest("with min 0"):
            self.assertAlmostEqual(compute_trend_value(12, 10, 0), 0.2)
            self.assertAlmostEqual(compute_trend_value(11, 10, 0), 0.1)
            self.assertAlmostEqual(compute_trend_value(10.5, 10, 0), 0.05)
            self.assertAlmostEqual(compute_trend_value(10, 10, 0), 0.0)
            self.assertAlmostEqual(compute_trend_value(9.5, 10, 0), -0.05)
            self.assertAlmostEqual(compute_trend_value(9, 10, 0), -0.1)
            self.assertAlmostEqual(compute_trend_value(8, 10, 0), -0.2)
        with self.subTest("with min 5"):
            self.assertAlmostEqual(compute_trend_value(12 + 5, 10 + 5, 5), 0.2)
            self.assertAlmostEqual(compute_trend_value(11 + 5, 10 + 5, 5), 0.1)
            self.assertAlmostEqual(compute_trend_value(10.5 + 5, 10 + 5, 5), 0.05)
            self.assertAlmostEqual(compute_trend_value(10 + 5, 10 + 5, 5), 0.0)
            self.assertAlmostEqual(compute_trend_value(9.5 + 5, 10 + 5, 5), -0.05)
            self.assertAlmostEqual(compute_trend_value(9 + 5, 10 + 5, 5), -0.1)
            self.assertAlmostEqual(compute_trend_value(8 + 5, 10 + 5, 5), -0.2)
        with self.subTest("basis is min"):
            self.assertAlmostEqual(compute_trend_value(11, 10, 10), 1)
        with self.subTest("current is min"):
            self.assertAlmostEqual(compute_trend_value(10, 15, 10), -1)

    def test_compute_trend_class(self):
        self.assertEqual(compute_trend_class(-0.3), TrendEnum.decreasing)
        self.assertEqual(compute_trend_class(-0.2), TrendEnum.decreasing)
        self.assertEqual(compute_trend_class(-0.1), TrendEnum.decreasing)
        self.assertEqual(compute_trend_class(-0.05), TrendEnum.steady)
        self.assertEqual(compute_trend_class(0), TrendEnum.steady)
        self.assertEqual(compute_trend_class(0.05), TrendEnum.steady)
        self.assertEqual(compute_trend_class(0.1), TrendEnum.increasing)
        self.assertEqual(compute_trend_class(0.2), TrendEnum.increasing)
        self.assertEqual(compute_trend_class(0.3), TrendEnum.increasing)

    def test_compute_trend(self):
        self.assertEqual(
            compute_trend("gt", "gv", "so", "si", 10, 8, [(10, 12), (8, 10), (0, 0)]),
            Trend(
                "gt",
                "gv",
                "so",
                "si",
                date=10,
                value=12,
                basis_date=8,
                basis_value=10,
                basis_trend=TrendEnum.increasing,
                min_date=0,
                min_value=0,
                min_trend=TrendEnum.increasing,
                max_date=10,
                max_value=12,
                max_trend=TrendEnum.steady,
            ),
        )

    def test_compute_trends(self):
        trends = compute_trends("gt", "gv", "so", "si", lambda x: x - 1, [(1, 12), (2, 10), (3, 0)])
        self.assertEqual(len(trends), 3)

        self.assertEqual(
            trends[0],
            Trend(
                "gt",
                "gv",
                "so",
                "si",
                date=1,
                value=12,
                basis_date=None,
                basis_value=None,
                basis_trend=TrendEnum.unknown,
                min_date=3,
                min_value=0,
                min_trend=TrendEnum.increasing,
                max_date=1,
                max_value=12,
                max_trend=TrendEnum.steady,
            ),
        )

        self.assertEqual(
            trends[1],
            Trend(
                "gt",
                "gv",
                "so",
                "si",
                date=2,
                value=10,
                basis_date=1,
                basis_value=12,
                basis_trend=TrendEnum.decreasing,
                min_date=3,
                min_value=0,
                min_trend=TrendEnum.increasing,
                max_date=1,
                max_value=12,
                max_trend=TrendEnum.decreasing,
            ),
        )

        self.assertEqual(
            trends[2],
            Trend(
                "gt",
                "gv",
                "so",
                "si",
                date=3,
                value=0,
                basis_date=2,
                basis_value=10,
                basis_trend=TrendEnum.decreasing,
                min_date=3,
                min_value=0,
                min_trend=TrendEnum.steady,
                max_date=1,
                max_value=12,
                max_trend=TrendEnum.decreasing,
            ),
        )
