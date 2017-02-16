'''
===============
=== Purpose ===
===============

Scrapes weekly flu data from Taiwan's National Infectious Disease Statistics
System (NIDSS): http://nidss.cdc.gov.tw/en/


=================
=== Changelog ===
=================

2016-07-19
 + Sample/debug usage in function `main`
 * Update for change to NIDSS website (__EVENTVALIDATION -> __VIEWSTATEGENERATOR)
2015-10-14
 * Update for change to NIDSS website (page starts on flu by default now)
2015-08-20
 + Aggregate dengue data
2015-08-10
 * Original version, inspired by healthtweets.py
'''

# built-in libraries
import argparse
import base64
import re
import urllib.parse
# external libraries
import requests
# local files
from epiweek import range_epiweeks, add_epiweeks, delta_epiweeks


class NIDSS:
  ''' An API for scraping the NIDSS site '''

  # The page where the flu data is kept
  BASE_URL = 'http://nidss.cdc.gov.tw/en/CDCWNH01.aspx?dc=wnh'

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

  def __init__(self):
    # Start a new session
    self.client = requests.Session()
    # Spoof the user agent
    self.client.headers.update({
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36',
    })
    # Get the required metadata
    response = self.client.get(NIDSS.BASE_URL)
    if response.status_code != 200:
      raise Exception('initial request failed [%d]' % response.status_code)
    self.latest_week, self.release_date = self._get_metadata(response.text)
    magic_params = self._get_magic_paramters(response.text)
    ## Switch to Influenza
    #epi_params = self._get_epi_parameters(self.latest_week, self.latest_week, False)
    #event_params = self._get_event_parameters('ctl00$NIDSSContentPlace$CDCWNH_query1$ICD_CTGRY')
    #data = {}
    #data.update(magic_params)
    #data.update(epi_params)
    #data.update(event_params)
    #response = self.client.post(NIDSS.BASE_URL, data=data)
    #if response.status_code != 200:
    #  raise Exception('category change failed [%d]' % response.status_code)
    # Get the required metadata
    self.magic_params = self._get_magic_paramters(response.text)

  def _get_metadata(self, html):
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

  def _get_magic_paramters(self, html):
    lines = [line.strip() for line in html.split('\n') if 'input type="hidden"' in line]
    params = {}
    for line in lines:
      name, value = None, None
      parts = line.split(' ')
      for part in parts:
        if part[:5] == 'name=':
          name = part[6:-1]
        if part[:6] == 'value=':
          value = part[7:-1]
      if name is not None and value is not None:
        params[name] = value
    #if '__VIEWSTATE' not in params or '__EVENTVALIDATION' not in params:
    if '__VIEWSTATE' not in params or '__VIEWSTATEGENERATOR' not in params:
      raise Exception('magic parameters not found')
    return params

  def _get_event_parameters(self, target=None):
    params = {
      '__EVENTARGUMENT': '',
      '__LASTFOCUS': '',
    }
    if target is not None:
      params['__EVENTTARGET'] = target
    return params

  def _get_epi_parameters(self, yearweek_start, yearweek_end, influenza):
    category = urllib.parse.unquote('%E9%A1%9E%E6%B5%81%E6%84%9F')
    year1, week1 = yearweek_start // 100, yearweek_start % 100
    year2, week2 = yearweek_end // 100, yearweek_end % 100
    if influenza:
      age, sub = 'rb_AGE2_0', '4'
    else:
      age, sub = 'rb_AGE1_0', '1'
    return {
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ddl_DateType': 'yw',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ddl_yw_y_s': '%04d' % (year1),
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ddl_yw_w_s': '%02d' % (week1),
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ddl_yw_y_e': '%04d' % (year2),
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ddl_yw_w_e': '%02d' % (week2),
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ddl_CASE_TYPE': '[1]',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ICD_CTGRY': category,
      'ctl00$NIDSSContentPlace$CDCWNH_query1$ICD_SUBCTGRY': sub,
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA0': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA1': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA2': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA3': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA4': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA5': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$cb_AREA6': 'on',
      'ctl00$NIDSSContentPlace$CDCWNH_query1$AGE': age,
    }

  def _parse_table(self, html):
    # Just a quick hack to extract values from an HTML table
    html = html.strip()
    html = html[html.find('</tr>') + 9:-19]
    rows = html.split('</tr><tr>')
    for (i, row) in enumerate(rows):
      row = row.replace('/', '')
      row = row.replace('<th>', '<td>')
      row = [x.strip() for x in row.split('<td>') if x != '']
      rows[i] = row
    header, data = rows[0], rows[1:]
    locations = []
    for j in range(len(data)):
      locations.append(data[j][0])
      data[j] = data[j][1:]
    result = {}
    for i in range(len(header)):
      week = int(header[i])
      for j in range(len(data)):
        location = locations[j]
        if week not in result:
          result[week] = {}
        result[week][location] = data[j][i]
    # Return results indexed by week and location
    return result

  def get_latest_week(self):
    return self.latest_week

  def get_release_date(self):
    return self.release_date

  def get_flu_data(self, first_week, last_week):
    # Check week order
    if first_week > last_week:
      first_week, last_week = last_week, first_week
    # Bounds check
    if not 200814 <= first_week <= self.latest_week:
      raise Exception('first week out of range')
    if not 200814 <= last_week <= self.latest_week:
      raise Exception('last week out of range')
    # Update the "page"
    epi_params = self._get_epi_parameters(first_week, last_week, True)
    event_params = self._get_event_parameters()
    data = {
      'ctl00$NIDSSContentPlace$CDCWNH_query1$btnSend': 'Query',
    }
    data.update(self.magic_params)
    data.update(epi_params)
    data.update(event_params)
    response = self.client.post(NIDSS.BASE_URL, data=data)
    if response.status_code != 200:
      raise Exception('query failed [%d]' % response.status_code)
    magic_params = self._get_magic_paramters(response.text)
    # Export ILI
    data = {
      'ctl00$NIDSSContentPlace$btnExcel1.x': '0',
      'ctl00$NIDSSContentPlace$btnExcel1.y': '0',
    }
    data.update(magic_params)
    data.update(epi_params)
    response = self.client.post(NIDSS.BASE_URL, data=data)
    if response.status_code != 200:
      raise Exception('export ILI failed [%d]' % response.status_code)
    ili = response.text
    # Export visits
    data = {
      'ctl00$NIDSSContentPlace$btnExcel2.x': '0',
      'ctl00$NIDSSContentPlace$btnExcel2.y': '0',
    }
    data.update(magic_params)
    data.update(epi_params)
    response = self.client.post(NIDSS.BASE_URL, data=data)
    if response.status_code != 200:
      raise Exception('export visits failed [%d]' % response.status_code)
    visits = response.text
    # Parse the data
    ili, visits = self._parse_table(ili), self._parse_table(visits)
    weeks1, weeks2 = sorted(list(ili.keys())), sorted(list(visits.keys()))
    # Sanity check
    if weeks1 != weeks2:
      raise Exception('ILI and visits are reported on different weeks')
    # Merge ILI and visits
    data = {}
    for week in weeks1:
      data[week] = {}
      for location in ili[week].keys():
        data[week][location] = {
          'ili': float(ili[week][location]),
          'visits': int(visits[week][location]),
        }
    # Return results indexed by week and location
    return data

  def get_dengue_data(self, first_week, last_week):
    return NIDSS.get_dengue_data()

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
  parser.add_argument('epiweek', action='store', type=int, help='fetch data on this epiweek (ex: 201537)')
  args = parser.parse_args()
  ew = args.epiweek

  # Get the data
  api = NIDSS()
  fdata = api.get_flu_data(ew, ew)
  ddata = api.get_dengue_data(ew, ew)

  # Print the results
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
