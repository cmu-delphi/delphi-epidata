"""
===============
=== Purpose ===
===============

Extract a useful subset of the CDC data. Reads from `cdc` and `cdc_meta` (all
pages, and daily resolution) and writes to `cdc_extract` (selected pages, and
weekly resolution). The Epidata API is then used to read from `cdc_extract` and
update the `sensors` and `nowcasts` tables.

This is necessary because the `cdc` table is huge, and string matching is slow.
If runtime was not an issue, everything could (in theory) be done in pure SQL
using just the `cdc` and `cdc_meta` tables.

A similar preprocessing step is performed for the wikipedia dataset in
signal_update.py.


=======================
=== Data Dictionary ===
=======================

`cdc_extract` is the table where the data is stored.
+---------+---------+------+-----+---------+----------------+
| Field   | Type    | Null | Key | Default | Extra          |
+---------+---------+------+-----+---------+----------------+
| id      | int(11) | NO   | PRI | NULL    | auto_increment |
| epiweek | int(11) | NO   | MUL | NULL    |                |
| state   | char(2) | NO   | MUL | NULL    |                |
| num1    | int(11) | NO   |     | NULL    |                |
| num2    | int(11) | NO   |     | NULL    |                |
| num3    | int(11) | NO   |     | NULL    |                |
| num4    | int(11) | NO   |     | NULL    |                |
| num5    | int(11) | NO   |     | NULL    |                |
| num6    | int(11) | NO   |     | NULL    |                |
| num7    | int(11) | NO   |     | NULL    |                |
| num8    | int(11) | NO   |     | NULL    |                |
| total   | int(11) | NO   |     | NULL    |                |
+---------+---------+------+-----+---------+----------------+
id: unique identifier for each record
epiweek: the epiweek during which the data was collected
state: where the data was collected (51 states, including DC)
num1: hits for pages like '%What You Should Know for the % Influenza Season%'
num2: hits for pages like '%What To Do If You Get Sick%'
num3: hits for pages like '%Flu Symptoms & Severity%'
num4: hits for pages like '%How Flu Spreads%'
num5: hits for pages like '%What You Should Know About Flu Antiviral Drugs%'
num6: hits for pages like '%Weekly US Map%'
num7: hits for pages like '%Basics%'
num8: hits for pages like '%Flu Activity & Surveillance%'
total: total number of hits for all CDC pages


=================
=== Changelog ===
=================

2017-02-23
  * secrets and minor cleanup
2016-04-16
  + initial version
"""

# standard library
import argparse
import sys
# third party
import mysql.connector
import numpy as np
# first party
import cdc_upload
from epidate import EpiDate
import epiweek as flu
import secrets


def get_num_hits(cur, epiweek, state, page):
  sql = '''
    SELECT
      sum(c.`num`) `num`
    FROM
      `cdc` c
    JOIN
      `cdc_meta` m
    ON
      m.`date` = c.`date` AND m.`state` = c.`state`
    WHERE
      m.`epiweek` = %s AND c.`state` = %s AND c.`page` LIKE %s
  '''
  num = None
  cur.execute(sql, (epiweek, state, page))
  for (num,) in cur:
    pass
  if num is None:
    return 0
  else:
    return num


def get_total_hits(cur, epiweek, state):
  sql = '''
    SELECT
      sum(m.`total`) `total`
    FROM
      `cdc_meta` m
    WHERE
      m.`epiweek` = %s AND m.`state` = %s
  '''
  total = None
  cur.execute(sql, (epiweek, state))
  for (total,) in cur:
    pass
  if total is None:
    raise Exception('missing data for %d-%s' % (epiweek, state))
  else:
    return total


def store_result(cur, epiweek, state, num1, num2, num3, num4, num5, num6, num7, num8, total):
  sql = '''
    INSERT INTO
      `cdc_extract` (`epiweek`, `state`, `num1`, `num2`, `num3`, `num4`, `num5`, `num6`, `num7`, `num8`, `total`)
    VALUES
      (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      `num1` = %s,
      `num2` = %s,
      `num3` = %s,
      `num4` = %s,
      `num5` = %s,
      `num6` = %s,
      `num7` = %s,
      `num8` = %s,
      `total` = %s
  '''
  values = [num1, num2, num3, num4, num5, num6, num7, num8, total]
  args = tuple([epiweek, state] + values + values)
  cur.execute(sql, args)


def extract(first_week=None, last_week=None, test_mode=False):
  # page title templates
  pages = [
    '%What You Should Know for the % Influenza Season%',
    '%What To Do If You Get Sick%',
    '%Flu Symptoms & Severity%',
    '%How Flu Spreads%',
    '%What You Should Know About Flu Antiviral Drugs%',
    '%Weekly US Map%',
    '%Basics%',
    '%Flu Activity & Surveillance%',
  ]

  # location information
  states = sorted(cdc_upload.STATES.values())

  # connect
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  # weeks to update
  if first_week is None:
    cur.execute('SELECT max(`epiweek`) FROM `cdc_extract`')
    for (first_week,) in cur:
      pass
  if last_week is None:
    cur.execute('SELECT max(`epiweek`) FROM `cdc_meta`')
    for (last_week,) in cur:
      pass
  print('extracting %d--%d' % (first_week, last_week))

  # update each epiweek
  for epiweek in flu.range_epiweeks(first_week, last_week, inclusive=True):
    # update each state
    for state in states:
      try:
        num1 = get_num_hits(cur, epiweek, state, pages[0])
        num2 = get_num_hits(cur, epiweek, state, pages[1])
        num3 = get_num_hits(cur, epiweek, state, pages[2])
        num4 = get_num_hits(cur, epiweek, state, pages[3])
        num5 = get_num_hits(cur, epiweek, state, pages[4])
        num6 = get_num_hits(cur, epiweek, state, pages[5])
        num7 = get_num_hits(cur, epiweek, state, pages[6])
        num8 = get_num_hits(cur, epiweek, state, pages[7])
        total = get_total_hits(cur, epiweek, state)
        store_result(cur, epiweek, state, num1, num2, num3, num4, num5, num6, num7, num8, total)
        print(' %d-%s: %d %d %d %d %d %d %d %d (%d)' % (epiweek, state, num1, num2, num3, num4, num5, num6, num7, num8, total))
      except Exception as ex:
        print(' %d-%s: failed' % (epiweek, state), ex)
        #raise ex
      sys.stdout.flush()

  # disconnect
  cur.close()
  if not test_mode:
    cnx.commit()
  cnx.close()


def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('--first', '-f', default=None, type=int, help='first epiweek override')
  parser.add_argument('--last', '-l', default=None, type=int, help='last epiweek override')
  parser.add_argument('--epiweek', '-w', default=None, type=int, help='epiweek override')
  parser.add_argument('--test', '-t', default=False, action='store_true', help='dry run only')
  args = parser.parse_args()

  # sanity check
  first, last, week = args.first, args.last, args.epiweek
  for ew in [first, last, week]:
    if ew is not None:
      flu.check_epiweek(ew)
  if first is not None and last is not None and first > last:
    raise Exception('epiweeks in the wrong order')
  if week is not None:
    first = last = week

  # extract the page hits for all states on the specified weeks
  extract(first, last, args.test)


if __name__ == '__main__':
  main()
