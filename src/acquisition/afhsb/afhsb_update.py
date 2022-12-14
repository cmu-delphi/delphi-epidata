# standard library
import argparse
import tempfile
import os
import stat
import shutil

# first party
from . import afhsb_sql

DEFAULT_DATAPATH = '/home/automation/afhsb_data'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--datapath', action='store', type=str, default=DEFAULT_DATAPATH, help='filepath to directory containing csv files to input into database')
    args = parser.parse_args()
    # MariaDB appears to refuse to LOAD DATA INFILE except on files under
    # /var/lib/mysql (which seems dedicated to its own files) or /tmp; create a
    # temporary directory, make rwx for automation & rx for mysql user, copy in
    # (or alternatively, symlink --- unimplemented) args.datapath to the
    # temporary directory, then run init_all_tables on this temporary datapath.
    #   Set up temporary directory that will hold temporary datapath (initial
    #   permissions are very restrictive):
    tmp_datapath_parent_dir = tempfile.mkdtemp()
    os.chmod(tmp_datapath_parent_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
    shutil.chown(tmp_datapath_parent_dir, group="mysql_automation")
    #     (here, mysql_automation is a group with members {mysql,automation})
    tmp_datapath = os.path.join(tmp_datapath_parent_dir, "afhsb_data")
    #   Copy datapath to temporary datapath (initial permission of copy are
    #   permissive, but require directory access, which was set appropriately
    #   above):
    shutil.copytree(args.datapath, tmp_datapath)
    #   Run init_all_tables on temporary datapath:
    afhsb_sql.init_all_tables(tmp_datapath)
    #   (Temporary parent directory should be deleted automatically.)


if __name__ == '__main__':
    main()
