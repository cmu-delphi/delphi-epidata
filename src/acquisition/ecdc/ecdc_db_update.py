"""
===============
=== Purpose ===
===============

Stores versioned ECDC ILI data from ECDC website.

=======================
=== Data Dictionary ===
=======================

`ecdc_ili` is where the ILI data from ECDC is stored.
+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date   | date        | NO   | MUL | NULL    |                | 
| issue          | int(11)     | NO   | MUL | NULL    |                |
| epiweek        | int(11)     | NO   | MUL | NULL    |                |
| region         | varchar(12) | NO   | MUL | NULL    |                |
| lag            | int(11)     | NO   | MUL | NULL    |                |
| incidence_rate | double      | YES  |     | NULL    |                |
+----------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
  and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
region: the name of the location (3 letter country code)
lag: number of weeks between `epiweek` and `issue`
incidence_rate: num_ili/100k
"""

import argparse
import datetime
import glob
import os
import tempfile

# third party
import MySQLdb

# first party
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.ecdc.ecdc_ili import download_ecdc_data
from delphi.utils.epiweek import delta_epiweeks
from delphi.utils.epidate import EpiDate


def ensure_tables_exist():
    (u, p) = secrets.db.epi
    cnx = MySQLdb.connect(user=u, password=p, database="epidata")
    try:
        cursor = cnx.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `ecdc_ili` (
                `id` INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                `release_date` DATE NOT NULL,
                `issue` INT(11) NOT NULL,
                `epiweek` INT(11) NOT NULL,
                `lag` INT(11) NOT NULL,
                `region` VARCHAR(30) NOT NULL,
                `incidence_rate` DOUBLE NOT NULL,
                UNIQUE KEY (`issue`, `epiweek`, `region`)
            );
        """
        )
        cnx.commit()
    finally:
        cnx.close()


def safe_float(f):
    try:
        return float(f.replace(",", ""))
    except:
        return 0


def safe_int(i):
    try:
        return int(i.replace(",", ""))
    except:
        return 0


def get_rows(cnx, table="ecdc_ili"):
    # Count and return the number of rows in the `ecdc_ili` table.
    select = cnx.cursor()
    select.execute(f"SELECT count(1) num FROM {table}")
    for (num,) in select:
        pass
    select.close()
    return num


def update_from_file(issue, date, dir, test_mode=False):
    # Read ECDC data from CSVs and insert into (or update) the database.
    # database connection
    u, p = secrets.db.epi
    cnx = MySQLdb.connect(user=u, password=p, database="epidata")
    rows1 = get_rows(cnx, "ecdc_ili")
    print(f"rows before: {int(rows1)}")
    insert = cnx.cursor()

    # load the data, ignoring empty rows
    files = glob.glob(os.path.join(dir, "*.csv"))
    rows = []
    for filename in files:
        with open(filename) as f:
            for l in f:
                data = list(map(lambda s: s.strip().replace('"', ""), l.split(",")))
                row = {}
                row["epiweek"] = int(data[1][:4] + data[1][5:])
                row["region"] = data[4]
                row["incidence_rate"] = data[3]
                rows.append(row)
    print(f" loaded {len(rows)} rows")
    entries = [obj for obj in rows if obj]
    print(f" found {len(entries)} entries")

    sql = """
    INSERT INTO
        `ecdc_ili` (`release_date`, `issue`, `epiweek`, `region`, `lag`,
        `incidence_rate`)
    VALUES
        ('%s', %s, %s, '%s', %s, %s)
    ON DUPLICATE KEY UPDATE
        `release_date` = least(`release_date`, '%s'),
        `incidence_rate` = %s
    """

    for row in entries:
        lag = delta_epiweeks(row["epiweek"], issue)
        data_args = [row["incidence_rate"]]

        insert_args = [date, issue, row["epiweek"], row["region"], lag] + data_args
        update_args = [date] + data_args
        try:
            insert.execute(sql % tuple(insert_args + update_args))
        except:
            pass

    # cleanup
    insert.close()
    if test_mode:
        print("test mode, not committing")
        rows2 = rows1
    else:
        cnx.commit()
        rows2 = get_rows(cnx)
    print(f"rows after: {int(rows2)} (added {int(rows2 - rows1)})")
    cnx.close()


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    # fmt: off
    parser.add_argument(
        "--test",
        action="store_true",
        help="do dry run only, do not update the database"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="load an existing zip file (otherwise fetch current data)"
    )
    parser.add_argument(
        "--issue",
        type=int,
        help="issue of the file (e.g. 201740); used iff --file is given"
    )
    # fmt: on
    args = parser.parse_args()

    if (args.file is None) != (args.issue is None):
        raise Exception("--file and --issue must both be present or absent")

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"assuming release date is today, {date}")

    ensure_tables_exist()
    if args.file:
        update_from_file(args.issue, date, args.file, test_mode=args.test)
    else:
        # Code doesn't always download all files, unreproducible errors
        # Try a few times and hopefully one will work
        flag = 0
        max_tries = 5
        while flag < max_tries:
            flag = flag + 1
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Use temporary directory to avoid data from different time
                #   downloaded to same folder
                download_ecdc_data(download_dir=tmp_dir)
                issue = EpiDate.today().get_ew()
                files = glob.glob(f"{tmp_dir}/*.csv")
                for filename in files:
                    with open(filename) as f:
                        _ = f.readline()
                db_error = False
                for filename in files:
                    try:
                        update_from_file(issue, date, filename, test_mode=args.test)
                    except:
                        db_error = True
                if not db_error:
                    break  # Exit loop with success
        if flag >= max_tries:
            print("WARNING: Database `ecdc_ili` did not update successfully")


if __name__ == "__main__":
    main()
