"""Collects and reads covidcast data from a set of local CSV files."""

# standard library
from datetime import date
import glob
import math
import os
import re

# third party
import pandas
import epiweeks as epi

# first party
from delphi_utils import Nans
from delphi.utils.epiweek import delta_epiweeks
from delphi.epidata.acquisition.covidcast.logger import get_structured_logger

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

  # NOTE: this should be a Python 3.7+ `dataclass`, but the server is on 3.4
  # See https://docs.python.org/3/library/dataclasses.html
  class RowValues:
    """A container for the values of a single covidcast row."""

    def __init__(self, geo_value, value, stderr, sample_size, missing_value, missing_stderr, missing_sample_size):
      self.geo_value = geo_value
      self.value = value
      self.stderr = stderr
      self.sample_size = sample_size
      self.missing_value = missing_value
      self.missing_stderr = missing_stderr
      self.missing_sample_size = missing_sample_size

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
  def find_issue_specific_csv_files(scan_dir, glob=glob):
    logger = get_structured_logger('find_issue_specific_csv_files')
    for path in sorted(glob.glob(os.path.join(scan_dir, '*'))):
      issuedir_match = CsvImporter.PATTERN_ISSUE_DIR.match(path.lower())
      if issuedir_match and os.path.isdir(path):
        issue_date_value = int(issuedir_match.group(2))
        issue_date = CsvImporter.is_sane_day(issue_date_value)
        if issue_date:
          logger.info(event='processing csv files from issue', detail=issue_date, file=path)
          yield from CsvImporter.find_csv_files(path, issue=(issue_date, epi.Week.fromdate(issue_date)), glob=glob)
        else:
          logger.info(event='invalid issue directory day', detail=issue_date_value, file=path)

  @staticmethod
  def find_csv_files(scan_dir, issue=(date.today(), epi.Week.fromdate(date.today())), glob=glob):
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

    for path in sorted(glob.glob(os.path.join(scan_dir, '*', '*'))):

      if not path.lower().endswith('.csv'):
        # safe to ignore this file
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

      yield (path, (source, signal, time_type, geo_type, time_value, issue_value, lag_value))

  @staticmethod
  def is_header_valid(columns):
    """Return whether the given pandas columns contains the required fields."""

    return set(columns) >= CsvImporter.REQUIRED_COLUMNS

  @staticmethod
  def floaty_int(value):
    """Cast a string to an int, even if it looks like a float.

    For example, "-1" and "-1.0" should both result in -1. Non-integer floats
    will cause `ValueError` to be reaised.
    """

    float_value = float(value)
    int_value = round(float_value)
    if float_value != int_value:
      raise ValueError('not an int: "%s"' % str(value))
    return int_value

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
    except (ValueError, AttributeError) as e:
      # val was a string or another data
      return "Error"

  @staticmethod
  def validate_missing_code(row, attr_quantity, attr_name):
    """Take a row and validate the missing code associated with
    a quantity (e.g., val, se, stderr).

    Returns either a nan code for assignment to the missing quantity
    or a None to signal an error with the missing code. We decline
    to infer missing codes except for a very simple cases; the default
    is to produce an error so that the issue can be fixed in indicators.
    """
    if hasattr(row, "missing_" + attr_name):
      missing_entry = getattr(row, "missing_" + attr_name)
      try:
        missing_entry = int(missing_entry)
      except ValueError:
        return None
      # A missing code should never contradict the quantity being present,
      # since that will be filtered in the export_to_csv util in
      # covidcast-indicators; nonetheless this code is here for safety.
      if attr_quantity is not None and missing_entry != Nans.NOT_MISSING.value:
        return None
      elif attr_quantity is None and missing_entry == Nans.NOT_MISSING.value:
        return None
      return missing_entry
    else:
      if attr_quantity is None:
        return Nans.OTHER.value
      return Nans.NOT_MISSING.value

  @staticmethod
  def extract_and_check_row(row, geo_type):
    """Extract and return `RowValues` from a CSV row, with sanity checks.

    Also returns the name of the field which failed sanity check, or None.

    row: the pandas table row to extract
    geo_type: the geographic resolution of the file
    """

    # use consistent capitalization (e.g. for states)
    try:
      geo_id = row.geo_id.lower()
    except AttributeError as e:
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
    value = CsvImporter.validate_quantity(row, "val")
    # val was a string or another dtype
    if value == "Error":
      return (None, 'val')
    stderr = CsvImporter.validate_quantity(row, "se")
    # Case 1: stderr was a string or another dtype
    # Case 2: stderr is negative
    if stderr == "Error" or (stderr is not None and stderr < 0):
      return (None, 'se')
    sample_size = CsvImporter.validate_quantity(row, "sample_size")
    # Case 1: sample_size was a string or another dtype
    # Case 2: sample_size was negative
    if sample_size == "Error" or (sample_size is not None and sample_size < 0):
      return (None, 'sample_size')

    # Validate and write missingness codes
    missing_value = CsvImporter.validate_missing_code(row, value, "val")
    if missing_value is None:
      return (None, 'missing_val')
    missing_stderr = CsvImporter.validate_missing_code(row, stderr, "se")
    if missing_stderr is None:
      return (None, 'missing_se')
    missing_sample_size = CsvImporter.validate_missing_code(row, sample_size, "sample_size")
    if missing_sample_size is None:
      return (None, 'missing_sample_size')

    # return extracted and validated row values
    row_values = CsvImporter.RowValues(
      geo_id, value, stderr, sample_size,
      missing_value, missing_stderr, missing_sample_size
    )
    return (row_values, None)

  @staticmethod
  def load_csv(filepath, geo_type, pandas=pandas):
    """Load, validate, and yield data as `RowValues` from a CSV file.

    filepath: the CSV file to be loaded
    geo_type: the geographic resolution (e.g. county)

    In case of a validation error, `None` is yielded for the offending row,
    including the header.
    """
    logger = get_structured_logger('load_csv')
    # don't use type inference, just get strings
    table = pandas.read_csv(filepath, dtype='str')

    if not CsvImporter.is_header_valid(table.columns):
      logger.warning(event='invalid header', detail=table.columns, file=filepath)
      yield None
      return

    for row in table.itertuples(index=False):
      row_values, error = CsvImporter.extract_and_check_row(row, geo_type)
      if error:
        logger.warning(event = 'invalid value for row', detail=(str(row), error), file=filepath)
        yield None
        continue
      yield row_values
