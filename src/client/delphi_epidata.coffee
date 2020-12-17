###
A module for DELPHI's Epidata API.

https://github.com/cmu-delphi/delphi-epidata

Notes:
 - If running in node.js (or using browserify), there are no external
   dependencies. Otherwise, a global jQuery object named `$` must be available.
###

# Use built-in node.js modules unless jQuery is available
unless $?.getJSON?
  https = require('https')
  querystring = require('querystring')


# Because the API is stateless, the Epidata class only contains static methods
class Epidata

  # API base url
  BASE_URL = 'https://delphi.cmu.edu/epidata/api.php'

  # Helper function to cast values and/or ranges to strings
  _listitem = (value) ->
    if value.hasOwnProperty('from') and value.hasOwnProperty('to')
      return "#{value['from']}-#{value['to']}"
    else
      return "#{value}"

  # Helper function to build a list of values and/or ranges
  _list = (values) ->
    if not Array.isArray(values)
      values = [values]
    return (_listitem(value) for value in values).join(',')

  # Helper function to request and parse epidata
  _request = (callback, params) ->
    # Function to handle the API response
    handler = (data) ->
      if data?.result?
        callback(data.result, data.message, data.epidata)
      else
        callback(0, 'unknown error', null)
    # Request data from the server
    isBrowser = $?.ajax?
    data = if isBrowser then $.param(params) else querystring.stringify(params)
    fullURL = "#{BASE_URL}?#{data}"

    # decide method to avoid that we getting a 414 request too large error
    method = if fullURL.length < 2048 then 'GET' else 'POST'

    if isBrowser
      # API call with jQuery
      $.ajax({
        url: BASE_URL,
        dataType: "json",
        method: method,
        success: handler,
        data: params,
      });
    else
      # Function to handle the HTTP response
      reader = (response) ->
        text = ''
        response.setEncoding('utf8')
        response.on('data', (chunk) -> text += chunk)
        response.on('error', (e) -> error(e.message))
        response.on('end', () -> handler(JSON.parse(text)))
      # API call with Node
      if method == 'GET'
        https.get(fullURL, reader)
      else
        req = https.request(BASE_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': Buffer.byteLength(data)
          }
        }, reader)
        # Write data to request body
        req.write(data)
        req.end()

  # Build a `range` object (ex: dates/epiweeks)
  @range = (from, to) ->
    if to <= from
      [from, to] = [to, from]
    return { from: from, to: to }

  # Fetch FluView data
  @fluview: (callback, regions, epiweeks, issues, lag, auth) ->
    # Check parameters
    unless regions? and epiweeks?
      throw { msg: '`regions` and `epiweeks` are both required' }
    if issues? and lag?
      throw { msg: '`issues` and `lag` are mutually exclusive' }
    # Set up request
    params =
      'source': 'fluview'
      'regions': _list(regions)
      'epiweeks': _list(epiweeks)
    if issues?
      params.issues = _list(issues)
    if lag?
      params.lag = lag
    if auth?
      params.auth = auth
    # Make the API call
    _request(callback, params)


  # Fetch FluView metadata
  @fluview_meta: (callback) ->
    # Set up request
    params =
      'source': 'fluview_meta'
    # Make the API call
    _request(callback, params)

  # Fetch FluView clinical data
  @fluview_clinical: (callback, regions, epiweeks, issues, lag) ->
    # Check parameters
    unless regions? and epiweeks?
      throw { msg: '`regions` and `epiweeks` are both required' }
    if issues? and lag?
      throw { msg: '`issues` and `lag` are mutually exclusive' }
    # Set up request
    params =
      'source': 'fluview_clinical'
      'regions': _list(regions)
      'epiweeks': _list(epiweeks)
    if issues?
      params.issues = _list(issues)
    if lag?
      params.lag = lag
    # Make the API call
    _request(callback, params)

  # Fetch FluSurv data
  @flusurv: (callback, locations, epiweeks, issues, lag) ->
    # Check parameters
    unless locations? and epiweeks?
      throw { msg: '`locations` and `epiweeks` are both required' }
    if issues? and lag?
      throw { msg: '`issues` and `lag` are mutually exclusive' }
    # Set up request
    params =
      'source': 'flusurv'
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
    if issues?
      params.issues = _list(issues)
    if lag?
      params.lag = lag
    # Make the API call
    _request(callback, params)

  # Fetch Google Flu Trends data
  @gft: (callback, locations, epiweeks) ->
    # Check parameters
    unless locations? and epiweeks?
      throw { msg: '`locations` and `epiweeks` are both required' }
    # Set up request
    params =
      'source': 'gft'
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
    # Make the API call
    _request(callback, params)

  # Fetch Google Health Trends data
  @ght: (callback, auth, locations, epiweeks, query) ->
    # Check parameters
    unless auth? and locations? and epiweeks? and query?
      throw { msg: '`auth`, `locations`, `epiweeks`, and `query` are all required' }
    # Set up request
    params =
      'source': 'ght'
      'auth': auth
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
      'query': query
    # Make the API call
    _request(callback, params)

  # Fetch HealthTweets data
  @twitter: (callback, auth, locations, dates, epiweeks) ->
    # Check parameters
    unless auth? and locations?
      throw { msg: '`auth` and `locations` are both required' }
    unless dates? ^ epiweeks?
      throw { msg: 'exactly one of `dates` and `epiweeks` is required' }
    # Set up request
    params =
      'source': 'twitter'
      'auth': auth
      'locations': _list(locations)
    if dates?
      params.dates = _list(dates)
    if epiweeks?
      params.epiweeks = _list(epiweeks)
    # Make the API call
    _request(callback, params)

  # Fetch Wikipedia access data
  @wiki: (callback, articles, dates, epiweeks, hours, language) ->
    # Check parameters
    unless articles?
      throw { msg: '`articles` is required' }
    unless dates? ^ epiweeks?
      throw { msg: 'exactly one of `dates` and `epiweeks` is required' }
    # Set up request
    params =
      'source': 'wiki'
      'articles': _list(articles)
      'language': language || 'en'
    if dates?
      params.dates = _list(dates)
    if epiweeks?
      params.epiweeks = _list(epiweeks)
    if hours?
      params.hours = _list(hours)
    # Make the API call
    _request(callback, params)

  # Fetch CDC page hits
  @cdc: (callback, auth, epiweeks, locations) ->
    # Check parameters
    unless auth? and epiweeks? and locations?
      throw { msg: '`auth`, `epiweeks`, and `locations` are all required' }
    # Set up request
    params =
      'source': 'cdc'
      'auth': auth
      'epiweeks': _list(epiweeks)
      'locations': _list(locations)
    # Make the API call
    _request(callback, params)

  # Fetch Quidel data
  @quidel: (callback, auth, epiweeks, locations) ->
    # Check parameters
    unless auth? and epiweeks? and locations?
      throw { msg: '`auth`, `epiweeks`, and `locations` are all required' }
    # Set up request
    params =
      'source': 'quidel'
      'auth': auth
      'epiweeks': _list(epiweeks)
      'locations': _list(locations)
    # Make the API call
    _request(callback, params)

  # Fetch NoroSTAT data (point data, no min/max)
  @norostat: (callback, auth, location, epiweeks) ->
    # Check parameters
    unless auth? and location? and epiweeks?
      throw { msg: '`auth`, `location`, and `epiweeks` are all required' }
    # Set up request
    params =
      'source': 'norostat'
      'auth': auth
      'location': location
      'epiweeks': _list(epiweeks)
    # Make the API call
    _request(callback, params)

  # Fetch NoroSTAT metadata
  @meta_norostat: (callback, auth) ->
    # Check parameters
    unless auth?
      throw { msg: '`auth` is required' }
    # Set up request
    params =
      'source': 'meta_norostat'
      'auth': auth
    # Make the API call
    _request(callback, params)

  # Fetch AFHSB data (point data, no min/max)
  @afhsb: (callback, auth, locations, epiweeks, flu_types) ->
    # Check parameters
    unless auth? and locations? and epiweeks? and flu_types?
      throw { msg: '`auth`, `locations`, `epiweeks` and `flu_types` are all required' }
    # Set up request
    params =
      'source': 'afhsb'
      'auth': auth
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
      'flu_types': _list(flu_types)
    # Make the API call
    _request(callback, params)

  # Fetch AFHSB metadata
  @meta_afhsb: (callback, auth) ->
    # Check parameters
    unless auth?
      throw { msg: '`auth` is required' }
    # Set up request
    params =
      'source': 'meta_afhsb'
      'auth': auth
    # Make the API call
    _request(callback, params)

  # Fetch NIDSS flu data
  @nidss_flu: (callback, regions, epiweeks, issues, lag) ->
    # Check parameters
    unless regions? and epiweeks?
      throw { msg: '`regions` and `epiweeks` are both required' }
    if issues? and lag?
      throw { msg: '`issues` and `lag` are mutually exclusive' }
    # Set up request
    params =
      'source': 'nidss_flu'
      'regions': _list(regions)
      'epiweeks': _list(epiweeks)
    if issues?
      params.issues = _list(issues)
    if lag?
      params.lag = lag
    # Make the API call
    _request(callback, params)

  # Fetch NIDSS dengue data
  @nidss_dengue: (callback, locations, epiweeks) ->
    # Check parameters
    unless locations? and epiweeks?
      throw { msg: '`locations` and `epiweeks` are both required' }
    # Set up request
    params =
      'source': 'nidss_dengue'
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
    # Make the API call
    _request(callback, params)

  # Fetch Delphi's forecast
  @delphi: (callback, system, epiweek) ->
    # Check parameters
    unless system? and epiweek?
      throw { msg: '`system` and `epiweek` are both required' }
    # Set up request
    params =
      'source': 'delphi'
      'system': system
      'epiweek': epiweek
    # Make the API call
    _request(callback, params)

  # Fetch Delphi's digital surveillance sensors
  @sensors: (callback, auth, names, locations, epiweeks) ->
    # Check parameters
    unless auth? and names? and locations? and epiweeks?
      throw { msg: '`auth`, `names`, `locations`, and `epiweeks` are all required' }
    # Set up request
    params =
      'source': 'sensors'
      'auth': auth
      'names': _list(names)
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
    # Make the API call
    _request(callback, params)

  # Fetch Delphi's wILI nowcast
  @nowcast: (callback, locations, epiweeks) ->
    # Check parameters
    unless locations? and epiweeks?
      throw { msg: '`locations` and `epiweeks` are both required' }
    # Set up request
    params =
      'source': 'nowcast'
      'locations': _list(locations)
      'epiweeks': _list(epiweeks)
    # Make the API call
    _request(callback, params)

  # Fetch API metadata
  @meta: (callback) ->
    _request(callback, {'source': 'meta'})

  # Fetch Delphi's COVID-19 Surveillance Streams
  @covidcast: (callback, data_source, signals, time_type, geo_type, time_values, geo_value, as_of, issues, lag, format) ->
    # Check parameters
    unless data_source? and signals? and time_type? and geo_type? and time_values? and geo_value?
      throw { msg: '`data_source`, `signals`, `time_type`, `geo_type`, `time_values`, and `geo_value` are all required' }
    if issues? and lag?
      throw { msg: '`issues` and `lag` are mutually exclusive' }
    # Set up request
    params =
      'source': 'covidcast'
      'data_source': data_source
      'signals': signals
      'time_type': time_type
      'geo_type': geo_type
      'time_values': _list(time_values)
    if Array.isArray(geo_value)
      params.geo_values = geo_value.join(',')
    else
      params.geo_value = geo_value
    if as_of?
      params.as_of = as_of
    if issues?
      params.issues = _list(issues)
    if lag?
      params.lag = lag
    if format?
      params.format = format
    # Make the API call
    _request(callback, params)

  # Fetch Delphi's COVID-19 Surveillance Streams metadata
  @covidcast_meta: (callback) ->
    _request(callback, {'source': 'covidcast_meta'})

  # Fetch COVID hospitalization data
  @covid_hosp: (callback, states, dates, issues) ->
    # Check parameters
    unless states? and dates?
      throw { msg: '`states` and `dates` are both required' }
    # Set up request
    params =
      'source': 'covid_hosp'
      'states': _list(states)
      'dates': _list(dates)
    if issues?
      params.issues = _list(issues)
    # Make the API call
    _request(callback, params)

  # Fetch COVID hospitalization data for specific facilities
  @covid_hosp_facility: (callback, hospital_pks, collection_weeks, publication_dates) ->
    # Check parameters
    unless hospital_pks? and collection_weeks?
      throw { msg: '`hospital_pks` and `collection_weeks` are both required' }
    # Set up request
    params =
      'source': 'covid_hosp_facility'
      'hospital_pks': _list(hospital_pks)
      'collection_weeks': _list(collection_weeks)
    if publication_dates?
      params.publication_dates = _list(publication_dates)
    # Make the API call
    _request(callback, params)

# Export the API to the global environment
(exports ? window).Epidata = Epidata
