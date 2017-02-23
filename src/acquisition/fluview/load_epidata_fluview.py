"""
===============
=== Purpose ===
===============

Stores CDC's fluview data (wILI in particular), preserving changes due to
backfill.


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
region: the name of the HHS region ('nat', 'hhs<#>', 'cen<#>')
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


=================
=== Changelog ===
=================

2017-02-22
  * use secrets
2016-03-25
  + support census regions
  * fixed age columns (see errata)
2015-10-14
  * updated for CDC's new file format (changed column ordering)
  * CRLF to LF
2015-08-04
  + fixed negative `lag` (`epiweek` and `issue` were swapped)
2015-06-23
  + new column `lag` (number of weeks between `epiweek` and `issue`)
2015-06-01
  * Reworked the `fluview` table
  * Column name, type, order, and NULL changes
  - Removed erroneous unique key over (`region`,`year`,`epiweek`,`wili`)
  + Loaded 2009-2015 in-season backfill data recently provided by the CDC
  + Reloaded scraped data from 2014w01 to present
  * Using 'epi' DB user
  * Using max float precision instead of rounding to 3 decimal places
2014-??-??
  * Original version


==============
=== Errata ===
==============

Age columns
-----------
On 2016-03-25 I decided to add in the nine census regions. Upon verifying that
the ILINet census file had the same layout as the National and HHS files, I
discovered that age columns 1 and 3 were transposed. I suspected that it
happened when CDC changed the column layout at the start of the 2015--2016
season. I was able to confirm this by checking the database for the age counts
on the same epiweek and location before and after the update:

> select * from fluview where region = 'nat' and epiweek = 201530 and issue in (201538, 201539);

Luckily, the fix was pretty easy because (1) only rows updated after 2015-10-09
were affected, and (2) `num_age_2` is NULL in all these rows, giving me an easy
way to swap the values between `num_age_1` and `num_age_3`. I could have used
the in-place XOR trick, but I'm not that brave with the `fluview` table. Here's
what I did:

> update fluview set num_age_2 = num_age_3 where release_date >= '2015-10-09';
> update fluview set num_age_3 = num_age_1 where release_date >= '2015-10-09';
> update fluview set num_age_1 = num_age_2 where release_date >= '2015-10-09';
> update fluview set num_age_2 = null where release_date >= '2015-10-09';
"""

# standard library
import argparse
import csv
import os
import re
# third party
import mysql.connector
# first party
from epiweek import delta_epiweeks
import secrets

# args and usage
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_const', const=True, help="show debugging output")
parser.add_argument('-t', '--test', action='store_const', const=True, help="do dry run only, don't update the database")
parser.add_argument('file', help="the file to load")
args = parser.parse_args()
args_path, args_file = os.path.split(args.file)

census_num = {
  'New England': 1,
  'Mid-Atlantic': 2,
  'East North Central': 3,
  'West North Central': 4,
  'South Atlantic': 5,
  'East South Central': 6,
  'West South Central': 7,
  'Mountain': 8,
  'Pacific': 9,
}

def get_int(x):
  try:
    return int(x)
  except:
    return None

def get_float(x):
  try:
    return float(x)
  except:
    return None

def to_string(values):
  out = []
  for v in values:
    if v is None:
      out.append('NULL')
    elif isinstance(v, int):
      out.append(str(v))
    elif isinstance(v, float):
      out.append(str(v))
    else:
      out.append('\'%s\''%(str(v)))
  return out

def parse_fluview(file):
  data = []
  with open(file) as f:
    reader = csv.reader(f)
    for row in reader:
      if(len(row) < 15):
        continue
      region = row[1]
      if region == 'X':
        region = 'nat'
      elif re.search('Region (\d+)', region) is not None:
        m = re.search('Region (\d+)', region)
        region = 'hhs%s' % m.group(1)
      elif region in census_num:
        region = 'cen%d' % census_num[region]
      else:
        raise Exception('Invalid region: %s' % region)
      year = get_int(row[2])
      epiweek = get_int(row[3])
      num_ili = get_int(row[12])
      num_patients = get_int(row[14])
      num_providers = get_int(row[13])
      wili = get_float(row[4])
      ili = get_float(row[5])
      num_age_0 = get_int(row[6])
      num_age_1 = get_int(row[9])  # previously [7]
      num_age_2 = get_int(row[8])
      num_age_3 = get_int(row[7])  # previously [9]
      num_age_4 = get_int(row[10])
      num_age_5 = get_int(row[11])
      if wili is not None:
        data.append([year * 100 + epiweek, region, num_ili, num_patients, num_providers, wili, ili, num_age_0, num_age_1, num_age_2, num_age_3, num_age_4, num_age_5])
  return data

def get_file(filename):
  match = re.search('ili_\S+_(\d{4})-(\d{2})-(\d{2})-(\d{2})\.csv', filename)
  if match is None:
    raise Exception('file name format not recognized')
  year = int(match.group(1))
  month = int(match.group(2))
  day = int(match.group(3))
  hour = int(match.group(4))
  return (match.group(0), year, month, day, hour)

def get_rows(cnx):
  select = cnx.cursor()
  select.execute('SELECT count(1) num FROM fluview')
  for (num,) in select:
    rows = num
  select.close()
  return rows

# database connection
u, p = secrets.db.epi
cnx = mysql.connector.connect(user=u, password=p, database='epidata')
rows1 = get_rows(cnx)
print('rows before: %d'%(rows1))
insert = cnx.cursor()

# load the file
path = args_path
fname, fyear, fmonth, fday, fhour = get_file(args_file)
print(fname)
data = parse_fluview('%s/%s'%(path, fname))
for row in data:
  issue, epiweek, region, num_ili, num_patients, num_providers, wili, ili, num_age_0, num_age_1, num_age_2, num_age_3, num_age_4, num_age_5 = to_string([data[-1][0]] + row)
  lag = delta_epiweeks(int(epiweek), int(issue))
  date_string = "'%04d-%02d-%02d'"%(fyear, fmonth, fday)
  sql = '''
  INSERT INTO `fluview` (`release_date`, `issue`, `epiweek`, `region`, `lag`, `num_ili`, `num_patients`, `num_providers`, `wili`, `ili`, `num_age_0`, `num_age_1`, `num_age_2`, `num_age_3`, `num_age_4`, `num_age_5`)
  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
  ON DUPLICATE KEY UPDATE
  `release_date` = least(`release_date`, %s), `num_ili` = %s, `num_patients` = %s, `num_providers` = %s, `wili` = %s, `ili` = %s, `num_age_0` = %s, `num_age_1` = %s, `num_age_2` = coalesce(%s, `num_age_2`), `num_age_3` = coalesce(%s, `num_age_3`), `num_age_4` = coalesce(%s, `num_age_4`), `num_age_5` = %s
  '''%(date_string, issue, epiweek, region, lag, num_ili, num_patients, num_providers, wili, ili, num_age_0, num_age_1, num_age_2, num_age_3, num_age_4, num_age_5, date_string, num_ili, num_patients, num_providers, wili, ili, num_age_0, num_age_1, num_age_2, num_age_3, num_age_4, num_age_5)
  if args.verbose:
    print(sql)
  if not args.test:
    #try:
    insert.execute(sql)
    #except mysql.connector.errors.IntegrityError:
    #  pass

# cleanup
cnx.commit()
insert.close()
rows2 = get_rows(cnx)
print('rows after: %d (added %d)'%(rows2, rows2 - rows1))
cnx.close()
