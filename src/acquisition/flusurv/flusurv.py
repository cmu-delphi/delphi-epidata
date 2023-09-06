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
from warnings import warn

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


def reformat_to_nested(data):
    """
    Convert the default data object into a dictionary grouped by location and epiweek

    Arg data is a list of dictionaries of the format
        [
            {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 4.3, 'weeklyrate': 1.7, 'mmwrid': 2493},
            {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.3, 'weeklyrate': 0.1, 'mmwrid': 2513},
            {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.6, 'weeklyrate': 0.1, 'mmwrid': 2516},
            ...
        ]

    This object is stored as the value associated with the 'default_data' key in the
    GRASP API response object, as fetched with 'fetch_flusurv_object()'

    Returns a dictionary of the format
        {
            <location>: {
                <epiweek>: {
                    <ageid1>: <value>,
                    ...
                    <raceid2>: <value>,
                    ...
                }
                ...
            }
            ...
        }
    """
    # Sanity check the input. We expect to see some epiweeks
    if len(data["default_data"]) == 0:
        raise Exception("no data found")

    # Create output object
    # First layer of keys is locations. Second layer of keys is epiweeks.
    #  Third layer of keys is groups (by id, not age in years, sex abbr, etc).
    #
    # If a top-level key doesn't already exist, create a new empty dict.
    # If a secondary key doesn't already exist, create a new empty dict.
    # If a tertiary key doesn't already exist, create a new key with a
    #  default value of None if not provided.
    data_out = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

    for obs in data["default_data"]:
        epiweek = mmwrid_to_epiweek(obs["mmwrid"])
        location = code_to_location[(obs["networkid"], obs["catchmentid"])]
        groupname = groupids_to_name((obs["ageid"], obs["sexid"], obs["raceid"]))

        prev_rate = data_out[location][epiweek][groupname]
        if prev_rate is None:
            # this is the first time to see a rate for this location-epiweek-
            #  group combo
            data_out[location][epiweek][groupname] = rate
        elif prev_rate != rate:
            # Skip and warn
            # a different rate was already found for this location-epiweek-
            #  group combo
            warn((f"warning: Multiple rates seen for {location} {epiweek} "
                   f"{groupname}, but previous value {prev_rate} does not "
                   f"equal new value {rate}. Using the first value."))

    # Sanity check the input. We expect to have populated our dictionary
    if len(data_out.keys()) == 0:
        raise Exception("no data loaded")

    print(f"found data for {len(data_out.keys())} locations")
    print(f"found data for {len(data_out[location].keys())} epiweeks for {location}")

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
    data_out = reformat_to_nested(data_in)

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
