"""
===============
=== Purpose ===
===============

Downloads wiki access logs and stores unprocessed article counts

See also: wiki.py
Note: for maximum portability, this program is compatible with both Python2 and
 Python3 and has no external dependencies (e.g. running on AWS)


=================
=== Changelog ===
=================

2017-02-24 v10
  + compute hmac over returned data
2016-08-14: v9
  * use pageviews instead of pagecounts-raw
2015-08-12: v8
  * Corrected `Influenzalike_illness` to `Influenza-like_illness`
2015-05-21: v7
  * Updated for Python3 and to be directly callable by wiki.py
2015-05-??: v1-v6
  * Original versions
"""

# python 2 and 3
from __future__ import print_function
import sys
if sys.version_info.major == 2:
  # python 2 libraries
  from urllib import urlencode
  from urllib2 import urlopen
else:
  # python 3 libraries
  from urllib.parse import urlencode
  from urllib.request import urlopen

# common libraries
import argparse
import datetime
import hashlib
import hmac
import json
import subprocess
import time


VERSION = 10
MASTER_URL = 'https://delphi.midas.cs.cmu.edu/~automation/public/wiki/master.php'


def text(data_string):
  return str(data_string.decode('utf-8'))


def data(text_string):
  if sys.version_info.major == 2:
    return text_string
  else:
    return bytes(text_string, 'utf-8')


def get_hmac_sha256(key, msg):
  key_bytes, msg_bytes = key.encode('utf-8'), msg.encode('utf-8')
  return hmac.new(key_bytes, msg_bytes, hashlib.sha256).hexdigest()


def run(secret, download_limit=None, job_limit=None, sleep_time=1, job_type=0, debug_mode=False):
  articles = [
    'Influenza_B_virus',
    'Influenza_A_virus',
    'Human_flu',
    'Influenzavirus_C',
    'Oseltamivir',
    'Influenza',
    'Influenzavirus_A',
    'Influenza_A_virus_subtype_H1N1',
    'Zanamivir',
    'Influenza-like_illness',
    'Common_cold',
    'Sore_throat',
    'Flu_season',
    'Chills',
    'Fever',
    'Influenza_A_virus_subtype_H2N2',
    'Swine_influenza',
    'Shivering',
    'Canine_influenza',
    'Influenza_A_virus_subtype_H3N2',
    'Neuraminidase_inhibitor',
    'Influenza_pandemic',
    'Viral_pneumonia',
    'Influenza_prevention',
    'Influenza_A_virus_subtype_H1N2',
    'Rhinorrhea',
    'Orthomyxoviridae',
    'Nasal_congestion',
    'Gastroenteritis',
    'Rimantadine',
    'Paracetamol',
    'Amantadine',
    'Viral_neuraminidase',
    'Headache',
    'Influenza_vaccine',
    'Vomiting',
    'Cough',
    'Influenza_A_virus_subtype_H5N1',
    'Nausea',
    'Avian_influenza',
    'Influenza_A_virus_subtype_H7N9',
    'Influenza_A_virus_subtype_H10N7',
    'Influenza_A_virus_subtype_H9N2',
    'Hemagglutinin_(influenza)',
    'Influenza_A_virus_subtype_H7N7',
    'Fatigue_(medical)',
    'Myalgia',
    'Influenza_A_virus_subtype_H7N3',
    'Malaise',
    'Equine_influenza',
    'Cat_flu',
    'Influenza_A_virus_subtype_H3N8',
    'Antiviral_drugs',
    'Influenza_A_virus_subtype_H7N2',
  ]
  articles = sorted(articles)

  worker = text(subprocess.check_output("echo `whoami`@`hostname`", shell=True)).strip()
  print('this is [%s]'%(worker))
  if debug_mode:
    print('*** running in debug mode ***')

  total_download = 0
  passed_jobs = 0
  failed_jobs = 0
  while (download_limit is None or total_download < download_limit) and (job_limit is None or (passed_jobs + failed_jobs) < job_limit):
    try:
      time_start = datetime.datetime.now()
      req = urlopen(MASTER_URL + '?get=x&type=%s'%(job_type))
      code = req.getcode()
      if code != 200:
        if code == 201:
          print('no jobs available')
          if download_limit is None and job_limit is None:
            time.sleep(60)
            continue
          else:
            print('nothing to do, exiting')
            return
        else:
          raise Exception('server response code (get) was %d'%(code))
      job = json.loads(text(req.readlines()[0]))
      print('received job [%d|%s]'%(job['id'], job['name']))
      # updated parsing for pageviews - maybe use a regex in the future
      #year, month = int(job['name'][11:15]), int(job['name'][15:17])
      year, month = int(job['name'][10:14]), int(job['name'][14:16])
      #print 'year=%d | month=%d'%(year, month)
      url = 'https://dumps.wikimedia.org/other/pageviews/%d/%d-%02d/%s'%(year, year, month, job['name'])
      print('downloading file [%s]...'%(url))
      subprocess.check_call('curl -s %s > raw.gz'%(url), shell=True)
      print('checking file size...')
      size = int(text(subprocess.check_output('ls -l raw.gz | cut -d" " -f 5', shell=True)))
      if debug_mode:
        print(size)
      total_download += size
      if job['hash'] != '00000000000000000000000000000000':
        print('checking hash...')
        out = text(subprocess.check_output('md5sum raw.gz', shell=True))
        result = out[0:32]
        if result != job['hash']:
          raise Exception('wrong hash [expected %s, got %s]'%(job['hash'], result))
        if debug_mode:
          print(result)
      print('decompressing...')
      subprocess.check_call('gunzip -f raw.gz', shell=True)
      #print 'converting case...'
      #subprocess.check_call('cat raw | tr "[:upper:]" "[:lower:]" > raw2', shell=True)
      #subprocess.check_call('rm raw', shell=True)
      subprocess.check_call('mv raw raw2', shell=True)
      print('extracting article counts...')
      counts = {}
      for article in articles:
        if debug_mode:
          print(' %s'%(article))
        out = text(subprocess.check_output('LC_ALL=C grep -a -i "^en %s " raw2 | cat'%(article.lower()), shell=True)).strip()
        count = 0
        if len(out) > 0:
          for line in out.split('\n'):
            fields = line.split()
            if len(fields) != 4:
              print('unexpected article format: [%s]'%(line))
            else:
              count += int(fields[2])
        #print ' %4d %s'%(count, article)
        counts[article.lower()] = count
        if debug_mode:
          print('  %d'%(count))
      print('getting total count...')
      out = text(subprocess.check_output('cat raw2 | LC_ALL=C grep -a -i "^en " | cut -d" " -f 3 | awk \'{s+=$1} END {printf "%.0f", s}\'', shell=True))
      total = int(out)
      if debug_mode:
        print(total)
      counts['total'] = total
      if not debug_mode:
        print('deleting files...')
        subprocess.check_call('rm raw2', shell=True)
      print('saving results...')
      time_stop = datetime.datetime.now()
      result = {
        'id': job['id'],
        'size': size,
        'data': json.dumps(counts),
        'worker': worker,
        'elapsed': (time_stop - time_start).total_seconds(),
      }
      payload = json.dumps(result)
      hmac_str = get_hmac_sha256(secret, payload)
      if debug_mode:
        print(' hmac: %s' % hmac_str)
      post_data = urlencode({'put': payload, 'hmac': hmac_str})
      req = urlopen(MASTER_URL, data=data(post_data))
      code = req.getcode()
      if code != 200:
        raise Exception('server response code (put) was %d'%(code))
      print('done! (dl=%d)'%(total_download))
      passed_jobs += 1
    except Exception as ex:
      print('***** Caught Exception: %s *****'%(str(ex)))
      failed_jobs += 1
      time.sleep(30)
    print('passed=%d | failed=%d | total=%d'%(passed_jobs, failed_jobs, passed_jobs + failed_jobs))
    time.sleep(sleep_time)

  if download_limit is not None and total_download >= download_limit:
    print('download limit has been reached [%d >= %d]'%(total_download, download_limit))
  if job_limit is not None and (passed_jobs + failed_jobs) >= job_limit:
    print('job limit has been reached [%d >= %d]'%(passed_jobs + failed_jobs, job_limit))


def main():
  # version info
  print('version', VERSION)

  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('secret', type=str, help='hmac secret key')
  parser.add_argument('-b', '--blimit', action='store', type=int, default=None, help='download limit, in bytes')
  parser.add_argument('-j', '--jlimit', action='store', type=int, default=None, help='job limit')
  parser.add_argument('-s', '--sleep', action='store', type=int, default=1, help='seconds to sleep between each job')
  parser.add_argument('-t', '--type', action='store', type=int, default=0, help='type of job')
  parser.add_argument('-d', '--debug', action='store_const', const=True, default=False, help='enable debug mode')
  args = parser.parse_args()

  # runtime options
  secret, download_limit, job_limit, sleep_time, job_type, debug_mode = args.secret, args.blimit, args.jlimit, args.sleep, args.type, args.debug

  # run
  run(secret, download_limit, job_limit, sleep_time, job_type, debug_mode)


if __name__ == '__main__':
  main()
