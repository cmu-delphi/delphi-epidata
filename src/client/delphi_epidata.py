"""
A module for DELPHI's Epidata API.

https://github.com/cmu-delphi/delphi-epidata

Notes:
 - Requires the `requests` module.
 - Compatible with Python 2 and 3.
"""

# External modules
import requests


# Because the API is stateless, the Epidata class only contains static methods
class Epidata:
  """An interface to DELPHI's Epidata API."""

  # API base url
  BASE_URL = 'https://delphi.midas.cs.cmu.edu/epidata/api.php'

  # Helper function to cast values and/or ranges to strings
  @staticmethod
  def _listitem(value):
    """Cast values and/or range to a string."""
    if isinstance(value, dict) and 'from' in value and 'to' in value:
      return str(value['from']) + '-' + str(value['to'])
    else:
      return str(value)

  # Helper function to build a list of values and/or ranges
  @staticmethod
  def _list(values):
    """Turn a list/tuple of values/ranges into a comma-separated string."""
    if not isinstance(values, (list, tuple)):
      values = [values]
    return ','.join([Epidata._listitem(value) for value in values])

  # Helper function to request and parse epidata
  @staticmethod
  def _request(params):
    """Request and parse epidata."""
    try:
      # API call
      return requests.get(Epidata.BASE_URL, params).json()
    except Exception as e:
      # Something broke
      return {'result': 0, 'message': 'error: ' + str(e)}

  # Raise an Exception on error, otherwise return epidata
  @staticmethod
  def check(resp):
    """Raise an Exception on error, otherwise return epidata."""
    if resp['result'] != 1:
      msg, code = resp['message'], resp['result']
      raise Exception('Error fetching epidata: %s. (result=%d)' % (msg, code))
    return resp['epidata']

  # Build a `range` object (ex: dates/epiweeks)
  @staticmethod
  def range(from_, to_):
    """Build a `range` object (ex: dates/epiweeks)."""
    if to_ <= from_:
      from_, to_ = to_, from_
    return {'from': from_, 'to': to_}

  # Fetch FluView data
  @staticmethod
  def fluview(regions, epiweeks, issues=None, lag=None, auth=None):
    """Fetch FluView data."""
    # Check parameters
    if regions is None or epiweeks is None:
      raise Exception('`regions` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'source': 'fluview',
      'regions': Epidata._list(regions),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
    if auth is not None:
      params['auth'] = auth
    # Make the API call
    return Epidata._request(params)

  # Fetch FluSurv data
  @staticmethod
  def flusurv(locations, epiweeks, issues=None, lag=None):
    """Fetch FluSurv data."""
    # Check parameters
    if locations is None or epiweeks is None:
      raise Exception('`locations` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'source': 'flusurv',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
    # Make the API call
    return Epidata._request(params)

  # Fetch Google Flu Trends data
  @staticmethod
  def gft(locations, epiweeks):
    """Fetch Google Flu Trends data."""
    # Check parameters
    if locations is None or epiweeks is None:
      raise Exception('`locations` and `epiweeks` are both required')
    # Set up request
    params = {
      'source': 'gft',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Google Health Trends data
  @staticmethod
  def ght(auth, locations, epiweeks, query):
    """Fetch Google Health Trends data."""
    # Check parameters
    if auth is None or locations is None or epiweeks is None or query is None:
      raise Exception('`auth`, `locations`, `epiweeks`, and `query` are all required')
    # Set up request
    params = {
      'source': 'ght',
      'auth': auth,
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
      'query': query,
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch HealthTweets data
  @staticmethod
  def twitter(auth, locations, dates=None, epiweeks=None):
    """Fetch HealthTweets data."""
    # Check parameters
    if auth is None or locations is None:
      raise Exception('`auth` and `locations` are both required')
    if not ((dates is None) ^ (epiweeks is None)):
      raise Exception('exactly one of `dates` and `epiweeks` is required')
    # Set up request
    params = {
      'source': 'twitter',
      'auth': auth,
      'locations': Epidata._list(locations),
    }
    if dates is not None:
      params['dates'] = Epidata._list(dates)
    if epiweeks is not None:
      params['epiweeks'] = Epidata._list(epiweeks)
    # Make the API call
    return Epidata._request(params)

  # Fetch Wikipedia access data
  @staticmethod
  def wiki(articles, dates=None, epiweeks=None, hours=None):
    """Fetch Wikipedia access data."""
    # Check parameters
    if articles is None:
      raise Exception('`articles` is required')
    if not ((dates is None) ^ (epiweeks is None)):
      raise Exception('exactly one of `dates` and `epiweeks` is required')
    # Set up request
    params = {
      'source': 'wiki',
      'articles': Epidata._list(articles),
    }
    if dates is not None:
      params['dates'] = Epidata._list(dates)
    if epiweeks is not None:
      params['epiweeks'] = Epidata._list(epiweeks)
    if hours is not None:
      params['hours'] = Epidata._list(hours)
    # Make the API call
    return Epidata._request(params)

  # Fetch CDC page hits
  @staticmethod
  def cdc(auth, epiweeks, locations):
    """Fetch CDC page hits."""
    # Check parameters
    if auth is None or epiweeks is None or locations is None:
      raise Exception('`auth`, `epiweeks`, and `locations` are all required')
    # Set up request
    params = {
      'source': 'cdc',
      'auth': auth,
      'epiweeks': Epidata._list(epiweeks),
      'locations': Epidata._list(locations),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Quidel data
  @staticmethod
  def quidel(auth, epiweeks, locations):
    """Fetch Quidel data."""
    # Check parameters
    if auth is None or epiweeks is None or locations is None:
      raise Exception('`auth`, `epiweeks`, and `locations` are all required')
    # Set up request
    params = {
      'source': 'quidel',
      'auth': auth,
      'epiweeks': Epidata._list(epiweeks),
      'locations': Epidata._list(locations),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch NIDSS flu data
  @staticmethod
  def nidss_flu(regions, epiweeks, issues=None, lag=None):
    """Fetch NIDSS flu data."""
    # Check parameters
    if regions is None or epiweeks is None:
      raise Exception('`regions` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'source': 'nidss_flu',
      'regions': Epidata._list(regions),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
    # Make the API call
    return Epidata._request(params)

  # Fetch NIDSS dengue data
  @staticmethod
  def nidss_dengue(locations, epiweeks):
    """Fetch NIDSS dengue data."""
    # Check parameters
    if locations is None or epiweeks is None:
      raise Exception('`locations` and `epiweeks` are both required')
    # Set up request
    params = {
      'source': 'nidss_dengue',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's forecast
  @staticmethod
  def delphi(system, epiweek):
    """Fetch Delphi's forecast."""
    # Check parameters
    if system is None or epiweek is None:
      raise Exception('`system` and `epiweek` are both required')
    # Set up request
    params = {
      'source': 'delphi',
      'system': system,
      'epiweek': epiweek,
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's digital surveillance sensors
  @staticmethod
  def sensors(auth, names, locations, epiweeks):
    """Fetch Delphi's digital surveillance sensors."""
    # Check parameters
    if auth is None or names is None or locations is None or epiweeks is None:
      raise Exception('`auth`, `names`, `locations`, and `epiweeks` are all required')
    # Set up request
    params = {
      'source': 'sensors',
      'auth': auth,
      'names': Epidata._list(names),
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's wILI nowcast
  @staticmethod
  def nowcast(locations, epiweeks):
    """Fetch Delphi's wILI nowcast."""
    # Check parameters
    if locations is None or epiweeks is None:
      raise Exception('`locations` and `epiweeks` are both required')
    # Set up request
    params = {
      'source': 'nowcast',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch API metadata
  @staticmethod
  def meta():
    """Fetch API metadata."""
    return Epidata._request({'source': 'meta'})
