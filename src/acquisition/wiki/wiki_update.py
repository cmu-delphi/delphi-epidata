"""
===============
=== Purpose ===
===============

Fetches and stores metadata for new wiki access logs

See also: wiki.py


=================
=== Changelog ===
=================

2017-02-23
  * secrets and minor cleanup
2016-08-14
  * use pageviews instead of pagecounts-raw
2015-05-21
  * Original version
"""

# standard library
from datetime import datetime, timedelta
# third party
import mysql.connector
import requests
# first party
import secrets


def floor_timestamp(timestamp):
  return datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)


def ceil_timestamp(timestamp):
  return floor_timestamp(timestamp) + timedelta(hours=1)


def round_timestamp(timestamp):
  before = floor_timestamp(timestamp)
  after = ceil_timestamp(timestamp)
  if (timestamp - before) < (after - timestamp):
    return before
  else:
    return after


def get_timestamp(name):
  # new parsing for pageviews compared to pagecounts - maybe switch to regex in the future
  #return datetime(int(name[11:15]), int(name[15:17]), int(name[17:19]), int(name[20:22]), int(name[22:24]), int(name[24:26]))
  return datetime(int(name[10:14]), int(name[14:16]), int(name[16:18]), int(name[19:21]), int(name[21:23]), int(name[23:25]))


def get_manifest(year, month, optional=False):
  # unlike pagecounts-raw, pageviews doesn't provide hashes
  #url = 'https://dumps.wikimedia.org/other/pagecounts-raw/%d/%d-%02d/md5sums.txt'%(year, year, month)
  url = 'https://dumps.wikimedia.org/other/pageviews/%d/%d-%02d/' % (year, year, month)
  print('Checking manifest at %s...'%(url))
  response = requests.get(url)
  if response.status_code == 200:
    #manifest = [line.strip().split() for line in response.text.split('\n') if 'pagecounts' in line]
    manifest = [('00000000000000000000000000000000', line[9:37]) for line in response.text.split('\n') if '<a href="pageviews-' in line]
  else:
    if optional:
      manifest = []
    else:
      raise Exception('expected 200 status code, but got %d'%(response.status_code))
  print('Found %d access log(s)'%(len(manifest)))
  return manifest


def run():
  # connect to the database
  u, p = secrets.db.epi
  cnx = mysql.connector.connect(user=u, password=p, database='epidata')
  cur = cnx.cursor()

  # get the most recent job in wiki_raw
  # luckily, "pageviews" is lexicographically greater than "pagecounts-raw"
  cur.execute('SELECT max(`name`) FROM `wiki_raw`')
  for (max_name,) in cur:
    pass
  print('Last known file: %s'%(max_name))
  timestamp = get_timestamp(max_name)

  # crawl dumps.wikimedia.org to find more recent access logs
  t1, t2 = floor_timestamp(timestamp), ceil_timestamp(timestamp)
  manifest = get_manifest(t1.year, t1.month, optional=False)
  if t2.month != t1.month:
    manifest += get_manifest(t2.year, t2.month, optional=True)

  # find access logs newer than the most recent job
  new_logs = {}
  for (hash, name) in manifest:
    if name > max_name:
      new_logs[name] = hash
      print(' New job: %s [%s]'%(name, hash))
  print('Found %d new job(s)'%(len(new_logs)))

  # store metadata for new jobs
  for name in sorted(new_logs.keys()):
    cur.execute('INSERT INTO `wiki_raw` (`name`, `hash`) VALUES (%s, %s)', (name, new_logs[name]))

  # cleanup
  cur.close()
  cnx.commit()
  cnx.close()


if __name__ == '__main__':
  run()
