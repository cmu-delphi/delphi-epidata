"""Updates the table for the `coverage_crossref` endpoint."""

import time

from delphi.epidata.acquisition.covidcast.database import Database
from delphi_utils import get_structured_logger


def main():
  """Updates the table for the `coverage_crossref`."""

  logger = get_structured_logger("coverage_crossref_updater")
  start_time = time.time()
  database = Database()
  database.connect()

  # compute and update coverage_crossref
  try:
    coverage = database.compute_coverage_crossref()
  finally:
    # clean up in success and in failure
    database.disconnect(True)

  logger.info(f"coverage_crossref returned: {coverage}")

  logger.info(
      "Generated and updated covidcast geo/signal coverage",
      total_runtime_in_seconds=round(time.time() - start_time, 2))
  return True


if __name__ == '__main__':
  main()
