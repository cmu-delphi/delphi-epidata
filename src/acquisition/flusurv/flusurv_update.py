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

US flu hospitalization rates are stored in the `flusurv` table. See
`strc/ddl/fluview.sql` for the `flusurv` schema. See `docs/api/flusurv.md` for
field descriptions.

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
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
from delphi.utils.epiweek import delta_epiweeks
from .api import FlusurvLocationFetcher
from .constants import (MAX_AGE_TO_CONSIDER_WEEKS, EXPECTED_GROUPS)


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
    nonrelease_fields = ("issue", "epiweek", "location", "lag", "season") + EXPECTED_GROUPS
    other_field_names = ", ".join(
        f"`{name}`" for name in nonrelease_fields
    )
    other_field_values = ", ".join(
        f"%({name})s" for name in nonrelease_fields
    )
    # Updates on duplicate key only for release date + signal fields, not metadata.
    other_field_coalesce = ", ".join(
        f"`{name}` = coalesce(%({name})s, `{name}`)" for name in EXPECTED_GROUPS
    )

    sql = f"""
    INSERT INTO `flusurv` (
      `release_date`,
      {other_field_names}
    )
    VALUES (
      %(release_date)s,
      {other_field_values}
    )
    ON DUPLICATE KEY UPDATE
      `release_date` = least(`release_date`, %(release_date)s),
      {other_field_coalesce}
    """

    # insert/update each row of data (one per epiweek)
    for epiweek in epiweeks:
        lag = delta_epiweeks(epiweek, fetcher.metadata.issue)
        if lag > fetcher.metadata.max_age_weeks:
            # Ignore obs older than `max_age_weeks` from user command line
            # argument `max_age`. We restricted our FluSurv API call to only
            # seasons older than `max_age_weeks` (in order to reduce the
            # amount of data being pulled), but the season by the cutoff date
            # may still have some weeks older than we'd like to include.
            continue

        missing_expected_groups = EXPECTED_GROUPS - data[epiweek].keys()
        # Remove the season description since we also store it in each epiweek obj
        unexpected_groups = data[epiweek].keys() - EXPECTED_GROUPS - {"season"}
        if len(missing_expected_groups) != 0:
            warn(
                f"{location} {epiweek} data is missing group(s) {missing_expected_groups}"
            )
            # Fill in expected values with `None` so SQL query injection below
            # doesn't fail with a key error.
            for key in missing_expected_groups:
                data[epiweek][key] = None
        if len(unexpected_groups) != 0:
            warn(
                f"{location} {epiweek} data includes new group(s) {unexpected_groups}"
            )
            # Remove unexpected values from the data. Construction of the SQL
            # query below fetches values by key, so these would be ignored even
            # if we left them.
            for key in unexpected_groups:
                del data[epiweek][key]

        args_meta = {
            # the date when this record was first received by Delphi
            "release_date": release_date,
            # the epiweek of receipt by Delphi (e.g. issue 201453 includes
            # epiweeks up to and including 2014w53, but not 2015w01 or
            # following)
            "issue": fetcher.metadata.issue,
            # the epiweek during which the data was collected
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
        type=str,
        help='location for which data should be scraped (e.g. "CA" or "all")'
    )
    parser.add_argument(
        "--max-age",
        default=MAX_AGE_TO_CONSIDER_WEEKS,
        type=int,
        help="age in weeks of data to ingest"
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

    fetcher = FlusurvLocationFetcher(args.max_age)
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
