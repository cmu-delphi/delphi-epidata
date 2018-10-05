"""
===============
=== Purpose ===
===============

Stores versioned ILINet data from CDC's FluView app.

Note that the ILINet age groups are not exactly the same as the flusurv age
groups. See flusurv.py for more details.

This file replaces load_epidata_fluview.py, which performed a similar function
for the old (pre 2017w40) FluView interface.

See also:
  - fluview.py
  - fluview_locations.py
  - flusurv.py
  - load_epidata_fluview.py


=======================
=== Data Dictionary ===
=======================

`fluview` is the table where the ILI data from the CDC is stored.
+---------------+-------------+------+-----+---------+----------------+
| Field         | Type        | Null | Key | Default | Extra          |
+---------------+-------------+------+-----+---------+----------------+
| id            | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date  | date        | NO   | MUL | NULL    |                |
| issue         | int(11)     | NO   | MUL | NULL    |                |
| epiweek       | int(11)     | NO   | MUL | NULL    |                |
| region        | varchar(12) | NO   | MUL | NULL    |                |
| lag           | int(11)     | NO   | MUL | NULL    |                |
| num_ili       | int(11)     | NO   |     | NULL    |                |
| num_patients  | int(11)     | NO   |     | NULL    |                |
| num_providers | int(11)     | NO   |     | NULL    |                |
| wili          | double      | NO   |     | NULL    |                |
| ili           | double      | NO   |     | NULL    |                |
| num_age_0     | int(11)     | YES  |     | NULL    |                |
| num_age_1     | int(11)     | YES  |     | NULL    |                |
| num_age_2     | int(11)     | YES  |     | NULL    |                |
| num_age_3     | int(11)     | YES  |     | NULL    |                |
| num_age_4     | int(11)     | YES  |     | NULL    |                |
| num_age_5     | int(11)     | YES  |     | NULL    |                |
+---------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
release_date: the date when this record was first published by the CDC
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
  and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
region: the name of the location (e.g. 'nat', 'hhs1', 'cen9', 'pa', 'jfk')
lag: number of weeks between `epiweek` and `issue`
num_ili: the number of ILI cases (numerator)
num_patients: the total number of patients (denominator)
num_providers: the number of reporting healthcare providers
wili: weighted percent ILI
ili: unweighted percent ILI
num_age_0: number of cases in ages 0-4
num_age_1: number of cases in ages 5-24
num_age_2: number of cases in ages 25-64
num_age_3: number of cases in ages 25-49
num_age_4: number of cases in ages 50-64
num_age_5: number of cases in ages 65+

`fluview_clinical` is the table that contains data from clinical labs.
+-----------------+-------------+------+-----+---------+----------------+
| Field           | Type        | Null | Key | Default | Extra          |
+-----------------+-------------+------+-----+---------+----------------+
| id              | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date    | date        | NO   | MUL | NULL    |                |
| issue           | int(11)     | NO   | MUL | NULL    |                |
| epiweek         | int(11)     | NO   | MUL | NULL    |                |
| region          | varchar(12) | NO   | MUL | NULL    |                |
| lag             | int(11)     | NO   | MUL | NULL    |                |
| total_specimens | int(11)     | NO   |     | NULL    |                |
| total_a         | int(11)     | YES  |     | NULL    |                |
| total_b         | int(11)     | YES  |     | NULL    |                |
+-----------------+-------------+------+-----+---------+----------------+
similar to fluview table. data taken right from the WHO_NREVSS dataset.

`fluview_public` is the table that contains data from pubic health labs.
+-----------------+-------------+------+-----+---------+----------------+
| Field           | Type        | Null | Key | Default | Extra          |
+-----------------+-------------+------+-----+---------+----------------+
| id              | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date    | date        | NO   | MUL | NULL    |                |
| issue           | int(11)     | NO   | MUL | NULL    |                |
| season          | varchar(12) | NO   | MUL | NULL    |                |
| region          | varchar(12) | NO   | MUL | NULL    |                |
| total_specimens | int(11)     | NO   |     | NULL    |                |
| total_a_h1n1    | int(11)     | YES  |     | NULL    |                |
| total_a_h3      | int(11)     | YES  |     | NULL    |                |
| total_a_no_sub  | int(11)     | YES  |     | NULL    |                |
| total_b         | int(11)     | YES  |     | NULL    |                |
| total_b_vic     | int(11)     | YES  |     | NULL    |                |
| total_b_yam     | int(11)     | YES  |     | NULL    |                |
| total_h3n2v     | int(11)     | YES  |     | NULL    |                |
+-----------------+-------------+------+-----+---------+----------------+
similar to fluview table. data taken right from the WHO_NREVSS dataset.

Changelog:
- 10/05/18: add/modify functions to also process clinical lab and public 
  health lab data.
"""

# standard library
import argparse
import csv
import datetime
import io
import os
import re
import zipfile

# third party
import mysql.connector

# first party
from . import fluview
from . import fluview_locations
import delphi.operations.secrets as secrets
from delphi.utils.epiweek import delta_epiweeks, join_epiweek

# sheet names
ILINET_SHEET = 'ILINet.csv'
PHL_SHEET = 'WHO_NREVSS_Public_Health_Labs.csv'
CL_SHEET = 'WHO_NREVSS_Clinical_Labs.csv'
# table names
CL_TABLE = 'fluview_clinical'
PHL_TABLE = 'fluview_public'

def optional_int(i):
  return int(i) if i not in ('', 'X') else None


def optional_float(i, j):
  return float(i) if i not in ('', 'X') else float(j)


def get_ilinet_data(row):
  if row[0] == 'REGION TYPE' and row != [
    'REGION TYPE',
    'REGION',
    'YEAR',
    'WEEK',
    '% WEIGHTED ILI',
    '%UNWEIGHTED ILI',
    'AGE 0-4',
    'AGE 25-49',
    'AGE 25-64',
    'AGE 5-24',
    'AGE 50-64',
    'AGE 65',
    'ILITOTAL',
    'NUM. OF PROVIDERS',
    'TOTAL PATIENTS'
  ]:
    raise Exception('header row has changed')
  if len(row) == 1 or row[0] == 'REGION TYPE':
    # this is a header row
    return None
  if row[5] == 'X':
    # ILI isn't reported, ignore this row
    return None
  return {
    'location': fluview_locations.get_location_name(*row[:2]),
    'epiweek': join_epiweek(int(row[2]), int(row[3])),
    'wili': optional_float(*row[4:6]),
    'ili': float(row[5]),
    'age0': optional_int(row[6]),
    'age1': optional_int(row[9]),
    'age2': optional_int(row[8]),
    'age3': optional_int(row[7]),
    'age4': optional_int(row[10]),
    'age5': optional_int(row[11]),
    'n_ili': optional_int(row[12]),
    'n_providers': optional_int(row[13]),
    'n_patients': optional_int(row[14]),
  }

def get_clinical_data(row):
  if row[0] == 'REGION TYPE' and row != [
    'REGION TYPE', 
    'REGION', 
    'YEAR', 
    'WEEK', 
    'TOTAL SPECIMENS', 
    'TOTAL A',
    'TOTAL B', 
    'PERCENT POSITIVE', 
    'PERCENT A', 
    'PERCENT B'
  ]:
    raise Exception('header row has changed for clinical lab data.')
  if len(row) == 1 or row[0] == 'REGION TYPE':
    # this is a header row
    return None
  if row[4] == 'X':
    # data is not reported, ignore this row
    return None
  # ignore percentage calculations for now
  return {
    'location': fluview_locations.get_location_name(*row[:2]),
    'epiweek': join_epiweek(int(row[2]), int(row[3])),
    'total_specimens': int(row[4]),
    'total_a': optional_int(row[5]),
    'total_b': optional_int(row[6])
  }

def get_public_data(row):
  if row[0] == 'REGION TYPE' and row != [
    'REGION TYPE', 
    'REGION', 
    'SEASON_DESCRIPTION', 
    'TOTAL SPECIMENS',
    'A (2009 H1N1)', 
    'A (H3)', 
    'A (Subtyping not Performed)', 
    'B', 
    'BVic',
    'BYam', 
    'H3N2v'
  ]:
    raise Exception('header row has changed for public health lab data.')
  if len(row) == 1 or row[0] == 'REGION TYPE':
    # header row
    return None
  if row[3] == 'X':
    # data is not reported, ignore this row
    return None 
  return {
    'location': fluview_locations.get_location_name(*row[:2]),
    'season': row[2],
    'total_specimens': int(row[3]),
    'total_a_h1n1': optional_int(row[4]),
    'total_a_h3': optional_int(row[5]),
    'total_a_no_sub': optional_int(row[6]),
    'total_b': optional_int(row[7]),
    'total_b_vic': optional_int(row[8]),
    'total_b_yam': optional_int(row[9]),
    'total_h3n2v': optional_int(row[10])
  }

def load_zipped_csv(filename, sheetname='ILINet.csv'):
  """Read rows from a zipped CSV, which is expected to be named as specified
  by the sheetname parameter. Default is ILINet.csv, for the default flu data."""
  with zipfile.ZipFile(filename) as f:
    with f.open(sheetname) as ff:
      return [row for row in csv.reader(io.StringIO(str(ff.read(), 'utf-8')))]

def get_rows(cnx, table='fluview'):
  """Count and return the number of rows in the `fluview` table."""
  select = cnx.cursor()
  select.execute('SELECT count(1) num FROM %s' % table)
  for (num,) in select:
    pass
  select.close()
  return num

def update_from_file_clinical(issue, date, filename, test_mode=False):
  """
  Read ILINet data from a zipped CSV and insert into (or update) the database.
  """

  # database connection
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  rows1 = get_rows(cnx, CL_TABLE)
  print('rows before: %d' % (rows1))
  insert = cnx.cursor()

  # load the data, ignoring empty rows
  print('loading data from %s as issued on %d' % (filename, issue))
  rows = load_zipped_csv(filename, CL_SHEET)
  print(' loaded %d rows' % len(rows))
  data = [get_clinical_data(row) for row in rows]
  entries = [obj for obj in data if obj]
  print(' found %d entries' % len(entries))

  sql = '''
  INSERT INTO
    `fluview_clinical` (`release_date`, `issue`, `epiweek`, `region`, `lag`, 
    `total_specimens`, `total_a`, `total_b`)
  VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
  ON DUPLICATE KEY UPDATE
  `release_date` = least(`release_date`, %s),
  `total_specimens` = %s,
  `total_a` = %s,
  `total_b` = %s
  '''

  # insert each row
  insert = cnx.cursor()
  for row in entries:
    lag = delta_epiweeks(row['epiweek'], issue)
    args = [
      row['total_specimens'], row['total_a'], row['total_b']
    ]
    ins_args = [date, issue, row['epiweek'], row['location'], lag] + args
    upd_args = [date] + args
    insert.execute(sql, ins_args + upd_args)

  # cleanup
  insert.close()
  if test_mode:
    print('test mode, not committing')
    rows2 = rows1
  else:
    cnx.commit()
    rows2 = get_rows(cnx)
  print('rows after: %d (added %d)' % (rows2, rows2 - rows1))
  cnx.close()

def update_from_file_public(issue, date, filename, test_mode=False):
  """
  Read ILINet data from a zipped CSV and insert into (or update) the database.
  """

  # database connection
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  rows1 = get_rows(cnx, PHL_TABLE)
  print('rows before: %d' % (rows1))
  insert = cnx.cursor()

  # load the data, ignoring empty rows
  print('loading data from %s as issued on %d' % (filename, issue))
  rows = load_zipped_csv(filename, PHL_SHEET)
  print(' loaded %d rows' % len(rows))
  data = [get_public_data(row) for row in rows]
  entries = [obj for obj in data if obj]
  print(' found %d entries' % len(entries))

  sql = '''
  INSERT INTO
    `fluview_public` (`release_date`, `issue`, `season`, `region`, 
    `total_specimens`, `total_a_h1n1`, `total_a_h3`, `total_a_no_sub`,
    `total_b`, `total_b_vic`, `total_b_yam`, `total_h3n2v`)
  VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
  ON DUPLICATE KEY UPDATE
  `release_date` = least(`release_date`, %s),
  `total_specimens` = %s,
  `total_a_h1n1` = %s,
  `total_a_h3` = %s,
  `total_a_no_sub` = %s,
  `total_b` = %s,
  `total_b_vic` = %s, 
  `total_b_yam` = %s, 
  `total_h3n2v` = %s
  '''

  # insert each row
  insert = cnx.cursor()
  for row in entries:
    args = [
      row['total_specimens'], row['total_a_h1n1'], row['total_a_h3'],
      row['total_a_no_sub'], row['total_b'], row['total_b_vic'], 
      row['total_b_yam'], row['total_h3n2v']
    ]
    ins_args = [date, issue, row['season'], row['location']] + args
    upd_args = [date] + args
    insert.execute(sql, ins_args + upd_args)

  # cleanup
  insert.close()
  if test_mode:
    print('test mode, not committing')
    rows2 = rows1
  else:
    cnx.commit()
    rows2 = get_rows(cnx)
  print('rows after: %d (added %d)' % (rows2, rows2 - rows1))
  cnx.close()

def update_from_file(issue, date, filename, test_mode=False):
  """
  Read ILINet data from a zipped CSV and insert into (or update) the database.
  """

  # database connection
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  rows1 = get_rows(cnx)
  print('rows before: %d' % (rows1))
  insert = cnx.cursor()

  # load the data, ignoring empty rows
  print('loading data from %s as issued on %d' % (filename, issue))
  rows = load_zipped_csv(filename)
  print(' loaded %d rows' % len(rows))
  data = [get_ilinet_data(row) for row in rows]
  entries = [obj for obj in data if obj]
  print(' found %d entries' % len(entries))

  sql = '''
  INSERT INTO
    `fluview` (`release_date`, `issue`, `epiweek`, `region`, `lag`, `num_ili`,
    `num_patients`, `num_providers`, `wili`, `ili`, `num_age_0`, `num_age_1`,
    `num_age_2`, `num_age_3`, `num_age_4`, `num_age_5`)
  VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
  ON DUPLICATE KEY UPDATE
  `release_date` = least(`release_date`, %s),
  `num_ili` = %s,
  `num_patients` = %s,
  `num_providers` = %s,
  `wili` = %s,
  `ili` = %s,
  `num_age_0` = coalesce(%s, `num_age_0`),
  `num_age_1` = coalesce(%s, `num_age_1`),
  `num_age_2` = coalesce(%s, `num_age_2`),
  `num_age_3` = coalesce(%s, `num_age_3`),
  `num_age_4` = coalesce(%s, `num_age_4`),
  `num_age_5` = coalesce(%s, `num_age_5`)
  '''

  # insert each row
  insert = cnx.cursor()
  for row in entries:
    lag = delta_epiweeks(row['epiweek'], issue)
    args = [
      row['n_ili'], row['n_patients'], row['n_providers'], row['wili'],
      row['ili'], row['age0'], row['age1'], row['age2'], row['age3'],
      row['age4'], row['age5']
    ]
    ins_args = [date, issue, row['epiweek'], row['location'], lag] + args
    upd_args = [date] + args
    insert.execute(sql, ins_args + upd_args)

  # cleanup
  insert.close()
  if test_mode:
    print('test mode, not committing')
    rows2 = rows1
  else:
    cnx.commit()
    rows2 = get_rows(cnx)
  print('rows after: %d (added %d)' % (rows2, rows2 - rows1))
  cnx.close()

def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--test',
    action='store_true',
    help='do dry run only, do not update the database'
  )
  parser.add_argument(
    '--file',
    type=str,
    help='load an existing zip file (otherwise fetch current data)'
  )
  parser.add_argument(
    '--issue',
    type=int,
    help='issue of the file (e.g. 201740); used iff --file is given'
  )
  parser.add_argument(
    '--clinical',
    action='store_true',
    help='update data from clinical labs'
  )
  parser.add_argument(
    '--public',
    action='store_true',
    help='update data from public health labs'
  )
  args = parser.parse_args()

  if (args.file is None) != (args.issue is None):
    raise Exception('--file and --issue must both be present or absent')

  date = datetime.datetime.now().strftime('%Y-%m-%d')
  print('assuming release date is today, %s' % date)

  if args.file:
    update_from_file(args.issue, date, args.file, test_mode=args.test)
    update_from_file_clinical(args.issue, date, args.file, test_mode=args.test)
    update_from_file_public(args.issue, date, args.file, test_mode=args.test)
  else:
    issue, files = fluview.save_latest(path='flu_data')
    for filename in files:
      update_from_file(issue, date, filename, test_mode=args.test)
      update_from_file_clinical(issue, date, filename, test_mode=args.test)
      update_from_file_public(issue, date, filename, test_mode=args.test)

if __name__ == '__main__':
  main()
