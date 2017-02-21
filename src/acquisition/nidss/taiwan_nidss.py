"""
===============
=== Purpose ===
===============

Scrapes weekly flu data from Taiwan's National Infectious Disease Statistics
System (NIDSS): http://nidss.cdc.gov.tw/en/


=================
=== Changelog ===
=================

2017-02-20
  * update for significant website changes (flu only)
2016-07-19
  + Sample/debug usage in function `main`
  * Update for change to NIDSS website (__EVENTVALIDATION -> __VIEWSTATEGENERATOR)
2015-10-14
  * Update for change to NIDSS website (page starts on flu by default now)
2015-08-20
  + Aggregate dengue data
2015-08-10
  * Original version, inspired by healthtweets.py
"""

# standard library
import argparse
import base64
import re
import urllib.parse
# third party
import requests
# first party
from epiweek import range_epiweeks, add_epiweeks, delta_epiweeks, check_epiweek


class NIDSS:
  """An API for scraping the NIDSS site."""

  # The page where the flu data is kept
  FLU_URL = 'https://nidss.cdc.gov.tw/en/CDCWNH01.aspx?dc=wnh'

  # Link to the dengue data
  DENGUE_URL = 'http://nidss.cdc.gov.tw/Download/Weekly_Age_County_Gender_061.csv'

  # Translate location names to English
  # https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_Taiwan
  _TRANSLATED = {
    b'5Y2X5oqV57ij': 'Nantou_County',
    b'5Y+w5Lit5biC': 'Taichung_City',
    b'5Y+w5YyX5biC': 'Taipei_City',
    b'5Y+w5Y2X5biC': 'Tainan_City',
    b'5Y+w5p2x57ij': 'Taitung_County',
    b'5ZiJ576p5biC': 'Chiayi_City',
    b'5ZiJ576p57ij': 'Chiayi_County',
    b'5Z+66ZqG5biC': 'Keelung_City',
    b'5a6c6Jit57ij': 'Yilan_County',
    b'5bGP5p2x57ij': 'Pingtung_County',
    b'5b2w5YyW57ij': 'Changhua_County',
    b'5paw5YyX5biC': 'New_Taipei_City',
    b'5paw56u55biC': 'Hsinchu_City',
    b'5paw56u557ij': 'Hsinchu_County',
    b'5qGD5ZyS5biC': 'Taoyuan_City',
    b'5r6O5rmW57ij': 'Penghu_County',
    b'6Iqx6JOu57ij': 'Hualien_County',
    b'6IuX5qCX57ij': 'Miaoli_County',
    b'6YeR6ZaA57ij': 'Kinmen_County',
    b'6Zuy5p6X57ij': 'Yunlin_County',
    b'6auY6ZuE5biC': 'Kaohsiung_City',
    b'6YCj5rGf57ij': 'Lienchiang_County',
  }

  # Map locations to regions
  # https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_Taiwan
  # https://en.wikipedia.org/wiki/Regions_of_Taiwan#Hexchotomy
  LOCATION_TO_REGION = {
    # Taipei
    'Taipei_City': 'Taipei',
    'Keelung_City': 'Taipei',
    'New_Taipei_City': 'Taipei',
    'Yilan_County': 'Taipei',
    'Kinmen_County': 'Taipei',
    'Lienchiang_County': 'Taipei',
    # Northern
    'Hsinchu_City': 'Northern',
    'Taoyuan_City': 'Northern',
    'Hsinchu_County': 'Northern',
    'Miaoli_County': 'Northern',
    # Central
    'Taichung_City': 'Central',
    'Changhua_County': 'Central',
    'Nantou_County': 'Central',
    # Southern
    'Tainan_City': 'Southern',
    'Chiayi_City': 'Southern',
    'Yunlin_County': 'Southern',
    'Chiayi_County': 'Southern',
    # Kaoping
    'Kaohsiung_City': 'Kaoping',
    'Pingtung_County': 'Kaoping',
    'Penghu_County': 'Kaoping',
    # Eastern
    'Hualien_County': 'Eastern',
    'Taitung_County': 'Eastern',
  }

  @staticmethod
  def _get_metadata(html):
    issue_pattern = re.compile('^.*Latest available data: Week (\\d+), (\\d{4})\\..*$')
    release_pattern = re.compile('^.*Data as of \\d+:\\d+:\\d+, (\\d{4})/(\\d{2})/(\\d{2})\\..*$')
    issue, release = None, None
    for line in html.split('\n'):
      match = issue_pattern.match(line)
      if match is not None:
        year, week = int(match.group(2)), int(match.group(1))
        issue = year * 100 + week
      match = release_pattern.match(line)
      if match is not None:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        release = '%04d-%02d-%02d' % (year, month, day)
    if issue is None or release is None:
      raise Exception('metadata not found')
    return issue, release

  @staticmethod
  def _get_flu_data(html):
    week_pattern = re.compile('^categories: \\[(.*)\\],$')
    value_pattern = re.compile('^series: \\[(.*)\\],$')
    data = {}
    parsing_ili = True
    for line in html.split('\n'):
      line = line.strip()
      match = week_pattern.match(line)
      if match is not None:
        weeks = [int(x[1:-1]) for x in match.group(1).split(',')]
        for week in weeks:
          check_epiweek(week)
          if week not in data:
            data[week] = {}
      match = value_pattern.match(line)
      if match is not None:
        for item in match.group(1).split('},{'):
          parts = item.replace('{', '').replace('}', '').strip().split(' ')
          location = parts[1][1:-2]
          def num(value):
            if parsing_ili:
              return float(value)
            else:
              if '.' in value:
                raise Exception('expected type int for visits')
              return int(value)
          values = [num(x) for x in parts[3][1:-1].split(',')]
          unit = 'ili' if parsing_ili else 'visits'
          if len(weeks) != len(values):
            raise Exception('len(weeks) != len(values)')
          for week, value in zip(weeks, values):
            if location not in data[week]:
              data[week][location] = {}
            data[week][location][unit] = value
        parsing_ili = False
    if len(data) == 0:
      raise Exception('no data')
    return data

  @staticmethod
  def get_flu_data():
    # Fetch the flu page
    response = requests.get(NIDSS.FLU_URL)
    if response.status_code != 200:
      raise Exception('request failed [%d]' % response.status_code)
    html = response.text
    # Parse metadata
    latest_week, release_date = NIDSS._get_metadata(html)
    # Parse flu data
    data = NIDSS._get_flu_data(html)
    # Return results indexed by week and location
    return latest_week, release_date, data

  @staticmethod
  def get_dengue_data(first_week, last_week):
    # Check week order
    if first_week > last_week:
      first_week, last_week = last_week, first_week
    # Bounds check
    if first_week < 200301 or last_week < 200301:
      raise Exception('week out of range')
    # Initialize data by week and location (zeroes are not reported)
    data = {}
    for week in range_epiweeks(first_week, add_epiweeks(last_week, 1)):
      data[week] = {}
      for location in NIDSS.LOCATION_TO_REGION.keys():
        data[week][location] = 0
    # Download CSV
    response = requests.get(NIDSS.DENGUE_URL)
    if response.status_code != 200:
      raise Exception('export Dengue failed [%d]' % response.status_code)
    csv = response.content.decode('big5-tw')
    # Parse the data
    lines = [l.strip() for l in csv.split('\n')[1:] if l.strip() != '']
    for line in lines:
      fields = line.split(',')
      location_b64 = base64.b64encode(fields[3].encode('utf-8'))
      location = NIDSS._TRANSLATED[location_b64]
      region = NIDSS.LOCATION_TO_REGION[location]
      imported_b64 = base64.b64encode(fields[6].encode('utf-8'))
      imported = imported_b64 == b'5piv'
      sex = fields[5]
      age = fields[7]
      count = int(fields[8])
      year = int(fields[1])
      week = int(fields[2])
      # Week 53 was reported each year in 2003-2007
      if year < 2008 and year != 2003 and week > 52:
        week = 52
      # Epiweek system change in 2009
      # See also: http://research.undefinedx.com/forum/index.php?topic=300.0
      if year == 2009:
        week -= 1
        if week == 0:
          year, week = 2008, 53
      epiweek = year * 100 + week
      if epiweek < first_week or epiweek > last_week:
        # Outside of the requested range
        continue
      if epiweek not in data or location not in data[epiweek]:
        # Not a vaild U.S. epiweek
        raise Exception('data missing %d-%s' % (epiweek, location))
      # Add the counts to the location on this epiweek
      data[epiweek][location] += count
    # Return results indexed by week and location
    return data


def main():
  # Args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'epiweek',
    action='store',
    type=int,
    help='fetch data on this epiweek (ex: 201537)'
  )
  args = parser.parse_args()
  ew = args.epiweek

  # Get the data
  latest_week, release_date, fdata = NIDSS.get_flu_data()
  ddata = NIDSS.get_dengue_data(ew, ew)

  # Print the results
  print('*** Meta ***')
  print('latest_week:', latest_week)
  print('release_date:', release_date)
  print('*** Flu ***')
  for region in sorted(list(fdata[ew].keys())):
    visits, ili = fdata[ew][region]['visits'], fdata[ew][region]['ili']
    print('region=%s | visits=%d | ili=%.3f' % (region, visits, ili))
  print('*** Dengue ***')
  for location in sorted(list(ddata[ew].keys())):
    region = NIDSS.LOCATION_TO_REGION[location]
    count = ddata[ew][location]
    print('location=%s | region=%s | count=%d' % (location, region, count))


if __name__ == '__main__':
  main()
