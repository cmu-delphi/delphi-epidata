"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._validate import require_all, require_any, extract_strings, extract_integers, extract_integer, extract_date, extract_dates
from delphi.epidata.server._exceptions import (
    ValidationFailedException,
)

# py3tester coverage target
__test_target__ = "delphi.epidata.server._validate"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_require_all(self):
        with self.subTest("all given"):
            with app.test_request_context("/"):
                self.assertTrue(require_all())
            with app.test_request_context("/?abc=abc&def=3"):
                self.assertTrue(require_all("abc", "def"))
        with self.subTest("missing parameter"):
            with app.test_request_context("/?abc=abc"):
                self.assertRaises(ValidationFailedException, lambda: require_all("abc", "def"))
        with self.subTest("missing empty parameter"):
            with app.test_request_context("/?abc=abc&def="):
                self.assertRaises(ValidationFailedException, lambda: require_all("abc", "def"))

    def test_require_any(self):
        with self.subTest("default given"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, lambda: require_any("abc"))
        with self.subTest("one option give"):
            with app.test_request_context("/?abc=abc"):
                self.assertTrue(require_any("abc", "def"))
        with self.subTest("multiple options given"):
            with app.test_request_context("/?abc=abc&def=d"):
                self.assertTrue(require_any("abc", "def"))
        with self.subTest("one options given with is empty"):
            with app.test_request_context("/?abc="):
                self.assertRaises(ValidationFailedException, lambda: require_any("abc"))
        with self.subTest("one options given with is empty but ok"):
            with app.test_request_context("/?abc="):
                self.assertTrue(require_any("abc", empty=True))

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
                self.assertEqual(extract_integers("s"), [1, 2])
        with self.subTest("multiple param"):
            with app.test_request_context("/?s=1&s=2"):
                self.assertEqual(extract_integers("s"), [1, 2])
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
