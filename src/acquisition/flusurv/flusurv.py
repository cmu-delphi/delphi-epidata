"""
===============
=== Purpose ===
===============

Fetches FluSurv-NET data (flu hospitaliation rates) from CDC. Unlike the other
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
from datetime import datetime
import json
# third party
import requests
# first party
from epidate import EpiDate


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


def fetch_json(path, payload):
  """Send a request to the server and return the parsed JSON response."""

  # it's polite to self-identify this "bot"
  delphi_url = 'https://delphi.midas.cs.cmu.edu/index.html'
  user_agent = 'Mozilla/5.0 (compatible; delphibot/1.0; +%s)' % delphi_url

  # the FluSurv AMF server
  flusurv_url = 'https://gis.cdc.gov/GRASP/Flu3/' + path

  # request headers
  headers = {
    'Accept-Encoding': 'gzip',
    'User-Agent': user_agent,
  }
  if payload is not None:
    headers['Content-Type'] = 'application/json;charset=UTF-8'

  # send the request and read the response
  if payload is None:
    method = requests.get
    data = None
  else:
    method = requests.post
    data = json.dumps(payload)
  resp = method(flusurv_url, headers=headers, data=data)

  # check the HTTP status code
  if resp.status_code != 200:
    raise Exception(['status code != 200', resp.status_code])

  # check response mine type
  if 'application/json' not in resp.headers.get('Content-Type', ''):
    raise Exception('response is not json')

  # return the decoded json object
  return resp.json()


def fetch_flusurv_object(location_code):
  """Return decoded FluSurv JSON object for the given location."""
  return fetch_json('PostPhase03GetData', {
    'appversion': 'Public',
    'networkid': location_code[0],
    'cacthmentid': location_code[1],
  })


def mmwrid_to_epiweek(mmwrid):
  """Convert a CDC week index into an epiweek."""

  # Add the difference in IDs, which are sequential, to a reference epiweek,
  # which is 2003w40 in this case.
  epiweek_200340 = EpiDate(2003, 9, 28)
  mmwrid_200340 = 2179
  return epiweek_200340.add_weeks(mmwrid - mmwrid_200340).get_ew()


def extract_from_object(data_in):
  """
  Given a FluSurv data object, return hospitaliation rates.

  The returned object is indexed first by epiweek, then by zero-indexed age
  group.
  """

  # an object to hold the result
  data_out = {}

  # iterate over all seasons and age groups
  for obj in data_in['busdata']['dataseries']:
    age = obj['age'] - 1
    # iterage over weeks
    for mmwrid, week, overall, rate in obj['data']:
      epiweek = mmwrid_to_epiweek(mmwrid)
      if epiweek not in data_out:
        # weekly rate of six age groups
        data_out[epiweek] = [None] * 6
      prev_rate = data_out[epiweek][age]
      if prev_rate is None:
        # this is the first time to see a rate for this epiweek/age
        data_out[epiweek][age] = rate
      elif prev_rate != rate:
        # a different rate was already found for this epiweek/age
        print('warning: %d %d %f != %f' % (epiweek, age + 1, prev_rate, rate))

  # sanity check the result
  if len(data_out) == 0:
    raise Exception('no data found')

  # print the result and return flu data
  print('found data for %d weeks' % len(data_out))
  return data_out


def get_data(location_code):
  """
  Fetch and parse flu data for the given location.

  This method performs the following operations:
    - fetches FluSurv data from CDC
    - extracts and returns hospitaliation rates
  """

  # fetch
  print('[fetching flusurv data...]')
  data_in = fetch_flusurv_object(location_code)

  # extract
  print('[extracting values...]')
  data_out = extract_from_object(data_in)

  # return
  print('[scraped successfully]')
  return data_out


def get_current_issue():
  """Scrape the current issue from the FluSurv main page."""

  # fetch
  data = fetch_json('GetPhase03InitApp?appVersion=Public', None)

  # extract
  date = datetime.strptime(data['loaddatetime'], '%b %d, %Y')

  # convert and return
  return EpiDate(date.year, date.month, date.day).get_ew()
