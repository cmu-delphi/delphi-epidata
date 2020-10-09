"""Classifies the direction of a signal based on its recent trajectory."""

# third party
import numpy as np
import scipy.stats


class Direction:
  """Utility class for computing signal direction."""

  # minimum number of points required to compute direction
  MIN_SAMPLE_SIZE = 3

  @staticmethod
  def get_direction(x, y, n=1, limit=0):
    """Return the direction of the given time-series.

    `x`: list of unique time offsets (e.g. 0, 1, 2, ...)
    `y`: list of signal values corresponding to time values in `x`
    `n`: multiplier of the standard error interval; must be non-negative
    `limit`: additional threshold which slope must exceed to make a non-zero
      direction call

    `x` and `y` must be the same length.

    Direction is defined as follows. Find the OLS regression fit, with
    intercept, of a line to the past week of data. If zero falls within [slope
    ± `n` * standard error], then direction is 0. Otherwise, direction is the
    sign of the slope (i.e. either +1 or -1).

    If there are not enough samples to compute direction (i.e. fewer than three
    points), direction is None.
    """

    if len(x) != len(y):
      raise ValueError('x and y must have same length')

    if n < 0:
      raise ValueError('n must be non-negative')

    if limit < 0:
      raise ValueError('limit must be non-negative')

    if len(x) < Direction.MIN_SAMPLE_SIZE:
      return None

    # check for coincident values in a way that is robust to extremely small
    # differences (requires at least two points, checked above)
    if np.isclose(min(np.diff(sorted(x))), 0):
      raise ValueError('x contains coincident values')

    # compute regression fit
    fit = scipy.stats.linregress(x, y)

    # classify the direction
    if abs(fit.slope) <= max(n * fit.stderr, limit):
      return 0
    else:
      # return an integer in {-1, +1}
      return int(np.sign(fit.slope))

  @staticmethod
  def scan_timeseries(
      offsets,
      days,
      values,
      value_updated_timestamps,
      direction_updated_timestamps,
      get_direction_impl):
    """Scan an entire time-series and return fresh direction updates.

    `offsets`: time offset, relative to any arbitrary fixed point in time, for
      each day in `days`
    `days`: day (YYYYMMDD) corresponding to each row in the other arrays
    `values`: value of the signal on each day
    `value_updated_timestamps`: primary timestamp for each row (i.e. when `value` was
      updated)
    `direction_updated_timestamps`: secondary timestamp for each row (i.e. when `direction` was
      last deemed to be fresh, relative to associated `value`s)
    `get_direction_impl`: a function which takes two arrays (time and value)
      and returns a classification of the direction (i.e. as -1, 0, +1)

    All arrays must be, and are assumed to be, sorted by offset, ascending.

    Two arrays are returned which contain days and directions, respectively.
    Directions are only computed when a particular day is stale, as determined
    by timestamp comparison across relevent days.
    """

    updated_days, directions = [], []

    # sliding window over the past week of data
    start = 0
    for end in range(len(offsets)):

      # find the start of the window, which is up to 6 days ago. this is not a
      # simple subtraction like `end - 6` because there could be missing rows.
      while offsets[end] - offsets[start] >= 7:
        # shrink the window
        start += 1

      # check whether this row needs an update
      direction_time = direction_updated_timestamps[end]
      value_time = np.max(value_updated_timestamps[start:end + 1])
      if direction_time > value_time:
        # this row is fresh
        continue

      x = offsets[start:end + 1]
      y = values[start:end + 1]
      direction = get_direction_impl(x, y)

      # record the direction update
      updated_days.append(days[end])
      directions.append(direction)

    return updated_days, directions
