"""Unit tests for direction.py."""

# standard library
import unittest

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.direction'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_get_direction_sanity_checks(self):
    """Validate direction computed for various timeseries."""

    # slope=+1.500 stderr=1.443
    x, y = [1, 2, 3], [2, 6, 5]
    self.assertEqual(Direction.get_direction(x, y), 1)
    self.assertEqual(Direction.get_direction(x, y, n=1.05), 0)

    # slope=-0.692 stderr=0.381
    x, y = [2, 4, 5, 7], [7, 4, 6, 3]
    self.assertEqual(Direction.get_direction(x, y), -1)
    self.assertEqual(Direction.get_direction(x, y, n=2), 0)

    # slope=+1.000 stderr=0.000
    x = y = list(range(10))
    self.assertEqual(Direction.get_direction(x, y, n=0), 1)
    self.assertEqual(Direction.get_direction(x, y, n=1), 1)
    self.assertEqual(Direction.get_direction(x, y, n=10), 1)
    self.assertEqual(Direction.get_direction(x, y, n=100), 1)

  def test_get_direction_returns_none_for_small_samples(self):
    """Direction should be `None` with too few samples."""

    self.assertIsNone(Direction.get_direction([1, 2], [3, 4]))

  def test_get_direction_validates_arguments(self):
    """Validate values passed to the function."""

    # x and y different length
    x, y = list(range(10)), list(range(11))
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y)

    # n is negative
    x = y = list(range(5))
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y, n=-1)

    # x has effectively coincident points
    y = [1, 2, 3]
    x = [1, 1, 3]
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y)
    x = [1, 1 + 1e-9, 3]
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y)
