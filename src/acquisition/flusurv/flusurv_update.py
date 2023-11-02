"""
===============
=== Purpose ===
===============

Stores FluSurv-NET data (flu hospitaliation rates) from CDC.

Note that the flusurv age groups are, in general, not the same as the ILINet
(fluview) age groups. However, the following groups are equivalent:
  - flusurv age_0 == fluview age_0  (0-4 years)
  - flusurv age_3 == fluview age_4  (50-64 years)
  - flusurv age_4 == fluview age_5  (65+ years)

See also:
  - flusurv.py


=======================
=== Data Dictionary ===
=======================

`flusurv` is the table where US flu hospitalization rates are stored.
+--------------+-------------+------+-----+---------+----------------+
| Field        | Type        | Null | Key | Default | Extra          |
+--------------+-------------+------+-----+---------+----------------+
| id           | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date | date        | NO   | MUL | NULL    |                |
| issue        | int(11)     | NO   | MUL | NULL    |                |
| epiweek      | int(11)     | NO   | MUL | NULL    |                |
| location     | varchar(32) | NO   | MUL | NULL    |                |
| lag          | int(11)     | NO   | MUL | NULL    |                |
| rate_age_0   | double      | YES  |     | NULL    |                |
| rate_age_1   | double      | YES  |     | NULL    |                |
| rate_age_2   | double      | YES  |     | NULL    |                |
| rate_age_3   | double      | YES  |     | NULL    |                |
| rate_age_4   | double      | YES  |     | NULL    |                |
| rate_overall | double      | YES  |     | NULL    |                |
| rate_age_5   | double      | YES  |     | NULL    |                |
| rate_age_6   | double      | YES  |     | NULL    |                |
| rate_age_7   | double      | YES  |     | NULL    |                |
+--------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
release_date: the date when this record was first published by the CDC
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
  and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
location: the name of the catchment (e.g. 'network_all', 'CA', 'NY_albany')
lag: number of weeks between `epiweek` and `issue`
rate_age_0: hospitalization rate for ages 0-4
rate_age_1: hospitalization rate for ages 5-17
rate_age_2: hospitalization rate for ages 18-49
rate_age_3: hospitalization rate for ages 50-64
rate_age_4: hospitalization rate for ages 65+
rate_overall: overall hospitalization rate
rate_age_5: hospitalization rate for ages 65-74
rate_age_6: hospitalization rate for ages 75-84
rate_age_7: hospitalization rate for ages 85+

=================
=== Changelog ===
=================

2017-05-22
  * update for new data source
2017-05-17
  * infer field `issue` from current date
2017-02-03
  + initial version
"""

# standard library
import argparse
from warnings import warn

# third party
import mysql.connector

# first party
from delphi.epidata.acquisition.flusurv.flusurv import FlusurvLocationFetcher
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
from delphi.utils.epiweek import delta_epiweeks
from constants import (MAX_AGE_TO_CONSIDER_WEEKS, EXPECTED_GROUPS)


def get_rows(cur):
    """Return the number of rows in the `flusurv` table."""

    # count all rows
    cur.execute("SELECT count(1) `num` FROM `flusurv`")
    for (num,) in cur:
        return num


def update(fetcher, location, test_mode=False):
    """Fetch and store the currently available weekly FluSurv dataset."""
    # Fetch location-specific data
    data = fetcher.get_data(location)

    # metadata
    epiweeks = sorted(data.keys())
    release_date = str(EpiDate.today())

    # connect to the database
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(host=secrets.db.host, user=u, password=p, database="epidata")
    cur = cnx.cursor()
    rows1 = get_rows(cur)
    print(f"rows before: {int(rows1)}")

    # SQL for insert/update
    sql = """
    INSERT INTO `flusurv` (
      `release_date`,
      `issue`,
      `epiweek`,
      `location`,
      `lag`,
      `season`,

      `rate_overall`,

      `rate_age_0`,
      `rate_age_1`,
      `rate_age_2`,
      `rate_age_3`,
      `rate_age_4`,
      `rate_age_5`,
      `rate_age_6`,
      `rate_age_7`,

      `rate_age_18t29`,
      `rate_age_30t39`,
      `rate_age_40t49`,
      `rate_age_5t11`,
      `rate_age_12t17`,
      `rate_age_lt18`,
      `rate_age_gte18`,

      `rate_race_white`,
      `rate_race_black`,
      `rate_race_hisp`,
      `rate_race_asian`,
      `rate_race_natamer`,

      `rate_sex_male`,
      `rate_sex_female`
    )
    VALUES (
      %(release_date)s,
      %(issue)s,
      %(epiweek)s,
      %(location)s,
      %(lag)s,
      %(season)s,

      %(rate_overall)s,

      %(rate_age_0)s,
      %(rate_age_1)s,
      %(rate_age_2)s,
      %(rate_age_3)s,
      %(rate_age_4)s,
      %(rate_age_5)s,
      %(rate_age_6)s,
      %(rate_age_7)s,

      %(rate_age_18t29)s,
      %(rate_age_30t39)s,
      %(rate_age_40t49)s,
      %(rate_age_5t11)s,
      %(rate_age_12t17)s,
      %(rate_age_<18)s,
      %(rate_age_>=18)s,

      %(rate_race_white)s,
      %(rate_race_black)s,
      %(rate_race_hispaniclatino)s,
      %(rate_race_asianpacificislander)s,
      %(rate_race_americanindianalaskanative)s,

      %(rate_sex_male)s,
      %(rate_sex_female)s
    )
    ON DUPLICATE KEY UPDATE
      `release_date` = least(`release_date`, %(release_date)s),
      `rate_overall` = coalesce(%(rate_overall)s, `rate_overall`),

      `rate_age_0` = coalesce(%(rate_age_0)s, `rate_age_0`),
      `rate_age_1` = coalesce(%(rate_age_1)s, `rate_age_1`),
      `rate_age_2` = coalesce(%(rate_age_2)s, `rate_age_2`),
      `rate_age_3` = coalesce(%(rate_age_3)s, `rate_age_3`),
      `rate_age_4` = coalesce(%(rate_age_4)s, `rate_age_4`),
      `rate_age_5` = coalesce(%(rate_age_5)s, `rate_age_5`),
      `rate_age_6` = coalesce(%(rate_age_6)s, `rate_age_6`),
      `rate_age_7` = coalesce(%(rate_age_7)s, `rate_age_7`),

      `rate_age_18t29` = coalesce(%(rate_age_18t29)s, `rate_age_18t29`),
      `rate_age_30t39` = coalesce(%(rate_age_30t39)s, `rate_age_30t39`),
      `rate_age_40t49` = coalesce(%(rate_age_40t49)s, `rate_age_40t49`),
      `rate_age_5t11` = coalesce(%(rate_age_5t11)s, `rate_age_5t11`),
      `rate_age_12t17` = coalesce(%(rate_age_12t17)s, `rate_age_12t17`),
      `rate_age_lt18` = coalesce(%(rate_age_<18)s, `rate_age_lt18`),
      `rate_age_gte18` = coalesce(%(rate_age_>=18)s, `rate_age_gte18`),

      `rate_race_white` = coalesce(%(rate_race_white)s, `rate_race_white`),
      `rate_race_black` = coalesce(%(rate_race_black)s, `rate_race_black`),
      `rate_race_hisp` = coalesce(%(rate_race_hispaniclatino)s, `rate_race_hisp`),
      `rate_race_asian` = coalesce(%(rate_race_asianpacificislander)s, `rate_race_asian`),
      `rate_race_natamer` = coalesce(%(rate_race_americanindianalaskanative)s, `rate_race_natamer`),

      `rate_sex_male` = coalesce(%(rate_sex_male)s, `rate_sex_male`),
      `rate_sex_female` = coalesce(%(rate_sex_female)s, `rate_sex_female`)
    """

    # insert/update each row of data (one per epiweek)
    for epiweek in epiweeks:
        lag = delta_epiweeks(epiweek, fetcher.metadata.issue)
        if lag > MAX_AGE_TO_CONSIDER_WEEKS:
            # Ignore values older than one year, as (1) they are assumed not to
            # change, and (2) it would adversely affect database performance if all
            # values (including duplicates) were stored on each run.
            continue

        missing_expected_groups = EXPECTED_GROUPS - data[epiweek].keys()
        # Remove the season description since we also store it in each epiweek obj
        unexpected_groups = data[epiweek].keys() - EXPECTED_GROUPS - {"season"}
        if len(missing_expected_groups) != 0:
            raise Exception(
                f"{location} {epiweek} data is missing group(s) {missing_expected_groups}"
            )
        if len(unexpected_groups) != 0:
            raise Exception(
                f"{location} {epiweek} data includes new group(s) {unexpected_groups}"
            )

        args_meta = {
            "release_date": release_date,
            "issue": fetcher.metadata.issue,
            "epiweek": epiweek,
            "location": location,
            "lag": lag
        }
        cur.execute(sql, {**args_meta, **data[epiweek]})

    # commit and disconnect
    rows2 = get_rows(cur)
    print(f"rows after: {int(rows2)} (+{int(rows2 - rows1)})")
    cur.close()
    if test_mode:
        print("test mode: not committing database changes")
    else:
        cnx.commit()
    cnx.close()


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    # fmt: off
    parser.add_argument(
        "location",
        help='location for which data should be scraped (e.g. "CA" or "all")'
    )
    parser.add_argument(
        "--test",
        "-t",
        default=False,
        action="store_true",
        help="do not commit database changes"
    )
    # fmt: on
    args = parser.parse_args()

    fetcher = FlusurvLocationFetcher(MAX_AGE_TO_CONSIDER_WEEKS)
    print(f"current issue: {int(fetcher.metadata.issue)}")

    # fetch flusurv data
    if args.location == "all":
        # all locations
        for location in fetcher.metadata.locations:
            update(fetcher, location, args.test)
    else:
        # single location
        if (args.location not in fetcher.metadata.locations):
            raise KeyError("Requested location {args.location} not available")
        update(fetcher, args.location, args.test)


if __name__ == "__main__":
    main()
