"""Unit tests for file_archiver.py."""

# standard library
import os
import unittest
from unittest.mock import MagicMock

from delphi.epidata.acquisition.covidcast.file_archiver import FileArchiver

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.file_archiver'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_archive_file_without_compression(self):
    """Archive a file without compression."""

    path_src = 'some/src/path'
    path_dst = 'some/dst/path'
    filename = 'data.csv'
    compress = False

    mock_os = MagicMock()
    # use the real `os.path.join`
    mock_os.path.join = os.path.join
    mock_os.path.exists.return_value = False
    mock_shutil = MagicMock()

    result = FileArchiver.archive_file(
        path_src, path_dst, filename, compress, os=mock_os, shutil=mock_shutil)

    self.assertTrue(mock_os.makedirs.called)
    self.assertEqual(mock_os.makedirs.call_args[0][0], 'some/dst/path')
    self.assertTrue(mock_os.makedirs.call_args[1]['exist_ok'])

    self.assertTrue(mock_shutil.move.called)
    move_src, move_dst = mock_shutil.move.call_args[0]
    self.assertEqual(move_src, 'some/src/path/data.csv')
    self.assertEqual(move_dst, 'some/dst/path/data.csv')

    self.assertTrue(mock_os.stat.called)
    self.assertEqual(mock_os.stat.call_args[0][0], 'some/dst/path/data.csv')

    self.assertEqual(result[0], 'some/dst/path/data.csv')

  def test_archive_file_with_compression(self):
    """Archive a file with compression."""

    path_src = 'some/src/path'
    path_dst = 'some/dst/path'
    filename = 'data.csv'
    compress = True

    mock_os = MagicMock()
    # use the real `os.path.join`
    mock_os.path.join = os.path.join
    mock_os.path.exists.return_value = False
    mock_gzip = MagicMock()
    mock_shutil = MagicMock()
    mock_open_impl = MagicMock()

    result = FileArchiver.archive_file(
        path_src,
        path_dst,
        filename,
        compress,
        gzip=mock_gzip,
        os=mock_os,
        shutil=mock_shutil,
        open_impl=mock_open_impl)

    self.assertTrue(mock_os.makedirs.called)
    self.assertEqual(mock_os.makedirs.call_args[0][0], 'some/dst/path')
    self.assertTrue(mock_os.makedirs.call_args[1]['exist_ok'])

    self.assertTrue(mock_open_impl.called)
    path, mode = mock_open_impl.call_args[0]
    self.assertEqual(path, 'some/src/path/data.csv')
    self.assertEqual(mode, 'rb')

    self.assertTrue(mock_gzip.open.called)
    path, mode = mock_gzip.open.call_args[0]
    self.assertEqual(path, 'some/dst/path/data.csv.gz')
    self.assertEqual(mode, 'wb')

    self.assertTrue(mock_shutil.copyfileobj.called)

    self.assertTrue(mock_os.remove.called)
    self.assertEqual(mock_os.remove.call_args[0][0], 'some/src/path/data.csv')

    self.assertTrue(mock_os.stat.called)
    self.assertEqual(mock_os.stat.call_args[0][0], 'some/dst/path/data.csv.gz')

    self.assertEqual(result[0], 'some/dst/path/data.csv.gz')

  def test_archive_overwrites_destination(self):
    """Overwrite an existing file when archiving."""

    path_src = 'some/src/path'
    path_dst = 'some/dst/path'
    filename = 'data.csv'
    compress = False

    mock_os = MagicMock()
    # use the real `os.path.join`
    mock_os.path.join = os.path.join
    mock_os.path.exists.return_value = True
    mock_gzip = MagicMock()
    mock_shutil = MagicMock()

    result = FileArchiver.archive_file(
        path_src, path_dst, filename, compress, os=mock_os, shutil=mock_shutil)

    self.assertTrue(mock_os.path.exists.called)
    path = 'some/dst/path/data.csv'
    self.assertEqual(mock_os.path.exists.call_args[0][0], path)
    self.assertEqual(result[0], path)
