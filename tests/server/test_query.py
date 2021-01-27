"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest
import base64

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._query import (
    date_string,
)
from delphi.epidata.server._exceptions import (
    ValidationFailedException,
    UnAuthenticatedException,
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
        self.assertEqual(date_string(20200101), '2020-01-01')
