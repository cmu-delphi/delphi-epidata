"""
Script to use DB backups to migrate data for covidcast issues and lag addition

Author: Eu Jing Chua
Created: 2020-06-26
"""

# Standard library
import argparse
from collections import defaultdict
import datetime
import glob
import gzip
from itertools import islice, chain, starmap
import logging
from multiprocessing import Pool
import os
from typing import Optional, List, Iterable, Iterator, Dict, Tuple

# Third party
import pandas as pd
from multiprocessing_logging import install_mp_handler, uninstall_mp_handler

COVIDCAST_INSERT_START = "INSERT INTO `covidcast` VALUES "

# Column names
INDEX_COLS = ["source", "signal", "time_type", "geo_type", "time_value", "geo_value"]
VALUE_COLS = ["timestamp1", "value", "stderr", "sample_size", "timestamp2", "direction"]
ALL_COLS = INDEX_COLS + VALUE_COLS
ALL_COLS_WITH_PK = ["id"] + ALL_COLS

# Dtypes that try save memory by using categoricals
DTYPES = {
    # skip "id", the primary key as it may have changed
    "source": "category",
    "signal": "category",
    "time_type": "category",
    "geo_type": "category",
    # time_value as str, because we need this parsed as a datetime anyway
    "time_value": "str",
    "geo_value": "category",
    "timestamp1": "int",
    "value": "str",
    "stderr": "str",
    "sample_size": "str",
    "timestamp2": "int",
    "direction": "category"
}

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
        "--par", dest="parallel", action="store_true",
        help="Enable multiprocessing")
    parser.add_argument(
        "--ncpu-csvs", dest="ncpu_csvs", default=1, type=int,
        help="Max number of processes to use for CSV processing (low memory usage)")
    parser.add_argument(
        "--ncpu-sources", dest="ncpu_sources", default=1, type=int,
        help="Max number of processes to use for processing sources (high memory usage)")
    parser.add_argument(
        "--incremental", dest="use_cache", action="store_true",
        help="Reuse results in --tmp-dir, and skip over existing results in --out-dir")
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
    logging.info("Parallel: %s", args.parallel)
    if args.parallel:
        logging.info("Num. CPU (CSVs): %d", args.ncpu_csvs)
        logging.info("Num. CPU (sources): %d", args.ncpu_sources)
    logging.info("Incremental: %s", args.use_cache)
    logging.info("Debug output: %s", args.debug)
    print()

def main(args):
    '''
    Overall flow:
        1) Extract relevant tuples from .sql into CSVs so we can use CSV diffing tools
        2) Split each CSV by 'source'
        3) For each source, do a CSV diff for each sliding pair of dates
        4) As diffs are found, write results to a .sql file for current source
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
    extract_args = []

    # Ensure files are in sorted order of date in filename
    for sql_file in sorted(args.sql_files):
        csv_file = os.path.join(
            args.tmp_dir,
            f"just_covidcast_{date_int_from_filename(sql_file)}.csv")

        if args.use_cache and os.path.exists(csv_file):
            logging.debug("CSV %s already exists, skipping processing of %s", csv_file, sql_file)
        else:
            extract_args.append((sql_file, csv_file))

        # Regardless of cache, keep track of csv files anyway
        csv_files.append(csv_file)

    starmap_mp_logging(
        extract_to_csv, extract_args,
        par=args.parallel, ncpu=args.ncpu_csvs)

    # 2) Split each backup's csv by source
    logging.info("Splitting csvs...")
    split_col = 1
    split_csv_args = []
    files_by_src = defaultdict(list)

    for csv_file in csv_files:
        base_name, f_ext = os.path.splitext(csv_file)
        split_patt = f"{base_name}_*{f_ext}"
        split_csv_files = glob.glob(split_patt)

        if args.use_cache and len(split_csv_files) > 0:
            logging.debug("CSV %s already split, skipping splitting", csv_file)

            # If split csvs already exist, update files_by_src directly
            for sub_csv_file in split_csv_files:
                src = sub_csv_file.split("_")[-1][:-4]
                files_by_src[src].append(sub_csv_file)
        else:
            split_csv_args.append((csv_file, split_col))

    by_srcs = starmap_mp_logging(
        split_csv_by_col, split_csv_args,
        par=args.parallel, ncpu=args.ncpu_csvs)

    # Combine all return dictionaries into a dictionary of lists instead
    # Note that each list may not be sorted
    for by_src in by_srcs:
        for src, sub_csv_file in by_src.items():
            files_by_src[src].append(sub_csv_file)

    # 3) Find issues from sliding pairs of [None, csv_1, csv_2, ... csv_N] for each source
    proc_args = []
    for source, src_files in files_by_src.items():
        if source in args.skip_sources:
            logging.info("Skipping group: %s", source)
            continue

        proc_args.append((args, source, src_files))

    output_sql_files = starmap_mp_logging(
        process_source, proc_args,
        par=args.parallel, ncpu=args.ncpu_sources)

    return output_sql_files

def starmap_mp_logging(func, args: Iterable, par: bool = False, ncpu: Optional[int] = None):
    '''
    Does a starmap of f over args, either in parallel or serially, with logging support

    Args:
        func: Callable to execute with each of args
        args: List-like of args to execute f with
        par: Whether to run in parallel or not
        ncpu: When par=True, how many processes to use

    Returns:
        Result equivalent to starmap(f, args)
    '''
    if par:
        install_mp_handler()
        try:
            with Pool(ncpu) as pool:
                return pool.starmap(func, args)
        finally:
            uninstall_mp_handler()
    else:
        return starmap(func, args)

def process_source(args, source: str, src_files: List[str]) -> List[List[str]]:
    logging.info("[%s] Finding issues and generating SQL files...", source)
    files = [None] + sorted(src_files)
    output_files = []

    for before_file, after_file in zip(files, files[1:]):
        date_int_after = date_int_from_filename(after_file)
        if before_file is None:
            logging.debug("[%s] First: %s", source, date_int_after)
            outfile = os.path.join(args.out_dir, f"{source}_00000000_{date_int_after}.sql")
        else:
            date_int_before = date_int_from_filename(before_file)
            logging.debug("[%s] Diffing: from %s to %s", source, date_int_before, date_int_after)
            outfile = os.path.join(args.out_dir, f"{source}_{date_int_before}_{date_int_after}.sql")

        # Diff and find new issues
        if args.use_cache and os.path.exists(outfile):
            logging.debug(
                "[%s] SQL file %s already generated, skipping diff",
                source, outfile)
            output_files.append(outfile)
            continue

        issues = generate_issues(before_file, after_file)

        # 4) Write out found issues into the SQL file
        logging.debug("[%s] Writing to %s", source, outfile)
        try:
            with open(outfile, "w") as f_sql:
                for issues_chunk in chunked(issues, args.chunk_size):
                    insert_stmt = COVIDCAST_INSERT_START + \
                        ",\n".join(issues_chunk) + \
                        ";\n"
                    f_sql.write(insert_stmt)
            output_files.append(outfile)

        except Exception as ex:
            logging.error(
                "[%s] Stopped unexpectedly while writing %s, deleting it",
                source, outfile, exc_info=True)
            os.remove(outfile)
            raise ex

    return output_files

def extract_to_csv(filename: str, output: str):
    '''
    Takes a backup .sql file and produces a CSV representing just the covidcast rows.
    Also accepts gzipped .sql.gz files as input.

    Args:
        filename: Input .sql or .sql.gz file
        output: Output .csv file
    '''

    logging.debug("Processing %s into %s", filename, output)

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
        filename: str, col_idx: int, add_header: bool = True) -> Dict[str, str]:
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

    logging.debug("Splitting %s by %s", filename, ALL_COLS_WITH_PK[col_idx])

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

def datetime_to_int(date: datetime.datetime) -> int:
    '''
    Convert input datetime.date to date integer format YYYYmmdd
    '''
    return int(date.strftime("%Y%m%d"))

def int_to_datetime(date_int: int) -> datetime.datetime:
    '''
    Convert input date integer format YYYYmmdd to datetime.datetime
    '''
    return datetime.datetime.strptime(str(date_int),"%Y%m%d")

def date_int_from_filename(filename: str) -> int:
    '''
    Extract date integer from a filename.
    Assumes file is of format '{dir}/just_covidcast_{date}_...{ext}'.
    '''
    file_base = os.path.basename(filename)
    return int(file_base.split("_")[2])

def pd_csvdiff(
        before_file: str, after_file: str,
        index_cols: List[str],
        dtypes: Dict[str, str],
        find_removals: bool = False
        ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    '''
    Finds the diff (additions and changes only by default) between two CSV files.
    Can find removals, but the additional index operations required add significant time.
    Uses pandas with specified dtypes to save some memory.

    Args:
        before_file: The "before" CSV file to diff from
        after_file: The "after" CSV file to diff to
        index_cols: Column names to use as the index that identifies an entry
        dtypes: Dtype definitions for column names to try save memory
        find_removals: Whether to find entries that were removed too

    Returns:
        A dataframe containing a subset of the after_file CSV that represents additions and changes
    '''
    df_before = pd.read_csv(
        before_file, usecols=dtypes.keys(), parse_dates=["time_value"],
        dtype=dtypes, na_filter=False)
    df_after = pd.read_csv(
        after_file, usecols=dtypes.keys(), parse_dates=["time_value"],
        dtype=dtypes, na_filter=False)

    # Efficiently union all categories together for comparison
    for col, dtype in dtypes.items():
        if dtype == "category":
            before_cats = df_before[col].cat.categories
            after_cats = df_after[col].cat.categories
            df_before[col].cat.add_categories(after_cats.difference(before_cats), inplace=True)
            df_after[col].cat.add_categories(before_cats.difference(after_cats), inplace=True)

            assert df_before[col].dtype == df_after[col].dtype

    df_before.set_index(index_cols, inplace=True)
    df_after.set_index(index_cols, inplace=True)

    # Ensure lex sorted indices for efficient indexing
    df_before.sort_index(inplace=True)
    df_after.sort_index(inplace=True)

    # Find additions and changes together
    # Re-index df_before to be like df_after, index-wise, then do a diff
    # For common indices, different field values be false in same_mask
    # Since df_before is filled with NaN for new indices, new indices turn false in same_mask
    same_mask = (df_before.reindex(df_after.index) == df_after)

    # Ignore timestamp2 in the diff
    is_diff = ~(same_mask.loc[:, same_mask.columns != "timestamp2"].all(axis=1))

    # Removed indices can be found via index difference, but is expensive
    if find_removals:
        removed_idx = df_before.index.difference(df_after.index)

        return (
            df_after.loc[is_diff, :],
            df_before.loc[removed_idx, :])

    return (
        df_after.loc[is_diff, :],
        None)

def generate_issues(
        before_file: Optional[str], after_file: str) -> Iterator[str]:
    '''
    A generator that diffs the input files, then yields formatted strings representing a row-tuple
    to be inserted in SQL. If before_file is None, we are simplying filling it with entries from
    after_file. The issue date for these "first" entries come from the after_file filename.
    Otherwise, we are updating accum with the diff between before_file to after_file.

    Args:
        before_file: The "before" CSV file in diffing. None if after_file is the 1st
        after_file: The "after" CSV file in diffing.

    Returns:
        An iterator that yields the string row-tuples to be inserted as an issue.
    '''

    # Get issue date from after_file
    issue_date_int = date_int_from_filename(after_file)
    issue_date = int_to_datetime(issue_date_int)

    row_fmt = "(" \
        "{id},{source},{signal},{time_type},{geo_type},{time_value},{geo_value}," \
        "{row.timestamp1},{row.value},{row.stderr},{row.sample_size},{row.timestamp2},{row.direction}," \
        "{issue},{row.lag})"

    try:
        if before_file is None:
            # At first file, just yield all contents as new issues
            df_diff = pd.read_csv(
                after_file, usecols=DTYPES.keys(), parse_dates=["time_value"],
                dtype=DTYPES, index_col=INDEX_COLS, na_filter=False)
        else:
            # Perform the CSV diff using INDEX_COLS to identify rows
            df_diff, _ = pd_csvdiff(before_file, after_file, INDEX_COLS, DTYPES)
    except Exception as ex:
        logging.error(
            "Diff Failed!!! Between files '%s', '%s'",
            before_file, after_file, exc_info=True)
        raise ex

    # TODO: Does not really handle weekly values properly. Weekly time_value are in YYYYww format
    df_diff["lag"] = (issue_date - df_diff.index.get_level_values("time_value")).days
    is_weekly = df_diff.index.get_level_values("time_type") == "week"
    df_diff.loc[is_weekly, "lag"] = df_diff.loc[is_weekly, "lag"] // 7

    for row in df_diff.itertuples():
        index = dict(zip(INDEX_COLS, row.Index))
        index["time_value"] = datetime_to_int(index["time_value"])

        yield row_fmt.format(id=0, **index, row=row, issue=issue_date_int)

def chunked(iterable: Iterable, size) -> Iterator[Iterator]:
    '''
    Chunks an iterable into desired size without walking whole iterable first.
    https://stackoverflow.com/questions/24527006/split-a-generator-into-chunks-without-pre-walking-it
    '''
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))

if __name__ == "__main__":
    main(parse_args())
