"""Unit tests for csv_to_database.py."""

# standard library
import argparse
from typing import Iterable
import unittest
from unittest.mock import MagicMock, patch

from delphi.epidata.acquisition.covidcast.csv_importer import PathDetails
from delphi.epidata.acquisition.covidcast.csv_to_database import get_argument_parser, main, collect_files, upload_archive, make_handlers

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.csv_to_database'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""
  _path_details = [
    # a good file
    ('path/a.csv', PathDetails('src_a', 'sig_a', 'day', 'hrr', 20200419, 20200420, 1)),
    # a file with a data error
    ('path/b.csv', PathDetails('src_b', 'sig_b', 'week', 'msa', 202016, 202017, 1)),
    # emulate a file that's named incorrectly
    ('path/c.csv', None)
  ]

  def test_get_argument_parser(self):
    """Return a parser for command-line arguments."""

    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)


  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.CsvImporter")
  def test_collect_files(self, mock_csv_importer: MagicMock):
    """Scan the data directory."""

    mock_csv_importer.find_csv_files.return_value = self._path_details
    collect_files("fake_data_dir", False) # no specific issue
    self.assertEqual(mock_csv_importer.find_csv_files.call_count, 1)


  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.CsvImporter")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.FileArchiver")
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
        yield make_row('a1', details)
        yield make_row('a2', details)
        yield make_row('a3', details)
      elif path == 'path/b.csv':
        # one validation error
        yield make_row('b1', details)
        yield None
        yield make_row('b3', details)
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


  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.upload_archive")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.collect_files")
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


  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.upload_archive", side_effect=Exception('testing'))
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.collect_files")
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


  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.upload_archive")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.collect_files")
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


  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.Database")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.CsvImporter")
  @patch("delphi.epidata.acquisition.covidcast.csv_to_database.FileArchiver")
  def test_database_exception_is_handled(self, mock_file_archiver: MagicMock, mock_csv_importer: MagicMock, mock_database: MagicMock):
    """Gracefully handle database exceptions."""

    data_dir = 'data_dir'
    mock_database.insert_or_update_bulk.side_effect = Exception('testing')
    mock_csv_importer.find_csv_files.return_value = [
      ('path/file.csv', PathDetails('src', 'sig', 'day', 'hrr', 20200423, 20200424, 1)),
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
