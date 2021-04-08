# standard library
import unittest

from delphi.epidata.server.endpoints.covidcast_utils.trend import compute_trend_value, compute_trend_class, TrendEnum, compute_trend, Trend


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