"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest
import base64

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._params import (
    parse_geo_arg,
    parse_source_signal_arg,
    GeoPair,
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

    def test_parse_geo_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertEqual(parse_geo_arg(), [])
        with self.subTest("single"):
            with app.test_request_context("/?geo=state:*"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', True)])
            with app.test_request_context("/?geo=state:AK"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', ['AK'])])
        with self.subTest("single list"):
            with app.test_request_context("/?geo=state:AK,TK"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', ['AK', 'TK'])])
        with self.subTest("multi"):
            with app.test_request_context("/?geo=state:*;nation:*"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', True), GeoPair('nation', True)])
            with app.test_request_context("/?geo=state:AK;nation:US"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', ['AK']), GeoPair('nation', ['US'])])
            with app.test_request_context("/?geo=state:AK;state:KY"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', ['AK']), GeoPair('state', ['KY'])])
        with self.subTest("multi list"):
            with app.test_request_context("/?geo=state:AK,TK;county:42003,40556"):
                self.assertEqual(parse_geo_arg(), [GeoPair('state', ['AK', 'TK']), GeoPair('county', ['42003', '40556'])])
        with self.subTest("hybrid"):
            with app.test_request_context("/?geo=nation:*;state:PA;county:42003,42002"):
                self.assertEqual(parse_geo_arg(), [GeoPair('nation', True), GeoPair('state', ['PA']), GeoPair('county', ['42003', '42002'])])

        with self.subTest("wrong"):
            with app.test_request_context("/?geo=abc"):
                self.assertRaises(ValidationFailedException, parse_geo_arg)
            with app.test_request_context("/?geo=state=4"):
                self.assertRaises(ValidationFailedException, parse_geo_arg)

    def test_parse_source_signal_arg(self):
        with self.subTest("empty"):
            with app.test_request_context("/"):
                self.assertEqual(parse_source_signal_arg(), [])
        with self.subTest("single"):
            with app.test_request_context("/?signals=src1:*"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', True)])
            with app.test_request_context("/?signals=src1:sig1"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', ['sig1'])])
        with self.subTest("single list"):
            with app.test_request_context("/?signals=src1:sig1,sig2"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', ['sig1', 'sig2'])])
        with self.subTest("multi"):
            with app.test_request_context("/?signals=src1:*;src2:*"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', True), SourceSignalPair('src2', True)])
            with app.test_request_context("/?signals=src1:sig1;src2:sig3"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', ['sig1']), SourceSignalPair('src2', ['sig3'])])
            with app.test_request_context("/?signals=src1:sig1;src1:sig4"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', ['sig1']), SourceSignalPair('src1', ['sig4'])])
        with self.subTest("multi list"):
            with app.test_request_context("/?signals=src1:sig1,sig2;county:sig5,sig6"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src1', ['sig1', 'sig2']), SourceSignalPair('county', ['sig5', 'sig6'])])
        with self.subTest("hybrid"):
            with app.test_request_context("/?signals=src2:*;src1:sig4;src3:sig5,sig6"):
                self.assertEqual(parse_source_signal_arg(), [SourceSignalPair('src2', True), SourceSignalPair('src1', ['sig4']), SourceSignalPair('src3', ['sig5', 'sig6'])])

        with self.subTest("wrong"):
            with app.test_request_context("/?signals=abc"):
                self.assertRaises(ValidationFailedException, parse_source_signal_arg)
            with app.test_request_context("/?signals=sig=4"):
                self.assertRaises(ValidationFailedException, parse_source_signal_arg)
