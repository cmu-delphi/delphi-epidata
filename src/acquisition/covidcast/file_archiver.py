"""Moves files into various archival directories."""

# standard library
import gzip
import os
import shutil

# first party
from delphi_utils import get_structured_logger

class FileArchiver:
  """Archives files by moving and compressing."""

  @staticmethod
  def archive_inplace(path, filename,
                      gzip=gzip,
                      os=os,
                      shutil=shutil,
                      open_impl=open):
    return FileArchiver.archive_file(path, path, filename, True, gzip, os, shutil, open_impl)

  @staticmethod
  def archive_file(
      path_src,
      path_dst,
      filename,
      compress,
      gzip=gzip,
      os=os,
      shutil=shutil,
      open_impl=open):
    """Archive a file and return the path and `stat` of the destination file.

    WARNING: This is a potentially destructive operation. See details below.

    path_src: the directory which contains the file to be archived
    path_dst: the directory into which the file should be moved
    filename: the name of the file within `path_src`
    compress: gzips the file if true, otherise moves the file unmodified

    The destination directory will be created if necessary. If the destination
    file already exists, it will be overwritten.
    """

    logger = get_structured_logger("file_archiver")
    src = os.path.join(path_src, filename)
    dst = os.path.join(path_dst, filename)

    if compress:
      dst += '.gz'

    # make sure the destination directory exists
    os.makedirs(path_dst, exist_ok=True)

    if os.path.exists(dst):
      # warn that destination is about to be overwritten
      logger.warning(event='destination exists, will overwrite', file=dst)

    if compress:
      # make a compressed copy
      with open_impl(src, 'rb') as f_in:
        with gzip.open(dst, 'wb') as f_out:
          shutil.copyfileobj(f_in, f_out)

      # delete the original
      os.remove(src)
    else:
      # just move (i.e. rename) the original
      shutil.move(src, dst)

    # return filesystem information about the destination file
    return (dst, os.stat(dst))
