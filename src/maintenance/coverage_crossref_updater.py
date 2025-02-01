"""Updates the table for the `coverage_crossref` endpoint."""

# standard library
import argparse
import sys
import time

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi_utils import get_structured_logger
from delphi.epidata.client.delphi_epidata import Epidata


def main():
  """Updates the table for the `coverage_crossref`."""

  logger = get_structured_logger("coverage_crossref_updater")
  start_time = time.time()
  database = Database()
  database.connect()

  # compute and update coverage_crossref
  try:
    coverage = database.compute_coverage_crossref()
  except:
    # clean up before failing
    database.disconnect(True)
    raise

  result = ("success",1)
  if coverage==0:
    result = ("no results",-2)

  logger.info('coverage_crossref result: %s (code %d)' % result)


  logger.info(
      "Generated and updated covidcast geo/signal coverage",
      total_runtime_in_seconds=round(time.time() - start_time, 2))
  return True


if __name__ == '__main__':
  main()
