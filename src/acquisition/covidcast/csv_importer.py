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
from typing import Callable, Iterable, List, NamedTuple, Optional, Tuple

import epiweeks as epi
import numpy as np
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

class GeoIdSanityCheckException(ValueError):

  def __init__(self, message, geo_id=None):
      self.message = message
      self.geo_id = geo_id

class GeoTypeSanityCheckException(ValueError):

  def __init__(self, message, geo_type=None):
      self.message = message
      self.geo_type = geo_type

class ValueSanityCheckException(ValueError):

  def __init__(self, message, value=None):
      self.message = message
      self.value = value


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
  def extract_and_check_row(geo_type: str, table: pd.DataFrame) -> pd.DataFrame:
    """Extract and return `CsvRowValue` from a CSV row, with sanity checks.

    Also returns the name of the field which failed sanity check, or None.

    row: the pandas table row to extract
    geo_type: the geographic resolution of the file
    """

    def validate_geo_code(fail_mask: pd.Series, geo_type: str):
      validation_fails = table[fail_mask]
      if not validation_fails.empty:
        first_fail = validation_fails.iloc[0]
        raise GeoIdSanityCheckException(f'{geo_type} does not satisfy validation check', geo_id=first_fail["geo_id"])

    def validate_quantity(column: pd.Series):
      """Validate a column of a table using a validation function."""
      infinities = column[column.isin([float('inf'), float('-inf')])]
      if not infinities.empty:
        first_fail = infinities.iloc[0]
        raise ValueSanityCheckException(f'Found infinity in {column.name}: {first_fail}')

      negative_values = column[column.lt(0)]
      if not negative_values.empty:
        first_fail = negative_values.iloc[0]
        raise ValueSanityCheckException(f'Found negative value in {column.name}: {first_fail}')

      return column

    def validate_missing_code(missing_code: pd.Series, column: pd.Series):
      """Take a row and validate the missing code associated with
      a quantity (e.g., val, se, stderr).

      Returns either a nan code for assignment to the missing quantity
      or a None to signal an error with the missing code. We decline
      to infer missing codes except for a very simple cases; the default
      is to produce an error so that the issue can be fixed in indicators.
      """
      logger = get_structured_logger('validate_missing_code') 

      missing_code[missing_code.isna() & column.notna()] = Nans.NOT_MISSING.value
      missing_code[missing_code.isna() & column.isna()] = Nans.OTHER.value

      contradict_mask = missing_code.ne(Nans.NOT_MISSING.value) & column.notna()
      if contradict_mask.any():
        first_fail = missing_code[contradict_mask].iloc[0]
        logger.warning(f'Correcting contradicting missing code: {first_fail}')
      missing_code[contradict_mask] = Nans.NOT_MISSING.value

      contradict_mask = missing_code.eq(Nans.NOT_MISSING.value) & column.isna()
      if contradict_mask.any():
        first_fail = missing_code[contradict_mask].iloc[0]
        logger.warning(f'Correcting contradicting missing code: {first_fail}')
      missing_code[contradict_mask] = Nans.OTHER.value

      return missing_code

    # use consistent capitalization (e.g. for states)
    table['geo_id'] = table['geo_id'].str.lower()

    # sanity check geo_id with respect to geo_type
    if geo_type == 'county':
      fail_mask = (table['geo_id'].str.len() != 5) | ~table['geo_id'].between('01000', '80000')
    elif geo_type == 'hrr':
      fail_mask = ~table['geo_id'].astype(int).between(1, 500)
    elif geo_type == 'msa':
      fail_mask = (table['geo_id'].str.len() != 5) | ~table['geo_id'].between('10000', '99999')
    elif geo_type == 'dma':
      fail_mask = ~table['geo_id'].astype(int).between(450, 950)
    elif geo_type == 'state':
      fail_mask = (table['geo_id'].str.len() != 2) | ~table['geo_id'].between('aa', 'zz')
    elif geo_type == 'hhs':
      fail_mask = ~table['geo_id'].astype(int).between(1, 10)
    elif geo_type == 'nation':
      fail_mask = table['geo_id'] != 'us'
    else:
      raise GeoTypeSanityCheckException(f'Unknown geo_type: {geo_type}')

    validate_geo_code(fail_mask, geo_type)

    # Validate row values
    table['value'] = validate_quantity(table['value'])
    table['stderr'] = validate_quantity(table['stderr'])
    table['sample_size'] = validate_quantity(table['sample_size'])

    # Validate and fix missingness codes
    table['missing_value'] = validate_missing_code(table['missing_value'], table['value'])
    table['missing_stderr'] = validate_missing_code(table['missing_stderr'], table['stderr'])
    table['missing_sample_size'] = validate_missing_code(table['missing_sample_size'], table['sample_size'])

    return table


  @staticmethod
  def load_csv(filepath: str, details: PathDetails) -> Optional[List[CovidcastRow]]:
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
      logger.warning(event='Failed to open CSV with specified dtypes', detail=str(e), file=filepath)
      return None
    except pd.errors.EmptyDataError as e:
      logger.warning(event='Empty data or header is encountered', detail=str(e), file=filepath)
      return None

    if not CsvImporter.is_header_valid(table.columns):
      logger.warning(event='invalid header', detail=table.columns, file=filepath)
      return None

    table.rename(columns={"val": "value", "se": "stderr", "missing_val": "missing_value", "missing_se": "missing_stderr"}, inplace=True)
    
    for key in ["missing_value", "missing_stderr", "missing_sample_size"]:
      if key not in table.columns:
        table[key] = np.nan

    try:
      table = CsvImporter.extract_and_check_row(details.geo_type, table)
    except GeoIdSanityCheckException as err:
      row = table.loc[table['geo_id'] == err.geo_id]
      logger.warning(event='invalid value for row', detail=(row.to_csv(header=False, index=False, na_rep='NA')), file=filepath)
      return None
    except GeoTypeSanityCheckException as err:
      logger.warning(event='invalid value for row', detail=err, file=filepath)
      return None
    except ValueSanityCheckException as err:
      logger.warning(event='invalid value for row', file=filepath)
      return None
    except Exception as err:
      logger.warning(event='unknown error occured in extract_and_check_row', detail=err, file=filepath)
      return None
    return [
        CovidcastRow(
            source=details.source,
            signal=details.signal,
            time_type=details.time_type,
            geo_type=details.geo_type,
            time_value=details.time_value,
            geo_value=row.geo_id,
            value=row.value if pd.notna(row.value) else None,
            stderr=row.stderr if pd.notna(row.stderr) else None,
            sample_size=row.sample_size if pd.notna(row.sample_size) else None,
            missing_value=int(row.missing_value),
            missing_stderr=int(row.missing_stderr),
            missing_sample_size=int(row.missing_sample_size),
            issue=details.issue,
            lag=details.lag
        ) for row in table.itertuples(index=False)
    ]


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

    all_rows_valid = True
    csv_rows = CsvImporter.load_csv(path, details)
    if csv_rows:
      try:
        modified_row_count = database.insert_or_update_bulk(csv_rows)
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
    if csv_rows and all_rows_valid:
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

if __name__ == '__main__':
  main(get_argument_parser().parse_args())
