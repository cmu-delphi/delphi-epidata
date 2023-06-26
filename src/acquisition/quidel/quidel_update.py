"""
===============
=== Purpose ===
===============

Stores data provided by Quidel Corp., which contains flu lab test results.
See: quidel.py


=======================
=== Data Dictionary ===
=======================

`quidel` is the table where quidel data is stored.
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| location | varchar(8)  | NO   | MUL | NULL    |                |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| value    | float       | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
location: hhs1-10
epiweek: the epiweek during which the queries were executed
value: number of total test records per facility, within each epiweek

=================
=== Changelog ===
=================
2017-12-14:
  * add "need update" check

2017-12-02:
  * original version
"""

# standard library
import argparse

# third party
import mysql.connector

# first party
from delphi.epidata.acquisition.quidel import quidel
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
import delphi.utils.epiweek as flu
from delphi.utils.geo.locations import Locations

LOCATIONS = Locations.hhs_list
DATAPATH = "/home/automation/quidel_data"


def update(locations, first=None, last=None, force_update=False, load_email=True):
    # download and prepare data first
    qd = quidel.QuidelData(DATAPATH, load_email)
    if not qd.need_update and not force_update:
        print("Data not updated, nothing needs change.")
        return
    
    qd_data = qd.load_csv()
    qd_measurements = qd.prepare_measurements(qd_data, start_weekday=4)
    qd_ts = quidel.measurement_to_ts(qd_measurements, 7, startweek=first, endweek=last)
    # connect to the database
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata", host=secrets.db.host)
    cur = cnx.cursor()

    def get_num_rows():
        cur.execute("SELECT count(1) `num` FROM `quidel`")
        for (num,) in cur:
            pass
        return num

    # check from 4 weeks preceeding the last week with data through this week
    cur.execute("SELECT max(`epiweek`) `ew0`, yearweek(now(), 6) `ew1` FROM `quidel`")
    for (ew0, ew1) in cur:
        ew0 = 200401 if ew0 is None else flu.add_epiweeks(ew0, -4)
    ew0 = ew0 if first is None else first
    ew1 = ew1 if last is None else last
    print(f"Checking epiweeks between {int(ew0)} and {int(ew1)}...")

    # keep track of how many rows were added
    rows_before = get_num_rows()

    # check Quidel for new and/or revised data
    sql = """
    INSERT INTO
      `quidel` (`location`, `epiweek`, `value`)
    VALUES
      (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
      `value` = %s
    """

    total_rows = 0

    for location in locations:
        if location not in qd_ts:
            continue
        ews = sorted(qd_ts[location].keys())
        num_missing = 0
        for ew in ews:
            v = qd_ts[location][ew]
            sql_data = (location, ew, v, v)
            cur.execute(sql, sql_data)
            total_rows += 1
            if v == 0:
                num_missing += 1
        if num_missing > 0:
            print(f" [{location}] missing {int(num_missing)}/{len(ews)} value(s)")

    # keep track of how many rows were added
    rows_after = get_num_rows()
    print(f"Inserted {int(rows_after - rows_before)}/{int(total_rows)} row(s)")

    # cleanup
    cur.close()
    cnx.commit()
    cnx.close()


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    # fmt: off
    parser.add_argument(
        "--location",
        action="store",
        type=str,
        default=None,
        help="location(s) (ex: all; any of hhs1-10)"
    )
    parser.add_argument(
        "--first",
        "-f",
        default=None,
        type=int,
        help="first epiweek override"
    )
    parser.add_argument(
        "--last",
        "-l",
        default=None,
        type=int,
        help="last epiweek override"
    )
    parser.add_argument(
        "--force_update",
        "-u",
        action="store_true",
        help="force update db values"
    )
    parser.add_argument(
        "--skip_email",
        "-s",
        action="store_true",
        help="skip email downloading step"
    )
    # fmt: on
    args = parser.parse_args()

    # sanity check
    first, last, force_update, skip_email = (
        args.first,
        args.last,
        args.force_update,
        args.skip_email,
    )
    load_email = not skip_email
    if first is not None:
        flu.check_epiweek(first)
    if last is not None:
        flu.check_epiweek(last)
    if first is not None and last is not None and first > last:
        raise Exception("epiweeks in the wrong order")

    # decide what to update
    if args.location.lower() == "all":
        locations = LOCATIONS
    else:
        locations = args.location.lower().split(",")

    # run the update
    update(locations, first, last, force_update, load_email)


if __name__ == "__main__":
    main()
