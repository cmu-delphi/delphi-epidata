"""
===============
=== Purpose ===
===============

Wrapper for the entire wiki data collection process:
  1. Uses wiki_update.py to fetch metadata for new access logs
  2. Uses wiki_download.py to download the access logs
  3. Uses wiki_extract.py to store article access counts

See also: master.php


=======================
=== Data Dictionary ===
=======================

`wiki_raw` is a staging table where extracted access log data is stored for
further processing. When wiki_update.py finds a new log, it saves the name and
hash to this table, with a status of 0. This table is read by master.php, which
then hands out "jobs" (independently and in parallel) to wiki_download.py.
After wiki_download.py downloads the log and extracts the counts, it submits
the data (as JSON) to master.php, which then stores the "raw" JSON counts in
this table.
+----------+---------------+------+-----+---------+----------------+
| Field    | Type          | Null | Key | Default | Extra          |
+----------+---------------+------+-----+---------+----------------+
| id       | int(11)       | NO   | PRI | NULL    | auto_increment |
| name     | varchar(64)   | NO   | UNI | NULL    |                |
| hash     | char(32)      | NO   |     | NULL    |                |
| status   | int(11)       | NO   | MUL | 0       |                |
| size     | int(11)       | YES  |     | NULL    |                |
| datetime | datetime      | YES  |     | NULL    |                |
| worker   | varchar(256)  | YES  |     | NULL    |                |
| elapsed  | float         | YES  |     | NULL    |                |
| data     | varchar(2048) | YES  |     | NULL    |                |
+----------+---------------+------+-----+---------+----------------+
id: unique identifier for each record
name: name of the access log
hash: md5 hash of the file, as reported by the dumps site (all zeroes if no
  hash is provided)
status: the status of the job, using the following values:
  0: queued for download
  1: download in progress
  2: queued for extraction
  3: extracted to `wiki` table
  (any negative value indicates failure)
size: the size, in bytes, of the downloaded file
datetime: the timestamp of the most recent status update
worker: name (user@hostname) of the machine working on the job
elapsed: time, in seconds, taken to complete the job
data: a JSON string containing counts for selected articles in the access log

`wiki` is the table where access counts are stored (parsed from wiki_raw). The
"raw" JSON counts are parsed by wiki_extract.py and stored directly in this
table.
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| datetime | datetime    | NO   | MUL | NULL    |                |
| article  | varchar(64) | NO   | MUL | NULL    |                |
| count    | int(11)     | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
id: unique identifier for each record
datetime: UTC timestamp (rounded to the nearest hour) of article access
article: name of the article
count: number of times the article was accessed in the hour

`wiki_meta` is a metadata table for this dataset. It contains pre-calculated
date and epiweeks fields, and more importantly, the total number of English
article hits (denominator) for each `datetime` in the `wiki` table. This table
is populated in parallel with `wiki` by the wiki_extract.py script.
+----------+----------+------+-----+---------+----------------+
| Field    | Type     | Null | Key | Default | Extra          |
+----------+----------+------+-----+---------+----------------+
| id       | int(11)  | NO   | PRI | NULL    | auto_increment |
| datetime | datetime | NO   | UNI | NULL    |                |
| date     | date     | NO   |     | NULL    |                |
| epiweek  | int(11)  | NO   |     | NULL    |                |
| total    | int(11)  | NO   |     | NULL    |                |
+----------+----------+------+-----+---------+----------------+
id: unique identifier for each record
datetime: UTC timestamp (rounded to the nearest hour) of article access
date: the date portion of `datetime`
epiweek: the year and week containing `datetime`
total: total number of English article hits in the hour


=================
=== Changelog ===
=================

2017-02-24
  * secrets and small improvements
2016-08-14
  * Increased job limit (6 -> 12) (pageviews files are ~2x smaller)
2015-08-26
  * Reduced job limit (8 -> 6)
2015-08-14
  * Reduced job limit (10 -> 8)
2015-08-11
  + New table `wiki_meta`
2015-05-22
  * Updated status codes for `wiki_raw` table
2015-05-21
  * Original version
"""

# first party
import wiki_update
import wiki_download
import wiki_extract
import secrets


def main():
  # step 1: find new access logs (aka "jobs")
  print('looking for new jobs...')
  try:
    wiki_update.run()
  except:
    print('wiki_update failed')

  # step 2: run a few jobs
  print('running jobs...')
  try:
    wiki_download.run(
      secrets.wiki.hmac,
      download_limit=1024 * 1024 * 1024,
      job_limit=12
    )
  except:
    print('wiki_download failed')

  # step 3: extract counts from the staging data
  print('extracting counts...')
  try:
    wiki_extract.run(job_limit=100)
  except:
    print('wiki_extract failed')


if __name__ == '__main__':
  main()
