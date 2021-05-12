"""Unit tests for impute_missing_values.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock

# first party
from delphi.utils.geo.locations import Locations
from delphi.epidata.acquisition.fluview.impute_missing_values import get_argument_parser, \
  get_lag_and_ili, impute_missing_values, StatespaceException

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.fluview.impute_missing_values'


class FunctionTests(unittest.TestCase):
  """Tests each function individually."""

  def test_get_argument_parser(self):
    """An ArgumentParser is returned."""
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
        self.assertEqual(actual, expected)

  def test_impute_missing_values(self):
    """Atoms are imputed and stored."""

    unknown_set = set(['pa', 'tx'])
    known_set = set(['nat', 'hhs6'] + Locations.atom_list) - unknown_set
    known_data = {}
    for loc in known_set:
      n = len(Locations.region_map[loc])
      known_data[loc] = (n, n, n)

    db = MagicMock()
    db.count_rows.return_value = 123
    db.find_missing_rows.return_value = [(201740, 201740)]
    db.get_known_values.return_value = known_data

    impute_missing_values(db, test_mode=True)

    self.assertEqual(db.connect.call_count, 1)
    self.assertTrue(db.count_rows.call_count >= 1)
    self.assertTrue(db.find_missing_rows.call_count >= 1)
    self.assertEqual(db.add_imputed_values.call_count, 1)
    self.assertEqual(db.close.call_count, 1)
    self.assertFalse(db.close.call_args[0][0])

    imputed = db.add_imputed_values.call_args[0][-1]
    self.assertTrue(unknown_set <= set(imputed.keys()))
    for loc, (lag, n_ili, n_pat, n_prov, ili) in imputed.items():
      with self.subTest(loc=loc):
        num = len(Locations.region_map[loc])
        self.assertEqual(lag, 0)
        self.assertEqual(n_ili, num)
        self.assertEqual(n_pat, num)
        self.assertEqual(n_prov, num)
        self.assertEqual(ili, 100)

  def test_impute_missing_values_vipr(self):
    """PR and VI are imputed only when appropriate."""

    unknown_set = set(['vi', 'pr'])
    known_set = set(['nat'] + Locations.atom_list) - unknown_set
    known_data = {}
    for loc in known_set:
      n = len(Locations.region_map[loc])
      known_data[loc] = (n, n, n)

    db = MagicMock()
    db.count_rows.return_value = 123
    db.get_known_values.return_value = known_data

    db.find_missing_rows.return_value = [(201340, 201340)]
    with self.assertRaises(Exception):
      impute_missing_values(db, test_mode=True)

    db.find_missing_rows.return_value = [(201339, 201339)]
    impute_missing_values(db, test_mode=True)

    imputed = db.add_imputed_values.call_args[0][-1]
    self.assertIn('pr', set(imputed.keys()))

  def test_impute_missing_values_regions(self):
    """Regions are imputed in addition to atoms."""

    known_set = set(Locations.atom_list)
    known_data = {}
    for loc in known_set:
      known_data[loc] = (1, 2, 3)

    db = MagicMock()
    db.count_rows.return_value = 123
    db.find_missing_rows.return_value = [(201740, 201740)]
    db.get_known_values.return_value = known_data

    impute_missing_values(db, test_mode=True)
    imputed = db.add_imputed_values.call_args[0][-1]
    self.assertIn('nat', set(imputed.keys()))
    self.assertIn('hhs2', set(imputed.keys()))
    self.assertIn('cen3', set(imputed.keys()))
    self.assertIn('ny', set(imputed.keys()))

  def test_impute_missing_values_underdetermined(self):
    """Fail when the system is underdetermined."""

    unknown_set = set(['pa', 'tx'])
    known_set = set(Locations.atom_list) - unknown_set
    known_data = {}
    for loc in known_set:
      n = len(Locations.region_map[loc])
      known_data[loc] = (n, n, n)

    db = MagicMock()
    db.count_rows.return_value = 123
    db.find_missing_rows.return_value = [(201740, 201740)]
    db.get_known_values.return_value = known_data

    with self.assertRaises(StatespaceException):
      impute_missing_values(db, test_mode=True)
