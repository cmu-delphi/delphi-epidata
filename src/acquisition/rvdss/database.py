"""
===============
=== Purpose ===
===============

Stores data provided by rvdss Corp., which contains flu lab test results.
See: rvdss.py


=======================
=== Data Dictionary ===
=======================

`rvdss` is the table where rvdss data is stored.
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
from delphi.epidata.acquisition.rvdss import rvdss
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
import delphi.utils.epiweek as flu
from delphi.utils.geo.locations import Locations

LOCATIONS = Locations.hhs_list
DATAPATH = "/home/automation/rvdss_data"


def update(locations, first=None, last=None, force_update=False, load_email=True):
    # download and prepare data first
    qd = rvdss.rvdssData(DATAPATH, load_email)
    if not qd.need_update and not force_update:
        print("Data not updated, nothing needs change.")
        return

    qd_data = qd.load_csv()
    qd_measurements = qd.prepare_measurements(qd_data, start_weekday=4)
    qd_ts = rvdss.measurement_to_ts(qd_measurements, 7, startweek=first, endweek=last)
    # connect to the database
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata")
    cur = cnx.cursor()

    def get_num_rows():
        cur.execute("SELECT count(1) `num` FROM `rvdss`")
        for (num,) in cur:
            pass
        return num

    # check from 4 weeks preceeding the last week with data through this week
    cur.execute("SELECT max(`epiweek`) `ew0`, yearweek(now(), 6) `ew1` FROM `rvdss`")
    for (ew0, ew1) in cur:
        ew0 = 200401 if ew0 is None else flu.add_epiweeks(ew0, -4)
    ew0 = ew0 if first is None else first
    ew1 = ew1 if last is None else last
    print(f"Checking epiweeks between {int(ew0)} and {int(ew1)}...")

    # keep track of how many rows were added
    rows_before = get_num_rows()

    # check rvdss for new and/or revised data
    sql = """
    INSERT INTO
      `rvdss` (`location`, `epiweek`, `value`)
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
