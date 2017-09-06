"""
===============
=== Purpose ===
===============

Reads zip/csv files from CDC and stores page hit counts in the database.

Files can be uploaded at:
https://delphi.midas.cs.cmu.edu/~automation/public/cdc_upload/

When someone uploads a new file, two things happen:
  1. the uploaded file is moved to /common/cdc_stage
  2. this program is queued to run

This program:
  1. extracts csv file(s)
  2. parses counts from csv file(s)
  3. stores counts in the database (see below)
  4. deletes csv file(s)
  5. moves zip file(s) from staging directory to /home/automation/cdc_page_stats


=======================
=== Data Dictionary ===
=======================

`cdc` is the table where individual page counts are stored.
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| id    | int(11)      | NO   | PRI | NULL    | auto_increment |
| date  | date         | NO   | MUL | NULL    |                |
| page  | varchar(128) | NO   | MUL | NULL    |                |
| state | char(2)      | NO   | MUL | NULL    |                |
| num   | int(11)      | NO   |     | NULL    |                |
+-------+--------------+------+-----+---------+----------------+
id: unique identifier for each record
date: the date when the hits were recorded (maybe by eastern time?)
page: the full page title
state: the state where the page was accessed from (maybe by IP address?)
num: the number of hits for this particular page

`cdc_meta` is the table where total counts are stored.
+---------+---------+------+-----+---------+----------------+
| Field   | Type    | Null | Key | Default | Extra          |
+---------+---------+------+-----+---------+----------------+
| id      | int(11) | NO   | PRI | NULL    | auto_increment |
| date    | date    | NO   | MUL | NULL    |                |
| epiweek | int(11) | NO   | MUL | NULL    |                |
| state   | char(2) | NO   | MUL | NULL    |                |
| total   | int(11) | NO   |     | NULL    |                |
+---------+---------+------+-----+---------+----------------+
id: unique identifier for each record
date: the date when the hits were recorded (maybe by eastern time?)
epiweek: the epiweek corresponding to the date
state: the state where the pages were accessed from (maybe by IP address?)
total: total number of hits for all CDC pages


=================
=== Changelog ===
=================

2017-02-23
  * secrets and minor cleanup
2016-06-11
  * work in automation dir
2016-04-18
  + initial version
"""

# standard library
import argparse
import csv
from datetime import datetime
import glob
import io
import os
import shutil
import sys
from zipfile import ZipFile
# third party
import mysql.connector
# first party
import epiweek as flu
import secrets


STATES = {
  'Alabama': 'AL',
  'Alaska': 'AK',
  'Arizona': 'AZ',
  'Arkansas': 'AR',
  'California': 'CA',
  'Colorado': 'CO',
  'Connecticut': 'CT',
  'Delaware': 'DE',
  'District of Columbia': 'DC',
  'Florida': 'FL',
  'Georgia': 'GA',
  'Hawaii': 'HI',
  'Idaho': 'ID',
  'Illinois': 'IL',
  'Indiana': 'IN',
  'Iowa': 'IA',
  'Kansas': 'KS',
  'Kentucky': 'KY',
  'Louisiana': 'LA',
  'Maine': 'ME',
  'Maryland': 'MD',
  'Massachusetts': 'MA',
  'Michigan': 'MI',
  'Minnesota': 'MN',
  'Mississippi': 'MS',
  'Missouri': 'MO',
  'Montana': 'MT',
  'Nebraska': 'NE',
  'Nevada': 'NV',
  'New Hampshire': 'NH',
  'New Jersey': 'NJ',
  'New Mexico': 'NM',
  'New York': 'NY',
  'North Carolina': 'NC',
  'North Dakota': 'ND',
  'Ohio': 'OH',
  'Oklahoma': 'OK',
  'Oregon': 'OR',
  'Pennsylvania': 'PA',
  'Rhode Island': 'RI',
  'South Carolina': 'SC',
  'South Dakota': 'SD',
  'Tennessee': 'TN',
  'Texas': 'TX',
  'Utah': 'UT',
  'Vermont': 'VT',
  'Virginia': 'VA',
  'Washington': 'WA',
  'West Virginia': 'WV',
  'Wisconsin': 'WI',
  'Wyoming': 'WY',
  #'Puerto Rico': 'PR',
  #'Virgin Islands': 'VI',
  #'Guam': 'GU',
}

sql_cdc = '''
  INSERT INTO
    `cdc` (`date`, `page`, `state`, `num`)
  VALUES
    (%s, %s, %s, %s)
  ON DUPLICATE KEY UPDATE
    `num` = %s
'''

sql_cdc_meta = '''
  INSERT INTO
    `cdc_meta` (`date`, `epiweek`, `state`, `total`)
  VALUES
    (%s, yearweek(%s, 6), %s, %s)
  ON DUPLICATE KEY UPDATE
    `total` = %s
'''


def upload(test_mode):
  # connect
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  # insert (or update) table `cdc`
  def insert_cdc(date, page, state, num):
    cur.execute(sql_cdc, (date, page, state, num, num))

  # insert (or update) table `cdc_meta`
  def insert_cdc_meta(date, state, total):
    cur.execute(sql_cdc_meta, (date, date, state, total, total))

  # loop over rows until the header row is found
  def find_header(reader):
    for row in reader:
      if len(row) > 0 and row[0] == 'Date':
        return True
    return False

  # parse csv files for `cdc` and `cdc_meta`
  def parse_csv(meta):
    def handler(reader):
      if not find_header(reader):
        raise Exception('header not found')
      count = 0
      cols = 3 if meta else 4
      for row in reader:
        if len(row) != cols:
          continue
        if meta:
          (a, c, d) = row
        else:
          (a, b, c, d) = row
        c = c[:-16]
        if c not in STATES:
          continue
        a = datetime.strptime(a, '%b %d, %Y').strftime('%Y-%m-%d')
        c = STATES[c]
        d = int(d)
        if meta:
          insert_cdc_meta(a, c, d)
        else:
          insert_cdc(a, b, c, d)
        count += 1
      return count
    return handler

  # recursively open zip files
  def parse_zip(zf, level=1):
    for name in zf.namelist():
      prefix = ' ' * level
      print(prefix, name)
      if name[-4:] == '.zip':
        with zf.open(name) as temp:
          with ZipFile(io.BytesIO(temp.read())) as zf2:
            parse_zip(zf2, level + 1)
      elif name[-4:] == '.csv':
        handler = None
        if 'Flu Pages by Region' in name:
          handler = parse_csv(False)
        elif 'Regions for all CDC' in name:
          handler = parse_csv(True)
        else:
          print(prefix, ' (skipped)')
        if handler is not None:
          with zf.open(name) as temp:
            count = handler(csv.reader(io.StringIO(str(temp.read(), 'utf-8'))))
          print(prefix, ' %d rows' % count)
      else:
        print(prefix, ' (ignored)')

  # find, parse, and move zip files
  zip_files = glob.glob('/common/cdc_stage/*.zip')
  print('searching...')
  for f in zip_files:
    print(' ', f)
  print('parsing...')
  for f in zip_files:
    with ZipFile(f) as zf:
      parse_zip(zf)
  print('moving...')
  for f in zip_files:
    src = f
    dst = os.path.join('/home/automation/cdc_page_stats/', os.path.basename(src))
    print(' ', src, '->', dst)
    if test_mode:
      print('  (test mode enabled - not moved)')
    else:
      shutil.move(src, dst)
      if not os.path.isfile(dst):
        raise Exception('unable to move file')

  # disconnect
  cur.close()
  if not test_mode:
    cnx.commit()
  cnx.close()


def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('--test', '-t', default=False, action='store_true', help='dry run only')
  args = parser.parse_args()

  # make it happen
  upload(args.test)


if __name__ == '__main__':
  main()
