"""Imports covidcast CSVs and stores them in the epidata database."""

# standard library
import argparse
import os

# first party
from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter
from delphi.epidata.acquisition.covidcast.database import Database
from delphi.epidata.acquisition.covidcast.file_archiver import FileArchiver


def get_argument_parser():
  """Define command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--data_dir',
    help='top-level directory where CSVs are stored')
  parser.add_argument(
    '--test',
    action='store_true',
    help='do a dry run without committing changes')
  return parser


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
    print('archiving as failed')
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

    (source, signal, time_type, geo_type, time_value) = details

    # iterate over rows and upload to the database
    all_rows_valid = True
    for row_values in csv_importer_impl.load_csv(path, geo_type):
      if not row_values:
        all_rows_valid = False
        continue

      database.insert_or_update(
          source,
          signal,
          time_type,
          geo_type,
          time_value,
          row_values.geo_value,
          row_values.value,
          row_values.stderr,
          row_values.sample_size)

    # archive the current file based on validation results
    if all_rows_valid:
      archive_as_successful(path_src, filename, source)
    else:
      archive_as_failed(path_src, filename, source)


def main(
    args,
    database_impl=Database,
    scan_upload_archive_impl=scan_upload_archive):
  """Find, parse, and upload covidcast signals."""

  database = database_impl()
  database.connect()
  num_starting_rows = database.count_all_rows()
  commit = False

  try:
    scan_upload_archive_impl(args.data_dir, database)
    commit = not args.test
  finally:
    num_inserted_rows = database.count_all_rows() - num_starting_rows
    print('inserted=%d committed=%s' % (num_inserted_rows, str(commit)))
    database.disconnect(commit)


if __name__ == '__main__':
  main(get_argument_parser().parse_args())
