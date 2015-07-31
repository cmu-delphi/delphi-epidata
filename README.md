# delphi-epidata

This repo provides documentation and sample code for [DELPHI](http://delphi.midas.cs.cmu.edu/)'s *real-time* epidemiological data API. The API currently only contains U.S. influenza data, but this may be expanded in the future to include additional locations and diseases.

# Influenza Data

### ILINet FluView

Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet).
 - Data source: [United States Centers for Disease Control and Prevention](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) (CDC)
 - Temporal Resolution: Weekly* from 1997w40
 - Spatial Resolution: By HHS region ([11](labels/regions.txt))
 - Open access

*Data is usually released on Friday

### Google Flu Trends

Estimate of influenza activity based on volume of certain search queries.
 - Data source: [Google](https://www.google.org/flutrends/)
 - Temporal Resolution: Weekly* from 2003w40
 - Spatial Resolution: By HHS region ([11](labels/regions.txt)), by state/territory ([51](labels/states.txt)), and by city ([97](labels/cities.txt))
 - Open access

*Data is reported by week, but values for the current week are revised daily

### Twitter Stream

Estimate of influenza activity based on analysis of language used in tweets.
 - Data source: [HealthTweets](http://www.healthtweets.org/)
 - Temporal Resolution: Daily and weekly from 2011-12-01 (2011w48)
 - Spatial Resolution: By HHS region ([11](labels/regions.txt)), and by state/territory ([51](labels/states.txt))
 - Restricted access: DELPHI doesn't have permission to share this dataset

### Wikipedia Access Logs

Number of page visits for selected English, Influenza-related wikipedia articles.
 - Data source: [Wikimedia](https://dumps.wikimedia.org/other/pagecounts-raw/)
 - Temporal Resolution: Hourly, daily, and weekly from 2007-12-09 (2007w50)
 - Spatial Resolution: N/A
 - Other resolution: By article ([55](labels/articles.txt))
 - Open access

# The API

The base URL is: http://delphi.midas.cs.cmu.edu/epidata/api.php

Epiweeks use the U.S. definition. That is, the first epiweek each year is the week, starting on a Sunday, containing January 4. See [this](http://www.cmmcp.org/epiweek.htm) page for more information.

`range` parameters can be a single value, a comma-separated list of values, or a hyphenated range of values. Examples include:
 - `201530` *(A single epiweek)*
 - `201401,201501,201601` *(Several epiweeks)*
 - `200501-200552` *(A range of epiweeks)*
 - `20070101-20071231` *(A range of dates)*

### Universal Parameters

The only universally required parameter is `source`, which must be one of: `fluview`, `gft`, `twitter`, or `wiki`

### FluView Parameters

Required:
 - `epiweeks`: a `range` of epiweeks
 - `regions`: a comma-separated list of [region](labels/regions.txt) labels

Optional:
 - `issues`: a `range` of epiweeks
 - `lag`: a number of weeks

### GFT Parameters

Required:
 - `epiweeks`: a `range` of epiweeks
 - `locations`: a comma-separated list of [region](labels/regions.txt)/[state](labels/states.txt)/[city](labels/cities.txt) labels

### Twitter Parameters

Required:
 - `auth`: an authorization token
 - `locations`: a comma-separated list of [region](labels/regions.txt)/[state](labels/states.txt) labels

Require one of:
 - `dates`: a `range` of dates
 - `epiweeks`: a `range` of epiweeks

### Wiki Parameters

Required:
 - `articles`: a comma-separated list of [article](labels/articles.txt) labels

Require one of:
 - `dates`: a `range` of dates
 - `epiweeks`: a `range` of epiweeks

Optional:
 - `hours`: a `range` of hours
