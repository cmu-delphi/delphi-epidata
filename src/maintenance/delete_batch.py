"""Deletes large numbers of rows from covidcast based on a CSV"""

# standard library
import argparse
import glob
import os
import time

# first party
from delphi.epidata.acquisition.covidcast.database import Database
from delphi_utils import get_structured_logger


def get_argument_parser():
    """Define command line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--deletion_dir',
      help='directory where deletion CSVs are stored')
    parser.add_argument(
      '--log_file',
      help="filename for log output (defaults to stdout)")
    return parser

def handle_file(deletion_file, database, logger):
    logger.info("Deleting from csv file", filename=deletion_file)
    rows = []
    with open(deletion_file) as f:
        for line in f:
            fields = line.strip().split(",")
            if len(fields) < 9: continue
            rows.append(fields + ["day"])
    rows = rows[1:]
    try:
        n = database.delete_batch(rows)
        logger.info("Deleted database rows", row_count=n)
        return n
    except Exception as e:
        logger.exception('Exception while deleting rows', exception=e)
        database.rollback()
    return 0

def main(args):
    """Delete rows from covidcast."""

    logger = get_structured_logger("csv_deletion", filename=args.log_file)
    start_time = time.time()
    database = Database()
    database.connect()
    all_n = 0

    try:
        for deletion_file in sorted(glob.glob(os.path.join(args.deletion_dir, '*.csv'))):
            n = handle_file(deletion_file, database, logger)
            if n is not None:
                all_n += n
            else:
                all_n = "rowcount unsupported"
    finally:
        database.disconnect(True)

    logger.info(
        "Deleted CSVs from database",
        total_runtime_in_seconds=round(time.time() - start_time, 2), row_count=all_n)

if __name__ == '__main__':
    main(get_argument_parser().parse_args())
