# standard library
import unittest

from flask.testing import FlaskClient
from flask import Response
from delphi.epidata.server.main import app

from delphi.epidata.server.endpoints.covidcast import guess_index_to_use, parse_transform_args
from delphi.epidata.server._params import (
    GeoPair,
    TimePair,
)

# py3tester coverage target
__test_target__ = "delphi.epidata.server.endpoints.covidcast"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    client: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        self.client = app.test_client()

    def test_url(self):
        rv: Response = self.client.get("/covidcast/", follow_redirects=True)
        msg = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(msg["result"], -1)
        self.assertRegex(msg["message"], r"missing parameter.*")

    def test_time(self):
        rv: Response = self.client.get("/covidcast/", query_string=dict(signal="src1:*", time="day:20200101", geo="state:*"))
        msg = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(msg["result"], -2)  # no result
        self.assertEqual(msg["message"], "no results")

    def test_guess_index_to_use(self):
        self.assertFalse(False, "deprecated tests...")
        return
        # TODO: remove this as we are no longer planning to hint at indexes...
        self.assertEqual(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a"])], issues=None, lag=None, as_of=None), "by_issue")
        self.assertEqual(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a", "b"])], issues=None, lag=None, as_of=None), "by_issue")
        self.assertEqual(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a", "b"])], issues=None, lag=None, as_of=None), "by_issue")
        self.assertEqual(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a", "b", "c"])], issues=None, lag=None, as_of=None), "by_issue")

        # to many geo
        self.assertIsNone(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a", "b", "c", "d", "e", "f"])], issues=None, lag=None, as_of=None))
        # to short time frame
        self.assertIsNone(guess_index_to_use([TimePair("day", [(20200101, 20200115)])], [GeoPair("county", ["a", "b", "c", "d", "e", "f"])], issues=None, lag=None, as_of=None))

        self.assertEqual(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a"])], issues=None, lag=3, as_of=None), "by_lag")
        self.assertEqual(guess_index_to_use([TimePair("day", True)], [GeoPair("county", ["a"])], issues=[20200202], lag=3, as_of=None), "by_issue")
        self.assertIsNone(guess_index_to_use([TimePair("day", [20200201])], [GeoPair("county", ["a"])], issues=[20200202], lag=3, as_of=None))
        self.assertIsNone(guess_index_to_use([TimePair("day", True)], [GeoPair("county", True)], issues=None, lag=3, as_of=None))

    # TODO
    def test_parse_transform_args(self):
        ...
