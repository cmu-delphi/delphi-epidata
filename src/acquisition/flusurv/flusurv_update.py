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

import argparse

from delphi.epidata.acquisition.flusurv import flusurv
from delphi.utils.epidate import EpiDate
from delphi.utils.epiweek import delta_epiweeks
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ...server._config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_ENGINE_OPTIONS
)
from .models import FluSurv

engine = create_engine(SQLALCHEMY_DATABASE_URI, **SQLALCHEMY_ENGINE_OPTIONS)


def get_rows(session):
    """Return the number of rows in the `flusurv` table."""
    return session.query(FluSurv.id).count()


def update(issue, location_name, test_mode=False):
    """Fetch and store the currently avialble weekly FluSurv dataset."""

    # fetch data
    location_code = flusurv.location_codes[location_name]
    print('fetching data for', location_name, location_code)
    data = flusurv.get_data(location_code)

    # metadata
    epiweeks = sorted(data.keys())
    location = location_name
    release_date = str(EpiDate.today())

    with Session(engine) as session:
        rows1 = get_rows(session)
        print('rows before: %d' % rows1)
        for epiweek in epiweeks:
            lag = delta_epiweeks(epiweek, issue)
            if lag > 52:
                # Ignore values older than one year, as (1) they are assumed not to
                # change, and (2) it would adversely affect database performance if all
                # values (including duplicates) were stored on each run.
                continue
            args_meta = {
                "issue": issue,
                "epiweek": epiweek,
                "location": location,
            }
            args_update = {
                "release_date": release_date,
                "lag": lag,
                "rate_age_0": data[epiweek][0],
                "rate_age_1": data[epiweek][1],
                "rate_age_2": data[epiweek][2],
                "rate_age_3": data[epiweek][3],
                "rate_age_4": data[epiweek][4],
                "rate_overall": data[epiweek][5],
                "rate_age_5": data[epiweek][6],
                "rate_age_6": data[epiweek][7],
                "rate_age_7": data[epiweek][8],
            }
            existing_flusurv = session.query(FluSurv).filter_by(**args_meta)
            if existing_flusurv.first() is not None:
                existing_flusurv.update(args_update)
            else:
                args_create = dict(**args_meta, **args_update)
                session.add(FluSurv(**args_create))

        rows2 = get_rows(session)
        print('rows after: %d (+%d)' % (rows2, rows2 - rows1))
        if test_mode:
            print('test mode: not committing database changes')
        else:
            session.commit()
        session.close()


def main():
    # args and usage
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'location',
        help='location for which data should be scraped (e.g. "CA" or "all")'
    )
    parser.add_argument(
        '--test', '-t',
        default=False, action='store_true', help='do not commit database changes'
    )
    args = parser.parse_args()

    # scrape current issue from the main page
    issue = flusurv.get_current_issue()
    print('current issue: %d' % issue)

    # fetch flusurv data
    if args.location == 'all':
        # all locations
        for location in flusurv.location_codes.keys():
            update(issue, location, args.test)
    else:
        # single location
        update(issue, args.location, args.test)


if __name__ == '__main__':
    main()
