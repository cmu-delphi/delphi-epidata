"""
===============
=== Purpose ===
===============

Fetches ILINet data (surveillance of outpatient influenza-like illness) from
CDC. 

This script provides functions for first fetching metadata from Fluview which 
are then used to build a request that will get all data for the different tier 
types (national, hhs regions, census divisions and states). This data is 
downloaded as one zip file per tier type (locally).

This file replaces scrape_flu_data.sh, which performed a similar function for
the old (pre 2017w40) FluView interface.

See also:
  - fluview_update.py
  - scrape_flu_data.sh
  - https://gis.cdc.gov/grasp/fluview/fluportaldashboard.html

Changes:
  - 10/03/18: added field for 'WHO_NREVSS' data to download data from clinical
    labs as well as public health labs. 
"""

# standard library
import datetime
import os
import time

# third party
import requests


class Key:
    """
    Constants for navigating the metadata object contained in the web response
    from CDC.
    """

    class TierType:
        nat = "National"
        hhs = "HHS Regions"
        cen = "Census Divisions"
        sta = "State"

    class TierListEntry:
        hhs = "hhsregion"
        cen = "censusregions"
        sta = "states"

    class TierIdEntry:
        hhs = "hhsregionid"
        cen = "censusregionid"
        sta = "stateid"


def check_status(resp, status, content_type):
    """Raise an exception if the status code or content type is unexpected."""
    if resp.status_code != status:
        raise Exception("got unexpected status code: " + str(resp.status_code))
    actual_type = resp.headers.get("Content-Type", None)
    if actual_type is None or content_type not in actual_type.lower():
        raise Exception("got unexpected content type: " + str(actual_type))


def fetch_metadata(sess):
    """
    Return metadata indicating the current issue and also numeric constants
    representing the various locations.
    """
    url = "https://gis.cdc.gov/grasp/flu2/GetPhase02InitApp?appVersion=Public"
    resp = sess.get(url)
    check_status(resp, 200, "application/json")
    return resp.json()


def get_issue_and_locations(data):
    """Extract the issue and per-tier location lists from the metadata object."""

    def get_tier_ids(name):
        for row in data["regiontypes"]:
            if row["description"] == name:
                return row["regiontypeid"]
        raise Exception()

    tier_ids = {
        name: get_tier_ids(name)
        for name in (
            Key.TierType.nat,
            Key.TierType.hhs,
            Key.TierType.cen,
            Key.TierType.sta,
        )
    }

    location_ids = {
        Key.TierType.nat: [0],
        Key.TierType.hhs: [],
        Key.TierType.cen: [],
        Key.TierType.sta: [],
    }

    # add location ids for HHS
    for row in data[Key.TierListEntry.hhs]:
        location_ids[Key.TierType.hhs].append(row[Key.TierIdEntry.hhs])
    location_ids[Key.TierType.hhs] = sorted(set(location_ids[Key.TierType.hhs]))
    num = len(location_ids[Key.TierType.hhs])
    if num != 10:
        raise Exception("expected 10 hhs regions, found %d" % num)

    # add location ids for census divisions
    for row in data[Key.TierListEntry.cen]:
        location_ids[Key.TierType.cen].append(row[Key.TierIdEntry.cen])
    location_ids[Key.TierType.cen] = sorted(set(location_ids[Key.TierType.cen]))
    num = len(location_ids[Key.TierType.cen])
    if num != 9:
        raise Exception("expected 9 census divisions, found %d" % num)

    # add location ids for states
    for row in data[Key.TierListEntry.sta]:
        location_ids[Key.TierType.sta].append(row[Key.TierIdEntry.sta])
    location_ids[Key.TierType.sta] = sorted(set(location_ids[Key.TierType.sta]))
    num = len(location_ids[Key.TierType.sta])
    if num != 57:
        raise Exception("expected 57 states/territories/cities, found %d" % num)

    # return a useful subset of the metadata
    # (latest epiweek, latest season, tier ids, location ids)
    return {
        "epiweek": data["mmwr"][-1]["yearweek"],
        "season_id": data["mmwr"][-1]["seasonid"],
        "tier_ids": tier_ids,
        "location_ids": location_ids,
    }


def download_data(tier_id, location_ids, season_ids, filename):
    """Download zipped ILINet data for the given locations and seasons."""

    def get_entry(num, name=None):
        return {"ID": num, "Name": (name if name else num)}

    # download the data (in memory)
    url = "https://gis.cdc.gov/grasp/flu2/PostPhase02DataDownload"
    data = {
        "AppVersion": "Public",
        "DatasourceDT": [get_entry(1, "ILINet"), get_entry(0, "WHO_NREVSS")],
        "RegionTypeId": tier_id,
        "SubRegionsDT": [get_entry(loc) for loc in sorted(location_ids)],
        "SeasonsDT": [get_entry(season) for season in sorted(season_ids)],
    }
    resp = requests.post(url, json=data)
    check_status(resp, 200, "application/octet-stream")
    payload = resp.content

    # save the data to file and return the file length
    with open(filename, "wb") as f:
        f.write(payload)
    return len(payload)


def save_latest(path=None):
    """
    Save the latest two seasons of data for all locations, separately for each
    location tier (i.e. national, HHS, census, and states).
    """

    # set up the session
    sess = requests.session()
    sess.headers.update(
        {
            # it's polite to self-identify this "bot"
            "User-Agent": "delphibot/1.0 (+https://delphi.cmu.edu/)",
        }
    )

    # get metatdata
    print("looking up ilinet metadata")
    data = fetch_metadata(sess)
    info = get_issue_and_locations(data)
    issue = info["epiweek"]
    print("current issue: %d" % issue)

    # establish timing
    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_season = info["season_id"]
    seasons = [s for s in range(current_season - 1, current_season + 1)]

    # make the destination path if it doesn't already exist
    if path is not None:
        os.makedirs(path, exist_ok=True)

    # download the data file for each tier
    files = []
    for delphi_name, cdc_name in (
        ("nat", Key.TierType.nat),
        ("hhs", Key.TierType.hhs),
        ("cen", Key.TierType.cen),
        ("sta", Key.TierType.sta),
    ):
        name = "ilinet_%s_%d_%s.zip" % (delphi_name, issue, dt)
        if path is None:
            filename = name
        else:
            filename = os.path.join(path, name)
        tier_id = info["tier_ids"][cdc_name]
        locations = info["location_ids"][cdc_name]

        # download and show timing information
        print("downloading %s" % delphi_name)
        t0 = time.time()
        size = download_data(tier_id, locations, seasons, filename)
        t1 = time.time()

        print(" saved %s (%d bytes in %.1f seconds)" % (filename, size, t1 - t0))
        files.append(filename)

    # return the current issue and the list of downloaded files
    return issue, files
