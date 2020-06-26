"""
Script to use DB backups to migrate data for covidcast issues and lag addition

Author: Eu Jing Chua
Created: 2020-06-26
"""

# Standard library
import argparse
import csv
from copy import deepcopy
from collections import defaultdict
import datetime
import glob
import gzip
from itertools import islice, chain
import logging
import os
from typing import Optional, List, Iterable, Iterator, Dict

# Third party
import csvdiff

COVIDCAST_INSERT_START = "INSERT INTO `covidcast` VALUES "

# Column names
INDEX_COLS = ["source", "signal", "time_type", "geo_type", "time_value", "geo_value"]
VALUE_COLS = ["timestamp1", "value", "stderr", "sample_size", "timestamp2", "direction"]
ALL_COLS = INDEX_COLS + VALUE_COLS
ALL_COLS_WITH_PK = ["id"] + ALL_COLS

def parse_args():
    '''
    Commandline arguments
    '''
    parser = argparse.ArgumentParser(
        description="Process DB backups to migrate data for covidcast issues and lag addition")
    parser.add_argument(
        "--input-files", nargs="+", dest="sql_files",
        default=glob.glob("./just_covidcast_*_database.sql.gz"),
        help="Input backup .sql files to process. May be compressed (.gz)")
    parser.add_argument(
        "--skip", nargs="+", dest="skip_sources", default=[],
        help="List of sources to skip")
    parser.add_argument(
        "--tmp-dir", dest="tmp_dir", default="./tmp", type=str,
        help="Temporary directory to use for intermediate files")
    parser.add_argument(
        "--out-dir", dest="out_dir", default="./out", type=str,
        help="Output directory to use for resulting .sql files")
    parser.add_argument(
        "--max-insert-chunk", dest="chunk_size", default=1000, type=int,
        help="Maximum number of rows to have per SQL INSERT statement")
    parser.add_argument(
        "--debug", dest="debug", action="store_true",
        help="More verbose debug output")

    args = parser.parse_args()
    return args

def show_args(args):
    '''
    Display arguments being used
    '''
    logging.info("Input files (in order):\n\t%s", "\n\t".join(sorted(args.sql_files)))
    logging.info("Skipping sources: [%s]", ", ".join(args.skip_sources))
    logging.info("Temporary dir: %s", args.tmp_dir)
    logging.info("Output dir: %s", args.out_dir)
    logging.info("Max insert chunk: %d", args.chunk_size)
    logging.info("Debug output: %s", args.debug)

def main(args):
    '''
    Overall flow:
        1) Extract relevant tuples from .sql into CSVs so we can use CSV diffing tools
        2) Split each CSV by 'source'
        3) For each source, accumulate CSV diffs for each CSVs across the dates
        4) For each source, write out the accumulated CSV diff as a .sql file
    '''

    # 0) Configuration stuff
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s:\t%(message)s")

    show_args(args)

    os.makedirs(args.tmp_dir, exist_ok=True)
    os.makedirs(args.out_dir, exist_ok=True)

    # 1) Extract relevant tuples from .sql into CSVs so we can use CSV diffing tools
    logging.info("Extracting to csvs...")
    csv_files = []

    # Ensure files are in sorted order of date in filename
    for sql_file in sorted(args.sql_files):
        csv_file = os.path.join(
            args.tmp_dir,
            f"just_covidcast_{date_int_from_filename(sql_file)}.csv")

        logging.debug("Processing %s into %s", sql_file, csv_file)
        extract_to_csv(sql_file, csv_file)
        csv_files.append(csv_file)

    # 2) Split each backup's csv by source
    logging.info("Splitting csvs...")
    files_by_src = defaultdict(list)

    split_col = 1
    for csv_file in csv_files:
        logging.debug("Splitting %s by %s", csv_file, ALL_COLS_WITH_PK[split_col])
        by_src = split_csv_by_col(csv_file, split_col, add_header=True)

        for src, sub_csv_file in by_src.items():
            files_by_src[src].append(sub_csv_file)

    # 3) Accumulate issues over sliding pairs of [None, csv_1, csv_2, ... csv_N] for each group
    for source, src_files in files_by_src.items():

        if source in args.skip_sources:
            logging.info("Skipping group: %s", source)
            continue

        logging.info("Processing group: %s", source)
        logging.info("Accumulating issues...")
        files = [None] + src_files
        accum = {}

        for before_file, after_file in zip(files, files[1:]):
            if before_file is None:
                logging.debug("First: %s", date_int_from_filename(after_file))
            else:
                logging.debug(
                    "Diffing: from %s to %s",
                    date_int_from_filename(before_file),
                    date_int_from_filename(after_file))
            update_issues(before_file, after_file, accum)

        # 4) Write out accumulated issues into one or several SQL files
        # TODO: Decide how to generate the SQL files, all-in-one or separately by source?
        logging.info("Generating SQL file...")
        outfile = os.path.join(args.out_dir, f"{source}.sql")

        logging.debug("Writing to %s", outfile)
        write_sql_insert(accum, outfile, chunked_size=args.chunk_size)

def extract_to_csv(filename: str, output: str):
    '''
    Takes a backup .sql file and produces a CSV representing just the covidcast rows
    Also accepts gzipped .sql.gz files as input

    Args:
        filename: Input .sql file
        output: Output .csv file
    '''

    is_covidcast = lambda line: line.startswith(COVIDCAST_INSERT_START)

    # Open gzipped .sql file or regular .sql file
    if filename.endswith(".gz"):
        open_file = lambda fname: gzip.open(fname, "rt")
    else:
        open_file = lambda fname: open(fname, "r")

    # Load bulk insert lines
    with open_file(filename) as f_in:

        # Try to keep everything as iterators to reduce memory usage
        inserts = filter(is_covidcast, f_in)

        # Extract just tuples as individual lines
        old_sep, new_sep = "),(", "\n"

        # Skip the initial insert statement and (, and trailing ');\n'
        start, end = len(COVIDCAST_INSERT_START) + 1, -3

        with open(output, "w") as f_out:
            for insert_cmd in inserts:
                split_up_insert = insert_cmd[start:end].replace(old_sep, new_sep)
                f_out.write(split_up_insert + "\n")

def split_csv_by_col(
        filename: str, col_idx: int, add_header: bool = False) -> Dict[str, str]:
    '''
    Splits up a CSV file by unique values of a specified column into subset CSVs.
    Produces subset CSVs in same directory as input, with '_{value}' appended to filename.
    Assumes the input CSV has no header row, as produced by extract_to_csv.

    Args:
        filename: Input CSV file
        col_idx: Column index to split-by-values on
        add_header: Add column header row to output CSVs

    Returns:
        Mapping from column value -> subset CSV filename
    '''

    open_file_writers = {}
    created_files = {}
    base_name, f_ext = os.path.splitext(filename)

    with open(filename, "r") as f_csv:
        # Assume no header
        prev_value = None
        for line in f_csv:
            # Not using in-built csv module as it was alot slower

            # Dont need the rest of the split beyond the column we are interested in
            value = line.split(",", col_idx + 1)[col_idx]

            # Get appropriate file to write to, and create it if it does not exist yet
            # Since most sources are in continuous rows, try do less dict lookups
            # Only change file handle when we see a different value
            if value != prev_value:
                if value not in open_file_writers:

                    # Strip value of surrounding quotes for nicer filenames
                    clean_value = value.strip("'")
                    created_file = f"{base_name}_{clean_value}{f_ext}"
                    created_files[clean_value] = created_file

                    # Create and store file handle
                    sub_f = open(created_file, "w")
                    open_file_writers[value] = sub_f

                    # Add headers as the first row if indicated
                    if add_header:
                        sub_f.write(",".join(ALL_COLS_WITH_PK) + "\n")
                else:
                    sub_f = open_file_writers[value]

            # Write to appropriate file
            sub_f.write(line)

            prev_value = value

    # Close all sub file handles
    for _, sub_f in open_file_writers.items():
        sub_f.close()

    return created_files

def date_to_int(date: datetime.date) -> int:
    '''
    Convert input datetime.date to date integer format YYYYmmdd
    '''
    return date.day + date.month * 100 + date.year * 10000

def int_to_date(date_int: int) -> datetime.date:
    '''
    Convert input date integer format YYYYmmdd to datetime.date
    '''
    day = date_int % 100
    month = (date_int // 100) % 100
    year = date_int // 10000
    return datetime.date(year, month, day)

def date_int_from_filename(filename: str) -> int:
    '''
    Extract date integer from a filename.
    Assumes file is of format '{dir}/just_covidcast_{date}_...{ext}'.
    '''
    file_base = os.path.basename(filename)
    return int(file_base.split("_")[2])

def create_index(entry: dict) -> tuple:
    '''
    Creates the index tuple that uniquely identifies an entry that may
    have multiple versions/issues.

    Args:
        entry: Dictionary that contains ALL fields of a row
    Returns:
        Tuple used to uniquely identity an entry
    '''
    return tuple(entry[col] for col in INDEX_COLS)

def create_issue(entry: dict, issue_date: datetime.date) -> dict:
    '''
    Creates an issue, i.e. the values that may change across time from an entry
    Takes 'time_type' into consideration when calculating 'lag'

    Args:
        entry: Dictionary that contains ALL fields of a row
        issue_date: Date of the new issue, usually from filename
    Returns:
        Fields related to an issue only as a subset of the entry dictionary
    '''
    time_value = int_to_date(int(entry["time_value"]))

    issue = {col: entry[col] for col in VALUE_COLS}

    issue["issue"] = date_to_int(issue_date)
    if entry["time_type"] == "'day'":
        issue["lag"] = (issue_date - time_value).days
    elif entry["time_type"] == "'week'":
        issue["lag"] = (issue_date - time_value).days // 7

    return issue

# Ensure the hard-coded index indices are right
assert INDEX_COLS[2] == "time_type"
assert INDEX_COLS[4] == "time_value"

def create_issue_from_change(
        latest_issue: dict, change: dict,
        index: tuple, issue_date: datetime.date) -> dict:
    '''
    Creates an issue, i.e. the values that may chaneg across time from the latest issue
    Takes 'time_type' into consideration when calculating 'lag'

    Args:
        latest_issue: Latest issue dict that has values from 'before' in the diff
        change: Changes (from csvdiff) from latest_issue to the new issue to be created
        index: Index tuple that latest_issue and new issue are associated with
        issue_date: Date of the new issue, usually from filename
    '''

    issue = deepcopy(latest_issue)
    time_type = index[2]
    time_value = int_to_date(int(index[4]))

    for col, diff in change["fields"].items():
        assert latest_issue[col] == diff["from"]
        issue[col] = diff["to"]

    issue["issue"] = date_to_int(issue_date)
    if time_type == "'day'":
        issue["lag"] = (issue_date - time_value).days
    elif time_type == "'week'":
        issue["lag"] = (issue_date - time_value).days // 7

    return issue

def update_issues(
        before_file: Optional[str], after_file: str, accum: dict) -> dict:
    '''
    Updates an accumulator (accum) that maps the unique indices to a list of issues
    If before_file is None, then accum should be empty and we are simplying filling
    it with entries from after_file. Otherwise, we are updating accum with the diff
    between before_file to after_file.

    Args:
        before_file: The "before" CSV file in diffing. None if after_file is the 1st
        after_file: The "after" CSV file in diffing.
        accum: Accumulating dictionary that maps index -> List[issue]

    Returns:
        The updated accum, although it is modified in-place already
    '''

    # Get issue date from after_file
    issue_date = int_to_date(date_int_from_filename(after_file))

    # At first file, just add all contents as new entries
    if before_file is None:
        with open(after_file, "r") as f_after:
            reader = csv.reader(f_after)
            header = next(reader)

            assert header == ALL_COLS_WITH_PK

            for row in reader:
                # The first actual header is 'id', skipping that
                entry = dict(zip(ALL_COLS, row[1:]))
                index = create_index(entry)

                # TODO: Should the first issue date be from the first backup date?
                issue = create_issue(entry, issue_date)

                accum[index] = [issue]
    else:
        # Perform the CSV diff using INDEX_COLS to identify rows
        patch = csvdiff.diff_files(before_file, after_file, INDEX_COLS)

        if len(patch["removed"]) > 0:
            logging.warning("Apparently there are %d removed entries!", len(patch["removed"]))

        for entry in patch["added"]:
            index = create_index(entry)
            issue = create_issue(entry, issue_date)

            assert index not in accum

            # Create initial list for this particular index
            accum[index] = [issue]

        for change in patch["changed"]:
            index = tuple(change["key"])

            assert index in accum
            latest_issue = accum[index][-1]
            new_issue = create_issue_from_change(latest_issue, change, index, issue_date)

            accum[index].append(new_issue)

    return accum

def read_rows(accum: dict):
    '''
    Is a generator that yields string tuples representing a row for SQL INSERT statements,
    from the accumulated issues dictionary.
    '''

    row_fmt = "(" \
        "{id},{source},{signal},{time_type},{geo_type},{time_value},{geo_value}," \
        "{timestamp1},{value},{stderr},{sample_size},{timestamp2},{direction},{issue},{lag})"

    for index, issues in accum.items():
        index_vals = dict(zip(INDEX_COLS, index))
        for issue in issues:
            yield row_fmt.format(id=0, **index_vals, **issue)

def chunked(iterable: Iterable, size) -> Iterator[List]:
    '''
    Chunks an iterable into desired size without walking whole iterable first.
    https://stackoverflow.com/questions/24527006/split-a-generator-into-chunks-without-pre-walking-it
    '''
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))

def write_sql_insert(accum: dict, outfile: str, chunked_size=1000):
    '''
    Writes the resulting SQL file of INSERT statements from the accumulated issues

    Args:
        accum: Accumulating dictionary that maps index -> List[issue]
        outfile: Output SQL filename
        chunked_size: Maximum number of rows to include in a single INSERT statement
    '''
    with open(outfile, "w") as f_sql:
        rows = read_rows(accum)
        for rows_chunk in chunked(rows, chunked_size):
            insert_stmt = COVIDCAST_INSERT_START + \
                ",\n".join(rows_chunk) + \
                ";\n"
            f_sql.write(insert_stmt)

if __name__ == "__main__":
    main(parse_args())
