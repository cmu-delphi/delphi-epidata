"""Classifies the direction of a signal based on its recent trajectory."""

# third party
import numpy
import scipy.stats


class Direction:
  """Utility class for computing signal direction."""

  # minimum number of points required to compute direction
  MIN_SAMPLE_SIZE = 3

  @staticmethod
  def get_direction(x, y, n=1):
    """Return the direction of the given time-series.

    `x`: list of time offsets (e.g. 0, 1, 2, ...)
    `y`: list of signal values corresponding to time values in `x`
    `n`: multiplier of the standard error interval; must be non-negative

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

    if len(x) < Direction.MIN_SAMPLE_SIZE:
      return None

    fit = scipy.stats.linregress(x, y)

    if numpy.abs(fit.slope) <= n * fit.stderr:
      return 0
    else:
      return numpy.sign(fit.slope)
