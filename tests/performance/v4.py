#
# Run using Docker method like:
#
# 1. Build the container:
#
#    docker build -t locust .
#
# 2. Run it, where ${CSV} is a CSV file with requests terminated by a newline.
#    A bit of a hacky thing is happening here, in which the `-i` ("iterations")
#    flag's value is set to the output of "$(cat ${CSV} | wc -l)". This
#    effectively runs locust for the same number of iterations as there are
#    lines in the CSV file. This seems to reliably use each line in the file
#    once, no matter if one or many locust clients have been spun up. There is
#    probably a nicer way to do this, though.
#    
#    You can fill in ${CSV} manually with the name of the file, or export it
#    into your shell env.
#
#    The below example assumes you want to run against the prod API endpoint,
#    but just change it as you need. Goes for the other params as well (port,
#    --users, --spawn-rate, etc.).
#
#    Ex. Prod API
#    ----
#    docker run -p 8089:8089 \
#      -v $PWD:/mnt/locust \
#      -e CSV=/mnt/locust/${CSV} \
#      locust -f /mnt/locust/v4.py \
#      --host https://api.covidcast.cmu.edu/ \
#      --users 10 \
#      --spawn-rate 1 \
#      --autostart \
#      -i "$(cat ${CSV} | wc -l)"
#
#     Ex. QA v3
#     ----
#     docker run - p 8089: 8089 \
#         -v $PWD: / mnt/locust \
#         -e CSV = /mnt/locust /${CSV} \
#         locust - f / mnt/locust/v4.py \
#         --host https: // staging.delphi.cmu.edu/qa/epi3 / \
#         --users 10 \
#         --spawn-rate 1 \
#         --autostart \
#         -i "$(cat ${CSV} | wc -l)"
#
#     Ex. QA v4
#     ----
#     docker run - p 8089: 8089 \
#         -v $PWD: / mnt/locust \
#         -e CSV = /mnt/locust /${CSV} \
#         locust - f / mnt/locust/v4.py \
#         --host https: // staging.delphi.cmu.edu/qa/epi4 / \
#         --users 10 \
#         --spawn-rate 1 \
#         --autostart \
#         -i "$(cat ${CSV} | wc -l)"
#

import os
from locust_plugins.csvreader import CSVReader
from locust import HttpUser, task, between

csv = os.environ['CSV']
session_reader = CSVReader(csv)


class EpidataUser(HttpUser):
    wait_time = between(1, 1)

    @task
    def epidata_request(self):
        url = next(session_reader)
        self.client.get(f"{url[0]}")
