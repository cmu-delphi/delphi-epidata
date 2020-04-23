"""Computes and updates the `direction` column in the `covidcast` table.

Update is only performed for stale rows.
"""

# standard library
import argparse

# third party
import numpy as np

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi.epidata.acquisition.covidcast.direction import Direction


def get_argument_parser():
  """Define command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--test',
    action='store_true',
    help='do a dry run without committing changes')
  return parser


def update_loop(database, direction_impl=Direction):
  """Find and update rows with a stale `direction` value.

  `database`: an open connection to the epidata database
  """

  stale_series = database.get_keys_with_potentially_stale_direction()
  num_series = len(stale_series)
  num_rows = 0
  for row in stale_series:
    num_rows += row[-1]
  msg = 'found %d time-series (%d rows) which may have stale direction'
  print(msg % (num_series, num_rows))

  # get the scaling factor (data stdev) for all signals and resolutions
  rows = database.get_data_stdev_across_locations()
  data_stdevs = {}
  for (source, signal, geo_type, aggregate_stdev) in rows:
    if source not in data_stdevs:
      data_stdevs[source] = {}
    if signal not in data_stdevs:
      data_stdevs[source][signal] = {}
    data_stdevs[source][signal][geo_type] = aggregate_stdev

  for ts_index, row in enumerate(stale_series):
    (
      source,
      signal,
      geo_type,
      geo_value,
      max_timestamp1,
      min_timestamp2,
      min_day,
      max_day,
      series_length,
    ) = row

    # progress reporting for anyone debugging/watching the output
    be_verbose = ts_index < 100
    be_verbose = be_verbose or ts_index % 100 == 0
    be_verbose = be_verbose or ts_index >= num_series - 100

    if be_verbose:
      msg = '[%d/%d] %s %s %s %s: span=%d--%d len=%d max_seconds_stale=%d'
      args = (
        ts_index + 1,
        num_series,
        source,
        signal,
        geo_type,
        geo_value,
        min_day,
        max_day,
        series_length,
        max_timestamp1 - min_timestamp2,
      )
      print(msg % args)

    timeseries_rows = database.get_daily_timeseries_for_direction_update(
        source, signal, geo_type, geo_value, min_day, max_day)

    # transpose result set and cast data types
    data = np.array(timeseries_rows)
    offsets, days, values, timestamp1s, timestamp2s = data.T
    offsets = offsets.astype(np.int64)
    days = days.astype(np.int64)
    values = values.astype(np.float64)
    timestamp1s = timestamp1s.astype(np.int64)
    timestamp2s = timestamp2s.astype(np.int64)

    # recompute any stale directions
    data_stdev = data_stdevs[source][signal][geo_type]
    days, directions = direction_impl.scan_timeseries(
      offsets, days, values, timestamp1s, timestamp2s, data_stdev)

    if be_verbose:
      print(' computed %d direction updates' % len(directions))

    # update database
    for (day, direction) in zip(days, directions):
      database.update_direction(
          source, signal, 'day', geo_type, day, geo_value, direction)

    # mark entire time-series as fresh with respect to direction
    database.update_timeseries_timestamp2(
        source, signal, 'day', geo_type, geo_value)


def main(
    args,
    database_impl=Database,
    update_loop_impl=update_loop):
  """Update the direction classification for covidcast signals.

  `args` parsed command-line arguments
  """

  database = database_impl()
  database.connect()
  commit = False

  try:
    update_loop_impl(database)
    commit = not args.test
  finally:
    print('committed=%s' % str(commit))
    database.disconnect(commit)


if __name__ == '__main__':
  main(get_argument_parser().parse_args())
