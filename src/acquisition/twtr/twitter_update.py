'''
===============
=== Purpose ===
===============

Wrapper for the entire twitter data collection process, using healthtweets.py.

The program checks all U.S. states and DC (51) over the following inclusive
date range:
  From: 7 days prior to the most recently stored date
  To: 1 day prior to the actual date at runtime

healthtweets.org sometimes behaves strangely when the date range is very short
(roughly spanning less than a week), so checking the extended range above
serves a dual purpose:
  1. get a successful and predictable response from the website
  2. update the database in case there have been delays (often?) or revisions
    (never?)


=======================
=== Data Dictionary ===
=======================

`twitter` is the table where data from healthtweets.org is stored.
+-------+---------+------+-----+---------+----------------+
| Field | Type    | Null | Key | Default | Extra          |
+-------+---------+------+-----+---------+----------------+
| id    | int(11) | NO   | PRI | NULL    | auto_increment |
| date  | date    | NO   | MUL | NULL    |                |
| state | char(2) | NO   | MUL | NULL    |                |
| num   | int(11) | NO   |     | NULL    |                |
| total | int(11) | NO   |     | NULL    |                |
+-------+---------+------+-----+---------+----------------+
id: unique identifier for each record
date: the date
state: two-letter U.S. state abbreviation
num: the number of flu tweets (numerator)
total: the total number of tweets (denominator)


=================
=== Changelog ===
=================

2017-02-16
  * Use secrets
2015-11-27
  * Small documentation update
2015-05-22
  * Original version
'''

# external libraries
import mysql.connector
# local files
from healthtweets import HealthTweets
import secrets


def run():
  # connect to the database
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  def get_num_rows():
    cur.execute('SELECT count(1) `num` FROM `twitter`')
    for (num,) in cur:
      pass
    return num

  # check from 7 days preceeding the last date with data through yesterday (healthtweets.org 404's if today's date is part of the range)
  cur.execute('SELECT date_sub(max(`date`), INTERVAL 7 DAY) `date1`, date_sub(date(now()), INTERVAL 1 DAY) `date2` FROM `twitter`')
  for (date1, date2) in cur:
    date1, date2 = date1.strftime('%Y-%m-%d'), date2.strftime('%Y-%m-%d')
  print('Checking dates between %s and %s...'%(date1, date2))

  # keep track of how many rows were added
  rows_before = get_num_rows()

  # check healthtweets.org for new and/or revised data
  ht = HealthTweets(*secrets.healthtweets.login)
  sql = 'INSERT INTO `twitter` (`date`, `state`, `num`, `total`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `num` = %s, `total` = %s'
  total_rows = 0
  for state in sorted(HealthTweets.STATE_CODES.keys()):
    values = ht.get_values(state, date1, date2)
    for date in sorted(list(values.keys())):
      sql_data = (date, state, values[date]['num'], values[date]['total'], values[date]['num'], values[date]['total'])
      cur.execute(sql, sql_data)
      total_rows += 1

  # keep track of how many rows were added
  rows_after = get_num_rows()
  print('Inserted %d/%d row(s)'%(rows_after - rows_before, total_rows))

  # cleanup
  cur.close()
  cnx.commit()
  cnx.close()


if __name__ == '__main__':
  run()
