"""Imports covidcast CSVs and stores them in the epidata database."""

# standard library
import argparse
import os
import time
from logging import Logger
from typing import Callable, Iterable, Optional, Tuple

# first party
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter, PathDetails
from delphi.epidata.acquisition.covidcast.database import Database, DBLoadStateException
from delphi.epidata.acquisition.covidcast.file_archiver import FileArchiver
from delphi_utils import get_structured_logger


def get_argument_parser():
  """Define command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--data_dir',
    help='top-level directory where CSVs are stored')
  parser.add_argument(
    '--specific_issue_date',
    action='store_true',
    help='indicates <data_dir> argument is where issuedate-specific subdirectories can be found.')
  parser.add_argument(
    '--log_file',
    help="filename for log output (defaults to stdout)")
  parser.add_argument(
    '--indicator_name',
    nargs='?',
    default='*',
    help='Name of one indicator directory to run acquisition on')
  return parser


def collect_files(data_dir: str, specific_issue_date: bool, indicator_name="*"):
  """Fetch path and data profile details for each file to upload."""
  logger= get_structured_logger('collect_files')
  if specific_issue_date:
    results = list(CsvImporter.find_issue_specific_csv_files(data_dir))
  else:
    results = list(CsvImporter.find_csv_files(os.path.join(data_dir, 'receiving'), indicator_dir=indicator_name))
  logger.info(f'found {len(results)} files')
  return results


def make_handlers(data_dir: str, specific_issue_date: bool):
  if specific_issue_date:
    # issue-specific uploads are always one-offs, so we can leave all
    # files in place without worrying about cleaning up
    def handle_failed(path_src, filename, source, logger):
      logger.info(event='leaving failed file alone', dest=source, file=filename)

    def handle_successful(path_src, filename, source, logger):
      logger.info(event='archiving as successful',file=filename)
      FileArchiver.archive_inplace(path_src, filename)
  else:
    # normal automation runs require some shuffling to remove files
    # from receiving and place them in the archive
    archive_successful_dir = os.path.join(data_dir, 'archive', 'successful')
    archive_failed_dir = os.path.join(data_dir, 'archive', 'failed')

    # helper to archive a failed file without compression
    def handle_failed(path_src, filename, source, logger):
      logger.info(event='archiving as failed - ', detail=source, file=filename)
      path_dst = os.path.join(archive_failed_dir, source)
      compress = False
      FileArchiver.archive_file(path_src, path_dst, filename, compress)

    # helper to archive a successful file with compression
    def handle_successful(path_src, filename, source, logger):
      logger.info(event='archiving as successful',file=filename)
      path_dst = os.path.join(archive_successful_dir, source)
      compress = True
      FileArchiver.archive_file(path_src, path_dst, filename, compress)

  return handle_successful, handle_failed


def upload_archive(
  path_details: Iterable[Tuple[str, Optional[PathDetails]]],
  database: Database,
  handlers: Tuple[Callable],
  logger: Logger
  ):
  """Upload CSVs to the database and archive them using the specified handlers.

  :path_details: output from CsvImporter.find*_csv_files

  :database: an open connection to the epidata database

  :handlers: functions for archiving (successful, failed) files

  :return: the number of modified rows
  """
  archive_as_successful, archive_as_failed = handlers
  total_modified_row_count = 0
  # iterate over each file
  for path, details in path_details:
    logger.info(event='handling', dest=path)
    path_src, filename = os.path.split(path)

    # file path or name was invalid, source is unknown
    if not details:
      archive_as_failed(path_src, filename, 'unknown',logger)
      continue

    csv_rows = CsvImporter.load_csv(path, details)
    rows_list = list(csv_rows)
    all_rows_valid = rows_list and all(r is not None for r in rows_list)
    if all_rows_valid:
      try:
        modified_row_count = database.insert_or_update_bulk(rows_list)
        logger.info(f"insert_or_update_bulk {filename} returned {modified_row_count}")
        logger.info(
          "Inserted database rows",
          row_count = modified_row_count,
          source = details.source,
          signal = details.signal,
          geo_type = details.geo_type,
          time_value = details.time_value,
          issue = details.issue,
          lag = details.lag
        )
        if modified_row_count is None or modified_row_count: # else would indicate zero rows inserted
          total_modified_row_count += (modified_row_count if modified_row_count else 0)
          database.commit()
      except DBLoadStateException as e:
        # if the db is in a state that is not fit for loading new data,
        # then we should stop processing any more files
        raise e
      except Exception as e:
        all_rows_valid = False
        logger.exception('exception while inserting rows', exc_info=e)
        database.rollback()

    # archive the current file based on validation results
    if all_rows_valid:
      archive_as_successful(path_src, filename, details.source, logger)
    else:
      archive_as_failed(path_src, filename, details.source, logger)

  return total_modified_row_count


def main(args):
  """Find, parse, and upload covidcast signals."""

  logger = get_structured_logger("csv_ingestion", filename=args.log_file)
  start_time = time.time()
  # shortcut escape without hitting db if nothing to do
  path_details=collect_files(args.data_dir, args.specific_issue_date, indicator_name = args.indicator_name)
  if not path_details:
    logger.info('nothing to do; exiting...')
    return

  logger.info("Ingesting CSVs", csv_count = len(path_details))

  database = Database()
  database.connect()

  try:
    modified_row_count = upload_archive(
      path_details,
      database,
      make_handlers(args.data_dir, args.specific_issue_date),
      logger
    )
    logger.info("Finished inserting/updating database rows", row_count = modified_row_count)
  finally:
    database.do_analyze()
    # unconditionally commit database changes since CSVs have been archived
    database.disconnect(True)

  logger.info(
      "Ingested CSVs into database",
      total_runtime_in_seconds=round(time.time() - start_time, 2))


if __name__ == '__main__':
  main(get_argument_parser().parse_args())
