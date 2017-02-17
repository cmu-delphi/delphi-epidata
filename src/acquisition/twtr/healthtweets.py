'''
===============
=== Purpose ===
===============

Scrapes daily state values from healthtweets.org


=================
=== Changelog ===
=================

2017-02-16
 + username/password command line arguments
2015-05-22
 + Runtime arguments
 * Returning num and total insterad of normalized value
 * Returning dictionary (by date) instead of list
 * Replaced external epidate.py with built-in datetime
 * Fetching daily values instead of weekly values
2015-03-??
 * Original version
'''

# built-in libraries
import argparse
from datetime import datetime, timedelta
import json
# external libraries
import requests
# local files
from pageparser import PageParser

class HealthTweets:

  # mapping from state abbreviations to location codes used by healthtweets.org
  STATE_CODES = {'AL': 3024, 'AK': 3025, 'AZ': 3026, 'AR': 3027, 'CA': 440, 'CO': 3029, 'CT': 3030, 'DE': 3031, 'DC': 3032, 'FL': 3033, 'GA': 3034, 'HI': 3035, 'ID': 3036, 'IL': 3037, 'IN': 3038, 'IA': 3039, 'KS': 3040, 'KY': 3041, 'LA': 2183, 'ME': 3043, 'MD': 3044, 'MA': 450, 'MI': 3046, 'MN': 3047, 'MS': 3048, 'MO': 3049, 'MT': 3050, 'NE': 3051, 'NV': 3052, 'NH': 3053, 'NJ': 478, 'NM': 2225, 'NY': 631, 'NC': 3057, 'ND': 3058, 'OH': 3059, 'OK': 3060, 'OR': 281, 'PA': 3062, 'RI': 3063, 'SC': 3064, 'SD': 3065, 'TN': 3066, 'TX': 3067, 'UT': 2272, 'VT': 3069, 'VA': 3070, 'WA': 3071, 'WV': 3072, 'WI': 3073, 'WY': 3074}

  def __init__(self, username, password, debug=False):
    self.debug = debug
    self.session = requests.Session()
    # spoof a web browser
    self.session.headers.update({
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    })
    # get the login token
    response = self._go('http://www.healthtweets.org/accounts/login')
    token = self._get_token(response.text)
    if self.debug:
      print('token=%s'%(token))
    data = {
      'csrfmiddlewaretoken': token,
      'username': username,
      'password': password,
      'next': '/',
    }
    # login to the site
    response = self._go('http://www.healthtweets.org/accounts/login', data=data)
    if response.status_code != 200 or 'Your username and password' in response.text:
      raise Exception('login failed')

  def get_values(self, state, date1, date2):
    '''
    state: two-letter state abbreviation (see STATE_CODES)
    date1: the first date in the range, inclusive (format: YYYY-MM-DD)
    date2: the last date in the range, inclusive (format: YYYY-MM-DD)
    returns a dictionary (by date) of number of flu tweets (num) and total tweets (total)
    '''
    # get raw values (number of flu tweets) and normalized values (flu tweets as a percent of total tweets)
    raw_values = self._get_values(state, date1, date2, False)
    normalized_values = self._get_values(state, date1, date2, True)
    values = {}
    # save the raw number and calculate the total
    for date in raw_values.keys():
      if normalized_values[date] == 0:
        continue
      values[date] = {
        'num': round(raw_values[date]),
        'total': round(100 * raw_values[date] / normalized_values[date]),
      }
      print(date, raw_values[date], normalized_values[date])
    return values

  def _get_values(self, state, date1, date2, normalized):
    if state not in HealthTweets.STATE_CODES:
      raise Exception('invalid state')
    state_code = HealthTweets.STATE_CODES[state]
    d1, d2 = datetime.strptime(date1, '%Y-%m-%d'), datetime.strptime(date2, '%Y-%m-%d')
    s1, s2 = d1.strftime('%m%%2F%d%%2F%Y'), d2.strftime('%m%%2F%d%%2F%Y')
    count_type = 'normalized' if normalized else 'raw'
    url = 'http://www.healthtweets.org/trends/plot?resolution=Day&count_type=%s&dayNum=%d&from=%s&to=%s&plot1_disease=65&location_plot1=%d'%(count_type, (d2 - d1).days, s1, s2, state_code)
    response = self._go('http://www.healthtweets.org/trends/plot?resolution=Day&count_type=%s&dayNum=%d&from=%s&to=%s&plot1_disease=65&location_plot1=%d'%(count_type, (d2 - d1).days, s1, s2, state_code))
    #print(state, date1, date2, normalized)
    #print(url)
    #print(response.status_code)
    if response.status_code != 200:
      raise Exception('plot status is ' + str(response.status_code) + ' (when was data last updated?)')
    lines = [line.strip() for line in response.text.split('\n')]
    data_line = [line for line in lines if line[:16] == 'var chartData = ']
    if len(data_line) != 1:
      raise Exception('lookup failed')
    values = json.loads(data_line[0][16:-1])
    return dict([(datetime.strptime(v[0], '%m/%d/%Y').strftime('%Y-%m-%d'), float(v[1])) for v in values])

  def check_state(self, state):
    '''
    Sanity checks state code mapping.
    state: two-letter state abbreviation (see STATE_CODES)
    returns the full state name associated with the state abbreviation
    '''
    if state not in HealthTweets.STATE_CODES:
      raise Exception('invalid state')
    state_code = HealthTweets.STATE_CODES[state]
    response = self._go('http://www.healthtweets.org/trends/plot?resolution=Day&count_type=normalized&dayNum=7&from=01%%2F01%%2F2015&to=01%%2F07%%2F2015&plot1_disease=65&location_plot1=%d'%(state_code))
    lines = [line.strip() for line in response.text.split('\n')]
    data_line = [line for line in lines if line[:29] == 'var plotNames = ["Influenza (']
    if len(data_line) == 0:
      raise Exception('check failed')
    name = data_line[0][29:]
    name = name.split('(')[0]
    return name.strip()

  def _get_token(self, html):
    page = PageParser.parse(html)
    hidden = PageParser.filter_all(page, [('html',), ('body',), ('div',), ('div',), ('div',), ('form',), ('input',)])
    return hidden['attrs']['value']

  def _go(self, url, method=None, referer=None, data=None):
    if self.debug:
      print('%s'%(url))
    if method is None:
      if data is None:
        method = self.session.get
      else:
        method = self.session.post
    response = method(url, headers={'referer': referer}, data=data)
    html = response.text
    if self.debug:
      for item in response.history:
        print(' [%d to %s]'%(item.status_code, item.headers['Location']))
      print(' %d (%d bytes)'%(response.status_code, len(html)))
    return response


def main():
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument('username', action='store', type=str, help='healthtweets.org username')
  parser.add_argument('password', action='store', type=str, help='healthtweets.org password')
  parser.add_argument('state', action='store', type=str, choices=list(HealthTweets.STATE_CODES.keys()), help='U.S. state (ex: TX)')
  parser.add_argument('date1', action='store', type=str, help='first date, inclusive (ex: 2015-01-01)')
  parser.add_argument('date2', action='store', type=str, help='last date, inclusive (ex: 2015-01-01)')
  parser.add_argument('-d', '--debug', action='store_const', const=True, default=False, help='enable debug mode')
  args = parser.parse_args()

  ht = HealthTweets(args.username, args.password, debug=args.debug)
  values = ht.get_values(args.state, args.date1, args.date2)
  print('Daily counts in %s from %s to %s:'%(ht.check_state(args.state), args.date1, args.date2))
  for date in sorted(list(values.keys())):
    print('%s: num=%-4d total=%-5d (%.3f%%)'%(date, values[date]['num'], values[date]['total'], 100 * values[date]['num'] / values[date]['total']))


if __name__ == '__main__':
  main()
