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

# third party
import mysql.connector

# first party
from delphi.epidata.acquisition.flusurv import flusurv
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
from delphi.utils.epiweek import delta_epiweeks


def get_rows(cur):
    """Return the number of rows in the `flusurv` table."""

    # count all rows
    cur.execute("SELECT count(1) `num` FROM `flusurv`")
    for (num,) in cur:
        return num


def update(issue, location, test_mode=False):
    """Fetch and store the currently avialble weekly FluSurv dataset."""

    # fetch data
    location_code = flusurv.location_to_code[location]
    print("fetching data for", location, location_code)
    data = flusurv.get_data(location_code)

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
        # As of Sept 2023, we expect to see these 24 groups, as described in
        #  the top-level "master_lookup" element of the new GRASP API
        #  (https://gis.cdc.gov/GRASP/Flu3/PostPhase03DataTool) response
        #  object:
        # 'master_lookup' = [
        #     {'Variable': 'Age', 'valueid': 1, 'parentid': 97, 'Label': '0-4 yr', 'Color_HexValue': '#d19833', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 2, 'parentid': 97, 'Label': '5-17 yr', 'Color_HexValue': '#707070', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 3, 'parentid': 98, 'Label': '18-49 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 4, 'parentid': 98, 'Label': '50-64 yr', 'Color_HexValue': '#516889', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 5, 'parentid': 98, 'Label': '65+ yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 7, 'parentid': 5, 'Label': '65-74 yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 8, 'parentid': 5, 'Label': '75-84 yr', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 9, 'parentid': 5, 'Label': '85+', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 10, 'parentid': 3, 'Label': '18-29 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 11, 'parentid': 3, 'Label': '30-39 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 12, 'parentid': 3, 'Label': '40-49 yr', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 21, 'parentid': 2, 'Label': '5-11  yr', 'Color_HexValue': '#707070', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 22, 'parentid': 2, 'Label': '12-17 yr', 'Color_HexValue': '#707070', 'Enabled': True}
        #     {'Variable': 'Age', 'valueid': 97, 'parentid': 0, 'Label': '< 18', 'Color_HexValue': '#000000', 'Enabled': True},
        #     {'Variable': 'Age', 'valueid': 98, 'parentid': 0, 'Label': '>= 18', 'Color_HexValue': '#000000', 'Enabled': True},
        #
        #     {'Variable': 'Race', 'valueid': 1, 'parentid': None, 'Label': 'White', 'Color_HexValue': '#516889', 'Enabled': True},
        #     {'Variable': 'Race', 'valueid': 2, 'parentid': None, 'Label': 'Black', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        #     {'Variable': 'Race', 'valueid': 3, 'parentid': None, 'Label': 'Hispanic/Latino', 'Color_HexValue': '#d19833', 'Enabled': True},
        #     {'Variable': 'Race', 'valueid': 4, 'parentid': None, 'Label': 'Asian/Pacific Islander', 'Color_HexValue': '#cc5e56', 'Enabled': True},
        #     {'Variable': 'Race', 'valueid': 5, 'parentid': None, 'Label': 'American Indian/Alaska Native', 'Color_HexValue': '#007d8e', 'Enabled': True},
        #
        #     {'Variable': 'Sex', 'valueid': 1, 'parentid': None, 'Label': 'Male', 'Color_HexValue': '#44b3c6', 'Enabled': True},
        #     {'Variable': 'Sex', 'valueid': 2, 'parentid': None, 'Label': 'Female', 'Color_HexValue': '#F2775F', 'Enabled': True},
        #
        #     {'Variable': None, 'valueid': 0, 'parentid': 0, 'Label': 'Overall', 'Color_HexValue': '#000000', 'Enabled': True},
        # ]
        #
        # The previous version of the GRASP API
        #  (https://gis.cdc.gov/GRASP/Flu3/GetPhase03InitApp)
        #  used a different age group-id mapping, as described in the
        #  top-level "ages" element:
        #    'ages' = [
        #        {'label': '0-4 yr', 'ageid': 1, 'color_hexvalue': '#1B9E77'},
        #        {'label': '5-17 yr', 'ageid': 2, 'color_hexvalue': '#D95F02'},
        #        {'label': '18-49 yr', 'ageid': 3, 'color_hexvalue': '#4A298B'},
        #        {'label': '50-64 yr', 'ageid': 4, 'color_hexvalue': '#E7298A'},
        #        {'label': '65+ yr', 'ageid': 5, 'color_hexvalue': '#6AA61E'},
        #        {'label': 'Overall', 'ageid': 6, 'color_hexvalue': '#000000'},
        #        {'label': '65-74 yr', 'ageid': 7, 'color_hexvalue': '#A6CEE3'},
        #        {'label': '75-84 yr', 'ageid': 8, 'color_hexvalue': '#CAB2D6'},
        #        {'label': '85+', 'ageid': 9, 'color_hexvalue': '#1f78b4'}
        #    ]
        #
        # In addition to the new age, race, and sex breakdowns, the
        # group id for overall reporting has changed from 6 to 0.
        n_max_expected_groups = 24
        assert len(epiweek.keys()) == n_max_expected_groups, \
            f"{location} {epiweek} data does not contain the expected {n_max_expected_groups} groups"

        lag = delta_epiweeks(epiweek, issue)
        if lag > 52:
            # Ignore values older than one year, as (1) they are assumed not to
            # change, and (2) it would adversely affect database performance if all
            # values (including duplicates) were stored on each run.
            continue
        args_meta = {
            "release_date": release_date,
            "issue": issue,
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

    data = fetch_flusurv_object()

    # scrape current issue from the main page
    issue = flusurv.get_current_issue(data)
    print(f"current issue: {int(issue)}")

    # fetch flusurv data
    if args.location == "all":
        # all locations
        for location in flusurv.location_to_code.keys():
            update(issue, location, args.test)
    else:
        # single location
        update(issue, args.location, args.test)


if __name__ == "__main__":
    main()
