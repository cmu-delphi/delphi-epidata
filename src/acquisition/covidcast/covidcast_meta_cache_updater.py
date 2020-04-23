"""Updates the cache for the `covidcast_meta` endpiont."""

# standard library
import argparse
import json

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

  # fetch live (not cached) metadata
  response = epidata_impl.covidcast_meta()
  args = (response['message'], response['result'])
  print('covidcast_meta result: %s (code %d)' % args)

  if response['result'] != 1:
    print('unable to cache epidata')
    return

  # serialize the data
  epidata_json = json.dumps(response['epidata'])

  # update the cache
  database = database_impl()
  database.connect()
  try:
    database.update_covidcast_meta_cache(epidata_json)
    print('successfully cached epidata')
  finally:
    # no catch block so that an exception above will cause the program to
    # fail after the following cleanup
    database.disconnect(True)


if __name__ == '__main__':
  main(get_argument_parser().parse_args())
