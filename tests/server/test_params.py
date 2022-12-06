"""Unit tests for parameter parsing."""

# standard library
from math import inf
import unittest

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._params import (
    parse_geo_arg,
    parse_single_geo_arg,
    parse_source_signal_arg,
    parse_single_source_signal_arg,
    parse_time_arg,
    parse_day_value,
    parse_week_value,
    parse_day_range_arg,
    parse_day_arg,
    GeoPair,
    TimePair,
    SourceSignalPair,
)
from delphi.epidata.server._exceptions import (
    ValidationFailedException,
)

# py3tester coverage target
__test_target__ = "delphi.epidata.server._params"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_geo_pair(self):
        with self.subTest("*"):
            p = GeoPair("hrr", True)
            self.assertTrue(p.matches("hrr", "any"))
            self.assertFalse(p.matches("msa", "any"))
        with self.subTest("subset"):
            p = GeoPair("hrr", ["a", "b"])
            self.assertTrue(p.matches("hrr", "a"))
            self.assertTrue(p.matches("hrr", "b"))
            self.assertFalse(p.matches("hrr", "c"))
            self.assertFalse(p.matches("msa", "any"))
        with self.subTest("count"):
            self.assertEqual(GeoPair("a", True).count(), inf)
            self.assertEqual(GeoPair("a", False).count(), 0)
            self.assertEqual(GeoPair("a", ["a", "b"]).count(), 2)

    def test_source_signal_pair(self):
        with self.subTest("*"):
            p = SourceSignalPair("src1", True)
            self.assertTrue(p.matches("src1", "any"))
            self.assertFalse(p.matches("src2", "any"))
        with self.subTest("subset"):
            p = SourceSignalPair("src1", ["a", "b"])
            self.assertTrue(p.matches("src1", "a"))
            self.assertTrue(p.matches("src1", "b"))
            self.assertFalse(p.matches("src1", "c"))
            self.assertFalse(p.matches("src2", "any"))
        with self.subTest("count"):
            self.assertEqual(SourceSignalPair("a", True).count(), inf)
            self.assertEqual(SourceSignalPair("a", False).count(), 0)
            self.assertEqual(SourceSignalPair("a", ["a", "b"]).count(), 2)

    def test_time_pair(self):
        with self.subTest("count"):
            self.assertEqual(TimePair("day", True).count(), inf)
            self.assertEqual(TimePair("day", False).count(), 0)
            self.assertEqual(TimePair("day", [20200202, 20200201]).count(), 2)
            self.assertEqual(TimePair("day", [(20200201, 20200202)]).count(), 2)
            self.assertEqual(TimePair("day", [(20200201, 20200205)]).count(), 5)
            self.assertEqual(TimePair("day", [(20200201, 20200205), 20201212]).count(), 6)

    def test_parse_geo_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertEqual(parse_geo_arg(), [])
        with self.subTest("single"):
            with app.test_request_context("/?geo=state:*"):
                self.assertEqual(parse_geo_arg(), [GeoPair("state", True)])
            with app.test_request_context("/?geo=state:AK"):
                self.assertEqual(parse_geo_arg(), [GeoPair("state", ["ak"])])
        with self.subTest("single list"):
            with app.test_request_context("/?geo=state:AK,TK"):
                self.assertEqual(parse_geo_arg(), [GeoPair("state", ["ak", "tk"])])
        with self.subTest("multi"):
            with app.test_request_context("/?geo=state:*;nation:*"):
                self.assertEqual(parse_geo_arg(), [GeoPair("state", True), GeoPair("nation", True)])
            with app.test_request_context("/?geo=state:AK;nation:US"):
                self.assertEqual(
                    parse_geo_arg(),
                    [GeoPair("state", ["ak"]), GeoPair("nation", ["us"])],
                )
            with app.test_request_context("/?geo=state:AK;state:KY"):
                self.assertEqual(
                    parse_geo_arg(),
                    [GeoPair("state", ["ak"]), GeoPair("state", ["ky"])],
                )
        with self.subTest("multi list"):
            with app.test_request_context("/?geo=state:AK,TK;county:42003,40556"):
                self.assertEqual(
                    parse_geo_arg(),
                    [
                        GeoPair("state", ["ak", "tk"]),
                        GeoPair("county", ["42003", "40556"]),
                    ],
                )
        with self.subTest("hybrid"):
            with app.test_request_context("/?geo=nation:*;state:PA;county:42003,42002"):
                self.assertEqual(
                    parse_geo_arg(),
                    [
                        GeoPair("nation", True),
                        GeoPair("state", ["pa"]),
                        GeoPair("county", ["42003", "42002"]),
                    ],
                )

        with self.subTest("wrong"):
            with app.test_request_context("/?geo=abc"):
                self.assertRaises(ValidationFailedException, parse_geo_arg)
            with app.test_request_context("/?geo=state=4"):
                self.assertRaises(ValidationFailedException, parse_geo_arg)

    def test_single_parse_geo_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, parse_single_geo_arg, "geo")
        with self.subTest("single"):
            with app.test_request_context("/?geo=state:AK"):
                self.assertEqual(parse_single_geo_arg("geo"), GeoPair("state", ["ak"]))
        with self.subTest("single list"):
            with app.test_request_context("/?geo=state:AK,TK"):
                self.assertRaises(ValidationFailedException, parse_single_geo_arg, "geo")
        with self.subTest("multi"):
            with app.test_request_context("/?geo=state:*;nation:*"):
                self.assertRaises(ValidationFailedException, parse_single_geo_arg, "geo")
        with self.subTest("wrong"):
            with app.test_request_context("/?geo=abc"):
                self.assertRaises(ValidationFailedException, parse_single_geo_arg, "geo")
            with app.test_request_context("/?geo=state=4"):
                self.assertRaises(ValidationFailedException, parse_single_geo_arg, "geo")

    def test_parse_source_signal_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertEqual(parse_source_signal_arg(), [])
        with self.subTest("single"):
            with app.test_request_context("/?signal=src1:*"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair("src1", True)])
            with app.test_request_context("/?signal=src1:sig1"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair("src1", ["sig1"])])
        with self.subTest("single list"):
            with app.test_request_context("/?signal=src1:sig1,sig2"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [SourceSignalPair("src1", ["sig1", "sig2"])],
                )
        with self.subTest("multi"):
            with app.test_request_context("/?signal=src1:*;src2:*"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [SourceSignalPair("src1", True), SourceSignalPair("src2", True)],
                )
            with app.test_request_context("/?signal=src1:sig1;src2:sig3"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalPair("src1", ["sig1"]),
                        SourceSignalPair("src2", ["sig3"]),
                    ],
                )
            with app.test_request_context("/?signal=src1:sig1;src1:sig4"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalPair("src1", ["sig1"]),
                        SourceSignalPair("src1", ["sig4"]),
                    ],
                )
        with self.subTest("multi list"):
            with app.test_request_context("/?signal=src1:sig1,sig2;county:sig5,sig6"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalPair("src1", ["sig1", "sig2"]),
                        SourceSignalPair("county", ["sig5", "sig6"]),
                    ],
                )
        with self.subTest("hybrid"):
            with app.test_request_context("/?signal=src2:*;src1:sig4;src3:sig5,sig6"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalPair("src2", True),
                        SourceSignalPair("src1", ["sig4"]),
                        SourceSignalPair("src3", ["sig5", "sig6"]),
                    ],
                )

        with self.subTest("wrong"):
            with app.test_request_context("/?signal=abc"):
                self.assertRaises(ValidationFailedException, parse_source_signal_arg)
            with app.test_request_context("/?signal=sig=4"):
                self.assertRaises(ValidationFailedException, parse_source_signal_arg)

    def test_single_parse_source_signal_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, parse_single_source_signal_arg, "signal")
        with self.subTest("single"):
            with app.test_request_context("/?signal=src1:sig1"):
                self.assertEqual(parse_single_source_signal_arg("signal"), SourceSignalPair("src1", ["sig1"]))
        with self.subTest("single list"):
            with app.test_request_context("/?signal=src1:sig1,sig2"):
                self.assertRaises(ValidationFailedException, parse_single_source_signal_arg, "signal")
        with self.subTest("multi"):
            with app.test_request_context("/?signal=src2:*;src1:*"):
                self.assertRaises(ValidationFailedException, parse_single_source_signal_arg, "signal")
        with self.subTest("wrong"):
            with app.test_request_context("/?signal=abc"):
                self.assertRaises(ValidationFailedException, parse_single_source_signal_arg, "signal")
            with app.test_request_context("/?signal=sig=4"):
                self.assertRaises(ValidationFailedException, parse_single_source_signal_arg, "signal")

    def test_parse_week_value(self):
        with app.test_request_context(""):
            with self.subTest("delphi week"):
                self.assertEqual(parse_week_value("202001"), 202001)
            with self.subTest("delphi week range"):
                self.assertEqual(parse_week_value("202001-202104"), (202001, 202104))
            with self.subTest("wrong"):
                self.assertRaises(ValidationFailedException, parse_week_value, "")
                self.assertRaises(ValidationFailedException, parse_week_value, "x")
                self.assertRaises(ValidationFailedException, parse_week_value, "2020")
                self.assertRaises(ValidationFailedException, parse_week_value, "20200100")
                self.assertRaises(ValidationFailedException, parse_week_value, "2020-03-11")
                self.assertRaises(ValidationFailedException, parse_week_value, "2020-02-30---20200403")

    def test_parse_day_value(self):
        with app.test_request_context(""):
            with self.subTest("delphi date"):
                self.assertEqual(parse_day_value("20200101"), 20200101)
            with self.subTest("iso date"):
                self.assertEqual(parse_day_value("2020-01-01"), 20200101)
            with self.subTest("delphi date range"):
                self.assertEqual(parse_day_value("20200101-20210404"), (20200101, 20210404))
            with self.subTest("iso date range"):
                self.assertEqual(parse_day_value("2020-01-01--2021-04-04"), (20200101, 20210404))

            with self.subTest("wrong"):
                self.assertRaises(ValidationFailedException, parse_day_value, "")
                self.assertRaises(ValidationFailedException, parse_day_value, "x")
                self.assertRaises(ValidationFailedException, parse_day_value, "2020")
                self.assertRaises(ValidationFailedException, parse_day_value, "202001")
                self.assertRaises(ValidationFailedException, parse_day_value, "2020-03-111")
                self.assertRaises(ValidationFailedException, parse_day_value, "2020-02-30---20200403")

    def test_parse_time_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertEqual(parse_time_arg(), None)
        with self.subTest("single"):
            with app.test_request_context("/?time=day:*"):
                self.assertEqual(parse_time_arg(), TimePair("day", True))
            with app.test_request_context("/?time=day:20201201"):
                self.assertEqual(parse_time_arg(), TimePair("day", [20201201]))
        with self.subTest("single list"):
            with app.test_request_context("/?time=day:20201201,20201202"):
                self.assertEqual(parse_time_arg(), TimePair("day", [20201201, 20201202]))
        with self.subTest("single range"):
            with app.test_request_context("/?time=day:20201201-20201204"):
                self.assertEqual(parse_time_arg(), TimePair("day", [(20201201, 20201204)]))
        with self.subTest("multi"):
            with app.test_request_context("/?time=day:*;day:20201201"):
                self.assertEqual(
                    parse_time_arg(),
                    TimePair("day", True)
                )
            with app.test_request_context("/?time=week:*;week:202012"):
                self.assertEqual(
                    parse_time_arg(),
                    TimePair("week", True)
                )
            with app.test_request_context("/?time=day:20201201;day:20201202-20201205"):
                self.assertEqual(
                    parse_time_arg(),
                    TimePair("day", [(20201201, 20201205)])
                )
            with app.test_request_context("/?time=week:202012;week:202013-202015"):
                self.assertEqual(
                    parse_time_arg(),
                    TimePair("week", [(202012, 202015)])
                )

        with self.subTest("wrong"):
            with app.test_request_context("/?time=abc"):
                self.assertRaises(ValidationFailedException, parse_time_arg)
            with app.test_request_context("/?time=sig=4"):
                self.assertRaises(ValidationFailedException, parse_time_arg)
            with app.test_request_context("/?time=month:201210"):
                self.assertRaises(ValidationFailedException, parse_time_arg)
            with app.test_request_context("/?time=week:20121010"):
                self.assertRaises(ValidationFailedException, parse_time_arg)
            with app.test_request_context("/?time=day:*;week:*"):
                self.assertRaisesRegex(ValidationFailedException, "mixes \"day\" and \"week\" time types", parse_time_arg)
            with app.test_request_context("/?time=day:20201201;week:202012"):
                self.assertRaisesRegex(ValidationFailedException, "mixes \"day\" and \"week\" time types", parse_time_arg)
            with app.test_request_context("/?time=day:*;day:20202012;week:202101-202104"):
                self.assertRaisesRegex(ValidationFailedException, "mixes \"day\" and \"week\" time types", parse_time_arg)

    def test_parse_day_range_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
        with self.subTest("single"):
            with app.test_request_context("/?time=*"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
            with app.test_request_context("/?time=20201201"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
        with self.subTest("single list"):
            with app.test_request_context("/?time=20201201,20201202"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
        with self.subTest("single range"):
            with app.test_request_context("/?time=20201201-20201204"):
                self.assertEqual(parse_day_range_arg("time"), (20201201, 20201204))
        with self.subTest("wrong"):
            with app.test_request_context("/?time=abc"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
            with app.test_request_context("/?time=sig=4"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
            with app.test_request_context("/?time=month:201210"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")
            with app.test_request_context("/?time=week:20121010"):
                self.assertRaises(ValidationFailedException, parse_day_range_arg, "time")

    def test_parse_day_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
        with self.subTest("single"):
            with app.test_request_context("/?time=*"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
            with app.test_request_context("/?time=20201201"):
                self.assertEqual(parse_day_arg("time"), 20201201)
        with self.subTest("single list"):
            with app.test_request_context("/?time=20201201,20201202"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
        with self.subTest("single range"):
            with app.test_request_context("/?time=20201201-20201204"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
        with self.subTest("wrong"):
            with app.test_request_context("/?time=abc"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
            with app.test_request_context("/?time=sig=4"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
            with app.test_request_context("/?time=month:201210"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
            with app.test_request_context("/?time=week:20121010"):
                self.assertRaises(ValidationFailedException, parse_day_arg, "time")
