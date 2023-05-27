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
import os
from sys import platform

from . import wiki_util


VERSION = 10
MASTER_URL = "https://delphi.cmu.edu/~automation/public/wiki/master.php"


def text(data_string):
    return str(data_string.decode("utf-8"))


def data(text_string):
    if sys.version_info.major == 2:
        return text_string
    else:
        return bytes(text_string, "utf-8")


def get_hmac_sha256(key, msg):
    key_bytes, msg_bytes = key.encode("utf-8"), msg.encode("utf-8")
    return hmac.new(key_bytes, msg_bytes, hashlib.sha256).hexdigest()


def extract_article_counts(filename, language, articles, debug_mode):
    """
    Support multiple languages ('en' | 'es' | 'pt')
    Running time optimized to O(M), which means only need to scan the whole file once
    :param filename:
    :param language: Different languages such as 'en', 'es', and 'pt'
    :param articles:
    :param debug_mode:
    :return:
    """
    counts = {}
    articles_set = set(map(lambda x: x.lower(), articles))
    total = 0
    with open(filename, "r", encoding="utf8") as f:
        for line in f:
            content = line.strip().split()
            if len(content) != 4:
                print("unexpected article format: {0}".format(line))
                continue
            article_title = content[1].lower()
            article_count = int(content[2])
            if content[0] == language:
                total += article_count
            if content[0] == language and article_title in articles_set:
                if debug_mode:
                    print("Find article {0}: {1}".format(article_title, line))
                counts[article_title] = article_count
    if debug_mode:
        print("Total number of counts for language {0} is {1}".format(language, total))
    counts["total"] = total
    return counts


def extract_article_counts_orig(articles, debug_mode):
    """
    The original method which extracts article counts by shell command grep (only support en articles).
    As it is difficult to deal with other languages (utf-8 encoding), we choose to use python read files.
    Another things is that it is slower to go over the whole file once and once again, the time complexity is O(NM),
    where N is the number of articles and M is the lines in the file
    In our new implementation extract_article_counts(), the time complexity is O(M), and it can cope with utf8 encoding
    :param articles:
    :param debug_mode:
    :return:
    """
    counts = {}
    for article in articles:
        if debug_mode:
            print(" %s" % (article))
        out = text(subprocess.check_output('LC_ALL=C grep -a -i "^en %s " raw2 | cat' % (article.lower()), shell=True)).strip()
        count = 0
        if len(out) > 0:
            for line in out.split("\n"):
                fields = line.split()
                if len(fields) != 4:
                    print("unexpected article format: [%s]" % (line))
                else:
                    count += int(fields[2])
        # print ' %4d %s'%(count, article)
        counts[article.lower()] = count
        if debug_mode:
            print("  %d" % (count))
    print("getting total count...")
    out = text(subprocess.check_output('cat raw2 | LC_ALL=C grep -a -i "^en " | cut -d" " -f 3 | awk \'{s+=$1} END {printf "%.0f", s}\'', shell=True))
    total = int(out)
    if debug_mode:
        print(total)
    counts["total"] = total
    return counts


def run(secret, download_limit=None, job_limit=None, sleep_time=1, job_type=0, debug_mode=False):

    worker = text(subprocess.check_output("echo `whoami`@`hostname`", shell=True)).strip()
    print("this is [%s]" % (worker))
    if debug_mode:
        print("*** running in debug mode ***")

    total_download = 0
    passed_jobs = 0
    failed_jobs = 0
    while (download_limit is None or total_download < download_limit) and (job_limit is None or (passed_jobs + failed_jobs) < job_limit):
        try:
            time_start = datetime.datetime.now()
            req = urlopen(MASTER_URL + "?get=x&type=%s" % (job_type))
            code = req.getcode()
            if code != 200:
                if code == 201:
                    print("no jobs available")
                    if download_limit is None and job_limit is None:
                        time.sleep(60)
                        continue
                    else:
                        print("nothing to do, exiting")
                        return
                else:
                    raise Exception("server response code (get) was %d" % (code))
            # Make the code compatible with mac os system
            if platform == "darwin":
                job_content = text(req.readlines()[1])
            else:
                job_content = text(req.readlines()[0])
            if job_content == "no jobs":
                print("no jobs available")
                if download_limit is None and job_limit is None:
                    time.sleep(60)
                    continue
                else:
                    print("nothing to do, exiting")
                    return
            job = json.loads(job_content)
            print("received job [%d|%s]" % (job["id"], job["name"]))
            # updated parsing for pageviews - maybe use a regex in the future
            # year, month = int(job['name'][11:15]), int(job['name'][15:17])
            year, month = int(job["name"][10:14]), int(job["name"][14:16])
            # print 'year=%d | month=%d'%(year, month)
            url = "https://dumps.wikimedia.org/other/pageviews/%d/%d-%02d/%s" % (year, year, month, job["name"])
            print("downloading file [%s]..." % (url))
            subprocess.check_call("curl -s %s > raw.gz" % (url), shell=True)
            print("checking file size...")
            # Make the code cross-platfrom, so use python to get the size of the file
            # size = int(text(subprocess.check_output('ls -l raw.gz | cut -d" " -f 5', shell=True)))
            size = os.stat("raw.gz").st_size
            if debug_mode:
                print(size)
            total_download += size
            if job["hash"] != "00000000000000000000000000000000":
                print("checking hash...")
                out = text(subprocess.check_output("md5sum raw.gz", shell=True))
                result = out[0:32]
                if result != job["hash"]:
                    raise Exception("wrong hash [expected %s, got %s]" % (job["hash"], result))
                if debug_mode:
                    print(result)
            print("decompressing...")
            subprocess.check_call("gunzip -f raw.gz", shell=True)
            # print 'converting case...'
            # subprocess.check_call('cat raw | tr "[:upper:]" "[:lower:]" > raw2', shell=True)
            # subprocess.check_call('rm raw', shell=True)
            subprocess.check_call("mv raw raw2", shell=True)
            print("extracting article counts...")

            # Use python to read the file and extract counts, if you want to use the original shell method, please use
            counts = {}
            for language in wiki_util.Articles.available_languages:
                lang2articles = {"en": wiki_util.Articles.en_articles, "es": wiki_util.Articles.es_articles, "pt": wiki_util.Articles.pt_articles}
                articles = lang2articles[language]
                articles = sorted(articles)
                if debug_mode:
                    print("Language is {0} and target articles are {1}".format(language, articles))
                temp_counts = extract_article_counts("raw2", language, articles, debug_mode)
                counts[language] = temp_counts

            if not debug_mode:
                print("deleting files...")
                subprocess.check_call("rm raw2", shell=True)
            print("saving results...")
            time_stop = datetime.datetime.now()
            result = {
                "id": job["id"],
                "size": size,
                "data": json.dumps(counts),
                "worker": worker,
                "elapsed": (time_stop - time_start).total_seconds(),
            }
            payload = json.dumps(result)
            hmac_str = get_hmac_sha256(secret, payload)
            if debug_mode:
                print(" hmac: %s" % hmac_str)
            post_data = urlencode({"put": payload, "hmac": hmac_str})
            req = urlopen(MASTER_URL, data=data(post_data))
            code = req.getcode()
            if code != 200:
                raise Exception("server response code (put) was %d" % (code))
            print("done! (dl=%d)" % (total_download))
            passed_jobs += 1
        except Exception as ex:
            print("***** Caught Exception: %s *****" % (str(ex)))
            failed_jobs += 1
            time.sleep(30)
        print("passed=%d | failed=%d | total=%d" % (passed_jobs, failed_jobs, passed_jobs + failed_jobs))
        time.sleep(sleep_time)

    if download_limit is not None and total_download >= download_limit:
        print("download limit has been reached [%d >= %d]" % (total_download, download_limit))
    if job_limit is not None and (passed_jobs + failed_jobs) >= job_limit:
        print("job limit has been reached [%d >= %d]" % (passed_jobs + failed_jobs, job_limit))


def main():
    # version info
    print("version", VERSION)

    # args and usage
    parser = argparse.ArgumentParser()
    parser.add_argument("secret", type=str, help="hmac secret key")
    parser.add_argument("-b", "--blimit", action="store", type=int, default=None, help="download limit, in bytes")
    parser.add_argument("-j", "--jlimit", action="store", type=int, default=None, help="job limit")
    parser.add_argument("-s", "--sleep", action="store", type=int, default=1, help="seconds to sleep between each job")
    parser.add_argument("-t", "--type", action="store", type=int, default=0, help="type of job")
    parser.add_argument("-d", "--debug", action="store_const", const=True, default=False, help="enable debug mode")
    args = parser.parse_args()

    # runtime options
    secret, download_limit, job_limit, sleep_time, job_type, debug_mode = args.secret, args.blimit, args.jlimit, args.sleep, args.type, args.debug

    # run
    run(secret, download_limit, job_limit, sleep_time, job_type, debug_mode)


if __name__ == "__main__":
    main()
