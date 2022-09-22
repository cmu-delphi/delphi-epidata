"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest
import base64

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._query import (
    date_string,
    to_condition,
    filter_strings,
    filter_integers,
    filter_dates,
    filter_geo_pairs,
    filter_source_signal_pairs,
    filter_time_pairs,
)
from delphi.epidata.server._params import (
    GeoPair,
    TimePair,
    SourceSignalPair,
)

# py3tester coverage target
__test_target__ = "delphi.epidata.server._query"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_date_string(self):
        self.assertEqual(date_string(20200101), "2020-01-01")

    def test_to_condition(self):
        params = {}
        self.assertEqual(to_condition("a", 0, "a", params), "a = :a")
        self.assertEqual(params, {"a": 0})
        params = {}
        self.assertEqual(to_condition("a", (1, 4), "a", params), "a BETWEEN :a AND :a_2")
        self.assertEqual(params, {"a": 1, "a_2": 4})

    def test_filter_strings(self):
        params = {}
        self.assertEqual(filter_strings("a", None, "a", params), "FALSE")
        self.assertEqual(params, {})
        params = {}
        self.assertEqual(filter_strings("a", ["1"], "a", params), "(a = :a_0)")
        self.assertEqual(params, {"a_0": "1"})
        params = {}
        self.assertEqual(filter_strings("a", ["1", "2"], "a", params), "(a = :a_0 OR a = :a_1)")
        self.assertEqual(params, {"a_0": "1", "a_1": "2"})
        params = {}
        self.assertEqual(
            filter_strings("a", ["1", "2", ("1", "4")], "a", params),
            "(a = :a_0 OR a = :a_1 OR a BETWEEN :a_2 AND :a_2_2)",
        )
        self.assertEqual(params, {"a_0": "1", "a_1": "2", "a_2": "1", "a_2_2": "4"})

    def test_filter_integers(self):
        params = {}
        self.assertEqual(filter_integers("a", None, "a", params), "FALSE")
        self.assertEqual(params, {})
        params = {}
        self.assertEqual(filter_integers("a", [1], "a", params), "(a = :a_0)")
        self.assertEqual(params, {"a_0": 1})
        params = {}
        self.assertEqual(filter_integers("a", [1, 2], "a", params), "(a = :a_0 OR a = :a_1)")
        self.assertEqual(params, {"a_0": 1, "a_1": 2})
        params = {}
        self.assertEqual(
            filter_integers("a", [1, 2, (1, 4)], "a", params),
            "(a = :a_0 OR a = :a_1 OR a BETWEEN :a_2 AND :a_2_2)",
        )
        self.assertEqual(params, {"a_0": 1, "a_1": 2, "a_2": 1, "a_2_2": 4})

    def test_filter_dates(self):
        params = {}
        self.assertEqual(filter_dates("a", None, "a", params), "FALSE")
        self.assertEqual(params, {})
        params = {}
        self.assertEqual(filter_dates("a", [20200101], "a", params), "(a = :a_0)")
        self.assertEqual(params, {"a_0": "2020-01-01"})
        params = {}
        self.assertEqual(
            filter_dates("a", [20200101, 20200102], "a", params),
            "(a BETWEEN :a_0 AND :a_0_2)",
        )
        self.assertEqual(params, {"a_0": "2020-01-01", "a_0_2": "2020-01-02"})
        params = {}
        self.assertEqual(
            filter_dates("a", [20200101, 20200103], "a", params),
            "(a = :a_0 OR a = :a_1)",
        )
        self.assertEqual(params, {"a_0": "2020-01-01", "a_1": "2020-01-03"})
        params = {}
        self.assertEqual(
            filter_dates("a", [20200101, 20200102, (20200101, 20200104)], "a", params),
            "(a BETWEEN :a_0 AND :a_0_2)",
        )
        self.assertEqual(
            params,
            {
                "a_0": "2020-01-01",
                "a_0_2": "2020-01-04"
            },
        )
        params = {}
        self.assertEqual(
            filter_dates("a", [20200101, 20200103, (20200105, 20200107)], "a", params),
            "(a = :a_0 OR a = :a_1 OR a BETWEEN :a_2 AND :a_2_2)",
        )
        self.assertEqual(
            params,
            {
                "a_0": "2020-01-01",
                "a_1": "2020-01-03",
                "a_2": "2020-01-05",
                "a_2_2": "2020-01-07",
            },
        )

    def test_filter_geo_pairs(self):
        with self.subTest("empty"):
            params = {}
            self.assertEqual(filter_geo_pairs("t", "v", [], "p", params), "FALSE")
            self.assertEqual(params, {})
        with self.subTest("*"):
            params = {}
            self.assertEqual(
                filter_geo_pairs("t", "v", [GeoPair("state", True)], "p", params),
                "(t = :p_0t)",
            )
            self.assertEqual(params, {"p_0t": "state"})
        with self.subTest("single"):
            params = {}
            self.assertEqual(
                filter_geo_pairs("t", "v", [GeoPair("state", ["KY"])], "p", params),
                "((t = :p_0t AND (v = :p_0t_0)))",
            )
            self.assertEqual(params, {"p_0t": "state", "p_0t_0": "KY"})
        with self.subTest("multi"):
            params = {}
            self.assertEqual(
                filter_geo_pairs("t", "v", [GeoPair("state", ["KY", "AK"])], "p", params),
                "((t = :p_0t AND (v = :p_0t_0 OR v = :p_0t_1)))",
            )
            self.assertEqual(params, {"p_0t": "state", "p_0t_0": "KY", "p_0t_1": "AK"})
        with self.subTest("multiple pairs"):
            params = {}
            self.assertEqual(
                filter_geo_pairs(
                    "t",
                    "v",
                    [GeoPair("state", True), GeoPair("nation", True)],
                    "p",
                    params,
                ),
                "(t = :p_0t OR t = :p_1t)",
            )
            self.assertEqual(params, {"p_0t": "state", "p_1t": "nation"})
        with self.subTest("multiple pairs with value"):
            params = {}
            self.assertEqual(
                filter_geo_pairs(
                    "t",
                    "v",
                    [GeoPair("state", ["AK"]), GeoPair("nation", ["US"])],
                    "p",
                    params,
                ),
                "((t = :p_0t AND (v = :p_0t_0)) OR (t = :p_1t AND (v = :p_1t_0)))",
            )
            self.assertEqual(
                params,
                {"p_0t": "state", "p_0t_0": "AK", "p_1t": "nation", "p_1t_0": "US"},
            )

    def test_filter_source_signal_pairs(self):
        with self.subTest("empty"):
            params = {}
            self.assertEqual(filter_source_signal_pairs("t", "v", [], "p", params), "FALSE")
            self.assertEqual(params, {})
        with self.subTest("*"):
            params = {}
            self.assertEqual(
                filter_source_signal_pairs("t", "v", [SourceSignalPair("src1", True)], "p", params),
                "(t = :p_0t)",
            )
            self.assertEqual(params, {"p_0t": "src1"})
        with self.subTest("single"):
            params = {}
            self.assertEqual(
                filter_source_signal_pairs("t", "v", [SourceSignalPair("src1", ["sig1"])], "p", params),
                "((t = :p_0t AND (v = :p_0t_0)))",
            )
            self.assertEqual(params, {"p_0t": "src1", "p_0t_0": "sig1"})
        with self.subTest("multi"):
            params = {}
            self.assertEqual(
                filter_source_signal_pairs("t", "v", [SourceSignalPair("src1", ["sig1", "sig2"])], "p", params),
                "((t = :p_0t AND (v = :p_0t_0 OR v = :p_0t_1)))",
            )
            self.assertEqual(params, {"p_0t": "src1", "p_0t_0": "sig1", "p_0t_1": "sig2"})
        with self.subTest("multiple pairs"):
            params = {}
            self.assertEqual(
                filter_source_signal_pairs(
                    "t",
                    "v",
                    [SourceSignalPair("src1", True), SourceSignalPair("src2", True)],
                    "p",
                    params,
                ),
                "(t = :p_0t OR t = :p_1t)",
            )
            self.assertEqual(params, {"p_0t": "src1", "p_1t": "src2"})
        with self.subTest("multiple pairs with value"):
            params = {}
            self.assertEqual(
                filter_source_signal_pairs(
                    "t",
                    "v",
                    [
                        SourceSignalPair("src1", ["sig2"]),
                        SourceSignalPair("src2", ["srcx"]),
                    ],
                    "p",
                    params,
                ),
                "((t = :p_0t AND (v = :p_0t_0)) OR (t = :p_1t AND (v = :p_1t_0)))",
            )
            self.assertEqual(
                params,
                {"p_0t": "src1", "p_0t_0": "sig2", "p_1t": "src2", "p_1t_0": "srcx"},
            )

    def test_filter_time_pairs(self):
        with self.subTest("empty"):
            params = {}
            self.assertEqual(filter_time_pairs("t", "v", [], "p", params), "FALSE")
            self.assertEqual(params, {})
        with self.subTest("*"):
            params = {}
            self.assertEqual(
                filter_time_pairs("t", "v", [TimePair("day", True)], "p", params),
                "(t = :p_0t)",
            )
            self.assertEqual(params, {"p_0t": "day"})
        with self.subTest("single"):
            params = {}
            self.assertEqual(
                filter_time_pairs("t", "v", [TimePair("day", [20201201])], "p", params),
                "((t = :p_0t AND (v = :p_0t_0)))",
            )
            self.assertEqual(params, {"p_0t": "day", "p_0t_0": 20201201})
        with self.subTest("multi"):
            params = {}
            self.assertEqual(
                filter_time_pairs("t", "v", [TimePair("day", [20201201, 20201203])], "p", params),
                "((t = :p_0t AND (v = :p_0t_0 OR v = :p_0t_1)))",
            )
            self.assertEqual(params, {"p_0t": "day", "p_0t_0": 20201201, "p_0t_1": 20201203})
        with self.subTest("range"):
            params = {}
            self.assertEqual(
                filter_time_pairs("t", "v", [TimePair("day", [(20201201, 20201203)])], "p", params),
                "((t = :p_0t AND (v BETWEEN :p_0t_0 AND :p_0t_0_2)))",
            )
            self.assertEqual(params, {"p_0t": "day", "p_0t_0": 20201201, "p_0t_0_2": 20201203})
