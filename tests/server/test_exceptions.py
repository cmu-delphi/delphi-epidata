# standard library
import unittest

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._exceptions import _is_using_status_codes 

# py3tester coverage target
__test_target__ = 'delphi.epidata.server._exceptions'

class UnitTests(unittest.TestCase):
  """Basic unit tests."""
  # app: FlaskClient

  def setUp(self):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DEBUG'] = False

  def test_is_using_status_codes(self):
    with app.test_request_context('/?format=csv'):
      self.assertTrue(_is_using_status_codes())
    with app.test_request_context('/?format=json'):
      self.assertTrue(_is_using_status_codes())
    with app.test_request_context('/?format=jsonl'):
      self.assertTrue(_is_using_status_codes())
    with app.test_request_context('/'):
      self.assertFalse(_is_using_status_codes())
    with app.test_request_context('/?format=classic'):
      self.assertFalse(_is_using_status_codes())
    with app.test_request_context('/?format=tree'):
      self.assertFalse(_is_using_status_codes())
