"""
===============
=== Purpose ===
===============

Extracts and stores article access counts

See also: wiki.py


=================
=== Changelog ===
=================

2017-02-23
  * secrets and minor cleanup
2016-08-14
  * use pageviews instead of pagecounts-raw
  * default job limit from 1000 to 100
2015-08-11
  + Store total and other metadata in `wiki_meta`
2015-05-21
  * Original version
"""

# standard library
from datetime import datetime, timedelta
import json

# third party
import mysql.connector

# first party
import delphi.operations.secrets as secrets


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
    # return datetime(int(name[11:15]), int(name[15:17]), int(name[17:19]), int(name[20:22]), int(name[22:24]), int(name[24:26]))
    return datetime(
        int(name[10:14]),
        int(name[14:16]),
        int(name[16:18]),
        int(name[19:21]),
        int(name[21:23]),
        int(name[23:25]),
    )


def run(job_limit=100):
    # connect to the database
    u, p = secrets.db.epi
    cnx = mysql.connector.connect(user=u, password=p, database="epidata", host=secrets.db.host)
    cur = cnx.cursor()

    # # Some preparation for utf-8, and it is a temporary trick solution. The real solution should change those char set and collation encoding to utf8 permanently
    # cur.execute("SET NAMES utf8;")
    # cur.execute("SET CHARACTER SET utf8;")
    # # I print SHOW SESSION VARIABLES LIKE 'character\_set\_%'; and SHOW SESSION VARIABLES LIKE 'collation\_%'; on my local computer
    # cur.execute("SET character_set_client=utf8mb4;")
    # cur.execute("SET character_set_connection=utf8mb4;")
    # cur.execute("SET character_set_database=utf8;")
    # cur.execute("SET character_set_results=utf8mb4;")
    # cur.execute("SET character_set_server=utf8;")
    # cur.execute("SET collation_connection=utf8mb4_general_ci;")
    # cur.execute("SET collation_database=utf8_general_ci;")
    # cur.execute("SET collation_server=utf8_general_ci;")

    # find jobs that are queued for extraction
    cur.execute(
        "SELECT `id`, `name`, `data` FROM `wiki_raw` WHERE `status` = 2 ORDER BY `name` ASC LIMIT %s",
        (job_limit,),
    )
    jobs = []
    for (id, name, data_str) in cur:
        jobs.append((id, name, json.loads(data_str)))
    print(f"Processing data from {len(jobs)} jobs")

    # get the counts from the json object and insert into (or update) the database
    # Notice that data_collect contains data with different languages
    for (id, name, data_collect) in jobs:
        print(f"processing job [{int(id)}|{name}]...")
        timestamp = round_timestamp(get_timestamp(name))
        for language in data_collect.keys():
            data = data_collect[language]
            for article in sorted(data.keys()):
                count = data[article]
                cur.execute(
                    "INSERT INTO `wiki` (`datetime`, `article`, `count`, `language`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `count` = `count` + %s",
                    (
                        str(timestamp),
                        article.encode("utf-8").decode("latin-1"),
                        count,
                        language,
                        count,
                    ),
                )
                if article == "total":
                    cur.execute(
                        "INSERT INTO `wiki_meta` (`datetime`, `date`, `epiweek`, `total`, `language`) VALUES (%s, date(%s), yearweek(%s, 6), %s, %s) ON DUPLICATE KEY UPDATE `total` = `total` + %s",
                        (str(timestamp), str(timestamp), str(timestamp), count, language, count),
                    )
        # update the job
        cur.execute("UPDATE `wiki_raw` SET `status` = 3 WHERE `id` = %s", (id,))

    # cleanup
    cur.close()
    cnx.commit()
    cnx.close()


if __name__ == "__main__":
    run()
