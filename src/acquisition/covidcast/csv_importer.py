"""
Collects and reads covidcast data from a set of local CSV files.

Imports covidcast CSVs and stores them in the epidata database.
"""

import argparse
import os
import re
import time
from dataclasses import dataclass
from datetime import date
from glob import glob
from logging import Logger
from typing import Callable, Iterable, Iterator, NamedTuple, Optional, Tuple

import epiweeks as epi
import pandas as pd
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.database import Database, DBLoadStateException
from delphi.epidata.acquisition.covidcast.file_archiver import FileArchiver
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger
from delphi.utils.epiweek import delta_epiweeks
from delphi_utils import Nans


DataFrameRow = NamedTuple('DFRow', [
  ('geo_id', str),
  ('value', float),
  ('stderr', float),
  ('sample_size', float),
  ('missing_value', int),
  ('missing_stderr', int),
  ('missing_sample_size', int)
])
PathDetails = NamedTuple('PathDetails', [
  ('issue', int),
  ('lag', int),
  ('source', str),
  ("signal", str),
  ('time_type', str),
  ('time_value', int),
  ('geo_type', str),
])


@dataclass
class CsvRowValue:
  """A container for the values of a single validated covidcast CSV row."""
  geo_value: str
  value: float
  stderr: float
  sample_size: float
  missing_value: int
  missing_stderr: int
  missing_sample_size: int


class CsvImporter:
  """Finds and parses covidcast CSV files."""

  # .../source/yyyymmdd_geo_signal.csv
  PATTERN_DAILY = re.compile(r'^.*/([^/]*)/(\d{8})_(\w+?)_(\w+)\.csv$')

  # .../source/weekly_yyyyww_geo_signal.csv
  PATTERN_WEEKLY = re.compile(r'^.*/([^/]*)/weekly_(\d{6})_(\w+?)_(\w+)\.csv$')

  # .../issue_yyyymmdd
  PATTERN_ISSUE_DIR = re.compile(r'^.*/([^/]*)/issue_(\d{8})$')

  # set of allowed resolutions (aka "geo_type")
  GEOGRAPHIC_RESOLUTIONS = {'county', 'hrr', 'msa', 'dma', 'state', 'hhs', 'nation'}

  # set of required CSV columns
  REQUIRED_COLUMNS = {'geo_id', 'val', 'se', 'sample_size'}

  # reasonable time bounds for sanity checking time values
  MIN_YEAR = 2019
  MAX_YEAR = 2030

  # The datatypes expected by pandas.read_csv. Int64 is like float in that it can handle both numbers and nans.
  DTYPES = {
    "geo_id": str,
    "val": float,
    "se": float,
    "sample_size": float,
    "missing_val": "Int64",
    "missing_se": "Int64",
    "missing_sample_size": "Int64"
  }


  @staticmethod
  def is_sane_day(value):
    """Return whether `value` is a sane (maybe not valid) YYYYMMDD date.

    Truthy return is is a datetime.date object representing `value`."""

    year, month, day = value // 10000, (value % 10000) // 100, value % 100

    nearby_year = CsvImporter.MIN_YEAR <= year <= CsvImporter.MAX_YEAR
    valid_month = 1 <= month <= 12
    sensible_day = 1 <= day <= 31

    if not (nearby_year and valid_month and sensible_day):
      return False
    return date(year=year,month=month,day=day)


  @staticmethod
  def is_sane_week(value):
    """Return whether `value` is a sane (maybe not valid) YYYYWW epiweek.

    Truthy return is `value`."""

    year, week = value // 100, value % 100

    nearby_year = CsvImporter.MIN_YEAR <= year <= CsvImporter.MAX_YEAR
    sensible_week = 1 <= week <= 53

    if not (nearby_year and sensible_week):
      return False
    return value


  @staticmethod
  def find_issue_specific_csv_files(scan_dir):
    logger = get_structured_logger('find_issue_specific_csv_files')
    for path in sorted(glob(os.path.join(scan_dir, '*'))):
      issuedir_match = CsvImporter.PATTERN_ISSUE_DIR.match(path.lower())
      if issuedir_match and os.path.isdir(path):
        issue_date_value = int(issuedir_match.group(2))
        issue_date = CsvImporter.is_sane_day(issue_date_value)
        if issue_date:
          logger.info(event='processing csv files from issue', detail=issue_date, file=path)
          yield from CsvImporter.find_csv_files(path, issue=(issue_date, epi.Week.fromdate(issue_date)))
        else:
          logger.warning(event='invalid issue directory day', detail=issue_date_value, file=path)


  @staticmethod
  def find_csv_files(scan_dir, issue=(date.today(), epi.Week.fromdate(date.today()))):
    """Recursively search for and yield covidcast-format CSV files.

    scan_dir: the directory to scan (recursively)

    The return value is a tuple of (path, details), where, if the path was
    valid, details is a tuple of (source, signal, time_type, geo_type,
    time_value, issue, lag) (otherwise None).
    """
    logger = get_structured_logger('find_csv_files')
    issue_day,issue_epiweek=issue
    issue_day_value=int(issue_day.strftime("%Y%m%d"))
    issue_epiweek_value=int(str(issue_epiweek))
    issue_value=-1
    lag_value=-1

    for path in sorted(glob(os.path.join(scan_dir, '*', '*'))):
      # safe to ignore this file
      if not path.lower().endswith('.csv'):
        continue

      # match a daily or weekly naming pattern
      daily_match = CsvImporter.PATTERN_DAILY.match(path.lower())
      weekly_match = CsvImporter.PATTERN_WEEKLY.match(path.lower())
      if not daily_match and not weekly_match:
        logger.warning(event='invalid csv path/filename', detail=path, file=path)
        yield (path, None)
        continue

      # extract and validate time resolution
      if daily_match:
        time_type = 'day'
        time_value = int(daily_match.group(2))
        match = daily_match
        time_value_day = CsvImporter.is_sane_day(time_value)
        if not time_value_day:
          logger.warning(event='invalid filename day', detail=time_value, file=path)
          yield (path, None)
          continue
        issue_value=issue_day_value
        lag_value=(issue_day-time_value_day).days
      else:
        time_type = 'week'
        time_value = int(weekly_match.group(2))
        match = weekly_match
        time_value_week=CsvImporter.is_sane_week(time_value)
        if not time_value_week:
          logger.warning(event='invalid filename week', detail=time_value, file=path)
          yield (path, None)
          continue
        issue_value=issue_epiweek_value
        lag_value=delta_epiweeks(time_value_week, issue_epiweek_value)

      # # extract and validate geographic resolution
      geo_type = match.group(3).lower()
      if geo_type not in CsvImporter.GEOGRAPHIC_RESOLUTIONS:
        logger.warning(event='invalid geo_type', detail=geo_type, file=path)
        yield (path, None)
        continue

      # extract additional values, lowercased for consistency
      source = match.group(1).lower()
      signal = match.group(4).lower()
      if len(signal) > 64:
        logger.warning(event='invalid signal name (64 char limit)',detail=signal, file=path)
        yield (path, None)
        continue

      yield (path, PathDetails(issue_value, lag_value, source, signal, time_type, time_value, geo_type))


  @staticmethod
  def is_header_valid(columns):
    """Return whether the given pandas columns contains the required fields."""

    return CsvImporter.REQUIRED_COLUMNS.issubset(set(columns))


  @staticmethod
  def floaty_int(value: str) -> int:
    """Cast a string to an int, even if it looks like a float.

    For example, "-1" and "-1.0" should both result in -1. Non-integer floats
    will cause `ValueError` to be reaised.
    """

    float_value = float(value)
    if not float_value.is_integer():
      raise ValueError('not an int: "%s"' % str(value))
    return int(float_value)


  @staticmethod
  def maybe_apply(func, quantity):
    """Apply the given function to the given quantity if not null-ish."""
    if str(quantity).lower() in ('inf', '-inf'):
      raise ValueError("Quantity given was an inf.")
    elif str(quantity).lower() in ('', 'na', 'nan', 'none'):
      return None
    else:
      return func(quantity)


  @staticmethod
  def validate_quantity(row, attr_quantity):
    """Take a row and validate a given associated quantity (e.g., val, se, stderr).

    Returns either a float, a None, or "Error".
    """
    try:
      quantity = CsvImporter.maybe_apply(float, getattr(row, attr_quantity))
      return quantity
    except (ValueError, AttributeError):
      # val was a string or another data
      return "Error"


  @staticmethod
  def validate_missing_code(row, attr_quantity, attr_name, filepath=None, logger=None):
    """Take a row and validate the missing code associated with
    a quantity (e.g., val, se, stderr).

    Returns either a nan code for assignment to the missing quantity
    or a None to signal an error with the missing code. We decline
    to infer missing codes except for a very simple cases; the default
    is to produce an error so that the issue can be fixed in indicators.
    """
    logger = get_structured_logger('load_csv') if logger is None else logger
    missing_entry = getattr(row, "missing_" + attr_name, None)

    try:
      missing_entry = CsvImporter.floaty_int(missing_entry) # convert from string to float to int
    except (ValueError, TypeError):
      missing_entry = None

    if missing_entry is None and attr_quantity is not None:
      return Nans.NOT_MISSING.value
    if missing_entry is None and attr_quantity is None:
      return Nans.OTHER.value

    if missing_entry != Nans.NOT_MISSING.value and attr_quantity is not None:
      logger.warning(event = f"missing_{attr_name} column contradicting {attr_name} presence.", detail = (str(row)), file = filepath)
      return Nans.NOT_MISSING.value
    if missing_entry == Nans.NOT_MISSING.value and attr_quantity is None:
      logger.warning(event = f"missing_{attr_name} column contradicting {attr_name} presence.", detail = (str(row)), file = filepath)
      return Nans.OTHER.value

    return missing_entry

  @staticmethod
  def extract_and_check_row(row: DataFrameRow, geo_type: str, filepath: Optional[str] = None) -> Tuple[Optional[CsvRowValue], Optional[str]]:
    """Extract and return `CsvRowValue` from a CSV row, with sanity checks.

    Also returns the name of the field which failed sanity check, or None.

    row: the pandas table row to extract
    geo_type: the geographic resolution of the file
    """

    # use consistent capitalization (e.g. for states)
    try:
      geo_id = row.geo_id.lower()
    except AttributeError:
      # geo_id was `None`
      return (None, 'geo_id')

    if geo_type in ('hrr', 'msa', 'dma', 'hhs'):
      # these particular ids are prone to be written as ints -- and floats
      try:
        geo_id = str(CsvImporter.floaty_int(geo_id))
      except ValueError:
        # expected a number, but got a string
        return (None, 'geo_id')

    # sanity check geo_id with respect to geo_type
    if geo_type == 'county':
      if len(geo_id) != 5 or not '01000' <= geo_id <= '80000':
        return (None, 'geo_id')

    elif geo_type == 'hrr':
      if not 1 <= int(geo_id) <= 500:
        return (None, 'geo_id')

    elif geo_type == 'msa':
      if len(geo_id) != 5 or not '10000' <= geo_id <= '99999':
        return (None, 'geo_id')

    elif geo_type == 'dma':
      if not 450 <= int(geo_id) <= 950:
        return (None, 'geo_id')

    elif geo_type == 'state':
      # note that geo_id is lowercase
      if len(geo_id) != 2 or not 'aa' <= geo_id <= 'zz':
        return (None, 'geo_id')

    elif geo_type == 'hhs':
      if not 1 <= int(geo_id) <= 10:
        return (None, 'geo_id')

    elif geo_type == 'nation':
      # geo_id is lowercase
      if len(geo_id) != 2 or not 'aa' <= geo_id <= 'zz':
        return (None, 'geo_id')

    else:
      return (None, 'geo_type')

    # Validate row values
    value = CsvImporter.validate_quantity(row, "value")
    # value was a string or another dtype
    if value == "Error":
      return (None, 'value')
    stderr = CsvImporter.validate_quantity(row, "stderr")
    # stderr is a string, another dtype, or negative
    if stderr == "Error" or (stderr is not None and stderr < 0):
      return (None, 'stderr')
    sample_size = CsvImporter.validate_quantity(row, "sample_size")
    # sample_size is a string, another dtype, or negative
    if sample_size == "Error" or (sample_size is not None and sample_size < 0):
      return (None, 'sample_size')

    # Validate and write missingness codes
    missing_value = CsvImporter.validate_missing_code(row, value, "value", filepath)
    missing_stderr = CsvImporter.validate_missing_code(row, stderr, "stderr", filepath)
    missing_sample_size = CsvImporter.validate_missing_code(row, sample_size, "sample_size", filepath)

    # return extracted and validated row values
    return (CsvRowValue(geo_id, value, stderr, sample_size, missing_value, missing_stderr, missing_sample_size), None)


  @staticmethod
  def load_csv(filepath: str, details: PathDetails) -> Iterator[Optional[CovidcastRow]]:
    """Load, validate, and yield data as `RowValues` from a CSV file.

    filepath: the CSV file to be loaded
    geo_type: the geographic resolution (e.g. county)

    In case of a validation error, `None` is yielded for the offending row,
    including the header.
    """
    logger = get_structured_logger('load_csv')

    try:
      table = pd.read_csv(filepath, dtype=CsvImporter.DTYPES)
    except pd.errors.DtypeWarning as e:
      logger.warning(event='Failed to open CSV with specified dtypes, switching to str', detail=str(e), file=filepath)
      try:
        table = pd.read_csv(filepath, dtype='str')
      except pd.errors.DtypeWarning as e:
        logger.warning(event='Failed to open CSV with str dtype', detail=str(e), file=filepath)
        return
    except pd.errors.EmptyDataError as e:
      logger.warning(event='Empty data or header is encountered', detail=str(e), file=filepath)
      return

    if not CsvImporter.is_header_valid(table.columns):
      logger.warning(event='invalid header', detail=table.columns, file=filepath)
      yield None
      return

    table.rename(columns={"val": "value", "se": "stderr", "missing_val": "missing_value", "missing_se": "missing_stderr"}, inplace=True)

    for row in table.itertuples(index=False):
      csv_row_values, error = CsvImporter.extract_and_check_row(row, details.geo_type, filepath)

      if error:
        logger.warning(event = 'invalid value for row', detail=(str(row), error), file=filepath)
        yield None
        continue

      yield CovidcastRow(
        details.source,
        details.signal,
        details.time_type,
        details.geo_type,
        details.time_value,
        csv_row_values.geo_value,
        csv_row_values.value,
        csv_row_values.stderr,
        csv_row_values.sample_size,
        csv_row_values.missing_value,
        csv_row_values.missing_stderr,
        csv_row_values.missing_sample_size,
        details.issue,
        details.lag,
      )


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
  return parser


def collect_files(data_dir: str, specific_issue_date: bool):
  """Fetch path and data profile details for each file to upload."""
  logger= get_structured_logger('collect_files')
  if specific_issue_date:
    results = list(CsvImporter.find_issue_specific_csv_files(data_dir))
  else:
    results = list(CsvImporter.find_csv_files(os.path.join(data_dir, 'receiving')))
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
  path_details = collect_files(args.data_dir, args.specific_issue_date)
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
