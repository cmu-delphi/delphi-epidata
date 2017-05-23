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
from epidate import EpiDate
from epiweek import delta_epiweeks
import flusurv
import secrets


def get_rows(cur):
  """Return the number of rows in the `flusurv` table."""

  # count all rows
  cur.execute('SELECT count(1) `num` FROM `flusurv`')
  for (num,) in cur:
    return num


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
