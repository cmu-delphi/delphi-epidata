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
    filter_dates
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

    def test_to_condition(self):
        params = {}
        self.assertEqual(to_condition('a', 0, 'a', params), 'a = :a')
        self.assertEqual(params, {'a': 0})
        params = {}
        self.assertEqual(to_condition('a', (1, 4), 'a', params), 'a BETWEEN :a AND :a_2')
        self.assertEqual(params, {'a': 1, 'a_2': 4})
    
    def test_filter_strings(self):
        params = {}
        self.assertEqual(filter_strings('a', None, 'a', params), 'FALSE')
        self.assertEqual(params, {})
        params = {}
        self.assertEqual(filter_strings('a', ['1'], 'a', params), '(a = :a_0)')
        self.assertEqual(params, {'a_0': '1'})
        params = {}
        self.assertEqual(filter_strings('a', ['1', '2'], 'a', params), '(a = :a_0 OR a = :a_1)')
        self.assertEqual(params, {'a_0': '1', 'a_1': '2'})
        params = {}
        self.assertEqual(filter_strings('a', ['1', '2', ('1','4')], 'a', params), '(a = :a_0 OR a = :a_1 OR a BETWEEN :a_2 AND :a_2_2)')
        self.assertEqual(params, {'a_0': '1', 'a_1': '2', 'a_2': '1', 'a_2_2': '4'})

    def test_filter_integers(self):
        params = {}
        self.assertEqual(filter_integers('a', None, 'a', params), 'FALSE')
        self.assertEqual(params, {})
        params = {}
        self.assertEqual(filter_integers('a', [1], 'a', params), '(a = :a_0)')
        self.assertEqual(params, {'a_0': 1})
        params = {}
        self.assertEqual(filter_integers('a', [1, 2], 'a', params), '(a = :a_0 OR a = :a_1)')
        self.assertEqual(params, {'a_0': 1, 'a_1': 2})
        params = {}
        self.assertEqual(filter_integers('a', [1, 2, (1,4)], 'a', params), '(a = :a_0 OR a = :a_1 OR a BETWEEN :a_2 AND :a_2_2)')
        self.assertEqual(params, {'a_0': 1, 'a_1': 2, 'a_2': 1, 'a_2_2': 4})

    def test_filter_dates(self):
        params = {}
        self.assertEqual(filter_dates('a', None, 'a', params), 'FALSE')
        self.assertEqual(params, {})
        params = {}
        self.assertEqual(filter_dates('a', [20200101], 'a', params), '(a = :a_0)')
        self.assertEqual(params, {'a_0': '2020-01-01'})
        params = {}
        self.assertEqual(filter_dates('a', [20200101, 20200102], 'a', params), '(a = :a_0 OR a = :a_1)')
        self.assertEqual(params, {'a_0': '2020-01-01', 'a_1': '2020-01-02'})
        params = {}
        self.assertEqual(filter_dates('a', [20200101, 20200102, (20200101,20200104)], 'a', params), '(a = :a_0 OR a = :a_1 OR a BETWEEN :a_2 AND :a_2_2)')
        self.assertEqual(params, {'a_0': '2020-01-01', 'a_1': '2020-01-02', 'a_2': '2020-01-01', 'a_2_2': '2020-01-04'})
