"""Unit tests for impute_missing_values.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.fluview.impute_missing_values'


class FunctionTests(unittest.TestCase):
  """Tests each function individually."""

  def test_get_argument_parser(self):
    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

  def test_get_lag_and_ili(self):
    samples = (
      ((201740, 201730, 5, 10), (10, 50)),
      ((201740, 201740, 1, 1), (0, 100)),
      ((201501, 201452, 0, 0), (2, 0)),
    )

    for args, expected in samples:
      with self.subTest(args=args):
        actual = get_lag_and_ili(*args)
        self.assertEquals(actual, expected)

  def test_impute_missing_values(self):
    unknown_set = set(['pa', 'tx'])
    known_set = set(['nat', 'hhs6'] + Locations.atoms) - unknown_set
    known_data = {}
    for loc in known_set:
      n = len(Locations.regions[loc])
      known_data[loc] = (n, n, n)

    db = MagicMock()
    db.connect = MagicMock()
    db.close = MagicMock()
    db.count_rows = MagicMock(return_value=123)
    db.find_missing_rows = MagicMock(return_value=[(201740, 201740)])
    db.get_known_values = MagicMock(return_value=known_data)
    db.add_imputed_values = MagicMock()

    impute_missing_values(db, test_mode=True)

    self.assertEquals(db.connect.call_count, 1)
    self.assertTrue(db.count_rows.call_count >= 1)
    self.assertTrue(db.find_missing_rows.call_count >= 1)
    self.assertEquals(db.add_imputed_values.call_count, 1)
    self.assertEquals(db.close.call_count, 1)
    self.assertFalse(db.close.call_args[0][0])

    imputed = db.add_imputed_values.call_args[0][-1]
    self.assertTrue(unknown_set <= set(imputed.keys()))
    for loc, (lag, n_ili, n_pat, n_prov, ili) in imputed.items():
      with self.subTest(loc=loc):
        num = len(Locations.regions[loc])
        self.assertEquals(lag, 0)
        self.assertEquals(n_ili, num)
        self.assertEquals(n_pat, num)
        self.assertEquals(n_prov, num)
        self.assertEquals(ili, 100)

  def test_impute_missing_values_vipr(self):
    unknown_set = set(['vi', 'pr'])
    known_set = set(['nat'] + Locations.atoms) - unknown_set
    known_data = {}
    for loc in known_set:
      n = len(Locations.regions[loc])
      known_data[loc] = (n, n, n)

    db = MagicMock()
    db.count_rows = MagicMock(return_value=123)
    db.get_known_values = MagicMock(return_value=known_data)

    db.find_missing_rows = MagicMock(return_value=[(201340, 201340)])
    with self.assertRaises(Exception):
      impute_missing_values(db, test_mode=True)

    db.find_missing_rows = MagicMock(return_value=[(201339, 201339)])
    impute_missing_values(db, test_mode=True)

    imputed = db.add_imputed_values.call_args[0][-1]
    self.assertIn('pr', set(imputed.keys()))

  def test_impute_missing_values_underdetermined(self):
    unknown_set = set(['pa', 'tx'])
    known_set = set(Locations.atoms) - unknown_set
    known_data = {}
    for loc in known_set:
      n = len(Locations.regions[loc])
      known_data[loc] = (n, n, n)

    db = MagicMock()
    db.count_rows = MagicMock(return_value=123)
    db.find_missing_rows = MagicMock(return_value=[(201740, 201740)])
    db.get_known_values = MagicMock(return_value=known_data)

    with self.assertRaises(Exception):
      impute_missing_values(db, test_mode=True)
