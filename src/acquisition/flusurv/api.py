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
from delphi.utils.epiweek import delta_epiweeks
from .constants import (MAP_REGION_NAMES_TO_ABBR, MAP_ENTIRE_NETWORK_NAMES,
    SEX_GROUPS, FLUSURV_BASE_URL, ID_TO_LABEL_MAP)


def fetch_json(path, payload, call_count=1, requests_impl=requests):
    """Send a request to the server and return the parsed JSON response."""

    # it's polite to self-identify this "bot"
    DELPHI_URL = "https://delphi.cmu.edu/index.html"
    USER_AGENT = f"Mozilla/5.0 (compatible; delphibot/1.0; +{DELPHI_URL})"

    # the FluSurv AMF server
    flusurv_url = FLUSURV_BASE_URL + path

    # request headers
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": USER_AGENT,
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


def mmwrid_to_epiweek(mmwrid):
    """Convert a CDC week index into an epiweek."""

    # Add the difference in IDs, which are sequential, to a reference
    # epiweek, which is 2003w40 in this case.
    epiweek_200340 = EpiDate(2003, 9, 28)
    mmwrid_200340 = 2179
    return epiweek_200340.add_weeks(mmwrid - mmwrid_200340).get_ew()


class FlusurvMetadata:
    def __init__(self, max_age_weeks):
        self.metadata = self._fetch_flusurv_metadata()

        self.issue = self._get_current_issue()
        self.max_age_weeks = max_age_weeks
        self.seasonids = self._get_recent_seasonids()

        self.location_to_code = self._make_location_to_code_map()
        self.locations = self.location_to_code.keys()

        self.id_to_group = ID_TO_LABEL_MAP
        self.id_to_season = self._make_id_season_map()

    def _fetch_flusurv_metadata(self):
        """Return FluSurv JSON metadata object."""
        return fetch_json(
            "PostPhase03DataTool",
            {"appversion": "Public", "key": "", "injson": []}
        )

    def _location_name_to_abbr(self, geo, network):
        """Find short geo name corresponding to a geo and network"""
        if geo == "Entire Network":
            return MAP_ENTIRE_NETWORK_NAMES[network]
        else:
            return MAP_REGION_NAMES_TO_ABBR[geo]

    def _make_location_to_code_map(self):
        """Create a map for all currently available FluSurv locations from names to codes"""
        location_to_code = dict()
        for location in self.metadata["catchments"]:
            # "area" is the long-form region (California, etc), and "name" is
            # the network/data source type (IHSP, EIP, etc)
            location_name = self._location_name_to_abbr(location["area"], location["name"])
            if location_name in location_to_code.keys():
                raise Exception(
                    f"catchment {location_name} already seen, but " +
                    "we expect catchments to be unique"
                )

            location_to_code[location_name] = (
                int(location["networkid"]), int(location["catchmentid"])
            )
        return location_to_code

    def _get_current_issue(self):
        """
        Extract the current issue from the FluSurv metadata result.

        Args:
            metadata: dictionary representing a JSON response from the FluSurv API
        """
        # extract
        date = datetime.strptime(self.metadata["loaddatetime"], "%b %d, %Y")

        # convert and return
        return EpiDate(date.year, date.month, date.day).get_ew()

    def _get_recent_seasonids(self):
        # Ignore seasons with all dates older than one year
        seasonids = {
            season_blob["seasonid"] for season_blob in self.metadata["seasons"]
            if delta_epiweeks(mmwrid_to_epiweek(season_blob["endweek"]), self.issue) < self.max_age_weeks
        }

        return seasonids

    def _make_id_season_map(self):
        """Create a map from seasonid to season description, in the format "YYYY-YY" """
        id_to_label = defaultdict(lambda: defaultdict(lambda: None))
        for season in self.metadata["seasons"]:
            id_to_label[season["seasonid"]] = season["label"].strip()

        return id_to_label


class FlusurvLocationFetcher:
    def __init__(self, max_age_weeks):
        self.metadata = FlusurvMetadata(max_age_weeks)

    def get_data(self, location):
        """
        Fetch and parse flu data for a given location.

        This method performs the following operations:
          - fetch location-specific FluSurv data from CDC API
          - extracts and returns hospitalization rates for each epiweek
        """
        # fetch
        print("[fetching flusurv data...]")
        data_in = self._fetch_flusurv_location(location)

        # extract
        print("[reformatting flusurv result...]")
        data_out = self._group_by_epiweek(data_in), location

        # return
        print(f"[successfully fetched data for {location}]")
        return data_out

    def _fetch_flusurv_location(self, location):
        """Return FluSurv JSON object for a given location."""
        location_code = self.metadata.location_to_code[location]

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
                    } for elem in self.metadata.seasonids],
            },
        )

        # If no data is returned (a given seasonid is not reported,
        # location codes are invalid, etc), the API returns a JSON like:
        #     {
        #        'default_data': {
        #            'response': 'No Data'
        #            }
        #     }
        #
        # If data is returned, then data["default_data"] is a list
        #  and data["default_data"]["response"] doesn't exist.
        if (len(result["default_data"]) == 0 or
            (
                isinstance(result["default_data"], dict) and
                "response" in result["default_data"].keys() and
                result["default_data"]["response"] == "No Data"
            )):
            warn(f"warning: No data was returned from the API for {location}")
            # Return empty obs with right format to avoid downstream errors
            return {"default_data": []}

        return result

    def _group_by_epiweek(self, data):
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

        # Create output object
        # First layer of keys is epiweeks. Second layer of keys is groups
        #  (by id, not age in years, sex abbr, etc).
        #
        # If a top-level key doesn't already exist, create a new empty dict.
        # If a secondary key doesn't already exist, create a new key with a
        #  default value of None.
        data_out = defaultdict(lambda: defaultdict(lambda: None))

        # data["default_data"] is a list of dictionaries, with the format
        #     [
        #         {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 4.3, 'weeklyrate': 1.7, 'mmwrid': 2493},
        #         {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 20.3, 'weeklyrate': 0.1, 'mmwrid': 2513},
        #         {'networkid': 1, 'catchmentid': 22, 'seasonid': 49, 'ageid': 0, 'sexid': 0, 'raceid': 1, 'flutype': 0, 'rate': 20.6, 'weeklyrate': 0.1, 'mmwrid': 2516},
        #         ...
        #     ]
        for obs in data:
            epiweek = mmwrid_to_epiweek(obs["mmwrid"])
            groupname = self._groupid_to_name(
                ageid = obs["ageid"], sexid = obs["sexid"],
                raceid = obs["raceid"], fluid = obs["flutype"]
            )

            # Set season description. This will be overwritten every iteration,
            #  but should always have the same value per epiweek group.
            data_out[epiweek]["season"] = self.metadata.id_to_season[obs["seasonid"]]

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

        print(f"found data for {len(data_out.keys())} epiweeks")

        return data_out

    def _groupid_to_name(self, ageid, sexid, raceid, fluid):
        if ((ageid, sexid, raceid, fluid).count(0) < 3):
            raise ValueError("Expect at least three of four group ids to be 0")
        if (ageid, sexid, raceid, fluid).count(0) == 4:
            group = "overall"
        # In all cases, if id is not available as a key in the dict, use the
        # raw id as the name suffix
        elif ageid != 0:
            if ageid == 6:
                # Ageid of 6 used to be used for the "overall" category.
                #  Now "overall" is represented by a valueid of 0, and ageid of 6
                #  is not used for any group. If we see an ageid of 6, something
                #  has gone wrong.
                raise ValueError("Ageid cannot be 6; please check for changes in the API")
            else:
                age_group = self.metadata.id_to_group["Age"].get(ageid, str(ageid))
            group = "age_" + age_group
        elif sexid != 0:
            group = "sex_" + self.metadata.id_to_group["Sex"].get(sexid, str(sexid))
        elif raceid != 0:
            group = "race_" + self.metadata.id_to_group["Race"].get(raceid, str(raceid))
        elif fluid != 0:
            group = "flu_" + self.metadata.id_to_group["Flutype"].get(fluid, str(fluid))

        return "rate_" + group
