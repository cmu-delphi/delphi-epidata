"""
A module for DELPHI's Epidata API.

https://github.com/cmu-delphi/delphi-epidata

Notes:
 - Requires the `requests` module.
 - Compatible with Python 2 and 3.
"""

# External modules
import requests
import asyncio
from tenacity import retry, stop_after_attempt

from aiohttp import ClientSession, TCPConnector
from pkg_resources import get_distribution, DistributionNotFound

# Obtain package version for the user-agent. Uses the installed version by
# preference, even if you've installed it and then use this script independently
# by accident.
try:
  _version = get_distribution('delphi-epidata').version
except DistributionNotFound:
  _version = "0.script"

_HEADERS = {
  "user-agent": "delphi_epidata/" + _version
}

# Because the API is stateless, the Epidata class only contains static methods
class Epidata:
  """An interface to DELPHI's Epidata API."""

  # API base url
  BASE_URL = 'https://delphi.cmu.edu/epidata/api.php'

  client_version = _version

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

  @staticmethod
  @retry(reraise=True, stop=stop_after_attempt(2))
  def _request_with_retry(params):
    """Make request with a retry if an exception is thrown."""
    req = requests.get(Epidata.BASE_URL, params, headers=_HEADERS)
    if req.status_code == 414:
      req = requests.post(Epidata.BASE_URL, params, headers=_HEADERS)
    return req

  @staticmethod
  def _request(params):
    """Request and parse epidata.

    We default to GET since it has better caching and logging
    capabilities, but fall back to POST if the request is too
    long and returns a 414.
    """
    try:
      return Epidata._request_with_retry(params).json()
    except Exception as e:
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
      'endpoint': 'fluview',
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

  # Fetch FluView metadata
  @staticmethod
  def fluview_meta():
    """Fetch FluView metadata."""
    # Set up request
    params = {
      'endpoint': 'fluview_meta',
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch FluView clinical data
  @staticmethod
  def fluview_clinical(regions, epiweeks, issues=None, lag=None):
    """Fetch FluView clinical data."""
    # Check parameters
    if regions is None or epiweeks is None:
      raise Exception('`regions` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'endpoint': 'fluview_clinical',
      'regions': Epidata._list(regions),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
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
      'endpoint': 'flusurv',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
    # Make the API call
    return Epidata._request(params)

  # Fetch PAHO Dengue data
  @staticmethod
  def paho_dengue(regions, epiweeks, issues=None, lag=None):
    """Fetch PAHO Dengue data."""
    # Check parameters
    if regions is None or epiweeks is None:
      raise Exception('`regions` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'endpoint': 'paho_dengue',
      'regions': Epidata._list(regions),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
    # Make the API call
    return Epidata._request(params)

  # Fetch ECDC ILI data
  @staticmethod
  def ecdc_ili(regions, epiweeks, issues=None, lag=None):
    """Fetch ECDC ILI data."""
    # Check parameters
    if regions is None or epiweeks is None:
      raise Exception('`regions` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'endpoint': 'ecdc_ili',
      'regions': Epidata._list(regions),
      'epiweeks': Epidata._list(epiweeks),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag
    # Make the API call
    return Epidata._request(params)

  # Fetch KCDC ILI data
  @staticmethod
  def kcdc_ili(regions, epiweeks, issues=None, lag=None):
    """Fetch KCDC ILI data."""
    # Check parameters
    if regions is None or epiweeks is None:
      raise Exception('`regions` and `epiweeks` are both required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'endpoint': 'kcdc_ili',
      'regions': Epidata._list(regions),
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
      'endpoint': 'gft',
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
      'endpoint': 'ght',
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
      'endpoint': 'twitter',
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
  def wiki(articles, dates=None, epiweeks=None, hours=None, language='en'):
    """Fetch Wikipedia access data."""
    # Check parameters
    if articles is None:
      raise Exception('`articles` is required')
    if not ((dates is None) ^ (epiweeks is None)):
      raise Exception('exactly one of `dates` and `epiweeks` is required')
    # Set up request
    params = {
      'endpoint': 'wiki',
      'articles': Epidata._list(articles),
      'language': language,
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
      'endpoint': 'cdc',
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
      'endpoint': 'quidel',
      'auth': auth,
      'epiweeks': Epidata._list(epiweeks),
      'locations': Epidata._list(locations),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch NoroSTAT data (point data, no min/max)
  @staticmethod
  def norostat(auth, location, epiweeks):
    """Fetch NoroSTAT data (point data, no min/max)."""
    # Check parameters
    if auth is None or location is None or epiweeks is None:
      raise Exception('`auth`, `location`, and `epiweeks` are all required')
    # Set up request
    params = {
      'endpoint': 'norostat',
      'auth': auth,
      'location': location,
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch NoroSTAT metadata
  @staticmethod
  def meta_norostat(auth):
    """Fetch NoroSTAT metadata."""
    # Check parameters
    if auth is None:
      raise Exception('`auth` is required')
    # Set up request
    params = {
      'endpoint': 'meta_norostat',
      'auth': auth,
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch AFHSB data
  @staticmethod
  def afhsb(auth, locations, epiweeks, flu_types):
    """Fetch AFHSB data (point data, no min/max)."""
    # Check parameters
    if auth is None or locations is None or epiweeks is None or flu_types is None:
      raise Exception('`auth`, `locations`, `epiweeks` and `flu_types` are all required')

    loc_exception = 'Location parameter  `{}` is invalid. Valid `location` parameters are: '\
      '`hhs[1-10]`, `cen[1-9]`, 2-letter state code or 3-letter country code.'
    for location in locations:
      location = location.lower()
      if (location.startswith('hhs') or location.startswith('cen')):
        prefix, postfix = location[:3], location[3:]
        if (postfix.isnumeric()):
          region_num = int(postfix)
          if (region_num < 1 or region_num > 10 or (region_num == 10 and prefix == 'cen')):
            raise Exception(loc_exception.format(location))
        else:
          raise Exception(loc_exception.format(location))
      elif (len(location) < 2 or len(location) > 3):
        raise Exception(loc_exception.format(location))

    flu_exception = 'Flu-type parameters `{}` is invalid. Valid flu-type parameters are: '\
      '`flu1`, `flu2`, `flu3`, `ili`, `flu2-flu1`, `flu3-flu2`, `ili-flu3`.'
    valid_flu_types = ['flu1', 'flu2', 'flu3', 'ili', 'flu2-flu1', 'flu3-flu2', 'ili-flu3']
    for flu_type in flu_types:
      if (not flu_type in valid_flu_types):
        raise Exception(flu_exception.format(flu_type))

    # Set up request
    params = {
      'endpoint': 'afhsb',
      'auth': auth,
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
      'flu_types': Epidata._list(flu_types)
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch AFHSB metadata
  @staticmethod
  def meta_afhsb(auth):
    """Fetch AFHSB metadata."""
    # Check parameters
    if auth is None:
      raise Exception('`auth` is required')
    # Set up request
    params = {
      'endpoint': 'meta_afhsb',
      'auth': auth,
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
      'endpoint': 'nidss_flu',
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
      'endpoint': 'nidss_dengue',
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
      'endpoint': 'delphi',
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
      'endpoint': 'sensors',
      'auth': auth,
      'names': Epidata._list(names),
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's dengue digital surveillance sensors
  @staticmethod
  def dengue_sensors(auth, names, locations, epiweeks):
    """Fetch Delphi's digital surveillance sensors."""
    # Check parameters
    if auth is None or names is None or locations is None or epiweeks is None:
      raise Exception('`auth`, `names`, `locations`, and `epiweeks` are all required')
    # Set up request
    params = {
      'endpoint': 'dengue_sensors',
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
      'endpoint': 'nowcast',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's dengue nowcast
  @staticmethod
  def dengue_nowcast(locations, epiweeks):
    """Fetch Delphi's dengue nowcast."""
    # Check parameters
    if locations is None or epiweeks is None:
      raise Exception('`locations` and `epiweeks` are both required')
    # Set up request
    params = {
      'endpoint': 'dengue_nowcast',
      'locations': Epidata._list(locations),
      'epiweeks': Epidata._list(epiweeks),
    }
    # Make the API call
    return Epidata._request(params)

  # Fetch API metadata
  @staticmethod
  def meta():
    """Fetch API metadata."""
    return Epidata._request({'endpoint': 'meta'})

  # Fetch Delphi's COVID-19 Surveillance Streams
  @staticmethod
  def covidcast(
          data_source, signals, time_type, geo_type,
          time_values, geo_value, as_of=None, issues=None, lag=None, **kwargs):
    """Fetch Delphi's COVID-19 Surveillance Streams"""
    # also support old parameter name
    if signals is None and 'signal' in kwargs:
      signals=kwargs['signal']
    # Check parameters
    if data_source is None or signals is None or time_type is None or geo_type is None or time_values is None or geo_value is None:
      raise Exception('`data_source`, `signals`, `time_type`, `geo_type`, `time_values`, and `geo_value` are all required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'endpoint': 'covidcast',
      'data_source': data_source,
      'signals': Epidata._list(signals),
      'time_type': time_type,
      'geo_type': geo_type,
      'time_values': Epidata._list(time_values)
    }

    if isinstance(geo_value, (list, tuple)):
      params['geo_values'] = ','.join(geo_value)
    else:
      params['geo_value'] = geo_value
    if as_of is not None:
      params['as_of'] = as_of
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag

    if 'format' in kwargs:
      params['format'] = kwargs['format']

    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's COVID-19 Surveillance Streams metadata
  @staticmethod
  def covidcast_meta():
    """Fetch Delphi's COVID-19 Surveillance Streams metadata"""
    return Epidata._request({'endpoint': 'covidcast_meta'})

  # Fetch COVID hospitalization data
  @staticmethod
  def covid_hosp(states, dates, issues=None, as_of=None):
    """Fetch COVID hospitalization data."""
    # Check parameters
    if states is None or dates is None:
      raise Exception('`states` and `dates` are both required')
    # Set up request
    params = {
      'endpoint': 'covid_hosp',
      'states': Epidata._list(states),
      'dates': Epidata._list(dates),
    }
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if as_of is not None:
      params['as_of'] = as_of
    # Make the API call
    return Epidata._request(params)

  # Fetch COVID hospitalization data for specific facilities
  @staticmethod
  def covid_hosp_facility(
      hospital_pks, collection_weeks, publication_dates=None):
    """Fetch COVID hospitalization data for specific facilities."""
    # Check parameters
    if hospital_pks is None or collection_weeks is None:
      raise Exception('`hospital_pks` and `collection_weeks` are both required')
    # Set up request
    params = {
      'source': 'covid_hosp_facility',
      'hospital_pks': Epidata._list(hospital_pks),
      'collection_weeks': Epidata._list(collection_weeks),
    }
    if publication_dates is not None:
      params['publication_dates'] = Epidata._list(publication_dates)
    # Make the API call
    return Epidata._request(params)

  # Lookup COVID hospitalization facility identifiers
  @staticmethod
  def covid_hosp_facility_lookup(
      state=None, ccn=None, city=None, zip=None, fips_code=None):
    """Lookup COVID hospitalization facility identifiers."""
    # Set up request
    params = {'source': 'covid_hosp_facility_lookup'}
    if state is not None:
      params['state'] = state
    elif ccn is not None:
      params['ccn'] = ccn
    elif city is not None:
      params['city'] = city
    elif zip is not None:
      params['zip'] = zip
    elif fips_code is not None:
      params['fips_code'] = fips_code
    else:
      raise Exception('one of `state`, `ccn`, `city`, `zip`, or `fips_code` is required')
    # Make the API call
    return Epidata._request(params)

  # Fetch Delphi's COVID-19 Nowcast sensors
  @staticmethod
  def covidcast_nowcast(
          data_source, signals, sensor_names, time_type, geo_type,
          time_values, geo_value, as_of=None, issues=None, lag=None, **kwargs):
    """Fetch Delphi's COVID-19 Nowcast sensors"""
    # Check parameters
    if data_source is None or signals is None or time_type is None or geo_type is None or time_values is None or geo_value is None or sensor_names is None:
      raise Exception('`data_source`, `signals`, `sensor_names`, `time_type`, `geo_type`, `time_values`, and `geo_value` are all required')
    if issues is not None and lag is not None:
      raise Exception('`issues` and `lag` are mutually exclusive')
    # Set up request
    params = {
      'source': 'covidcast_nowcast',
      'data_source': data_source,
      'signals': Epidata._list(signals),
      'sensor_names': Epidata._list(sensor_names),
      'time_type': time_type,
      'geo_type': geo_type,
      'time_values': Epidata._list(time_values)
    }

    if isinstance(geo_value, (list, tuple)):
      params['geo_values'] = ','.join(geo_value)
    else:
      params['geo_value'] = geo_value
    if as_of is not None:
      params['as_of'] = as_of
    if issues is not None:
      params['issues'] = Epidata._list(issues)
    if lag is not None:
      params['lag'] = lag

    if 'format' in kwargs:
      params['format'] = kwargs['format']

    # Make the API call
    return Epidata._request(params)

  @staticmethod
  def async_epidata(param_list, batch_size=50):
    """Make asynchronous Epidata calls for a list of parameters."""
    async def async_get(params, session):
      """Helper function to make Epidata GET requests."""
      async with session.get(Epidata.BASE_URL, params=params) as response:
        response.raise_for_status()
        return await response.json(), params

    async def async_make_calls(param_combos):
      """Helper function to asynchronously make and aggregate Epidata GET requests."""
      tasks = []
      connector = TCPConnector(limit=batch_size)
      async with ClientSession(connector=connector, headers=_HEADERS) as session:
        for param in param_combos:
          task = asyncio.ensure_future(async_get(param, session))
          tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(async_make_calls(param_list))
    responses = loop.run_until_complete(future)
    return responses
