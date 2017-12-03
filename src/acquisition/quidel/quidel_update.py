'''
===============
=== Purpose ===
===============

Stores data provided by Quidel Corp., which contains flu lab test result.
See: quidel.py


=======================
=== Data Dictionary ===
=======================

`quidel` is the table where quidel data is stored.
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| location | varchar(8)  | NO   | MUL | NULL    |                |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| value    | float       | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
location: hhs1-10
epiweek: the epiweek during which the queries were executed
value: number of total test records per facility, within each epiweek

=================
=== Changelog ===
=================

2017-12-02
  * original version
'''

# standard library
import argparse

# third party
import mysql.connector

# first party
from . import quidel
import delphi.operations.secrets as secrets
from delphi.utils.epidate import EpiDate
import delphi.utils.epiweek as flu

LOCATIONS = ['hhs%d'%i for i in range(1,11)]
DATAPATH = '/quidel_data'

def update(locations, terms, first=None, last=None):
  # connect to the database
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  def get_num_rows():
    cur.execute('SELECT count(1) `num` FROM `quidel`')
    for (num,) in cur:
      pass
    return num

  # check from 4 weeks preceeding the last week with data through this week
  cur.execute('SELECT max(`epiweek`) `ew0`, yearweek(now(), 6) `ew1` FROM `quidel`')
  for (ew0, ew1) in cur:
    ew0 = 200401 if ew0 is None else flu.add_epiweeks(ew0, -4)
  ew0 = ew0 if first is None else first
  ew1 = ew1 if last is None else last
  print('Checking epiweeks between %d and %d...' % (ew0, ew1))

  # keep track of how many rows were added
  rows_before = get_num_rows()

  # check Quidel for new and/or revised data
  sql = '''
    INSERT INTO
      `quidel` (`location`, `epiweek`, `value`)
    VALUES
      (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
      `value` = %s
  '''

  total_rows = 0
  qd = quidel.QuidelData(DATAPATH)
  qd_data = qd.load_csv()
  qd_measurements = qd.prepare_measurements(qd_data,start_weekday=4)
  qd_ts = quidel.measurement_to_ts(qd_measurements,7,startweek=first,endweek=last)

  for location in locations:
    if location not in qd_ts:
      continue
    ews = sorted(qd_ts[location].keys())
    num_missing = 0
    for ew in ews:
      v = qd_ts[location][ew]
      sql_data = (location, ew, v, v)
      cur.execute(sql, sql_data)
      total_rows += 1
      if v == 0:
        num_missing += 1
    if num_missing > 0:
      print(' [%s] missing %d/%d value(s)' % (location, num_missing, len(ews)))

  # keep track of how many rows were added
  rows_after = get_num_rows()
  print('Inserted %d/%d row(s)'%(rows_after - rows_before, total_rows))

  # cleanup
  cur.close()
  cnx.commit()
  cnx.close()


def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('location', action='store', type=str, default=None, help='location(s) (ex: all; any of hhs1-10)')
  parser.add_argument('--first', '-f', default=None, type=int, help='first epiweek override')
  parser.add_argument('--last', '-l', default=None, type=int, help='last epiweek override')
  args = parser.parse_args()

  # sanity check
  first, last = args.first, args.last
  if first is not None:
    flu.check_epiweek(first)
  if last is not None:
    flu.check_epiweek(last)
  if first is not None and last is not None and first > last:
    raise Exception('epiweeks in the wrong order')

  # decide what to update
  if args.location.lower() == 'all':
    locations = LOCATIONS
  else:
    locations = args.location.lower().split(',')

  # run the update
  update(locations, first, last)


if __name__ == '__main__':
  main()
