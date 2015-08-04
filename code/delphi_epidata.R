# A module for DELPHI's Epidata API.
#
# https://github.com/undefx/delphi-epidata
#
# Notes:
#  - Requires the `httr` library.

# External libraries
library(httr)


# Because the API is stateless, the Epidata class only contains static methods
Epidata <- (function() {

  # API base url
  BASE_URL <- 'http://delphi.midas.cs.cmu.edu/epidata/api.php'

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
  fluview <- function(regions, epiweeks, issues, lag) {
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

  # Export the public methods
  return(list(
    range = range,
    fluview = fluview,
    gft = gft,
    twitter = twitter,
    wiki = wiki
  ))
})()
