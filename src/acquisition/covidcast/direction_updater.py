"""Computes and updates the `direction` column in the `covidcast` table.

Update is only performed for stale rows.
"""

# standard library
import argparse

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

  # counters across batches
  overall_done, overall_total = 0, 0

  while True:

    stale_rows = database.get_rows_with_stale_direction()
    print('stale rows in batch:', len(stale_rows))

    if not stale_rows:
      # nothing left to do
      break

    overall_total += len(stale_rows)

    for (row_index, stale_row) in enumerate(stale_rows):
      (
        source,
        signal,
        time_type,
        geo_type,
        time_value,
        geo_value,
        timestamp2,
        max_timestamp1,
        support,
      ) = stale_row

      if support < 3:
        # there's not enough history to compute direction
        direction = None
      else:
        # get history from the database
        value_rows = database.get_rows_to_compute_direction(
            source,
            signal,
            geo_type,
            time_value,
            geo_value)
        x, y = [], []
        for (time_offset, value) in value_rows:
          x.append(time_offset)
          y.append(value)

        # compute direction from historical trend
        direction = direction_impl.get_direction(x, y)

      # update the `direction` column for this row
      database.update_direction(
          source,
          signal,
          time_type,
          geo_type,
          time_value,
          geo_value,
          direction)

      overall_done += 1

      # progress report for anyone debugging/watching the output
      power_of_two = ((row_index + 1) & row_index) == 0
      if power_of_two:
        args = (overall_done, overall_total)
        print('updated row %d/%d:' % args, stale_row, direction)


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
