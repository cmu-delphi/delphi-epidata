"""Updates the cache for the `covidcast_meta` endpiont."""

# standard library
import argparse
import sys
import time

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi_utils import get_structured_logger
from delphi.epidata.client.delphi_epidata import Epidata

def get_argument_parser():
  """Define command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument("--log_file", help="filename for log output")
  parser.add_argument("--num_threads", type=int, help="number of worker threads to spawn for processing source/signal pairs")
  return parser


def main(args, epidata_impl=Epidata, database_impl=Database):
  """Update the covidcast metadata cache.

  `args`: parsed command-line arguments
  """
  log_file = None
  num_threads = None
  if (args):
    log_file = args.log_file
    num_threads = args.num_threads

  logger = get_structured_logger(
      "metadata_cache_updater",
      filename=log_file)
  start_time = time.time()
  database = database_impl()
  database.connect()

  # fetch metadata
  try:
    metadata_calculation_start_time = time.time()
    metadata = database.compute_covidcast_meta(n_threads=num_threads)
    metadata_calculation_interval_in_seconds = time.time() - metadata_calculation_start_time
  except:
    # clean up before failing
    database.disconnect(True)
    raise

  args = ("success",1)
  if len(metadata)==0:
    args = ("no results",-2)

  logger.info('covidcast_meta result: %s (code %d)' % args)

  if args[-1] != 1:
    logger.error('unable to cache epidata')
    return False

  # update the cache
  try:
    metadata_update_start_time = time.time()
    database.update_covidcast_meta_cache(metadata)
    metadata_update_interval_in_seconds = time.time() - metadata_update_start_time
    logger.info('successfully cached epidata')
  finally:
    # no catch block so that an exception above will cause the program to
    # fail after the following cleanup
    database.disconnect(True)

  logger.info(
      "Generated and updated covidcast metadata",
      metadata_calculation_interval_in_seconds=round(
          metadata_calculation_interval_in_seconds, 2),
      metadata_update_interval_in_seconds=round(
          metadata_update_interval_in_seconds, 2),
      total_runtime_in_seconds=round(time.time() - start_time, 2))
  return True


if __name__ == '__main__':
  if not main(get_argument_parser().parse_args()):
    sys.exit(1)
