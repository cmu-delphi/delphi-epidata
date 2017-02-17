'''
===============
=== Purpose ===
===============

A Python interface for accessing the Google Trends (for Health) API. The API
is currently private, experimental, and unstable.


=================
=== Changelog ===
=================

2016-04-14:
  * fixed argument help typo
  * print zero values in sample usage
2016-01-29:
  + sample command line usage
  + extract array of values from returned data
  * separated GHT class from ght_update.py
'''

# built-in
import argparse
import time
# external
from apiclient.discovery import build
# local
from epidate import EpiDate
import epiweek as flu


class GHT:

  # Google Trends API endpoint
  DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/trends/v1beta/rest'

  def __init__(self, key, delay=1):
    self.service = build('trends', 'v1beta', developerKey=key, discoveryServiceUrl=GHT.DISCOVERY_URL)
    self.delay = delay

  # converts a YYYYWW week into a YYYY-MM-DD date (using Sunday of the week)
  @staticmethod
  def _ew2date(ew):
    # parse the epiweek
    year, week = flu.split_epiweek(ew)
    # get the date object (middle of the week; Wednesday)
    date = EpiDate.from_epiweek(year, week)
    # go to the first day of the week (Sunday)
    date = date.add_days(-3)
    # date as string
    return str(date)

  # get data from Google APIs
  # see: https://developers.google.com/apis-explorer/#p/trends/v1beta/trends.getTimelinesForHealth
  def get_data(self, start_week, end_week, location, term, resolution='week'):
    start_date = GHT._ew2date(start_week)
    end_date = GHT._ew2date(end_week)
    num_weeks = flu.delta_epiweeks(start_week, end_week) + 1

    # getTimelinesForHealth parameters
    params = {
      'terms': term,
      'time_startDate': start_date,
      'time_endDate': end_date,
      'timelineResolution': resolution,
    }
    if location == 'US':
      params['geoRestriction_country'] = location
    else:
      params['geoRestriction_region'] = 'US-' + location

    # make the API call
    data = self.service.getTimelinesForHealth(**params).execute()

    # extract the values
    try:
      values = [p['value'] for p in data['lines'][0]['points']]
    except:
      values = None

    # throttle request rate
    time.sleep(self.delay)

    # return the results
    return {
      'start_week': start_week,
      'end_week': end_week,
      'num_weeks': num_weeks,
      'location': location,
      'term': term,
      'resolution': resolution,
      'data': data,
      'values': values,
    }


def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('apikey', action='store', type=str, default=None, help='API key')
  parser.add_argument('startweek', action='store', type=int, default=None, help='first week (ex: 201440)')
  parser.add_argument('endweek', action='store', type=int, default=None, help='last week (ex: 201520)')
  parser.add_argument('location', action='store', type=str, default=None, help='location (ex: US)')
  parser.add_argument('term', action='store', type=str, default=None, help='term/query/topic (ex: /m/0cycc)')
  args = parser.parse_args()

  # get the data
  ght = GHT(args.apikey)
  result = ght.get_data(args.startweek, args.endweek, args.location, args.term)
  values = result['values']

  # sanity check
  expected_weeks = result['num_weeks']
  received_weeks = len([v for v in values if v is not None and type(v) == float and v >= 0])
  if expected_weeks != received_weeks:
    raise Exception('expected %d weeks, received %d' % (expected_weeks, received_weeks))

  # results
  epiweeks = [ew for ew in flu.range_epiweeks(args.startweek, args.endweek, inclusive=True)]
  for (epiweek, value) in zip(epiweeks, values):
    print('%6d: %.3f' % (epiweek, value))


if __name__ == '__main__':
  main()
