"""Unit tests for parameter parsing."""

# standard library
from math import inf
import unittest

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._params import (
    extract_strings,
    extract_integers,
    extract_integer,
    extract_date,
    extract_dates,
    parse_geo_arg,
    parse_single_geo_arg,
    parse_source_signal_arg,
    parse_single_source_signal_arg,
    parse_time_arg,
    parse_day_value,
    parse_week_value,
    parse_day_range_arg,
    parse_day_arg,
    GeoSet,
    TimeSet,
    SourceSignalSet,
)
from delphi.epidata.server._exceptions import (
    ValidationFailedException,
)
from delphi.epidata.acquisition.covidcast.test_utils import FIPS, MSA

# py3tester coverage target
__test_target__ = "delphi.epidata.server._params"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_geo_set(self):
        with self.subTest("*"):
            p = GeoSet("fips", True)
            self.assertTrue(p.matches("fips", "any"))
            self.assertFalse(p.matches("msa", "any"))
        with self.subTest("subset"):
            p = GeoSet("fips", [FIPS[0], FIPS[1]])
            self.assertTrue(p.matches("fips", FIPS[0]))
            self.assertTrue(p.matches("fips", FIPS[1]))
            self.assertFalse(p.matches("fips", "c"))
            self.assertFalse(p.matches("msa", "any"))
        with self.subTest("count"):
            self.assertEqual(GeoSet("a", True).count(), inf)
            self.assertEqual(GeoSet("a", False).count(), 0)
            self.assertEqual(GeoSet("fips", [FIPS[0], FIPS[1]]).count(), 2)

    def test_source_signal_set(self):
        with self.subTest("*"):
            p = SourceSignalSet("src1", True)
            self.assertTrue(p.matches("src1", "any"))
            self.assertFalse(p.matches("src2", "any"))
        with self.subTest("subset"):
            p = SourceSignalSet("src1", ["a", "b"])
            self.assertTrue(p.matches("src1", "a"))
            self.assertTrue(p.matches("src1", "b"))
            self.assertFalse(p.matches("src1", "c"))
            self.assertFalse(p.matches("src2", "any"))
        with self.subTest("count"):
            self.assertEqual(SourceSignalSet("a", True).count(), inf)
            self.assertEqual(SourceSignalSet("a", False).count(), 0)
            self.assertEqual(SourceSignalSet("a", ["a", "b"]).count(), 2)

    def test_time_set(self):
        with self.subTest("count"):
            self.assertEqual(TimeSet("day", True).count(), inf)
            self.assertEqual(TimeSet("day", False).count(), 0)
            self.assertEqual(TimeSet("day", [20200202, 20200201]).count(), 2)
            self.assertEqual(TimeSet("day", [(20200201, 20200202)]).count(), 2)
            self.assertEqual(TimeSet("day", [(20200201, 20200205)]).count(), 5)
            self.assertEqual(TimeSet("day", [(20200201, 20200205), 20201212]).count(), 6)

    def test_parse_geo_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertEqual(parse_geo_arg(), [])
        with self.subTest("single"):
            with app.test_request_context("/?geo=fips:*"):
                self.assertEqual(parse_geo_arg(), [GeoSet("fips", True)])
            with app.test_request_context(f"/?geo=fips:{FIPS[0]}"):
                self.assertEqual(parse_geo_arg(), [GeoSet("fips", [FIPS[0]])])
        with self.subTest("covidcast"):
            for geo_type in "county dma hhs hrr msa nation state".split():
                with app.test_request_context(f"/?geo={geo_type}:*"):
                    self.assertEqual(parse_geo_arg(), [GeoSet(geo_type, True)])
        with self.subTest("single list"):
            with app.test_request_context(f"/?geo=fips:{FIPS[0]},{FIPS[1]}"):
                self.assertEqual(parse_geo_arg(), [GeoSet("fips", [FIPS[0], FIPS[1]])])
        with self.subTest("multi"):
            with app.test_request_context("/?geo=fips:*;msa:*"):
                self.assertEqual(parse_geo_arg(), [GeoSet("fips", True), GeoSet("msa", True)])
            with app.test_request_context(f"/?geo=fips:{FIPS[0]};msa:{MSA[0]}"):
                self.assertEqual(
                    parse_geo_arg(),
                    [GeoSet("fips", [FIPS[0]]), GeoSet("msa", [MSA[0]])],
                )
            with app.test_request_context(f"/?geo=fips:{FIPS[0]};fips:{FIPS[1]}"):
                self.assertEqual(
                    parse_geo_arg(),
                    [GeoSet("fips", [FIPS[0]]), GeoSet("fips", [FIPS[1]])],
                )
        with self.subTest("multi list"):
            with app.test_request_context(f"/?geo=fips:{FIPS[0]},{FIPS[1]};msa:{MSA[0]},{MSA[1]}"):
                self.assertEqual(
                    parse_geo_arg(),
                    [
                        GeoSet("fips", [FIPS[0], FIPS[1]]),
                        GeoSet("msa", [MSA[0], MSA[1]]),
                    ],
                )
        with self.subTest("hybrid"):
            with app.test_request_context(f"/?geo=nation:*;fips:{FIPS[0]};msa:{MSA[0]},{MSA[1]}"):
                self.assertEqual(
                    parse_geo_arg(),
                    [
                        GeoSet("nation", True),
                        GeoSet("fips", [FIPS[0]]),
                        GeoSet("msa", [MSA[0], MSA[1]]),
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
            with app.test_request_context(f"/?geo=fips:{FIPS[0]}"):
                self.assertEqual(parse_single_geo_arg("geo"), GeoSet("fips", [FIPS[0]]))
        with self.subTest("single list"):
            with app.test_request_context(f"/?geo=fips:{FIPS[0]},{FIPS[1]}"):
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
                self.assertEqual(parse_source_signal_arg(), [SourceSignalSet("src1", True)])
            with app.test_request_context("/?signal=src1:sig1"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalSet("src1", ["sig1"])])
        with self.subTest("single list"):
            with app.test_request_context("/?signal=src1:sig1,sig2"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [SourceSignalSet("src1", ["sig1", "sig2"])],
                )
        with self.subTest("multi"):
            with app.test_request_context("/?signal=src1:*;src2:*"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [SourceSignalSet("src1", True), SourceSignalSet("src2", True)],
                )
            with app.test_request_context("/?signal=src1:sig1;src2:sig3"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalSet("src1", ["sig1"]),
                        SourceSignalSet("src2", ["sig3"]),
                    ],
                )
            with app.test_request_context("/?signal=src1:sig1;src1:sig4"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalSet("src1", ["sig1"]),
                        SourceSignalSet("src1", ["sig4"]),
                    ],
                )
        with self.subTest("multi list"):
            with app.test_request_context("/?signal=src1:sig1,sig2;county:sig5,sig6"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalSet("src1", ["sig1", "sig2"]),
                        SourceSignalSet("county", ["sig5", "sig6"]),
                    ],
                )
        with self.subTest("hybrid"):
            with app.test_request_context("/?signal=src2:*;src1:sig4;src3:sig5,sig6"):
                self.assertEqual(
                    parse_source_signal_arg(),
                    [
                        SourceSignalSet("src2", True),
                        SourceSignalSet("src1", ["sig4"]),
                        SourceSignalSet("src3", ["sig5", "sig6"]),
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
                self.assertEqual(parse_single_source_signal_arg("signal"), SourceSignalSet("src1", ["sig1"]))
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
                self.assertEqual(parse_time_arg(), TimeSet("day", True))
            with app.test_request_context("/?time=day:20201201"):
                self.assertEqual(parse_time_arg(), TimeSet("day", [20201201]))
        with self.subTest("single list"):
            with app.test_request_context("/?time=day:20201201,20201202"):
                self.assertEqual(parse_time_arg(), TimeSet("day", [20201201, 20201202]))
        with self.subTest("single range"):
            with app.test_request_context("/?time=day:20201201-20201204"):
                self.assertEqual(parse_time_arg(), TimeSet("day", [(20201201, 20201204)]))
        with self.subTest("multi"):
            with app.test_request_context("/?time=day:*;day:20201201"):
                self.assertEqual(
                    parse_time_arg(),
                    TimeSet("day", True)
                )
            with app.test_request_context("/?time=week:*;week:202012"):
                self.assertEqual(
                    parse_time_arg(),
                    TimeSet("week", True)
                )
            with app.test_request_context("/?time=day:20201201;day:20201202-20201205"):
                self.assertEqual(
                    parse_time_arg(),
                    TimeSet("day", [(20201201, 20201205)])
                )
            with app.test_request_context("/?time=week:202012;week:202013-202015"):
                self.assertEqual(
                    parse_time_arg(),
                    TimeSet("week", [(202012, 202015)])
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

    def test_extract_strings(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertIsNone(extract_strings("s"))
        with self.subTest("single"):
            with app.test_request_context("/?s=a"):
                self.assertEqual(extract_strings("s"), ["a"])
        with self.subTest("multiple"):
            with app.test_request_context("/?s=a,b"):
                self.assertEqual(extract_strings("s"), ["a", "b"])
        with self.subTest("multiple param"):
            with app.test_request_context("/?s=a&s=b"):
                self.assertEqual(extract_strings("s"), ["a", "b"])
        with self.subTest("multiple param mixed"):
            with app.test_request_context("/?s=a&s=b,c"):
                self.assertEqual(extract_strings("s"), ["a", "b", "c"])

    def test_extract_integer(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertIsNone(extract_integer("s"))
        with self.subTest("single"):
            with app.test_request_context("/?s=1"):
                self.assertEqual(extract_integer("s"), 1)
        with self.subTest("not a number"):
            with app.test_request_context("/?s=a"):
                self.assertRaises(ValidationFailedException, lambda: extract_integer("s"))

    def test_extract_integers(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertIsNone(extract_integers("s"))
        with self.subTest("single"):
            with app.test_request_context("/?s=1"):
                self.assertEqual(extract_integers("s"), [1])
        with self.subTest("multiple"):
            with app.test_request_context("/?s=1,2"):
                self.assertEqual(extract_integers("s"), [1,2])
        with self.subTest("multiple param"):
            with app.test_request_context("/?s=1&s=2"):
                self.assertEqual(extract_integers("s"), [1,2])
        with self.subTest("multiple param mixed"):
            with app.test_request_context("/?s=1&s=2,3"):
                self.assertEqual(extract_integers("s"), [1, 2, 3])

        with self.subTest("not a number"):
            with app.test_request_context("/?s=a"):
                self.assertRaises(ValidationFailedException, lambda: extract_integers("s"))

        with self.subTest("simple range"):
            with app.test_request_context("/?s=1-2"):
                self.assertEqual(extract_integers("s"), [(1, 2)])
        with self.subTest("inverted range"):
            with app.test_request_context("/?s=2-1"):
                self.assertRaises(ValidationFailedException, lambda: extract_integers("s"))
        with self.subTest("single range"):
            with app.test_request_context("/?s=1-1"):
                self.assertEqual(extract_integers("s"), [1])

    def test_extract_date(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertIsNone(extract_date("s"))
        with self.subTest("single"):
            with app.test_request_context("/?s=2020-01-01"):
                self.assertEqual(extract_date("s"), 20200101)
            with app.test_request_context("/?s=20200101"):
                self.assertEqual(extract_date("s"), 20200101)
        with self.subTest("not a date"):
            with app.test_request_context("/?s=abc"):
                self.assertRaises(ValidationFailedException, lambda: extract_date("s"))

    def test_extract_dates(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertIsNone(extract_dates("s"))
        with self.subTest("single"):
            with app.test_request_context("/?s=20200101"):
                self.assertEqual(extract_dates("s"), [20200101])
        with self.subTest("multiple"):
            with app.test_request_context("/?s=20200101,20200102"):
                self.assertEqual(extract_dates("s"), [20200101, 20200102])
        with self.subTest("multiple param"):
            with app.test_request_context("/?s=20200101&s=20200102"):
                self.assertEqual(extract_dates("s"), [20200101, 20200102])
        with self.subTest("multiple param mixed"):
            with app.test_request_context("/?s=20200101&s=20200102,20200103"):
                self.assertEqual(extract_dates("s"), [20200101, 20200102, 20200103])
        with self.subTest("single iso"):
            with app.test_request_context("/?s=2020-01-01"):
                self.assertEqual(extract_dates("s"), [20200101])
        with self.subTest("multiple iso"):
            with app.test_request_context("/?s=2020-01-01,2020-01-02"):
                self.assertEqual(extract_dates("s"), [20200101, 20200102])
        with self.subTest("multiple param iso"):
            with app.test_request_context("/?s=2020-01-01&s=2020-01-02"):
                self.assertEqual(extract_dates("s"), [20200101, 20200102])
        with self.subTest("multiple param mixed iso"):
            with app.test_request_context("/?s=2020-01-01&s=2020-01-02,2020-01-03"):
                self.assertEqual(extract_dates("s"), [20200101, 20200102, 20200103])
        with self.subTest("iso range"):
            with app.test_request_context("/?s=2020-01-01--2020-01-30"):
                self.assertEqual(extract_dates("s"), [(20200101, 20200130)])
        with self.subTest("wildcard"):
            with app.test_request_context("/?s=*"):
                self.assertEqual(extract_dates("s"), ["*"])

        with self.subTest("not a date"):
            with app.test_request_context("/?s=a"):
                self.assertRaises(ValidationFailedException, lambda: extract_dates("s"))

        with self.subTest("simple range"):
            with app.test_request_context("/?s=20200101-20200102"):
                self.assertEqual(extract_dates("s"), [(20200101, 20200102)])
        with self.subTest("inverted range"):
            with app.test_request_context("/?s=20200102-20200101"):
                self.assertRaises(ValidationFailedException, lambda: extract_dates("s"))
        with self.subTest("single range"):
            with app.test_request_context("/?s=20200101-20200101"):
                self.assertEqual(extract_dates("s"), [20200101])

        with self.subTest("simple range iso"):
            with app.test_request_context("/?s=2020-01-01:2020-01-02"):
                self.assertEqual(extract_dates("s"), [(20200101, 20200102)])
        with self.subTest("inverted range iso"):
            with app.test_request_context("/?s=2020-01-02:2020-01-01"):
                self.assertRaises(ValidationFailedException, lambda: extract_dates("s"))
        with self.subTest("single range iso"):
            with app.test_request_context("/?s=2020-01-01:2020-01-01"):
                self.assertEqual(extract_dates("s"), [20200101])
