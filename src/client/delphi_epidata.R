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
  BASE_URL <- 'https://delphi.midas.cs.cmu.edu/epidata/api.php'

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
    # API call
    return(content(GET(BASE_URL, query=params), 'parsed'))
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
      source = 'fluview',
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
      source = 'fluview_clinical',
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
      source = 'flusurv',
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

  # Fetch Google Flu Trends data
  gft <- function(locations, epiweeks) {
    # Check parameters
    if(missing(locations) || missing(epiweeks)) {
      stop('`locations` and `epiweeks` are both required')
    }
    # Set up request
    params <- list(
      source = 'gft',
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
      source = 'ght',
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
      source = 'twitter',
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
  wiki <- function(articles, dates, epiweeks, hours) {
    # Check parameters
    if(missing(articles)) {
      stop('`articles` is required')
    }
    if(!xor(missing(dates), missing(epiweeks))) {
      stop('exactly one of `dates` and `epiweeks` is required')
    }
    # Set up request
    params <- list(
      source = 'wiki',
      articles = .list(articles)
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
      source = 'cdc',
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
      source = 'quidel',
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
        source = 'norostat',
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
      source = 'meta_norostat',
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
      source = 'nidss_flu',
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
      source = 'nidss_dengue',
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
      source = 'delphi',
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
      source = 'sensors',
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
      source = 'dengue_sensors',
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
      source = 'nowcast',
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
      source = 'dengue_nowcast',
      locations = .list(locations),
      epiweeks = .list(epiweeks)
    )
    # Make the API call
    return(.request(params))
  }

  # Fetch API metadata
  meta <- function() {
    return(.request(list(source='meta')))
  }

  # Export the public methods
  return(list(
    range = range,
    fluview = fluview,
    fluview_clinical = fluview_clinical,
    flusurv = flusurv,
    gft = gft,
    ght = ght,
    twitter = twitter,
    wiki = wiki,
    cdc = cdc,
    quidel = quidel,
    norostat = norostat,
    meta_norostat = meta_norostat,
    nidss.flu = nidss.flu,
    nidss.dengue = nidss.dengue,
    delphi = delphi,
    sensors = sensors,
    dengue_sensors = dengue_sensors,
    nowcast = nowcast,
    dengue_nowcast = dengue_nowcast,
    meta = meta
  ))
})()
