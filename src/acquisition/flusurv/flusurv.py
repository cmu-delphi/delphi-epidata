"""
===============
=== Purpose ===
===============

Fetches FluSurv-NET data (flu hospitalization rates) from CDC. Unlike the other
CDC-hosted datasets (e.g. FluView), FluSurv is not available as a direct
download. This program emulates web browser requests for the web app and
extracts data of interest from the JSON response.

For unknown reasons, the server appears to provide two separate rates for any
given location, epiweek, and age group. These rates are usually identical--but
not always. When two given rates differ, the first is kept. This appears to be
the behavior of the web app, at the following location:
  - https://gis.cdc.gov/GRASP/Fluview/FluView3References/Main/FluView3.js:859

See also:
  - flusurv_update.py
  - https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html
  - https://wwwnc.cdc.gov/eid/article/21/9/14-1912_article
  - Chaves, S., Lynfield, R., Lindegren, M., Bresee, J., & Finelli, L. (2015).
    The US Influenza Hospitalization Surveillance Network. Emerging Infectious
    Diseases, 21(9), 1543-1550. https://dx.doi.org/10.3201/eid2109.141912.


=================
=== Changelog ===
=================

2017-05-22
  * rewrite for new data source
2017-02-17
  * handle discrepancies by prefering more recent values
2017-02-03
  + initial version
"""

# standard library
from collections import defaultdict
from datetime import datetime
import json
import time

# third party
import requests

# first party
from delphi.utils.epidate import EpiDate


# all currently available FluSurv locations and their associated codes
# the number pair represents NetworkID and CatchmentID
location_to_code = {
    "CA": (2, 1),
    "CO": (2, 2),
    "CT": (2, 3),
    "GA": (2, 4),
    "IA": (3, 5),
    "ID": (3, 6),
    "MD": (2, 7),
    "MI": (3, 8),
    "MN": (2, 9),
    "NM": (2, 11),
    "NY_albany": (2, 13),
    "NY_rochester": (2, 14),
    "OH": (3, 15),
    "OK": (3, 16),
    "OR": (2, 17),
    "RI": (3, 18),
    "SD": (3, 19),
    "TN": (2, 20),
    "UT": (3, 21),
    "network_all": (1, 22),
    "network_eip": (2, 22),
    "network_ihsp": (3, 22),
}


def fetch_json(path, payload, call_count=1, requests_impl=requests):
    """Send a request to the server and return the parsed JSON response."""

    # it's polite to self-identify this "bot"
    delphi_url = "https://delphi.cmu.edu/index.html"
    user_agent = f"Mozilla/5.0 (compatible; delphibot/1.0; +{delphi_url})"

    # the FluSurv AMF server
    flusurv_url = "https://gis.cdc.gov/GRASP/Flu3/" + path

    # request headers
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": user_agent,
    }
    if payload is not None:
        headers["Content-Type"] = "application/json;charset=UTF-8"

    # send the request and read the response
    if payload is None:
        method = requests_impl.get
        data = None
    else:
        method = requests_impl.post
        data = json.dumps(payload)
    resp = method(flusurv_url, headers=headers, data=data)

    # check the HTTP status code
    if resp.status_code == 500 and call_count <= 2:
        # the server often fails with this status, so wait and retry
        delay = 10 * call_count
        print(f"got status {int(resp.status_code)}, will retry in {int(delay)} sec...")
        time.sleep(delay)
        return fetch_json(path, payload, call_count=call_count + 1)
    elif resp.status_code != 200:
        raise Exception(["status code != 200", resp.status_code])

    # check response mime type
    if "application/json" not in resp.headers.get("Content-Type", ""):
        raise Exception("response is not json")

    # return the decoded json object
    return resp.json()


def fetch_flusurv_location(location_code):
    """Return decoded FluSurv JSON object for the given location."""
    return fetch_json(
        "PostPhase03DataTool",
        {
            "appversion": "Public",
            "key": "getdata",
            "injson": [{
                "networkid": location_code[0],
                "cacthmentid": location_code[1],
                "seasonid": seasonid
            }],
        },
    )

def fetch_flusurv_object():
    """Return raw FluSurv JSON object for all locations."""
    return fetch_json(
        "PostPhase03DataTool",
        {"appversion": "Public", "key": "", "injson": []}
    )


def mmwrid_to_epiweek(mmwrid):
    """Convert a CDC week index into an epiweek."""

    # Add the difference in IDs, which are sequential, to a reference epiweek,
    # which is 2003w40 in this case.
    epiweek_200340 = EpiDate(2003, 9, 28)
    mmwrid_200340 = 2179
    return epiweek_200340.add_weeks(mmwrid - mmwrid_200340).get_ew()


def extract_from_object(data_in):
    """
    Given a FluSurv data object, return hospitalization rates.

    The returned object is indexed first by epiweek, then by zero-indexed age
    group.
    """

    # Create output object
    # First layer of keys is epiweeks. Second layer of keys is age groups
    # (by id, not age).
    #
    # If a top-level key doesn't already exist, create a new empty dict.
    # If a secondary key doesn't already exist, create a new dict. Default
    #  value is None if not provided.
    data_out = defaultdict(lambda: defaultdict(lambda: None))

    # iterate over all seasons and age groups
    for obj in data_in["busdata"]["dataseries"]:
        age_group = obj["age"]
        if age_group in (10, 11, 12):
            # TODO(https://github.com/cmu-delphi/delphi-epidata/issues/242):
            #   capture as-of-yet undefined age groups 10, 11, and 12
            continue
        # iterate over weeks
        for mmwrid, _, _, rate in obj["data"]:
            epiweek = mmwrid_to_epiweek(mmwrid)
            prev_rate = data_out[epiweek][age_group]
            if prev_rate is None:
                # this is the first time to see a rate for this epiweek-age
                #  group combo
                data_out[epiweek][age_group] = rate
            elif prev_rate != rate:
                # a different rate was already found for this epiweek-age
                #  group combo
                format_args = (epiweek, age_group, prev_rate, rate)
                print("warning: %d %d %f != %f" % format_args)

    # Sanity check the result. We expect to have seen some epiweeks
    if len(data_out.keys()) == 0:
        raise Exception("no data found")

    # print the result and return flu data
    print(f"found data for {len(data_out)} weeks")
    return data_out


def get_data(location_code):
    """
    Fetch and parse flu data for the given location.

    This method performs the following operations:
      - fetches FluSurv data from CDC
      - extracts and returns hospitalization rates
    """

    # fetch
    print("[fetching flusurv data...]")
    data_in = fetch_flusurv_location(location_code)

    # extract
    print("[extracting values...]")
    data_out = extract_from_object(data_in)

    # return
    print("[scraped successfully]")
    return data_out


def get_current_issue(data):
    """
    Extract the current issue from the FluSurv API result.

    data: dictionary representing a JSON response from the FluSurv API
    """
    # extract
    date = datetime.strptime(data["loaddatetime"], "%b %d, %Y")

    # convert and return
    return EpiDate(date.year, date.month, date.day).get_ew()
