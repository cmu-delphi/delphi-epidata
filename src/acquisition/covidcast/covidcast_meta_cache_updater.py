"""Updates the cache for the `covidcast_meta` endpiont."""

# standard library
import argparse
import sys

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi.epidata.client.delphi_epidata import Epidata


def get_argument_parser():
  """Define command line arguments."""

  # there are no flags, but --help will still work
  return argparse.ArgumentParser()


def main(args, epidata_impl=Epidata, database_impl=Database):
  """Update the covidcast metadata cache.

  `args`: parsed command-line arguments
  """
  database = database_impl()
  database.connect()

  # fetch metadata
  try:
    metadata = database.compute_covidcast_meta()
  except:
    # clean up before failing
    database.disconnect(True)
    raise

  args = ("success",1)
  if len(metadata)==0:
    args = ("no results",-2)

  print('covidcast_meta result: %s (code %d)' % args)

  if args[-1] != 1:
    print('unable to cache epidata')
    return False

  # update the cache
  try:
    database.update_covidcast_meta_cache(metadata)
    print('successfully cached epidata')
  finally:
    # no catch block so that an exception above will cause the program to
    # fail after the following cleanup
    database.disconnect(True)

  return True


if __name__ == '__main__':
  if not main(get_argument_parser().parse_args()):
    sys.exit(1)
