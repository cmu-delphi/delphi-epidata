# delphi-epidata

This repo provides documentation and sample code for [DELPHI](http://delphi.midas.cs.cmu.edu/)'s *real-time* epidemiological data API. The API currently only contains U.S. influenza data, but this may be expanded in the future to include additional locations and diseases.

# Influenza Data

### ILINet FluView

Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet).
 - Data source: [United States Centers for Disease Control and Prevention](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) (CDC)
 - Temporal Resolution: Weekly* from 1997w40
 - Spatial Resolution: national (1), and by HHS region (10)

*Data is usually released on Friday

### Google Flu Trends

Estimate of influenza activity based on volume of certain search queries.
 - Data source: [Google](https://www.google.org/flutrends/)
 - Temporal Resolution: Weekly* from 2003w40
 - Spatial Resolution: national (1), by HHS region (10), by state/territory (51), and by city (97)

*Data is reported by week, but values for the current week are revised daily

### Wikipedia Access Logs

Number of page visits for selected English, Influenza-related wikipedia articles.
 - Data source: [Wikimedia](https://dumps.wikimedia.org/other/pagecounts-raw/)
 - Temporal Resolution: Hourly, daily, and weekly from 2007-12-09 (2007w50)
 - Spatial Resolution: N/A

# The API

The base URL is: http://delphi.midas.cs.cmu.edu/epidata/api.php

Note: `range` parameters can be a single value, a comma-separated list of values, or a hyphenated range of values. Examples include:
 - `201530` *(A single epiweek)*
 - `201401,201501,201601` *(Several epiweeks)*
 - `200501-200552` *(A range of epiweeks)*
 - `20070101-20071231` *(A range of dates)*

Note: epiweeks use the U.S. definition. That is, the first epiweek each year is the week, starting on a Sunday, containing January 4. See [this](http://www.cmmcp.org/epiweek.htm) page for more information.

### Universal Parameters

The only universally required parameter is `source`, which must be one of: `fluview`, `gft`, or `wiki`

### FluView Parameters

Required:
 - `epiweeks`: a `range` of epiweeks
 - `regions`: a comma-separated list of region labels

Optional:
 - `issues`: a `range` of epiweeks
 - `lag`: a number of weeks

### GFT Parameters

Required:
 - `epiweeks`: a `range` of epiweeks
 - `locations`: a comma-separated list of location labels

### Wiki Parameters

Required:
 - `articles`: a comma-separated list of region labels

Require one of:
 - `dates`: a `range` of dates
 - `epiweeks`: a `range` of epiweeks

Optional:
 - `hours`: a `range` of hours
