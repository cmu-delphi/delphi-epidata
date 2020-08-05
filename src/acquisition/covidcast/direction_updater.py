"""Computes and updates the `direction` column in the `covidcast` table.

Update is only performed for stale rows.
"""

# standard library
import argparse

# third party
import numpy as np
import pandas as pd

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi.epidata.acquisition.covidcast.direction import Direction


class Constants:
  """Constants used for direction classification."""

  # Display height is currently defined as 6 standard deviations of the
  # historical values of a particular signal across all locations at a
  # particular geographic resolution.
  SIGNAL_STDEV_SCALE = 6

  # Historical data is roughly defined to be all signal values up to, and
  # including, but not after, 2020-04-22.
  SIGNAL_STDEV_MAX_DAY = 20200422

  # Direction is non-zero when the following two conditions are met, given a
  # regression fit on a 7-day trend:
  #   - slope is statistically significant (±1 standard error)
  #   - slope is subjectively up or down (±10% of display height, per day)
  TREND_NUM_DAYS = 7
  SLOPE_STERR_SCALE = 1
  SLOPE_PERCENT_CHANGE = 0.1
  BASE_SLOPE_THRESHOLD = (
          SIGNAL_STDEV_SCALE * (SLOPE_PERCENT_CHANGE / TREND_NUM_DAYS)
  )


# partition configuration
PARTITION_VARIABLE = 'geo_value'
PARTITION_SPLITS = ["'05101'", "'101'", "'13071'", "'15007'", "'17161'", "'19039'", "'20123'", "'21213'", "'24035'",
                    "'27005'", "'28115'", "'29510'", "'31161'", "'35100'", "'37117'", "'39081'", "'41013'", "'44140'",
                    "'47027'", "'48140'", "'48461'", "'51169'", "'55033'"]



def get_argument_parser():
  """Define command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--partitions',
    type=int,
    nargs='+',
    default=list(range(len(PARTITION_SPLITS) + 1)),  # default is to process all partitions
    help='a list of integers for indexes of partitions to be processed')
  return parser


def update_loop(database, direction_impl=Direction):
  """Find and update rows with a stale `direction` value.

  `database`: an open connection to the epidata database
  """

  # get the keys for time-seres which may be stale
  stale_series = database.get_keys_with_potentially_stale_direction()
  num_series = len(stale_series)
  num_rows = 0
  for row in stale_series:
    num_rows += row[-1]
  msg = 'found %d time-series (%d rows) which may have stale direction'
  print(msg % (num_series, num_rows))

  # get the historical standard deviation of all signals and resolutions
  rows = database.get_data_stdev_across_locations(
    Constants.SIGNAL_STDEV_MAX_DAY)
  data_stdevs = {}
  for (source, signal, geo_type, aggregate_stdev) in rows:
    if source not in data_stdevs:
      data_stdevs[source] = {}
    if signal not in data_stdevs[source]:
      data_stdevs[source][signal] = {}
    data_stdevs[source][signal][geo_type] = aggregate_stdev

  # update direction for each time-series
  for ts_index, row in enumerate(stale_series):
    (
      source,
      signal,
      geo_type,
      geo_value,
      max_value_updated_timestamp,
      min_direction_updated_timestamp,
      min_day,
      max_day,
      series_length,
    ) = row

    if source not in data_stdevs or signal not in data_stdevs[source]:
      msg = '%s.%s is too new a signal to have a historical stdev reference; skipping'
      print(msg % (source,signal))
      continue

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
        max_value_updated_timestamp - min_direction_updated_timestamp,
      )
      print(msg % args)

    # get the data for this time-series
    timeseries_rows = database.get_daily_timeseries_for_direction_update(
      source, signal, geo_type, geo_value, min_day, max_day)

    # transpose result set and cast data types
    data = np.array(timeseries_rows)
    offsets, days, values, value_updated_timestamps, direction_updated_timestamps = data.T
    offsets = offsets.astype(np.int64)
    days = days.astype(np.int64)
    values = values.astype(np.float64)
    value_updated_timestamps = value_updated_timestamps.astype(np.int64)
    direction_updated_timestamps = direction_updated_timestamps.astype(np.int64)

    # create a direction classifier for this signal
    data_stdev = data_stdevs[source][signal][geo_type]
    slope_threshold = data_stdev * Constants.BASE_SLOPE_THRESHOLD

    def get_direction_impl(x, y):
      return direction_impl.get_direction(
        x, y, n=Constants.SLOPE_STERR_SCALE, limit=slope_threshold)

    # recompute any stale directions
    days, directions = direction_impl.scan_timeseries(
      offsets, days, values, value_updated_timestamps, direction_updated_timestamps, get_direction_impl)

    if be_verbose:
      print(' computed %d direction updates' % len(directions))

    # update directions in the database
    for (day, direction) in zip(days, directions):
      # the database can't handle numpy types, so use a python type
      day = int(day)
      database.update_direction(
        source, signal, 'day', geo_type, day, geo_value, direction)

    # mark the entire time-series as fresh with respect to direction
    database.update_timeseries_direction_updated_timestamp(
      source, signal, 'day', geo_type, geo_value)


def optimized_update_loop(database, partition_index, direction_impl=Direction):
  """An optimized implementation of update_loop, finds and updates rows with a stale `direction` value.

  `database`: an open connection to the epidata database
  `partition_index`: the index of the partition to be processed
  """

  # constructing the partitoin condition from partition index
  ge_condition = 'TRUE' if partition_index == 0 else f'`{PARTITION_VARIABLE}` >= {PARTITION_SPLITS[partition_index-1]}'
  l_condition = 'TRUE' if partition_index == len(PARTITION_SPLITS) else \
                f'`{PARTITION_VARIABLE}` < {PARTITION_SPLITS[partition_index]}'
  partition_condition = f'({ge_condition}) AND ({l_condition})'

  # Name of temporary table, which will store all rows from potentially stale time-series
  tmp_table_name = 'tmp_ts_rows'

  # A pandas DataFrame that will hold all rows from potentially stale time-series
  df_all = pd.DataFrame(columns=['id', 'source', 'signal', 'time_type', 'geo_type', 'geo_value', 'time_value',
                                 'value_updated_timestamp', 'value', 'direction_updated_timestamp', 'direction'],
                        data=database.get_all_record_values_of_timeseries_with_potentially_stale_direction(
                          tmp_table_name, partition_condition))
  df_all.drop(columns=['time_type'], inplace=True)
  df_all['time_value_datetime'] = pd.to_datetime(df_all.time_value, format="%Y%m%d")
  df_all.direction = df_all.direction.astype(np.float64)

  # Grouping by time-series key, 'time_type' as only time-series with value 'day' were retrieved.
  groupby_object = df_all.groupby(['source', 'signal', 'geo_type', 'geo_value'])

  num_series = len(groupby_object)
  num_rows = len(df_all)
  msg = 'found %d time-series (%d rows) which may have stale direction'
  print(msg % (num_series, num_rows))

  # get the historical standard deviation of all signals and resolutions
  rows = database.get_data_stdev_across_locations(
    Constants.SIGNAL_STDEV_MAX_DAY)
  data_stdevs = {}
  for (source, signal, geo_type, aggregate_stdev) in rows:
    if source not in data_stdevs:
      data_stdevs[source] = {}
    if signal not in data_stdevs[source]:
      data_stdevs[source][signal] = {}
    data_stdevs[source][signal][geo_type] = aggregate_stdev

  # Dictionary to store the ids of rows with changed direction value
  changed_rows = {-1.0: [], 0.0: [], 1.0: [], np.nan: []}

  # looping over time-series
  for ts_index, ts_key in enumerate(groupby_object.groups):
    (
        source,
        signal,
        geo_type,
        geo_value,
    ) = ts_key

    ts_rows = groupby_object.get_group(ts_key).sort_values('time_value_datetime')
    ts_rows['offsets'] = (ts_rows.time_value_datetime - ts_rows.time_value_datetime.iloc[0]).dt.days

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
          ts_rows.time_value.min(),
          ts_rows.time_value.max(),
          len(ts_rows),
          ts_rows.value_updated_timestamp.max() - ts_rows.direction_updated_timestamp.min()
      )
      print(msg % args)

    offsets = ts_rows.offsets.values.astype(np.int64)
    days = ts_rows.time_value.values.astype(np.int64)
    values = ts_rows.value.values.astype(np.float64)
    value_updated_timestamps = ts_rows.value_updated_timestamp.values.astype(np.int64)
    direction_updated_timestamps = ts_rows.direction_updated_timestamp.values.astype(np.int64)

    if (source in data_stdevs) and (signal in data_stdevs[source]) and (geo_type in data_stdevs[source][signal]):
      # create a direction classifier for this signal
      data_stdev = data_stdevs[source][signal][geo_type]
      slope_threshold = data_stdev * Constants.BASE_SLOPE_THRESHOLD

      def get_direction_impl(x, y):
        return direction_impl.get_direction(
          x, y, n=Constants.SLOPE_STERR_SCALE, limit=slope_threshold)

      # recompute any stale directions
      days, directions = direction_impl.scan_timeseries(
        offsets, days, values, value_updated_timestamps, direction_updated_timestamps, get_direction_impl)

      if be_verbose:
        print(' computed %d direction updates' % len(directions))

      # A DataFrame holding rows that potentially changed direction value
      ts_pot_changed = ts_rows.set_index('time_value').loc[days]
      ts_pot_changed['new_direction'] = np.array(directions, np.float64)

    # This is a Quick-Fix [in case no data for (source, signal, geo_type) exists before Constants.SIGNAL_STDEV_MAX_DAY]
    else:
      ts_pot_changed = ts_rows.set_index('time_value')
      ts_pot_changed['new_direction'] = np.nan

    # Adding changed values to the changed_rows dictionary
    gb_o = ts_pot_changed.groupby('new_direction')
    for v in gb_o.groups:
      changed_rows[v].extend(gb_o.get_group(v).id)
    changed_rows[np.nan].extend(ts_pot_changed[ts_pot_changed.new_direction.isnull()].id)

  # Updating direction
  for v, id_list in changed_rows.items():
    database.batched_update_direction(v, id_list)

  # Updating direction_updated_timestamp
  database.update_direction_updated_timestamp_from_temporary_table(tmp_table_name)
  # Dropping temporary table
  database.drop_temporary_table(tmp_table_name)


def main(
    args,
    database_impl=Database,
    update_loop_impl=optimized_update_loop):
  """Update the direction classification for covidcast signals.

  `args`: parsed command-line arguments
  """
  for partition_index in args.partitions:
    database = database_impl()
    database.connect()
    commit = False
    try:
      update_loop_impl(database, partition_index)
      # only commit on success so that directions are consistent with respect
      # to methodology
      commit = True
    except Exception as e:
      raise e
    finally:
      database.disconnect(commit)
      print('partition %d committed=%s' % (partition_index, str(commit)))


if __name__ == '__main__':
  main(get_argument_parser().parse_args())
