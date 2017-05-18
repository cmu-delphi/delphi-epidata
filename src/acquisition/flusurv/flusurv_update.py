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


=================
=== Changelog ===
=================

2017-05-17
  * infer field `issue` from current date
2017-02-03
  + initial version
"""

# standard library
import argparse
import os
import os.path
# third party
import mysql.connector
# first party
from epidate import EpiDate
from epiweek import delta_epiweeks
import flusurv
import secrets


def get_rows(cur):
  """Return the number of rows in the flusurv table."""

  # count all rows
  cur.execute('SELECT count(1) `num` FROM `flusurv`')
  for (num,) in cur:
    return num


def update(location_name, test_mode=False):
  """Fetch and store the currently avialble weekly flusurv dataset."""

  # fetch data
  location_code = flusurv.location_codes[location_name]
  print('fetching data for', location_name, location_code)
  data = flusurv.get_data(location_code)

  # metadata
  epiweeks = sorted(data.keys())
  today = EpiDate.today()
  release_date = str(today)
  location = location_name

  # There is some ambiguity about what value issue should take. In general,
  # "issue" refers to the previous whole epiweek as of publication time. For
  # example, the issue 201717 was published on Friday of 201718. For ILINet
  # that's always equal to the largest value of "epiweek" in the dataset. But
  # here, for FluSurv, summer epiweeks are omitted. So it's not always the case
  # that issue = max(epiweek). Since new data is usually published on the first
  # Friday following the issue week (otherwise, later), we assume that issue
  # increments on Friday of each week. This assumuption is violated from 00:00
  # ET Friday morning until the point in time at which data is made available.
  # During this time, the database will store last week's values in duplicate
  # for both the current issue and the previous issue. Once data is available
  # and has been fetched, the database rows for the current issue will be
  # updated with the new values, correct for the current issue. In practice,
  # this means that sometimes (e.g. some part of Friday morning) the last value
  # of any given flusurv timeseries will be duplicated.
  issue = max(epiweeks[-1], today.add_days(-12).get_ew())

  # connect to the database
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()
  rows1 = get_rows(cur)
  print('rows before: %d' % rows1)

  # SQL for insert/update
  sql = '''
  INSERT INTO `flusurv` (
    `release_date`, `issue`, `epiweek`, `location`, `lag`, `rate_age_0`,
    `rate_age_1`, `rate_age_2`, `rate_age_3`, `rate_age_4`, `rate_overall`
  )
  VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
  )
  ON DUPLICATE KEY UPDATE
    `release_date` = least(`release_date`, %s),
    `rate_age_0` = coalesce(%s, `rate_age_0`),
    `rate_age_1` = coalesce(%s, `rate_age_1`),
    `rate_age_2` = coalesce(%s, `rate_age_2`),
    `rate_age_3` = coalesce(%s, `rate_age_3`),
    `rate_age_4` = coalesce(%s, `rate_age_4`),
    `rate_overall` = coalesce(%s, `rate_overall`)
  '''

  # insert/update each row of data (one per epiweek)
  for epiweek in epiweeks:
    lag = delta_epiweeks(epiweek, issue)
    if lag > 52:
      # Ignore values older than one year, as (1) they are assumed not to
      # change, and (2) it would adversely affect database performance if all
      # values (including duplicates) were stored on each run.
      continue
    args_meta = [release_date, issue, epiweek, location, lag]
    args_insert = data[epiweek]
    args_update = [release_date] + data[epiweek]
    cur.execute(sql, tuple(args_meta + args_insert + args_update))

  # commit and disconnect
  rows2 = get_rows(cur)
  print('rows after: %d (+%d)' % (rows2, rows2 - rows1))
  cur.close()
  if test_mode:
    print('test mode: not committing database changes')
  else:
    cnx.commit()
  cnx.close()


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

  # The flusurv module makes a shell call to a local script, but this script
  # is likely called by Automation from another directory. In order for the
  # shell call to work, the working directory needs to be set to the location
  # of flusurv.py, which is the same location as this file.
  script_path = os.path.realpath(__file__)
  script_dir = os.path.dirname(script_path)
  os.chdir(script_dir)
  print('working directory set to %s' % os.getcwd())

  # fetch flusurv data
  if args.location == 'all':
    # all locations
    for location in flusurv.location_codes.keys():
      update(location, args.test)
  else:
    # single location
    update(args.location, args.test)


if __name__ == '__main__':
  main()
