"""Unit tests for csv_importer.py."""

import argparse
import unittest
from datetime import date
from typing import Iterable
from unittest.mock import MagicMock, patch

import epiweeks as epi
import numpy as np
import pandas as pd
import pytest
from delphi.epidata.acquisition.covidcast.csv_importer import (
    CsvImporter,
    PathDetails,
    collect_files,
    get_argument_parser,
    main,
    make_handlers,
    upload_archive,
    GeoIdSanityCheckException,
    GeoTypeSanityCheckException,
    ValueSanityCheckException
)
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow 
from delphi.utils.epiweek import delta_epiweeks
from delphi_utils import Nans


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  _path_details = [
    # a good file
    ('path/a.csv', PathDetails(20200420, 1, 'src_a', 'sig_a', 'day', 20200419, 'hrr')),
    # a file with a data error
    ('path/b.csv', PathDetails(202017, 1, 'src_b', 'sig_b', 'week', 202016, 'msa')),
    # emulate a file that's named incorrectly
    ('path/c.csv', None)
  ]

  def test_is_sane_day(self):
    """Sanity check some dates."""

    self.assertTrue(CsvImporter.is_sane_day(20200418))

    self.assertFalse(CsvImporter.is_sane_day(22222222))
    self.assertFalse(CsvImporter.is_sane_day(20200001))
    self.assertFalse(CsvImporter.is_sane_day(20200199))
    self.assertFalse(CsvImporter.is_sane_day(202015))


  def test_is_sane_week(self):
    """Sanity check some weeks."""

    self.assertTrue(CsvImporter.is_sane_week(202015))

    self.assertFalse(CsvImporter.is_sane_week(222222))
    self.assertFalse(CsvImporter.is_sane_week(202000))
    self.assertFalse(CsvImporter.is_sane_week(202054))
    self.assertFalse(CsvImporter.is_sane_week(20200418))


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.glob")
  @patch("os.path.isdir")
  def test_find_issue_specific_csv_files(self, mock_os_isdir: MagicMock, mock_glob: MagicMock):
      """Recursively explore and find issue specific CSV files."""
      # check valid path
      path_prefix='prefix/to/the/data/issue_20200408'
      mock_os_isdir.return_value=True
      issue_path=path_prefix+'ght/20200408_state_rawsearch.csv'

      mock_glob.side_effect = ([path_prefix], [issue_path])

      #check if the day is a valid day.
      issuedir_match= CsvImporter.PATTERN_ISSUE_DIR.match(path_prefix.lower())
      issue_date_value = int(issuedir_match.group(2))
      self.assertTrue(CsvImporter.is_sane_day(issue_date_value))

      found = set(CsvImporter.find_issue_specific_csv_files(path_prefix))
      self.assertTrue(len(found) > 0)

      # check unvalid path:
      path_prefix_invalid='invalid/prefix/to/the/data/issue_20200408'
      mock_os_isdir.return_value=False
      issue_path_invalid=path_prefix_invalid+'ght/20200408_state_rawsearch.csv'
      mock_glob.side_effect = ([path_prefix_invalid], [issue_path_invalid])

      found = set(CsvImporter.find_issue_specific_csv_files(path_prefix_invalid))
      self.assertFalse(len(found)>0)


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.glob")
  def test_find_csv_files(self, mock_glob: MagicMock):
    """Recursively explore and find CSV files."""

    path_prefix = 'prefix/to/the/data/'
    glob_paths = [
      # valid weekly
      path_prefix + 'fb_survey/weekly_202015_county_cli.csv',
      # valid daily
      path_prefix + 'ght/20200408_state_rawsearch.csv',
      # valid national
      path_prefix + 'valid/20200408_nation_sig.csv',
      # valid hhs
      path_prefix + 'valid/20200408_hhs_sig.csv',
      # invalid
      path_prefix + 'invalid/hello_world.csv',
      # invalid day
      path_prefix + 'invalid/22222222_b_c.csv',
      # invalid week
      path_prefix + 'invalid/weekly_222222_b_c.csv',
      # invalid geography
      path_prefix + 'invalid/20200418_province_c.csv',
      # ignored
      path_prefix + 'ignored/README.md',
    ]
    mock_glob.return_value = glob_paths

    found = set(CsvImporter.find_csv_files(path_prefix))

    expected_issue_day=int(date.today().strftime("%Y%m%d"))
    expected_issue_week=int(str(epi.Week.fromdate(date.today())))
    time_value_day = 20200408
    expected = set([
      (glob_paths[0], PathDetails(expected_issue_week, delta_epiweeks(202015, expected_issue_week), 'fb_survey', 'cli', 'week', 202015, 'county')),
      (glob_paths[1], PathDetails(expected_issue_day, (date.today() - date(year=time_value_day // 10000, month=(time_value_day // 100) % 100, day=time_value_day % 100)).days, 'ght', 'rawsearch', 'day', time_value_day, 'state')),
      (glob_paths[2], PathDetails(expected_issue_day, (date.today() - date(year=time_value_day // 10000, month=(time_value_day // 100) % 100, day=time_value_day % 100)).days, 'valid', 'sig', 'day', time_value_day, 'nation')),
      (glob_paths[3], PathDetails(expected_issue_day, (date.today() - date(year=time_value_day // 10000, month=(time_value_day // 100) % 100, day=time_value_day % 100)).days, 'valid', 'sig', 'day', time_value_day, 'hhs')),
      (glob_paths[4], None),
      (glob_paths[5], None),
      (glob_paths[6], None),
      (glob_paths[7], None),
    ])
    self.assertEqual(found, expected)


  def test_is_header_valid_allows_extra_columns(self):
    """Allow and ignore extra columns in the header."""

    columns = CsvImporter.REQUIRED_COLUMNS

    self.assertTrue(CsvImporter.is_header_valid(columns))
    self.assertTrue(CsvImporter.is_header_valid(columns | {'foo', 'bar'}))


  def test_is_header_valid_does_not_depend_on_column_order(self):
    """Allow columns to appear in any order."""

    # sorting changes the order of the columns
    columns = sorted(CsvImporter.REQUIRED_COLUMNS)

    self.assertTrue(CsvImporter.is_header_valid(columns))


  def test_extract_and_check_row(self):
    """Apply various sanity checks to a row of data."""

    def make_row(
      geo_id='vi',
      value=1.23,
      stderr=4.56,
      sample_size=100.5,
      missing_value=Nans.NOT_MISSING,
      missing_stderr=Nans.NOT_MISSING,
      missing_sample_size=Nans.NOT_MISSING
    ):
      row = pd.DataFrame({
        "geo_id": [geo_id],
        "value": [value],
        "stderr": [stderr],
        "sample_size": [sample_size],
        "missing_value": [missing_value],
        "missing_stderr": [missing_stderr],
        "missing_sample_size": [missing_sample_size]
      })
      return row
    
    details = PathDetails(20200408, 0, 'src', 'sig', 'day', 20200408, 'state')

    # Failure cases.
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('county', make_row(geo_id='1234'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('county', make_row(geo_id='00000'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('hrr', make_row(geo_id='600'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('msa', make_row(geo_id='1234'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('msa', make_row(geo_id='01234'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('dma', make_row(geo_id='400'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('state', make_row(geo_id='48'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('state', make_row(geo_id='iowa'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('nation', make_row(geo_id='0000'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('hhs', make_row(geo_id='0'), details)
    with pytest.raises(GeoIdSanityCheckException):
      CsvImporter.extract_and_check_row('county', make_row(geo_id=None), details)

    with pytest.raises(Exception):
      CsvImporter.extract_and_check_row('hrr', make_row(geo_id='hrr001'), details)

    with pytest.raises(GeoTypeSanityCheckException):
      CsvImporter.extract_and_check_row('province', make_row(geo_id='ab'), details)
    with pytest.raises(GeoTypeSanityCheckException):
      CsvImporter.extract_and_check_row(None, make_row(), details)

    with pytest.raises(ValueSanityCheckException):
      CsvImporter.extract_and_check_row('state', make_row(stderr=-1), details)
    with pytest.raises(ValueSanityCheckException):
      CsvImporter.extract_and_check_row('state', make_row(value=float('inf')), details)
    with pytest.raises(ValueSanityCheckException):
      CsvImporter.extract_and_check_row('state', make_row(stderr=float('inf')), details)
    with pytest.raises(ValueSanityCheckException):
      CsvImporter.extract_and_check_row('state', make_row(sample_size=float('inf')), details)

    # Success cases with NANs.
    table = CsvImporter.extract_and_check_row('state', make_row(), details)
    assert table.compare(make_row('vi', 1.23, 4.56, 100.5, Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.NOT_MISSING)).empty

    table = CsvImporter.extract_and_check_row('state', make_row(value=None, stderr=np.nan, sample_size=None, missing_value=Nans.DELETED, missing_stderr=Nans.DELETED, missing_sample_size=Nans.DELETED), details)
    assert table.compare(make_row('vi', None, None, None, Nans.DELETED, Nans.DELETED, Nans.DELETED)).empty

    table = CsvImporter.extract_and_check_row('state', make_row(stderr=None, sample_size=np.nan, missing_stderr=Nans.OTHER, missing_sample_size=Nans.OTHER), details)
    assert table.compare(make_row('vi', 1.23, None, None, Nans.NOT_MISSING, Nans.OTHER, Nans.OTHER)).empty

    table = CsvImporter.extract_and_check_row('state', make_row(sample_size=None, missing_value=Nans.NOT_MISSING, missing_stderr=Nans.OTHER, missing_sample_size=Nans.NOT_MISSING), details)
    assert table.compare(make_row('vi', 1.23, 4.56, None, Nans.NOT_MISSING, Nans.NOT_MISSING, Nans.OTHER)).empty


  @patch("pandas.read_csv")
  def test_load_csv_with_invalid_header(self, mock_read_csv):
    """Bail loading a CSV when the header is invalid."""

    data = {'foo': [1, 2, 3]}
    filepath = 'path/name.csv'
    details = PathDetails(20200101, 0, "src", "name", "day", 20200101, "state")

    mock_read_csv.return_value = pd.DataFrame(data)
    rows = CsvImporter.load_csv(filepath, details)

    self.assertTrue(mock_read_csv.called)
    self.assertTrue(mock_read_csv.call_args[0][0], filepath)
    self.assertEqual(rows, None)


  @patch("pandas.read_csv")
  def test_load_csv_with_valid_header(self, mock_read_csv):
    """Yield sanity checked `CsvRowValues` from a valid CSV file."""

    # valid header, but invalid geo_id
    data = {
      'geo_id': ['ca', 'tx', 'fl', '123'],
      'val': ['1.1', '1.2', '1.3', '1.4'],
      'se': ['2.1', '2.2', '2.3', '2.4'],
      'sample_size': ['301', '302', '303', '304'],
    }
    filepath = 'path/name.csv'
    details = PathDetails(20200101, 0, "src", "name", "day", 20200101, "state")

    mock_read_csv.return_value = pd.DataFrame(data=data)
    rows = CsvImporter.load_csv(filepath, details)

    self.assertTrue(mock_read_csv.called)
    self.assertTrue(mock_read_csv.call_args[0][0], filepath)
    self.assertEqual(rows, None)

    # now with missing values!
    def make_covidcast_row(geo_value, value, stderr, sample_size, missing_value, missing_stderr, missing_sample_size):
      return CovidcastRow(
        source=details.source,
        signal=details.signal,
        time_type=details.time_type,
        geo_type=details.geo_type,
        issue=details.issue,
        lag=details.lag,
        time_value=details.time_value,
        geo_value=geo_value,
        value=value,
        stderr=stderr,
        sample_size=sample_size,
        missing_value=missing_value,
        missing_stderr=missing_stderr,
        missing_sample_size=missing_sample_size,
      )
    data = {
      'geo_id': ['ca', 'tx', 'fl', 'ak', 'wa'],
      'val': [np.nan, 1.2, 1.3, 1.4, 1.5],
      'se': [2.1, None, 2.3, 2.4, 2.5],
      'sample_size': [301, 302, None, 304, None],
      'missing_value': [Nans.NOT_APPLICABLE] + [Nans.NOT_MISSING] * 3 + [None],
      'missing_stderr': [Nans.NOT_MISSING, Nans.REGION_EXCEPTION, Nans.NOT_MISSING, Nans.NOT_MISSING] + [None],
      'missing_sample_size': [Nans.NOT_MISSING] * 2 + [Nans.REGION_EXCEPTION] * 2 + [None]
    }
    filepath = 'path/name.csv'
    details = PathDetails(20200101, 0, "src", "name", "day", 20200101, "state")

    mock_read_csv.return_value = pd.DataFrame(data)
    rows = CsvImporter.load_csv(filepath, details)

    self.assertTrue(mock_read_csv.called)
    self.assertTrue(mock_read_csv.call_args[0][0], filepath)
    self.assertEqual(len(rows), 5)

    self.assertEqual(rows[0], make_covidcast_row(
      geo_value='ca',
      value=None,
      stderr=2.1,
      sample_size=301,
      missing_value=Nans.NOT_APPLICABLE,
      missing_stderr=Nans.NOT_MISSING,
      missing_sample_size=Nans.NOT_MISSING
    ))
    
    self.assertEqual(rows[1], make_covidcast_row(
      geo_value='tx',
      value=1.2,
      stderr=None,
      sample_size=302,
      missing_value=Nans.NOT_MISSING,
      missing_stderr=Nans.REGION_EXCEPTION,
      missing_sample_size=Nans.NOT_MISSING,
    ))

    self.assertEqual(rows[2], make_covidcast_row(
      geo_value='fl',
      value=1.3,
      stderr=2.3,
      sample_size=None,
      missing_value=Nans.NOT_MISSING,
      missing_stderr=Nans.NOT_MISSING,
      missing_sample_size=Nans.REGION_EXCEPTION,
    ))

    self.assertEqual(rows[3], make_covidcast_row(
      geo_value='ak',
      value=1.4,
      stderr=2.4,
      sample_size=304,
      missing_value=Nans.NOT_MISSING,
      missing_stderr=Nans.NOT_MISSING,
      missing_sample_size=Nans.NOT_MISSING,
    ))

    self.assertEqual(rows[4], make_covidcast_row(
      geo_value='wa',
      value=1.5,
      stderr=2.5,
      sample_size=None,
      missing_value=Nans.NOT_MISSING,
      missing_stderr=Nans.NOT_MISSING,
      missing_sample_size=Nans.OTHER,
    ))


  def test_get_argument_parser(self):
    """Return a parser for command-line arguments."""

    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.CsvImporter")
  def test_collect_files(self, mock_csv_importer: MagicMock):
    """Scan the data directory."""

    mock_csv_importer.find_csv_files.return_value = self._path_details
    collect_files("fake_data_dir", False) # no specific issue
    self.assertEqual(mock_csv_importer.find_csv_files.call_count, 1)


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.CsvImporter")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.FileArchiver")
  def test_upload_archive(self, mock_file_archiver: MagicMock, mock_csv_importer: MagicMock, mock_database: MagicMock):
    """Upload to the database, and archive."""

    def make_row(value: float, details: PathDetails):
      return MagicMock(
        source=details.source,
        signal=details.signal,
        time_type=details.time_type,
        geo_type=details.geo_type,
        time_value=details.time_value,
        issue=details.issue,
        lag=details.lag,
        geo_value=value,
        value=value,
        stderr=value,
        sample_size=value,
      )

    def load_csv_impl(path, details):
      if path == 'path/a.csv':
        # no validation errors
        return [
          make_row('a1', details),
          make_row('a2', details),
          make_row('a3', details)
        ]
      elif path == 'path/b.csv':
        # one validation error
        return None
      else:
        # fail the test for any other path
        raise Exception('unexpected path')

    def iter_len(l: Iterable) -> int:
      return len(list(l))

    data_dir = 'data_dir'
    mock_database.insert_or_update_bulk = MagicMock(wraps=iter_len)
    mock_csv_importer.load_csv = load_csv_impl
    mock_logger = MagicMock()

    modified_row_count = upload_archive(
      self._path_details,
      mock_database,
      make_handlers(data_dir, False),
      mock_logger
    )

    self.assertEqual(modified_row_count, 3)
    # verify that appropriate rows were added to the database
    self.assertEqual(mock_database.insert_or_update_bulk.call_count, 1)
    call_args_list = mock_database.insert_or_update_bulk.call_args_list
    actual_args = [[(a.source, a.signal, a.time_type, a.geo_type, a.time_value,
                     a.geo_value, a.value, a.stderr, a.sample_size, a.issue, a.lag)
                    for a in call.args[0]] for call in call_args_list]

    expected_args = [
      [('src_a', 'sig_a', 'day', 'hrr', 20200419, 'a1', 'a1', 'a1', 'a1', 20200420, 1),
       ('src_a', 'sig_a', 'day', 'hrr', 20200419, 'a2', 'a2', 'a2', 'a2', 20200420, 1),
       ('src_a', 'sig_a', 'day', 'hrr', 20200419, 'a3', 'a3', 'a3', 'a3', 20200420, 1)]
    ]
    self.assertEqual(actual_args, expected_args)

    # verify that two files were successful (a, d) and two failed (b, c)
    self.assertEqual(mock_file_archiver.archive_file.call_count, 3)
    call_args_list = mock_file_archiver.archive_file.call_args_list
    actual_args = [args for (args, kwargs) in call_args_list]
    expected_args = [
      ('path', 'data_dir/archive/successful/src_a', 'a.csv', True),
      ('path', 'data_dir/archive/failed/src_b', 'b.csv', False),
      ('path', 'data_dir/archive/failed/unknown', 'c.csv', False),
    ]
    self.assertEqual(actual_args, expected_args)


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.upload_archive")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.collect_files")
  def test_main_successful(self, mock_collect_files: MagicMock, mock_upload_archive: MagicMock, mock_database: MagicMock):
    """Run the main program successfully, then commit changes."""

    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(log_file=None, data_dir='data', specific_issue_date=False)
    # `return_value` because we mocked the class constructor
    mock_database.return_value.count_all_rows.return_value = 0
    mock_collect_files.return_value = [("a",False)]

    main(args)
    self.assertTrue(mock_collect_files.called)
    self.assertEqual(mock_collect_files.call_args[0][0], 'data')
    
    self.assertTrue(mock_upload_archive.called)
    self.assertEqual(mock_upload_archive.call_args[0][0], [("a",False)])

    self.assertTrue(mock_database.return_value.connect.called)
    self.assertTrue(mock_database.return_value.disconnect.called)
    self.assertTrue(mock_database.return_value.disconnect.call_args[0][0])


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.upload_archive", side_effect=Exception('testing'))
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.collect_files")
  def test_main_unsuccessful(self, mock_collect_files: MagicMock, mock_upload_archive: MagicMock, mock_database: MagicMock):
    """Run the main program with failure, then commit changes."""

    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(log_file=None, data_dir='data', specific_issue_date=False)
    mock_database.return_value.count_all_rows.return_value = 0
    mock_collect_files.return_value = [("a",False)]

    with self.assertRaises(Exception):
      main(args)

    self.assertTrue(mock_upload_archive.called)
    self.assertEqual(mock_upload_archive.call_args[0][0], [("a",False)])

    self.assertTrue(mock_database.return_value.connect.called)
    self.assertTrue(mock_database.return_value.disconnect.called)
    self.assertTrue(mock_database.return_value.disconnect.call_args[0][0])


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.upload_archive")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.collect_files")
  def test_main_early_exit(self, mock_collect_files: MagicMock, mock_upload_archive: MagicMock, mock_database: MagicMock):
    """Run the main program with an empty receiving directory."""

    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(log_file=None, data_dir='data', specific_issue_date=False)
    mock_database.count_all_rows.return_value = 0
    mock_collect_files.return_value = []

    main(args)

    self.assertTrue(mock_collect_files.called)
    self.assertEqual(mock_collect_files.call_args[0][0], 'data')

    self.assertFalse(mock_upload_archive.called)

    self.assertFalse(mock_database.return_value.connect.called)
    self.assertFalse(mock_database.return_value.disconnect.called)


  @patch("delphi.epidata.acquisition.covidcast.csv_importer.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.CsvImporter")
  @patch("delphi.epidata.acquisition.covidcast.csv_importer.FileArchiver")
  def test_database_exception_is_handled(self, mock_file_archiver: MagicMock, mock_csv_importer: MagicMock, mock_database: MagicMock):
    """Gracefully handle database exceptions."""

    data_dir = 'data_dir'
    mock_database.insert_or_update_bulk.side_effect = Exception('testing')
    mock_csv_importer.find_csv_files.return_value = [
      ('path/file.csv', PathDetails(20200424, 1, 'src', 'sig', 'day', 20200423, 'hrr')),
    ]
    mock_csv_importer.load_csv.return_value = [
      MagicMock(geo_value='geo', value=1, stderr=1, sample_size=1),
    ]
    mock_logger = MagicMock()

    upload_archive(
        collect_files(data_dir, False),
        mock_database,
        make_handlers(data_dir, False),
        mock_logger
    )

    # verify that insertions were attempted
    self.assertTrue(mock_database.insert_or_update_bulk.called)

    # verify that the file was archived as having failed
    self.assertTrue(mock_file_archiver.archive_file.called)
    actual_args = mock_file_archiver.archive_file.call_args[0]
    expected_args = ('path', 'data_dir/archive/failed/src', 'file.csv', False)
    self.assertEqual(actual_args, expected_args)
