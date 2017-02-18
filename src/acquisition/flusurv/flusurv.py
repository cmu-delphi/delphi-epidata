"""
===============
=== Purpose ===
===============

Fetches FluSurv-NET data (flu hospitaliation rates) from CDC. Unlike the other
CDC-hosted datasets (e.g. FluView), FluSurv is not available as a direct
download. Instead, this program emulates the web-based flash app and extracts
values from the response. Theses communications use the AMF data format.

For unknown reasons, the server appears to provide two separate rates for any
given location, epiweek, and age group. These rates are usually identical--but
not always. Each rate comes along with an increasing identifier which is
ostensibly a counter representing the week of publication. In other words, the
data appears to be versioned. When two given rates differ, the one with the
highest version number is kept. An Exception will be raised if two different
rates are found for the same version number.

See also:
  - flusurv_update.py
  - amf_to_json.py
  - https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html
  - https://wwwnc.cdc.gov/eid/article/21/9/14-1912_article
  - Chaves, S., Lynfield, R., Lindegren, M., Bresee, J., & Finelli, L. (2015).
    The US Influenza Hospitalization Surveillance Network. Emerging Infectious
    Diseases, 21(9), 1543-1550. https://dx.doi.org/10.3201/eid2109.141912.


=================
=== Changelog ===
=================

2017-02-17
  * handle discrepancies by prefering more recent values
2017-02-03
  + initial version
"""

# standard library
import base64
import json
import os
import random
import subprocess
import time
# third party
import requests

# all currently available FluSurv locations and their associated codes
# the number pair represents NetworkID and CatchmentID
location_codes = {
  'CA': (2, 1),
  'CO': (2, 2),
  'CT': (2, 3),
  'GA': (2, 4),
  'IA': (3, 5),
  'ID': (3, 6),
  'MD': (2, 7),
  'MI': (3, 8),
  'MN': (2, 9),
  'NM': (2, 11),
  'NY_albany': (2, 13),
  'NY_rochester': (2, 14),
  'OH': (3, 15),
  'OK': (3, 16),
  'OR': (2, 17),
  'RI': (3, 18),
  'SD': (3, 19),
  'TN': (2, 20),
  'UT': (3, 21),
  'network_all': (1, 22),
  'network_eip': (2, 22),
  'network_ihsp': (3, 22),
}


def get_uuid():
  """Generate a randomized, timestamp-based, UUID."""

  # based on analysis of the AMF requests sent by the flash app to the server
  rand = lambda bits: random.randint(0, (1 << bits) - 1)
  timestamp = round(time.time() * 1e3) & 0xffffffff
  values = (rand(32), rand(16), rand(16), rand(16), timestamp, rand(16))
  return ('%08x-%04x-%04x-%04x-%08x%04x' % values).upper()


def get_request_amf(location_code):
  """Build an AMF request for the specified location."""

  # the following binary blob contains a very basic AMF template for FluSurv
  # it was built by comparing many different requests sent by the browser
  amf = bytearray(base64.b64decode('''
  AAMAAAABAARudWxsAAIvMQAAATEKAAAAAREKgRNPZmxleC5tZXNzYWdpbmcubWVz
  c2FnZXMuUmVtb3RpbmdNZXNzYWdlDXNvdXJjZRNvcGVyYXRpb24PaGVhZGVycwli
  b2R5EWNsaWVudElkF2Rlc3RpbmF0aW9uE21lc3NhZ2VJZBV0aW1lVG9MaXZlE3Rp
  bWVzdGFtcAYxRmx1RGF0YUhhbmRsZXIuRmx1V29ya2VyBhVHZXRFSVBEYXRhCgsB
  FURTRW5kcG9pbnQGDW15LWFtZglEU0lkBkk0QUQyMjg3Ni1EODc5LTQyN0QtOThB
  My1FRkYzQzMxNTUwQ0YBCQUBBAAEAAEGJUdlbmVyaWNEZXN0aW5hdGlvbgZJAAAA
  AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEAA==
  '''))
  # the location code (NetworkID, CatchmentID) takes two bytes
  amf[0x103], amf[0x105] = location_code
  # the ascii representation of a random/timestamp UUID takes 36 bytes
  amf[0x11D:0x141] = bytes(get_uuid(), 'ascii')
  return amf


def fetch_flusurv_amf(location_code, filename):
  """Send an AMF request to the server and write the response to a file."""

  # it's polite to self-identify this "bot"
  delphi_url = 'http://delphi.midas.cs.cmu.edu/index.html'
  user_agent = 'Mozilla/5.0 (compatible; delphibot/1.0; +%s)' % delphi_url

  # the FluSurv AMF server
  flusurv_url = 'https://gis.cdc.gov/GRASP/Fluview/weborb.aspx'

  # the minimum required request headers
  headers = {
    'Accept-Encoding': 'gzip',
    'User-Agent': user_agent,
    'Content-Type': 'application/x-amf',
  }

  # build the request
  data = get_request_amf(location_code)

  # send the request and read the response
  resp = requests.post(flusurv_url, headers=headers, data=data)

  # check the HTTP status code
  if resp.status_code != 200:
    raise Exception(['status code != 200', resp.status_code])
  print('received %d byte response' % len(resp.content))

  # check response mine type and initial data
  mime_ok = resp.headers.get('Content-Type', None) == 'application/x-amf'
  data_ok = resp.content[:2] == b'\x00\x03'
  if not mime_ok or not data_ok:
    raise Exception('response is not amf')

  # save the binary response to a file
  with open(filename, 'wb') as f:
    f.write(resp.content)


def convert_amf_to_json(amf_file, json_file):
  """Create a file containing JSON data from one containing AMF data."""

  # run amf_to_json.py in a separate python process (python2)
  # this is because the required module `pyamf` won't run in this one (python3)
  cmd = "python amf_to_json.py '%s' '%s'" % (amf_file, json_file)
  return subprocess.check_call(cmd, shell=True)


def extract_row(node, location_code):
  """Return a tuple of (epiweek, age, version, rate), if present."""

  # use weekly rate field to identify nodes containing flu data
  rate = node.get('WeeklyRate', None)
  if rate is None:
    return None

  # location parameters
  network_id = node['NetworkID']
  catchment_id = node['CatchmentID']
  current_location = (network_id, catchment_id)

  # Usually the server responds with the same network and catchment that
  # was requested. But for catchment 22 ("entire network"), the returned
  # network appears to always be 3 (IHSP), regardless of requested network.
  # However, the rates appear to match that of the requested network.
  if location_code[1] != 22 and current_location != location_code:
    raise Exception(['wrong location', current_location, location_code])

  # epiweek
  year = node['Year']
  week = node['WeekNumber']
  epiweek = year * 100 + week

  # age group
  age_id = node['AgeID']
  age = age_id - 1

  # presumably, an identifier for the week of publication (higher is newer)
  version = node['PublishYearID']

  # the result
  return (epiweek, age, version, rate)


def extract_values(data_in, data_out, location_code):
  """
  Given an arbitrary JSON object, return FluSurv data for the given location.

  More specifically, the object is visited in a depth-first search, and
  any node containing recognizable flu data (i.e. the `WeeklyRate` field) is
  added to the result object.
  """

  # read flu data from the dict, or visit each of its members
  if isinstance(data_in, dict):
    row = extract_row(data_in, location_code)
    if row is not None:
      # add the data from this node to the result object
      epiweek, age, version, rate = row
      value = version, rate
      if epiweek not in data_out:
        data_out[epiweek] = [None] * 6  # weekly rate of six age groups
      if data_out[epiweek][age] is None:
        # this is the first time to see a rate for this epiweek/age
        data_out[epiweek][age] = value
      elif data_out[epiweek][age] != value:
        # a different rate was already found for this epiweek/age
        stored_version, stored_rate = data_out[epiweek][age]
        if version > stored_version:
          # use the newer version instead
          if rate != stored_rate:
            params = (epiweek, age, str(data_out[epiweek][age]), str(value))
            print('warning: at %d/%d, replace %s with %s' % params)
          data_out[epiweek][age] = value
        elif version == stored_version and rate != stored_rate:
          # no way to know which version is correct
          params = [epiweek, age, data_out[epiweek][age], value]
          raise Exception(['found different rates'] + params)
    else:
      # this node doesn't have flu data, so check each of its members
      for k in data_in.keys():
        extract_values(data_in[k], data_out, location_code)

  # visit each element of the list
  if isinstance(data_in, list):
    for item in data_in:
      extract_values(item, data_out, location_code)


def extract_from_json(location_code, filename):
  """Extract flu data for the given location from the given file."""

  # load JSON data from the file
  with open(filename) as f:
    data_in = json.loads(f.read())

  # initialize the result object
  data_out = {}

  # call the helper function to populate the result object
  extract_values(data_in, data_out, location_code)

  # sanity check the result
  if len(data_out) == 0:
    raise Exception('file contains no recognizable data')

  # remove version codes since only the rates are needed
  for epiweek in data_out:
    for age in range(len(data_out[epiweek])):
      if data_out[epiweek][age] is None:
        continue
      version, rate = data_out[epiweek][age]
      data_out[epiweek][age] = rate

  # print the result and return flu data
  print('found data for %d weeks' % len(data_out))
  return data_out


def get_data(location_code, debug=False):
  """
  Fetch and parse flu data for the given location.

  This method performs the following operations:
    - fetches flu data from CDC (as AMF)
    - converts AMF to JSON (in a separate process)
    - extracts flu data from JSON
    - returns flu data indexed by epiweek
  """

  # temporary files for storing AMF and JSON data
  basename = '__flusurv_%d-%d' % location_code
  amf_file, json_file = '%s.amf' % basename, '%s.json' % basename

  try:
    # fetch
    print('[fetching flusurv amf...]')
    fetch_flusurv_amf(location_code, amf_file)

    # convert
    print('[converting amf to json...]')
    convert_amf_to_json(amf_file, json_file)

    # extract
    print('[extracting values from json...]')
    data = extract_from_json(location_code, json_file)

    # return
    print('[flusurv data scraped successfully]')
    return data

  finally:
    # remove temporary files (unless debugging)
    if not debug:
      for filename in (amf_file, json_file):
        try:
          # remove the file
          os.remove(filename)
        except:
          pass
