"""
===============
=== Purpose ===
===============

Stores flu and dengue data from Taiwan's National Infectious Disease Statistics
System (NIDSS). Like the updater for the U.S. CDC version, this program keeps
track of changes due to backfill (for flu only).

See also:
 - load_epidata_fluview.py: U.S. CDC version
 - taiwan_nidss.py: An API for scraping the data from the NIDSS site


=======================
=== Data Dictionary ===
=======================

`nidss_flu` is the table where the ILI data from the NIDSS is stored.
+--------------+-------------+------+-----+---------+----------------+
| Field        | Type        | Null | Key | Default | Extra          |
+--------------+-------------+------+-----+---------+----------------+
| id           | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date | date        | NO   | MUL | NULL    |                |
| issue        | int(11)     | NO   | MUL | NULL    |                |
| epiweek      | int(11)     | NO   | MUL | NULL    |                |
| region       | varchar(12) | NO   | MUL | NULL    |                |
| lag          | int(11)     | NO   | MUL | NULL    |                |
| visits       | int(11)     | NO   |     | NULL    |                |
| ili          | double      | NO   |     | NULL    |                |
+--------------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
release_date: the date when this record was first published by the NIDSS
issue: the epiweek of publication (e.g. issue 201453 includes epiweeks up to
 and including 2014w53, but not 2015w01 or following)
epiweek: the epiweek during which the data was collected
region: the name of the region (there are 6, plus 'Nationwide')
lag: number of weeks between `epiweek` and `issue`
visits: the total number of patients with ILI (numerator)
ili: percent ILI (on a 0-100 scale)


`nidss_dengue` is the table where the dengue counts from the NIDSS are stored.
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| location | varchar(32) | NO   | MUL | NULL    |                |
| region   | varchar(12) | NO   | MUL | NULL    |                |
| count    | int(11)     | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
epiweek: the epiweek during which the data was collected
location: the name of the location (there are 22 cities and counties)
region: the name of the region (there are 6, but not 'Nationwide')
count: the number of dengue cases


=================
=== Changelog ===
=================

2017-02-16
 * use secrets
2015-08-20
 + Also storing dengue data
2015-08-10
 * Original version, inspired by load_epidata_fluview.py
"""

# built-in libraries
# external libraries
import mysql.connector
# local libraries
from epiweek import *
from taiwan_nidss import NIDSS
import secrets


# Get a row count just to know how many new rows are inserted
def get_rows(cnx):
  select = cnx.cursor()
  select.execute('SELECT count(1) num FROM nidss_flu')
  for (num,) in select:
    rows_flu = num
  select.execute('SELECT count(1) num FROM nidss_dengue')
  for (num,) in select:
    rows_dengue = num
  select.close()
  return (rows_flu, rows_dengue)

# API initialization
api = NIDSS()
current_week = api.get_latest_week()
release_date = api.get_release_date()

# Database connection
u, p = secrets.db.epi
cnx = mysql.connector.connect(user=u, password=p, database='epidata')
rows1 = get_rows(cnx)
print('rows before (flu): %d' % (rows1[0]))
print('rows before (dengue): %d' % (rows1[1]))
insert = cnx.cursor()
sql_flu = '''
INSERT INTO
  `nidss_flu` (`release_date`, `issue`, `epiweek`, `region`, `lag`, `visits`, `ili`)
VALUES
  (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
  `release_date` = least(`release_date`, %s), `visits` = %s, `ili` = %s
'''
sql_dengue = '''
INSERT INTO
  `nidss_dengue` (`epiweek`, `location`, `region`, `count`)
VALUES
  (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
  `count` =  %s
'''

# Scrape the flu data from the past year
data = api.get_flu_data(add_epiweeks(current_week, -51), current_week)
for epiweek in sorted(list(data.keys())):
  lag = delta_epiweeks(epiweek, current_week)
  for region in data[epiweek].keys():
    visits, ili = data[epiweek][region]['visits'], data[epiweek][region]['ili']
    params1 = [release_date, current_week, epiweek, region, lag, visits, ili]
    params2 = [release_date, visits, ili]
    insert.execute(sql_flu, tuple(params1 + params2))

# Scrape the dengue data from the past year
data = api.get_dengue_data(add_epiweeks(current_week, -51), current_week)
for epiweek in sorted(list(data.keys())):
  for location in sorted(list(data[epiweek].keys())):
    region = NIDSS.LOCATION_TO_REGION[location]
    count = data[epiweek][location]
    params = (epiweek, location, region, count, count)
    insert.execute(sql_dengue, params)

# Cleanup
insert.close()
cnx.commit()
rows2 = get_rows(cnx)
print('rows after (flu): %d (added %d)' % (rows2[0], rows2[0] - rows1[0]))
print('rows after (dengue): %d (added %d)' % (rows2[1], rows2[1] - rows1[1]))
cnx.close()
