"""Unit tests for csv_to_database.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock

from delphi.epidata.acquisition.covidcast.csv_to_database import get_argument_parser, main, \
  collect_files, upload_archive, make_handlers

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.csv_to_database'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_get_argument_parser(self):
    """Return a parser for command-line arguments."""

    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

  def _path_details(self):
    return [
      # a good file
      ('path/a.csv', ('src_a', 'sig_a', 'day', 'hrr', 20200419, 20200420, 1)),
      # a file with a data error
      ('path/b.csv', ('src_b', 'sig_b', 'week', 'msa', 202016, 202017, 1)),
      # emulate a file that's named incorrectly
      ('path/c.csv', None),
      # another good file w/ wip
      ('path/d.csv', ('src_d', 'wip_sig_d', 'week', 'msa', 202016, 202017, 1)),
    ]

  def test_collect_files(self):
    """Scan the data directory."""

    mock_csv_importer = MagicMock()
    mock_csv_importer.find_csv_files.return_value = self._path_details()
    collect_files(
      "fake_data_dir",
      False, # no specific issue
      csv_importer_impl=mock_csv_importer)
    self.assertEqual(mock_csv_importer.find_csv_files.call_count, 1)
    
  def test_upload_archive(self):
    """Upload to the database, and archive."""

    def make_row(value):
      return MagicMock(
        geo_value=value,
        value=value,
        stderr=value,
        sample_size=value,
      )

    def load_csv_impl(path, *args):
      if path == 'path/a.csv':
        # no validation errors
        yield make_row('a1')
        yield make_row('a2')
        yield make_row('a3')
      elif path == 'path/b.csv':
        # one validation error
        yield make_row('b1')
        yield None
        yield make_row('b3')
      elif path == 'path/d.csv':
        yield make_row('d1')
      else:
        # fail the test for any other path
        raise Exception('unexpected path')

    data_dir = 'data_dir'
    mock_database = MagicMock()
    mock_database.insert_datapoints_bulk.return_value = 2
    mock_csv_importer = MagicMock()
    mock_csv_importer.load_csv = load_csv_impl
    mock_file_archiver = MagicMock()
    mock_logger = MagicMock()

    modified_row_count = upload_archive(
      self._path_details(),
      mock_database,
      make_handlers(data_dir, False,
                    file_archiver_impl=mock_file_archiver),
      mock_logger,
      csv_importer_impl=mock_csv_importer)

    self.assertEqual(modified_row_count, 4)
    # verify that appropriate rows were added to the database
    self.assertEqual(mock_database.insert_datapoints_bulk.call_count, 2)
    call_args_list = mock_database.insert_datapoints_bulk.call_args_list
    actual_args = [[(a.source, a.signal, a.time_type, a.geo_type, a.time_value,
                     a.geo_value, a.value, a.stderr, a.sample_size, a.issue, a.lag, a.is_wip)
                    for a in call.args[0]] for call in call_args_list]
    expected_args = [
      [('src_a', 'sig_a', 'day', 'hrr', 20200419, 'a1', 'a1', 'a1', 'a1', 20200420, 1, False),
       ('src_a', 'sig_a', 'day', 'hrr', 20200419, 'a2', 'a2', 'a2', 'a2', 20200420, 1, False),
       ('src_a', 'sig_a', 'day', 'hrr', 20200419, 'a3', 'a3', 'a3', 'a3', 20200420, 1, False)],
      [('src_d', 'wip_sig_d', 'week', 'msa', 202016, 'd1', 'd1', 'd1', 'd1', 202017, 1, True)]
    ]
    self.assertEqual(actual_args, expected_args)

    # verify that two files were successful (a, d) and two failed (b, c)
    self.assertEqual(mock_file_archiver.archive_file.call_count, 4)
    call_args_list = mock_file_archiver.archive_file.call_args_list
    actual_args = [args for (args, kwargs) in call_args_list]
    expected_args = [
      ('path', 'data_dir/archive/successful/src_a', 'a.csv', True),
      ('path', 'data_dir/archive/failed/src_b', 'b.csv', False),
      ('path', 'data_dir/archive/failed/unknown', 'c.csv', False),
      ('path', 'data_dir/archive/successful/src_d', 'd.csv', True),
    ]
    self.assertEqual(actual_args, expected_args)

  def test_main_successful(self):
    """Run the main program successfully, then commit changes."""

    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(log_file=None, data_dir='data', is_wip_override=False, not_wip_override=False, specific_issue_date=False)
    mock_database = MagicMock()
    mock_database.count_all_rows.return_value = 0
    fake_database_impl = lambda: mock_database
    mock_collect_files = MagicMock()
    mock_collect_files.return_value = [("a",False)]
    mock_upload_archive = MagicMock()

    main(
        args,
        database_impl=fake_database_impl,
        collect_files_impl=mock_collect_files,
        upload_archive_impl=mock_upload_archive)

    self.assertTrue(mock_collect_files.called)
    self.assertEqual(mock_collect_files.call_args[0][0], 'data')
    
    self.assertTrue(mock_upload_archive.called)
    self.assertEqual(mock_upload_archive.call_args[0][0], [("a",False)])

    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    self.assertTrue(mock_database.disconnect.call_args[0][0])

  def test_main_unsuccessful(self):
    """Run the main program with failure, then commit changes."""

    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(log_file=None, data_dir='data', is_wip_override=False, not_wip_override=False, specific_issue_date=False)
    mock_database = MagicMock()
    mock_database.count_all_rows.return_value = 0
    fake_database_impl = lambda: mock_database
    mock_upload_archive = MagicMock(side_effect=Exception('testing'))
    mock_collect_files = MagicMock()
    mock_collect_files.return_value=[("a",False)]

    with self.assertRaises(Exception):
      main(
          args,
          database_impl=fake_database_impl,
          collect_files_impl=mock_collect_files,
          upload_archive_impl=mock_upload_archive)

    self.assertTrue(mock_upload_archive.called)
    self.assertEqual(mock_upload_archive.call_args[0][0], [("a",False)])

    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    self.assertTrue(mock_database.disconnect.call_args[0][0])

  def test_main_early_exit(self):
    """Run the main program with an empty receiving directory."""

    # TODO: use an actual argparse object for the args instead of a MagicMock
    args = MagicMock(log_file=None, data_dir='data', is_wip_override=False, not_wip_override=False, specific_issue_date=False)
    mock_database = MagicMock()
    mock_database.count_all_rows.return_value = 0
    fake_database_impl = lambda: mock_database
    mock_collect_files = MagicMock()
    mock_collect_files.return_value = []
    mock_upload_archive = MagicMock()

    main(
        args,
        database_impl=fake_database_impl,
        collect_files_impl=mock_collect_files,
        upload_archive_impl=mock_upload_archive)

    self.assertTrue(mock_collect_files.called)
    self.assertEqual(mock_collect_files.call_args[0][0], 'data')

    self.assertFalse(mock_upload_archive.called)

    self.assertFalse(mock_database.connect.called)
    self.assertFalse(mock_database.disconnect.called)

  def test_database_exception_is_handled(self):
    """Gracefully handle database exceptions."""

    data_dir = 'data_dir'
    mock_database = MagicMock()
    mock_database.insert_datapoints_bulk.side_effect = Exception('testing')
    mock_csv_importer = MagicMock()
    mock_csv_importer.find_csv_files.return_value = [
      ('path/file.csv', ('src', 'sig', 'day', 'hrr', 20200423, 20200424, 1)),
    ]
    mock_csv_importer.load_csv.return_value = [
      MagicMock(geo_value='geo', value=1, stderr=1, sample_size=1),
    ]
    mock_file_archiver = MagicMock()
    mock_logger = MagicMock()

    upload_archive(
        collect_files(data_dir, False, csv_importer_impl=mock_csv_importer),
        mock_database,
        make_handlers(data_dir, False, file_archiver_impl=mock_file_archiver),
        mock_logger,
        csv_importer_impl=mock_csv_importer,
        )

    # verify that insertions were attempted
    # TODO: should probbly check that a different method is called...
    self.assertTrue(mock_database.get_dataref_id_map.called)

    # verify that the file was archived as having failed
    self.assertTrue(mock_file_archiver.archive_file.called)
    actual_args = mock_file_archiver.archive_file.call_args[0]
    expected_args = ('path', 'data_dir/archive/failed/src', 'file.csv', False)
    self.assertEqual(actual_args, expected_args)
