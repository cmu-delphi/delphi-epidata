"""Unit tests for the retirement cutoff guard."""

# standard library
import unittest

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._config import (
    RETIREMENT_CUTOFF_DAY,
    RETIREMENT_CUTOFF_WEEK,
    RETIREMENT_RESULT_CODE,
)
from delphi.epidata.server._exceptions import DataRetiredException
from delphi.epidata.server._params import (
    extract_date,
    extract_dates,
    extract_integers,
    parse_day_arg,
    parse_day_or_week_arg,
    parse_day_range_arg,
    parse_time_arg,
)
from delphi.epidata.server._retirement import is_time_param, require_servable_times

# py3tester coverage target
__test_target__ = "delphi.epidata.server._retirement"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_is_time_param(self):
        self.assertTrue(is_time_param("epiweeks"))
        self.assertTrue(is_time_param("issues"))
        self.assertTrue(is_time_param(("as_of", "issues")))
        self.assertTrue(is_time_param("as_of"))
        # end of a window that can include servable days
        self.assertFalse(is_time_param("latest"))
        # counts, not time values
        self.assertFalse(is_time_param("lag"))
        self.assertFalse(is_time_param("hours"))
        self.assertFalse(is_time_param("basis_shift"))
        # `basis` is a day value, so the tuple form matches on it; only `extract_integer` reads
        # ("basis", "basis_shift") and that helper is not hooked, so the count is never checked
        self.assertTrue(is_time_param(("basis", "basis_shift")))

    def test_require_servable_times_days(self):
        # a request context is needed: raising DataRetiredException inspects request.values to
        # decide whether to use real HTTP status codes
        with app.test_request_context("/"):
            # the cutoff day itself is still served
            require_servable_times("dates", RETIREMENT_CUTOFF_DAY, "day")
            require_servable_times("dates", 20200101, "day")
            # a range or list that includes servable days is still served
            require_servable_times("dates", (20200101, 20300101), "day")
            require_servable_times("dates", [20270101, 20200101], "day")
            # unbounded requests are never retired
            require_servable_times("dates", ["*"], "day")
            require_servable_times("dates", True, "day")
            require_servable_times("dates", None, "day")

            with self.assertRaises(DataRetiredException):
                require_servable_times("dates", 20270101, "day")
            with self.assertRaises(DataRetiredException):
                require_servable_times("dates", (20261001, 20270101), "day")
            with self.assertRaises(DataRetiredException):
                require_servable_times("dates", [20270101, 20261001], "day")

    def test_require_servable_times_weeks(self):
        with app.test_request_context("/"):
            # the cutoff week is only partially covered but we still serve it
            require_servable_times("epiweeks", RETIREMENT_CUTOFF_WEEK, "week")
            require_servable_times("epiweeks", (202001, 202652), "week")

            with self.assertRaises(DataRetiredException):
                require_servable_times("epiweeks", RETIREMENT_CUTOFF_WEEK + 1, "week")
            with self.assertRaises(DataRetiredException):
                require_servable_times("epiweeks", [202650], "week")

    def test_require_servable_times_guesses_time_type(self):
        with app.test_request_context("/"):
            # 6 digits -> epiweek, 8 digits -> day
            with self.assertRaises(DataRetiredException):
                require_servable_times("epiweeks", [202650])
            with self.assertRaises(DataRetiredException):
                require_servable_times("dates", [20270101])
            require_servable_times("epiweeks", [202601])
            require_servable_times("dates", [20260101])

    def test_extract_integers(self):
        with app.test_request_context("/?epiweeks=202001-202050"):
            self.assertEqual(extract_integers("epiweeks"), [(202001, 202050)])
        with app.test_request_context("/?epiweeks=202650"):
            self.assertRaises(DataRetiredException, lambda: extract_integers("epiweeks"))
        # a range that starts before the cutoff is still served
        with app.test_request_context("/?epiweeks=202001-202652"):
            self.assertEqual(extract_integers("epiweeks"), [(202001, 202652)])
        # non-time params are untouched
        with app.test_request_context("/?lag=202650"):
            self.assertEqual(extract_integers("lag"), [202650])

    def test_extract_dates(self):
        with app.test_request_context("/?issues=20270101"):
            self.assertRaises(DataRetiredException, lambda: extract_dates("issues"))
        with app.test_request_context("/?issues=*"):
            self.assertEqual(extract_dates("issues"), ["*"])
        with app.test_request_context("/?issues=20200101:20270101"):
            self.assertEqual(extract_dates("issues"), [(20200101, 20270101)])

    def test_extract_date(self):
        with app.test_request_context("/?as_of=20270101"):
            self.assertRaises(DataRetiredException, lambda: extract_date("as_of"))
        with app.test_request_context("/?as_of=20200101"):
            self.assertEqual(extract_date("as_of"), 20200101)

    def test_parse_day_or_week_as_of(self):
        # backfill parses as_of as a day or a week
        with app.test_request_context("/?as_of=20270101"):
            self.assertRaises(DataRetiredException, lambda: parse_day_or_week_arg("as_of"))
        with app.test_request_context("/?as_of=202701"):
            self.assertRaises(DataRetiredException, lambda: parse_day_or_week_arg("as_of"))
        with app.test_request_context(f"/?as_of={RETIREMENT_CUTOFF_DAY}"):
            self.assertEqual(parse_day_or_week_arg("as_of").time_values, [RETIREMENT_CUTOFF_DAY])

    def test_latest_after_cutoff_is_served(self):
        # latest is the end of the coverage window, which can include servable days
        with app.test_request_context("/?latest=20270101"):
            self.assertEqual(extract_date("latest"), 20270101)

    def test_parse_day_args(self):
        with app.test_request_context("/?date=20270101"):
            self.assertRaises(DataRetiredException, lambda: parse_day_arg("date"))
        with app.test_request_context("/?window=20261001-20270101"):
            self.assertRaises(DataRetiredException, lambda: parse_day_range_arg("window"))
        with app.test_request_context("/?window=20200101-20270101"):
            self.assertEqual(parse_day_range_arg("window"), (20200101, 20270101))

    def test_parse_time_arg(self):
        with app.test_request_context("/?time=day:20270101"):
            self.assertRaises(DataRetiredException, lambda: parse_time_arg())
        with app.test_request_context("/?time=week:202650"):
            self.assertRaises(DataRetiredException, lambda: parse_time_arg())
        with app.test_request_context("/?time=day:*"):
            self.assertIsNotNone(parse_time_arg())
        with app.test_request_context("/?time=day:20200101-20270101"):
            self.assertIsNotNone(parse_time_arg())

    def test_cutoff_week_is_derived_from_cutoff_day(self):
        # 2026-09-22 falls in epiweek 2026-38 (2026-09-20 to 2026-09-26)
        self.assertEqual(RETIREMENT_CUTOFF_DAY, 20260922)
        self.assertEqual(RETIREMENT_CUTOFF_WEEK, 202638)

    def test_exception_shape(self):
        # classic format keeps HTTP 200 per the existing convention, but the result code is ours
        with app.test_request_context("/?format=json"):
            e = DataRetiredException()
            self.assertEqual(e.code, 410)
            self.assertIn("cast-api", e.response.get_data(as_text=True))
            self.assertIn(f'"result": {RETIREMENT_RESULT_CODE}', e.response.get_data(as_text=True))
        with app.test_request_context("/"):
            self.assertEqual(DataRetiredException().code, 200)

    def test_deprecation_headers(self):
        with app.test_client() as client:
            # headers are attached in after_request, so they ride along even on an error response
            response = client.get("/version")
            # RFC 9745 structured field date for 2026-09-22T00:00:00Z
            self.assertEqual(response.headers["Deprecation"], "@1790035200")
            self.assertIn("Sunset", response.headers)
            self.assertIn("successor-version", response.headers["Link"])
            self.assertIn("X-Delphi-Epidata-Retirement", response.headers)
