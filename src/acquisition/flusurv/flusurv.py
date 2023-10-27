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


def fetch_flusurv_location(location, seasonids):
    """Return FluSurv JSON object for the given location."""
    location_code = location_to_code[location]

    result = fetch_json(
        "PostPhase03DataTool",
        {
            "appversion": "Public",
            "key": "getdata",
            "injson": [
                {
                    "networkid": location_code[0],
                    "catchmentid": location_code[1],
                    "seasonid": elem,
                } for elem in seasonids],
        },
    )

    # If no data is returned (a given seasonid is not reported,
    # location codes are invalid, etc), the API returns a JSON like:
    #    {
    #        'default_data': {
    #            'response': 'No Data'
    #            }
    #    }
    #
    # If data is returned, then data["default_data"] is a list
    #  and data["default_data"]["response"] doesn't exist.
    assert isinstance(result["default_data"], list) and len(result["default_data"]) > 0, \
        f"Data was not correctly returned from the API for {location}"
    return result


def fetch_flusurv_metadata():
    """Return FluSurv JSON metadata object."""
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


def group_by_epiweek(data, metadata):
    """
    Convert default data for a single location into an epiweek-grouped dictionary

    Args:
        data: The "default_data" element of a GRASP API response object,
          as fetched with 'fetch_flusurv_location' or `fetch_flusurv_metadata`
        metadata: The JSON result returned from `fetch_flusurv_metadata()`
          containing mappings from strata IDs and season IDs to descriptions.

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
    data = data["default_data"]

    # Sanity check the input. We expect to see some epiweeks
    if len(data) == 0:
        raise Exception("no data found")

    id_label_map = make_id_label_map(metadata)
    id_season_map = make_id_season_map(metadata)

    # Create output object
    # First layer of keys is epiweeks. Second layer of keys is groups
    #  (by id, not age in years, sex abbr, etc).
    #
    # If a top-level key doesn't already exist, create a new empty dict.
    # If a secondary key doesn't already exist, create a new key with a
    #  default value of None if not provided.
    data_out = defaultdict(lambda: defaultdict(lambda: None))

    # data["default_data"] is a list of dictionaries, with the format
    #     [
    #         {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 4.3, 'weeklyrate': 1.7, 'mmwrid': 2493},
    #         {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.3, 'weeklyrate': 0.1, 'mmwrid': 2513},
    #         {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'rate': 20.6, 'weeklyrate': 0.1, 'mmwrid': 2516},
    #         ...
    #     ]
    for obs in data:
        epiweek = mmwrid_to_epiweek(obs["mmwrid"])
        groupname = groupids_to_name(
            ageid = obs["ageid"], sexid = obs["sexid"], raceid = obs["raceid"],
            id_label_map = id_label_map
        )

        # Set season description. This will be overwritten every iteration,
        #  but should always have the same value per epiweek group.
        data_out[epiweek]["season"] = id_season_map[obs["seasonid"]]

        rate = obs["weeklyrate"]
        prev_rate = data_out[epiweek][groupname]
        if prev_rate is None:
            # This is the first time to see a rate for this epiweek-group
            #  combo
            data_out[epiweek][groupname] = rate
        elif prev_rate != rate:
            # Skip and warn; a different rate was already found for this
            # epiweek-group combo
            warn((f"warning: Multiple rates seen for {epiweek} "
                   f"{groupname}, but previous value {prev_rate} does not "
                   f"equal new value {rate}. Using the first value."))

    # Sanity check the input. We expect to have populated our dictionary
    if len(data_out.keys()) == 0:
        raise Exception("no data loaded")

    print(f"found data for {len(data_out.keys())} epiweeks")

    return data_out


def get_data(location, seasonids, metadata):
    """
    Fetch and parse flu data for the given location.

    This method performs the following operations:
      - fetch location-specific FluSurv data from CDC API
      - extracts and returns hospitalization rates for each epiweek
    """
    # fetch
    print("[fetching flusurv data...]")
    data_in = fetch_flusurv_location(location, seasonids)

    # extract
    print("[reformatting flusurv result...]")
    data_out = group_by_epiweek(data_in, metadata)

    # return
    print(f"[successfully fetched data for {location}]")
    return data_out


def get_current_issue(metadata):
    """
    Extract the current issue from the FluSurv API result.

    Args:
        metadata: dictionary representing a JSON response from the FluSurv API
    """
    # extract
    date = datetime.strptime(metadata["loaddatetime"], "%b %d, %Y")

    # convert and return
    return EpiDate(date.year, date.month, date.day).get_ew()


def make_id_label_map(metadata):
    """Create a map from valueid to group description"""
    id_to_label = defaultdict(lambda: defaultdict(lambda: None))
    for group in metadata["master_lookup"]:
        # Skip "overall" group
        if group["Variable"] is None:
            continue
        id_to_label[group["Variable"]][group["valueid"]] = group["Label"].replace(
            " ", ""
        ).replace(
            "/", ""
        ).replace(
            "-", "t"
        ).replace(
            "yr", ""
        ).lower()

    return id_to_label


def make_id_season_map(metadata):
    """Create a map from seasonid to season description, in the format "YYYY-YY" """
    id_to_label = defaultdict(lambda: defaultdict(lambda: None))
    for season in metadata["seasons"]:
        id_to_label[season["seasonid"]] = season["label"]

    return id_to_label


def groupids_to_name(ageid, sexid, raceid, id_label_map):
    if ((ageid, sexid, raceid).count(0) < 2):
        raise ValueError("Expect at least two of three group ids to be 0")
    if (ageid, sexid, raceid).count(0) == 3:
        group = "overall"
    elif ageid != 0:
        # The column names used in the DB for the original age groups
        #  are ordinal, such that:
        #     "rate_age_0" corresponds to age group 1, 0-4 yr
        #     "rate_age_1" corresponds to age group 2, 5-17 yr
        #     "rate_age_2" corresponds to age group 3, 18-49 yr
        #     "rate_age_3" corresponds to age group 4, 50-64 yr
        #     "rate_age_4" corresponds to age group 5, 65+ yr
        #     "rate_age_5" corresponds to age group 7, 65-74 yr
        #     "rate_age_6" corresponds to age group 8, 75-84 yr
        #     "rate_age_7" corresponds to age group 9, 85+ yr
        #
        #  Group 6 was the "overall" category and not included in the
        #  ordinal naming scheme. Because of that, groups 1-5 have column
        #  ids equal to the ageid - 1; groups 7-9 have column ids equal
        #  to ageid - 2.
        #
        #  Automatically map from ageids 1-9 to column ids to match
        #  the historical convention.
        if ageid <= 5:
            age_group = str(ageid - 1)
        elif ageid == 6:
            # Ageid of 6 used to be used for the "overall" category.
            #  Now "overall" is represented by a valueid of 0, and ageid of 6
            #  is not used for any group. If we see an ageid of 6, something
            #  has gone wrong.
            raise ValueError("Ageid cannot be 6; please check for changes in the API")
        elif ageid <= 9:
            age_group = str(ageid - 2)
        else:
            age_group = id_label_map["Age"][ageid]
        group = "age_" + age_group
    elif sexid != 0:
        group = "sex_" + id_label_map["Sex"][sexid]
    elif raceid != 0:
        group = "race_" + id_label_map["Race"][raceid]

    return "rate_" + group
