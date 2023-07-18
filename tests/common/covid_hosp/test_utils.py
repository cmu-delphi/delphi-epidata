"""Unit tests for utils.py."""

# standard library
import unittest

# first party
from delphi.epidata.common.covid_hosp.utils import Utils, CovidHospException

# py3tester coverage target
__test_target__ = 'delphi.epidata.common.covid_hosp.utils'

class UtilsTests(unittest.TestCase):

  def test_int_from_date(self):
    """Convert a YYY-MM-DD date to a YYYYMMDD int."""

    self.assertEqual(Utils.int_from_date('2020-11-17'), 20201117)
    self.assertEqual(Utils.int_from_date('2020/11/17'), 20201117)
    self.assertEqual(Utils.int_from_date('2020/11/17 10:00:00'), 20201117)

  def test_parse_bool(self):
    """Parse a boolean value from a string."""

    with self.subTest(name='None'):
      self.assertIsNone(Utils.parse_bool(None))

    with self.subTest(name='empty'):
      self.assertIsNone(Utils.parse_bool(''))

    with self.subTest(name='true'):
      self.assertTrue(Utils.parse_bool('true'))
      self.assertTrue(Utils.parse_bool('True'))
      self.assertTrue(Utils.parse_bool('tRuE'))

    with self.subTest(name='false'):
      self.assertFalse(Utils.parse_bool('false'))
      self.assertFalse(Utils.parse_bool('False'))
      self.assertFalse(Utils.parse_bool('fAlSe'))

    with self.subTest(name='exception'):
      with self.assertRaises(CovidHospException):
        Utils.parse_bool('maybe')
