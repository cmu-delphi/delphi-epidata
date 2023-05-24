# A module for DELPHI's Epidata API.
#
# https://github.com/cmu-delphi/delphi-epidata
#
# Notes:
#  - Requires the `httr` library.

# External libraries
library(httr)


# Because the API is stateless, the Epidata class only contains static methods
Epidata <- (function() {

  # API base url
  BASE_URL <- getOption('epidata.url', default = 'https://api.delphi.cmu.edu/epidata/')

  client_version <- '0.4.12'

  auth <- getOption("epidata.auth", default = NA)

  client_user_agent <- user_agent(paste("delphi_epidata/", client_version, " (R)", sep=""))

  # Helper function to cast values and/or ranges to strings
  .listitem <- function(value) {
    if(is.list(value) && 'from' %in% names(value) && 'to' %in% names(value)) {
      return(paste0(toString(value$from), '-', toString(value$to)))
    } else {
      return(toString(value))
    }
  }

  # Helper function to build a list of values and/or ranges
  .list <- function(values) {
    if(!is.list(values) || ('from' %in% names(values) && 'to' %in% names(values))) {
      values <- list(values)
    }
    return(paste(sapply(values, .listitem), collapse=','))
  }

  # Helper function to request and parse epidata
  .request <- function(params) {
    headers <- add_headers(Authorization = ifelse(is.na(auth), "", paste("Bearer", auth)))
    url <- paste(BASE_URL, params$endpoint, sep="")
    params <- within(params, rm(endpoint))
    # API call
    res <- GET(url,
               client_user_agent,
               headers,
               query=params)
    if (res$status_code == 414) {
      res <- POST(url,
                  client_user_agent,
                  headers,
                  body=params, encode='form')
    }
    if (res$status_code != 200) {
      # 500, 429, 401 are possible
      msg <- "fetch data from API"
      if (http_type(res) == "text/html") {
        # grab the error information out of the returned HTML document
        msg <- paste(msg, ":", xml2::xml_text(xml2::xml_find_all(
          xml2::read_html(content(res, 'text')),
          "//p"
        )))
      }
      stop_for_status(res, task = msg)
    }
    return(content(res, 'parsed'))
  }

  # Build a `range` object (ex: dates/epiweeks)
  range <- function(from, to) {
    if(to <= from) {
        temp <- to
        to <- from
        from <- temp
    }
    return(list(from=from, to=to))
  }

  # Fetch FluView data
  fluview <- function(regions, epiweeks, issues, lag, auth) {
    # Check parameters
    if(missing(regions) || missing(epiweeks)) {
      stop('`regions` and `epiweeks` are both required')
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    # Set up request
    params <- list(
      endpoint = 'fluview',
      regions = .list(regions),
      epiweeks = .list(epiweeks)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    if(!missing(auth)) {
      params$auth <- auth
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch FluView metadata
  fluview_meta <- function() {
    # Set up request
    params <- list(
      endpoint = 'fluview_meta'
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch FluView virological data
  fluview_clinical <- function(regions, epiweeks, issues, lag) {
    # Check parameters
    if(missing(regions) || missing(epiweeks)) {
      stop('`regions` and `epiweeks` are both required')
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    # Set up request
    params <- list(
      endpoint = 'fluview_clinical',
      regions = .list(regions),
      epiweeks = .list(epiweeks)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch FluSurv data
  flusurv <- function(locations, epiweeks, issues, lag) {
    # Check parameters
    if(missing(locations) || missing(epiweeks)) {
      stop('`locations` and `epiweeks` are both required')
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    # Set up request
    params <- list(
      endpoint = 'flusurv',
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch ECDC data
  ecdc_ili <- function(regions, epiweeks, issues, lag) {
    # Check parameters
    if(missing(regions) || missing(epiweeks)) {
      stop('`regions` and `epiweeks` are both required')
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    # Set up request
    params <- list(
      endpoint = 'ecdc_ili',
      regions = .list(regions),
      epiweeks = .list(epiweeks)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch KCDC data
  kcdc_ili <- function(regions, epiweeks, issues, lag) {
    # Check parameters
    if(missing(regions) || missing(epiweeks)) {
      stop('`regions` and `epiweeks` are both required')
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    # Set up request
    params <- list(
      endpoint = 'kcdc_ili',
      regions = .list(regions),
      epiweeks = .list(epiweeks)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    # Make the API call
    return(.request(params))
  }


  # Fetch Google Flu Trends data
  gft <- function(locations, epiweeks) {
    # Check parameters
    if(missing(locations) || missing(epiweeks)) {
      stop('`locations` and `epiweeks` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'gft',
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Google Health Trends data
  ght <- function(auth, locations, epiweeks, query) {
    # Check parameters
    if(missing(auth) || missing(locations) || missing(epiweeks) || missing(query)) {
      stop('`auth`, `locations`, `epiweeks`, and `query` are all required')
    }
    # Set up request
    params <- list(
      endpoint = 'ght',
      auth = auth,
      locations = .list(locations),
      epiweeks = .list(epiweeks),
      query = query
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch HealthTweets data
  twitter <- function(auth, locations, dates, epiweeks) {
    # Check parameters
    if(missing(auth) || missing(locations)) {
      stop('`auth` and `locations` are both required')
    }
    if(!xor(missing(dates), missing(epiweeks))) {
      stop('exactly one of `dates` and `epiweeks` is required')
    }
    # Set up request
    params <- list(
      endpoint = 'twitter',
      auth = auth,
      locations = .list(locations)
    )
    if(!missing(dates)) {
      params$dates <- .list(dates)
    }
    if(!missing(epiweeks)) {
      params$epiweeks <- .list(epiweeks)
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch Wikipedia access data
  wiki <- function(articles, dates, epiweeks, hours, language='en') {
    # Check parameters
    if(missing(articles)) {
      stop('`articles` is required')
    }
    if(!xor(missing(dates), missing(epiweeks))) {
      stop('exactly one of `dates` and `epiweeks` is required')
    }
    # Set up request
    params <- list(
      endpoint = 'wiki',
      articles = .list(articles),
      language = language
    )
    if(!missing(dates)) {
      params$dates <- .list(dates)
    }
    if(!missing(epiweeks)) {
      params$epiweeks <- .list(epiweeks)
    }
    if(!missing(hours)) {
      params$hours <- .list(hours)
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch CDC page hits
  cdc <- function(auth, epiweeks, locations) {
    # Check parameters
    if(missing(auth) || missing(epiweeks) || missing(locations)) {
      stop('`auth`, `epiweeks`, and `locations` are all required')
    }
    # Set up request
    params <- list(
      endpoint = 'cdc',
      auth = auth,
      epiweeks = .list(epiweeks),
      locations = .list(locations)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Quidel data
  quidel <- function(auth, epiweeks, locations) {
    # Check parameters
    if(missing(auth) || missing(epiweeks) || missing(locations)) {
      stop('`auth`, `epiweeks`, and `locations` are all required')
    }
    # Set up request
    params <- list(
      endpoint = 'quidel',
      auth = auth,
      epiweeks = .list(epiweeks),
      locations = .list(locations)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch NoroSTAT data (point data, no min/max)
  norostat <- function(auth, location, epiweeks) {
    # Check parameters
    if(missing(auth) || missing(location) || missing(epiweeks)) {
      stop('`auth`, `location`, and `epiweeks` are all required')
    }
    # Set up request
    params <- list(
        endpoint = 'norostat',
        auth = auth,
        location = location,
        epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch NoroSTAT metadata
  meta_norostat <- function(auth) {
    # Check parameters
    if(missing(auth)) {
      stop('`auth` is required')
    }
    # Set up request
    params <- list(
      endpoint = 'meta_norostat',
      auth = auth
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch AFHSB data (point data, no min/max)
  afhsb <- function(auth, locations, epiweeks, flu_types) {
    # Check parameters
    if(missing(auth) || missing(locations) || missing(epiweeks) || missing(flu_types)) {
      stop('`auth`, `locations`, `epiweeks` and `flu_types` are all required')
    }
    # Set up request
    params <- list(
        endpoint = 'afhsb',
        auth = auth,
        locations = .list(locations),
        epiweeks = .list(epiweeks),
        flu_types = .list(flu_types)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch AFHSB metadata
  meta_afhsb <- function(auth) {
    # Check parameters
    if(missing(auth)) {
      stop('`auth` is required')
    }
    # Set up request
    params <- list(
      endpoint = 'meta_afhsb',
      auth = auth
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch NIDSS flu data
  nidss.flu <- function(regions, epiweeks, issues, lag) {
    # Check parameters
    if(missing(regions) || missing(epiweeks)) {
      stop('`regions` and `epiweeks` are both required')
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    # Set up request
    params <- list(
      endpoint = 'nidss_flu',
      regions = .list(regions),
      epiweeks = .list(epiweeks)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch NIDSS dengue data
  nidss.dengue <- function(locations, epiweeks) {
    # Check parameters
    if(missing(locations) || missing(epiweeks)) {
      stop('`locations` and `epiweeks` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'nidss_dengue',
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Delphi's forecast
  delphi <- function(system, epiweek) {
    # Check parameters
    if(missing(system) || missing(epiweek)) {
      stop('`system` and `epiweek` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'delphi',
      system = system,
      epiweek = epiweek
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Delphi's digital surveillance sensors
  sensors <- function(auth, names, locations, epiweeks) {
    # Check parameters
    if(missing(auth) || missing(names) || missing(locations) || missing(epiweeks)) {
      stop('`auth`, `names`, `locations`, and `epiweeks` are all required')
    }
    # Set up request
    params <- list(
      endpoint = 'sensors',
      auth = auth,
      names = .list(names),
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Delphi's digital surveillance sensors
  dengue_sensors <- function(auth, names, locations, epiweeks) {
    # Check parameters
    if(missing(auth) || missing(names) || missing(locations) || missing(epiweeks)) {
      stop('`auth`, `names`, `locations`, and `epiweeks` are all required')
    }
    # Set up request
    params <- list(
      endpoint = 'dengue_sensors',
      auth = auth,
      names = .list(names),
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Delphi's wILI nowcast
  nowcast <- function(locations, epiweeks) {
    # Check parameters
    if(missing(locations) || missing(epiweeks)) {
      stop('`locations` and `epiweeks` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'nowcast',
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch Delphi's PAHO Dengue nowcast
  dengue_nowcast <- function(locations, epiweeks) {
    # Check parameters
    if(missing(locations) || missing(epiweeks)) {
      stop('`locations` and `epiweeks` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'dengue_nowcast',
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch API metadata
  meta <- function() {
    return(.request(list(endpoint='meta')))
  }

  # Fetch Delphi's COVID-19 Surveillance Streams
  covidcast <- function(data_source, signals, time_type, geo_type, time_values, geo_value, as_of, issues, lag, format=c("classic","tree"), signal) {
    # Check parameters
    if(missing(data_source) || (missing(signals) && missing(signal)) || missing(time_type) || missing(geo_type) || missing(time_values) || missing(geo_value)) {
      stop('`data_source`, `signals`, `time_type`, `geo_type`, `time_values`, and `geo_value` are all required')
    }
    if (missing(signals)) {
      signals <- signal
    }
    if(!missing(issues) && !missing(lag)) {
      stop('`issues` and `lag` are mutually exclusive')
    }
    format <- match.arg(format)
    # Set up request
    params <- list(
      endpoint = 'covidcast',
      data_source = data_source,
      signals = .list(signals),
      time_type = time_type,
      geo_type = geo_type,
      time_values = .list(time_values),
      format = format
    )
    if(is.list(geo_value)) {
      params$geo_values = paste(geo_value, collapse=',')
    } else {
      params$geo_value = geo_value
    }
    if(!missing(as_of)) {
      params$as_of <- as_of
    }
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    if(!missing(lag)) {
      params$lag <- lag
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch Delphi's COVID-19 Surveillance Streams metadata
  covidcast_meta <- function() {
    return(.request(list(endpoint='covidcast_meta', cached='true')))
  }

  # Fetch COVID hospitalization data
  covid_hosp <- function(states, dates, issues) {
    # Check parameters
    if(missing(states) || missing(dates)) {
      stop('`states` and `dates` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'covid_hosp_state_timeseries',
      states = .list(states),
      dates = .list(dates)
    )
    if(!missing(issues)) {
      params$issues <- .list(issues)
    }
    # Make the API call
    return(.request(params))
  }

  # Fetch COVID hospitalization data for specific facilities
  covid_hosp_facility <- function(hospital_pks, collection_weeks, publication_dates) {
    # Check parameters
    if(missing(hospital_pks) || missing(collection_weeks)) {
      stop('`hospital_pks` and `collection_weeks` are both required')
    }
    # Set up request
    params <- list(
      endpoint = 'covid_hosp_facility',
      hospital_pks = .list(hospital_pks),
      collection_weeks = .list(collection_weeks)
    )
    if(!missing(publication_dates)) {
      params$publication_dates <- .list(publication_dates)
    }
    # Make the API call
    return(.request(params))
  }

  # Lookup COVID hospitalization facility identifiers
  covid_hosp_facility_lookup <- function(state, ccn, city, zip, fips_code) {
    # Set up request
    params <- list(endpoint = 'covid_hosp_facility_lookup')
    if(!missing(state)) {
      params$state <- state
    } else if(!missing(ccn)) {
      params$ccn <- ccn
    } else if(!missing(city)) {
      params$city <- city
    } else if(!missing(zip)) {
      params$zip <- zip
    } else if(!missing(fips_code)) {
      params$fips_code <- fips_code
    } else {
      stop('one of `state`, `ccn`, `city`, `zip`, or `fips_code` is required')
    }
    # Make the API call
    return(.request(params))
  }

  server_version <- function() {
    return(.request(list(endpoint = 'version')))
  }

  # Export the public methods
  return(list(
    range = range,
    client_version = client_version,
    server_version = server_version,
    fluview = fluview,
    fluview_meta = fluview_meta,
    fluview_clinical = fluview_clinical,
    flusurv = flusurv,
    ecdc_ili = ecdc_ili,
    kcdc_ili = kcdc_ili,
    gft = gft,
    ght = ght,
    twitter = twitter,
    wiki = wiki,
    cdc = cdc,
    quidel = quidel,
    norostat = norostat,
    meta_norostat = meta_norostat,
    afhsb = afhsb,
    meta_afhsb = meta_afhsb,
    nidss.flu = nidss.flu,
    nidss.dengue = nidss.dengue,
    delphi = delphi,
    sensors = sensors,
    dengue_sensors = dengue_sensors,
    nowcast = nowcast,
    dengue_nowcast = dengue_nowcast,
    meta = meta,
    covidcast = covidcast,
    covidcast_meta = covidcast_meta,
    covid_hosp = covid_hosp,
    covid_hosp_facility = covid_hosp_facility,
    covid_hosp_facility_lookup = covid_hosp_facility_lookup
  ))
})()
