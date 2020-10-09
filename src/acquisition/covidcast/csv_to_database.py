"""Imports covidcast CSVs and stores them in the epidata database."""

# standard library
import argparse
import os

# first party
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter
from delphi.epidata.acquisition.covidcast.database import Database, CovidcastRow
from delphi.epidata.acquisition.covidcast.file_archiver import FileArchiver


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
  return parser

def scan_issue_specific(data_dir, database, is_wip_override=None, csv_importer_impl=CsvImporter, file_archiver_impl=FileArchiver):
  """  is_wip_override: None (default) for standard 'wip_' prefix processing, True for forcing all as WIP, False for forcing all as not WIP"
  """ # TODO: better docstring

  # TODO: this has *A LOT* of copypasta from scan_upload_archive() ... make it less so
  
  # collect files
  results = list(csv_importer_impl.find_issue_specific_csv_files(data_dir))
  print('found %d files' % len(results))

  # iterate over each file
  for path, details in results:
    print('handling ', path)
    path_src, filename = os.path.split(path)

    if not details:
      # file path or name was invalid, source is unknown
      print('unknown file, leaving alone:', path)
      continue

    (source, signal, time_type, geo_type, time_value, issue, lag) = details

    if is_wip_override is None:
      is_wip = signal[:4].lower() == "wip_"
    else:
      is_wip = is_wip_override
      # we are overriding, so remove prefix if it exists
      if signal[:4].lower() == "wip_":
        signal = signal[4:]
      # prepend (or put back) prefix if we are forcing as WIP
      if is_wip:
        signal = "wip_" + signal

    csv_rows = csv_importer_impl.load_csv(path, geo_type)

    cc_rows = CovidcastRow.fromCsvRows(csv_rows, source, signal, time_type, geo_type, time_value, issue, lag, is_wip)
    rows_list = list(cc_rows)
    all_rows_valid = rows_list and all(r is not None for r in rows_list)
    if all_rows_valid:
      try:
        result = database.insert_or_update_bulk(rows_list)
        print(f"insert_or_update_bulk {filename} returned {result}")
        if result is None or result: # else would indicate zero rows inserted
          database.commit()
      except Exception as e:
        all_rows_valid = False
        print('exception while inserting rows:', e)
        database.rollback()

    # archive the current file based on validation results
    if all_rows_valid:
      print('archiving as successful')
      file_archiver_impl.archive_inplace(path_src, filename)
    else:
      print('unsuccessful - not archiving file')

# TODO: consider extending is_wip_override behavior option to this method
def scan_upload_archive(
    data_dir,
    database,
    csv_importer_impl=CsvImporter,
    file_archiver_impl=FileArchiver):
  """Find CSVs, upload them to the database, and archive them.

  data_dir: top-level directory where CSVs are stored
  database: an open connection to the epidata database

  The CSV storage layout is assumed to be as follows:

  - Receiving: <data_dir>/receiving/<source name>/*.csv
  - Archival: <data_dir>/archive/<status>/<source name>/*.csv[.gz]

  Status above is one of `successful` or `failed`. See the accompanying readme
  for further details.
  """

  receiving_dir = os.path.join(data_dir, 'receiving')
  archive_successful_dir = os.path.join(data_dir, 'archive', 'successful')
  archive_failed_dir = os.path.join(data_dir, 'archive', 'failed')

  # helper to archive a failed file without compression
  def archive_as_failed(path_src, filename, source):
    print('archiving as failed - '+source)
    path_dst = os.path.join(archive_failed_dir, source)
    compress = False
    file_archiver_impl.archive_file(path_src, path_dst, filename, compress)

  # helper to archive a successful file with compression
  def archive_as_successful(path_src, filename, source):
    print('archiving as successful')
    path_dst = os.path.join(archive_successful_dir, source)
    compress = True
    file_archiver_impl.archive_file(path_src, path_dst, filename, compress)


  # collect files
  results = list(csv_importer_impl.find_csv_files(receiving_dir))
  print('found %d files' % len(results))

  # iterate over each file
  for path, details in results:
    print('handling ', path)
    path_src, filename = os.path.split(path)

    if not details:
      # file path or name was invalid, source is unknown
      archive_as_failed(path_src, filename, 'unknown')
      continue

    (source, signal, time_type, geo_type, time_value, issue, lag) = details

    is_wip = signal[:4].lower() == "wip_"

    csv_rows = csv_importer_impl.load_csv(path, geo_type)

    cc_rows = CovidcastRow.fromCsvRows(csv_rows, source, signal, time_type, geo_type, time_value, issue, lag, is_wip)
    rows_list = list(cc_rows)
    all_rows_valid = rows_list and all(r is not None for r in rows_list)
    if all_rows_valid:
      try:
        result = database.insert_or_update_bulk(rows_list)
        print(f"insert_or_update_bulk {filename} returned {result}")
        if result is None or result: # else would indicate zero rows inserted
          database.commit()
      except Exception as e:
        all_rows_valid = False
        print('exception while inserting rows:', e)
        database.rollback()

    # archive the current file based on validation results
    if all_rows_valid:
      archive_as_successful(path_src, filename, source)
    else:
      archive_as_failed(path_src, filename, source)


def main(
    args,
    database_impl=Database,
    scan_upload_archive_impl=scan_upload_archive,
    scan_issue_specific_impl=scan_issue_specific):
  """Find, parse, and upload covidcast signals."""

  if args.is_wip_override and args.not_wip_override:
    print('conflicting overrides for forcing WIP option!  exiting...')
    exit()
  wip_override = None
  if args.is_wip_override:
    wip_override = True
  if args.not_wip_override:
    wip_override = False

  database = database_impl()
  database.connect()
  num_starting_rows = database.count_all_rows()


  try:
    if args.specific_issue_date:
      scan_issue_specific_impl(args.data_dir, database, is_wip_override=wip_override)
    else:
      scan_upload_archive_impl(args.data_dir, database)
  finally:
    # no catch block so that an exception above will cause the program to fail
    # after the following cleanup
    try:
      num_inserted_rows = database.count_all_rows() - num_starting_rows
      print('inserted/updated %d rows' % num_inserted_rows)
    finally:
      # unconditionally commit database changes since CSVs have been archived
      database.disconnect(True)


if __name__ == '__main__':
  main(get_argument_parser().parse_args())
