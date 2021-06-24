"""Imports covidcast CSVs and stores them in the epidata database."""

# standard library
import argparse
import os
import time

# first party
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
from delphi.epidata.acquisition.covidcast.file_archiver import FileArchiver
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger


def get_argument_parser():
  """Define command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--data_dir',
    help='top-level directory where CSVs are stored')
  parser.add_argument(
    '--specific_issue_date',
    action='store_true',
    help='indicates <data_dir> argument is where issuedate-specific subdirectories can be found.  also enables --*_wip_override arguments.')
  # TODO: better options for wip overriding, such sa mutual exclusion and such
  parser.add_argument(
    '--is_wip_override',
    action='store_true',
    help='overrides all signals to mark them as WIP.  NOTE: specify neither or only one of --is_wip_override and --not_wip_override.')
  parser.add_argument(
    '--not_wip_override',
    action='store_true',
    help='overrides all signals to mark them as *not* WIP.  NOTE: specify neither or only one of --is_wip_override and --not_wip_override.')
  parser.add_argument(
    '--log_file',
    help="filename for log output (defaults to stdout)")
  return parser

def collect_files(data_dir, specific_issue_date,csv_importer_impl=CsvImporter):
  """Fetch path and data profile details for each file to upload."""
  logger= get_structured_logger('collect_files')
  if specific_issue_date:
    results = list(csv_importer_impl.find_issue_specific_csv_files(data_dir))
  else:
    results = list(csv_importer_impl.find_csv_files(os.path.join(data_dir, 'receiving')))
  logger.info(f'found {len(results)} files')
  return results

def make_handlers(data_dir, specific_issue_date, file_archiver_impl=FileArchiver):
  if specific_issue_date:
    # issue-specific uploads are always one-offs, so we can leave all
    # files in place without worrying about cleaning up
    def handle_failed(path_src, filename, source):
      logger= get_structured_logger('handle_failed')
      logger.info(f'leaving failed file alone - {source}')

    def handle_successful(path_src, filename, source):
      logger= get_structured_logger('handle_successful')
      logger.info('archiving as successful')
      file_archiver_impl.archive_inplace(path_src, filename)
  else:
    # normal automation runs require some shuffling to remove files
    # from receiving and place them in the archive
    archive_successful_dir = os.path.join(data_dir, 'archive', 'successful')
    archive_failed_dir = os.path.join(data_dir, 'archive', 'failed')

    # helper to archive a failed file without compression
    def handle_failed(path_src, filename, source):
      logger= get_structured_logger('handle_failed')
      logger.info('archiving as failed - '+source)
      path_dst = os.path.join(archive_failed_dir, source)
      compress = False
      file_archiver_impl.archive_file(path_src, path_dst, filename, compress)

    # helper to archive a successful file with compression
    def handle_successful(path_src, filename, source):
      logger= get_structured_logger('handle_successful')
      logger.info('archiving as successful')
      path_dst = os.path.join(archive_successful_dir, source)
      compress = True
      file_archiver_impl.archive_file(path_src, path_dst, filename, compress)
  return handle_successful, handle_failed

def upload_archive(
    path_details,
    database,
    handlers,
    logger,
    is_wip_override=None,
    csv_importer_impl=CsvImporter):
  """Upload CSVs to the database and archive them using the specified handlers.

  :path_details: output from CsvImporter.find*_csv_files 
  
  :database: an open connection to the epidata database

  :handlers: functions for archiving (successful, failed) files
  
  :is_wip_override: default None (detect WIP status using
  filename). If boolean, whether to force WIP status (True) or
  production status (False) regardless of what the filename says

  :return: the number of modified rows
  """
  archive_as_successful, archive_as_failed = handlers
  total_modified_row_count = 0
  # iterate over each file
  for path, details in path_details:
    logger.info(f'handling {path}')
    path_src, filename = os.path.split(path)

    if not details:
      # file path or name was invalid, source is unknown
      archive_as_failed(path_src, filename, 'unknown')
      continue

    (source, signal, time_type, geo_type, time_value, issue, lag) = details

    if is_wip_override is None:
      is_wip = signal[:4].lower() == "wip_"
    else:
      is_wip = is_wip_override
      # strip wip from signal name if we're forcing production status
      if signal[:4].lower() == "wip_" and not is_wip:
        signal = signal[4:]

    csv_rows = csv_importer_impl.load_csv(path, geo_type)

    cc_rows = CovidcastRow.fromCsvRows(csv_rows, source, signal, time_type, geo_type, time_value, issue, lag, is_wip)
    rows_list = list(cc_rows)
    all_rows_valid = rows_list and all(r is not None for r in rows_list)
    if all_rows_valid:
      try:
        modified_row_count = database.insert_or_update_bulk(rows_list)
        logger.info(f"insert_or_update_bulk {filename} returned {modified_row_count}")
        logger.info(
          "Inserted database rows",
          row_count = modified_row_count,
          source = source,
          signal = signal,
          geo_type = geo_type,
          time_value = time_value,
          issue = issue,
          lag = lag)
        if modified_row_count is None or modified_row_count: # else would indicate zero rows inserted
          total_modified_row_count += (modified_row_count if modified_row_count else 0)
          database.commit()
      except Exception as e:
        all_rows_valid = False
        logger.exception('exception while inserting rows:', e)
        database.rollback()

    # archive the current file based on validation results
    if all_rows_valid:
      archive_as_successful(path_src, filename, source)
    else:
      archive_as_failed(path_src, filename, source)
  
  return total_modified_row_count


def main(
    args,
    database_impl=Database,
    collect_files_impl=collect_files,
    upload_archive_impl=upload_archive):
  """Find, parse, and upload covidcast signals."""

  logger = get_structured_logger("csv_ingestion", filename=args.log_file)
  start_time = time.time()

  if args.is_wip_override and args.not_wip_override:
    logger.error('conflicting overrides for forcing WIP option!  exiting...')
    return
  wip_override = None
  if args.is_wip_override:
    wip_override = True
  if args.not_wip_override:
    wip_override = False

  # shortcut escape without hitting db if nothing to do
  path_details = collect_files_impl(args.data_dir, args.specific_issue_date)
  if not path_details:
    logger.info('nothing to do; exiting...')
    return
  
  logger.info("Ingesting CSVs", csv_count = len(path_details))

  database = database_impl()
  database.connect()

  try:
    modified_row_count = upload_archive_impl(
      path_details,
      database,
      make_handlers(args.data_dir, args.specific_issue_date),
      logger,
      is_wip_override=wip_override)
    logger.info("Finished inserting database rows", row_count = modified_row_count)
    # the following print statement serves the same function as the logger.info call above
    # print('inserted/updated %d rows' % modified_row_count)
  finally:
    # unconditionally commit database changes since CSVs have been archived
    database.disconnect(True)
  
  logger.info(
      "Ingested CSVs into database",
      total_runtime_in_seconds=round(time.time() - start_time, 2))

if __name__ == '__main__':
  main(get_argument_parser().parse_args())
