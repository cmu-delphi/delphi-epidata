"""Unit tests for direction.py."""

# standard library
import unittest
from unittest.mock import MagicMock

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.direction'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_get_direction_type(self):
    """The returned direction should always be a built-in `int`."""

    x = y = range(3)

    direction = Direction.get_direction(x, y)
    self.assertEqual(direction, 1)
    self.assertIs(type(direction), int)

    direction = Direction.get_direction(x, y[::-1])
    self.assertEqual(direction, -1)
    self.assertIs(type(direction), int)

    direction = Direction.get_direction(x, [0, 0, 0])
    self.assertEqual(direction, 0)
    self.assertIs(type(direction), int)

  def test_get_direction_sanity_checks(self):
    """Validate direction computed for various timeseries."""

    # slope=+1.500 stderr=1.443
    x, y = [1, 2, 3], [2, 6, 5]
    self.assertEqual(Direction.get_direction(x, y), 1)
    self.assertEqual(Direction.get_direction(x, y, n=1.05), 0)
    self.assertEqual(Direction.get_direction(x, y, limit=1.6), 0)

    # slope=-0.692 stderr=0.381
    x, y = [2, 4, 5, 7], [7, 4, 6, 3]
    self.assertEqual(Direction.get_direction(x, y), -1)
    self.assertEqual(Direction.get_direction(x, y, n=2), 0)
    self.assertEqual(Direction.get_direction(x, y, limit=0.7), 0)

    # slope=+1.000 stderr=0.000
    x = y = list(range(10))
    self.assertEqual(Direction.get_direction(x, y, n=0), 1)
    self.assertEqual(Direction.get_direction(x, y, n=1), 1)
    self.assertEqual(Direction.get_direction(x, y, n=10), 1)
    self.assertEqual(Direction.get_direction(x, y, n=100), 1)
    self.assertEqual(Direction.get_direction(x, y, limit=1.1), 0)

  def test_get_direction_returns_none_for_small_samples(self):
    """Direction should be `None` with too few samples."""

    self.assertIsNone(Direction.get_direction([1], [1]))
    self.assertIsNone(Direction.get_direction([1, 2], [1, 2]))

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

    # limit is negative
    x = y = list(range(5))
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y, limit=-1)

    # x has effectively coincident points
    y = [1, 2, 3]
    x = [1, 1, 3]
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y)
    x = [1, 1 + 1e-9, 3]
    with self.assertRaises(ValueError):
      Direction.get_direction(x, y)

  def test_scan_timeseries(self):
    """Scan a time-series and update stale directions."""

    offsets, days, values, value_updated_timestamps, direction_updated_timestamps = [
      # missing days '230', '240', and '250' (the gap helps test windowing)
      [100, 101, 102, 106, 107, 108],
      [200, 210, 220, 260, 270, 280],
      [350, 351, 352, 353, 354, 355],
      # days '210' and '280' are stale
      # day '210' doesn't have enough history
      [401, 401, 401, 405, 405, 405],
      [403, 400, 404, 406, 407, 400],
    ]

    get_direction_impl = Direction.get_direction

    days, directions = Direction.scan_timeseries(
        offsets,
        days,
        values,
        value_updated_timestamps,
        direction_updated_timestamps,
        get_direction_impl)

    self.assertEqual(days, [210, 280])
    self.assertEqual(directions, [None, 1])
