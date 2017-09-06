# Status

[![Deploy Status](https://delphi.midas.cs.cmu.edu/~automation/public/github_deploy_repo/badge.php?repo=cmu-delphi/delphi-epidata)](#)


# About

This repo provides documentation and sample code for [DELPHI](https://delphi.midas.cs.cmu.edu/)'s *real-time* epidemiological data API. The API currently contains influenza and dengue data for the United States and Taiwan.

This document contains the following sections:

 - [Influenza Data Sources](#influenza-data)
 - [Dengue Data Sources](#dengue-data)
 - [Technical Description of the API](#the-api)
 - [Sample URLs for Manual Access](#example-urls)
 - [Sample code for Programatic Access](#code-samples)
 - [References to Related Work](#references)


# Influenza Data

### FluView

Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet), aggregated at the regional and national levels.
 - Data source: [United States Centers for Disease Control and Prevention](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) (CDC)
 - Temporal Resolution: Weekly* from 1997w40
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), and [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](labels/regions.txt))
 - Open access

\* Data is usually released on Friday


### ILINet

An *estimate* of state-level ILI as reported to ILINet. Most of the data was digitized from charts and other lossy sources, and is not necessarily accurate or up-to-date. This is a static data source, and will not be frequently updated.
 - Data source: Several online sources, including each state's health department website (listed [here](http://www.cdc.gov/flu/weekly/))
 - Temporal Resolution: Weekly, from 2010w40 (or later) until 2015w34 (or earlier)
 - Spatial Resolution: By state/territory ([51](labels/states.txt))
 - Open access


### ILI-Nearby

A nowcast of U.S. national, regional, and state-level (weighted) %ILI, available seven days (regionally) or five days (state-level) before the first ILINet report for the corresponding week.
 - Data source: [Delphi's ILI-Nearby system](https://delphi.midas.cs.cmu.edu/nowcast/)
 - Temporal Resolution: Weekly, from 2010w30*
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](labels/regions.txt)), and by state/territory ([51](labels/states.txt))
 - Open access

\* Data is usually released on Friday and updated on Sunday and Monday


### Google Flu Trends

Estimate of influenza activity based on volume of certain search queries. Google has discontinued Flu Trends, and this is now a static data source.
 - Data source: [Google](https://www.google.org/flutrends/)
 - Temporal Resolution: Weekly from 2003w40 until 2015w32
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/) ([1+10](labels/regions.txt)); by state/territory ([50+1](labels/states.txt)); and by city ([97](labels/cities.txt))
 - Open access


### Twitter Stream

Estimate of influenza activity based on analysis of language used in tweets.
 - Data source: [HealthTweets](http://www.healthtweets.org/)
 - Temporal Resolution: Daily and weekly from 2011-12-01 (2011w48)
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), and [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](labels/regions.txt)); and by state/territory ([51](labels/states.txt))
 - Restricted access: DELPHI doesn't have permission to share this dataset


### Wikipedia Access Logs

Number of page visits for selected English, Influenza-related wikipedia articles.
 - Data source: [Wikimedia](https://dumps.wikimedia.org/other/pagecounts-raw/)
 - Temporal Resolution: Hourly, daily, and weekly from 2007-12-09 (2007w50)
 - Spatial Resolution: N/A
 - Other resolution: By article ([54](labels/articles.txt))
 - Open access


### NIDSS Flu

Outpatient ILI from Taiwan's National Infectious Disease Statistics System (NIDSS).
 - Data source: [Taiwan CDC](http://nidss.cdc.gov.tw/en/CDCWNH01.aspx?dc=wnh)
 - Temporal Resolution: Weekly* from 2008w14
 - Spatial Resolution: By [hexchotomy region](https://en.wikipedia.org/wiki/Regions_of_Taiwan#Hexchotomy) ([6+1](labels/nidss_regions.txt))
 - Open access

\* Data is usually released on Tuesday


# Dengue Data

### NIDSS Dengue

Counts of confirmed dengue cases from Taiwan's NIDSS.
 - Data source: [Taiwan CDC](http://nidss.cdc.gov.tw/en/SingleDisease.aspx?dc=1&dt=4&disease=061&position=1)
 - Temporal Resolution: Weekly from 2003w01
 - Spatial Resolution: By [hexchotomy region](https://en.wikipedia.org/wiki/Regions_of_Taiwan#Hexchotomy) ([6+1](labels/nidss_regions.txt)) and by [city/county](https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_Taiwan) ([22](labels/nidss_locations.txt))
 - Open access


# The API

The base URL is: https://delphi.midas.cs.cmu.edu/epidata/api.php

Epiweeks use the U.S. definition. That is, the first epiweek each year is the week, starting on a Sunday, containing January 4. See [this page](http://www.cmmcp.org/epiweek.htm) for more information.

Formatting for epiweeks is YYYYWW and for dates is YYYYMMDD.

`list` parameters consist of a comma-separated list of individual values or, for numeric parameters, a hyphenated range of values. Examples include:
 - `param=201530` *(A single epiweek)*
 - `param=201401,201501,201601` *(Several epiweeks)*
 - `param=200501-200552` *(A range of epiweeks)*
 - `param=201440,201501-201510` *(Several epiweeks, including a range)*
 - `param=20070101-20071231` *(A range of dates)*

### Universal Parameters

The only universally required parameter is `source`, which must be one of: `fluview`, `ilinet`, `nowcast`, `gft`, `twitter`, `wiki`, `nidss_flu`, or `nidss_dengue`

### FluView Parameters

Required:
 - `epiweeks`: a `list` of epiweeks
 - `regions`: a `list` of [region](labels/regions.txt) labels

Optional:
 - `issues`: a `list` of epiweeks
 - `lag`: a number of weeks

### ILINet Parameters

Required:
 - `epiweeks`: a `list` of epiweeks
 - `locations`: a `list` of [region](labels/regions.txt)/[state](labels/states.txt) labels

Note: For convenience and consistency, the `ilinet` source provides national and regional ILI in addition to state-level ILI, transparently using the `fluview` data source when necessary.

### ILI-Nearby Parameters

Required:
 - `epiweeks`: a `list` of epiweeks
 - `locations`: a `list` of [region](labels/regions.txt)/[state](labels/states.txt) labels

### GFT Parameters

Required:
 - `epiweeks`: a `list` of epiweeks
 - `locations`: a `list` of [region](labels/regions.txt)/[state](labels/states.txt)/[city](labels/cities.txt) labels

### Twitter Parameters

Required:
 - `auth`: an authorization token
 - `locations`: a `list` of [region](labels/regions.txt)/[state](labels/states.txt) labels

Require one of:
 - `dates`: a `list` of dates
 - `epiweeks`: a `list` of epiweeks

### Wiki Parameters

Required:
 - `articles`: a `list` of [article](labels/articles.txt) labels

Require one of:
 - `dates`: a `list` of dates
 - `epiweeks`: a `list` of epiweeks

Optional:
 - `hours`: a `list` of hours

### NIDSS-Flu Parameters

Required:
 - `epiweeks`: a `list` of epiweeks
 - `regions`: a `list` of [region](labels/nidss_regions.txt) labels

Optional:
 - `issues`: a `list` of epiweeks
 - `lag`: a number of weeks

### NIDSS-Dengue Parameters

Required:
 - `epiweeks`: a `list` of epiweeks
 - `locations`: a `list` of [region](labels/nidss_regions.txt) and/or [location](labels/nidss_locations.txt) labels


# Example URLs

### FluView/GFT/Twitter on 2015w01 (national)
 - https://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201501

        {"result":1,"epidata":[{"release_date":"2015-07-31","region":"nat","issue":201529,"epiweek":201501,"lag":-28,"num_ili":31834,"num_patients":777188,"num_providers":1977,"num_age_0":7177,"num_age_1":9694,"num_age_2":0,"num_age_3":8221,"num_age_4":3670,"num_age_5":3072,"wili":4.2403781703231,"ili":4.0960488324575}],"message":"success"}

 - https://delphi.midas.cs.cmu.edu/epidata/api.php?source=gft&locations=nat&epiweeks=201501

        {"result":1,"epidata":[{"location":"nat","epiweek":201501,"num":4647}],"message":"success"}

 - https://delphi.midas.cs.cmu.edu/epidata/api.php?source=twitter&auth=...&locations=nat&epiweeks=201501

        {"result":1,"epidata":[...],"message":"success"}

### ILINet on 2015w01 (state, regional, and national)

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=ilinet&epiweeks=201501&locations=tx,hhs6,nat

    {"result":1,"epidata":[{"epiweek":201501,"location":"nat","ili":4.0936926847062,"wili":4.2379135658604},{"epiweek":201501,"location":"hhs6","ili":6.0084085989824,"wili":8.32554468951},{"location":"TX","epiweek":201501,"ili":11.18}],"message":"success"}

### Wiki article "influenza" on 2015w01

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=wiki&articles=influenza&epiweeks=201501

    {"result":1,"epidata":[{"article":"influenza","count":30819,"hour":-1,"epiweek":201501}],"message":"success"}

### FluView in HHS Regions 4 and 6 for the 2014/2015 flu season

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=hhs4,hhs6&epiweeks=201440-201520

### Updates to FluView on 2014w53, reported from 2015w01 through 2015w10 (national)

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201453&issues=201501-201510

### NIDSS-Flu on 2015w01 (national)

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=nidss_flu&regions=Nationwide&epiweeks=201501

    {"result":1,"epidata":[{"release_date":"2015-08-04","region":"Nationwide","issue":201530,"epiweek":201501,"lag":29,"visits":65685,"ili":1.21}],"message":"success"}

### NIDSS-Dengue on 2015w01 (national)

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=nidss_dengue&locations=Nationwide&epiweeks=201501

    {"result":1,"epidata":[{"location":"nationwide","epiweek":201501,"count":20}],"message":"success"}


# Code Samples

Libraries are available for [CoffeeScript](code/client/delphi_epidata.coffee), [JavaScript](code/client/delphi_epidata.js), [Python](code/client/delphi_epidata.py), and [R](code/client/delphi_epidata.R). The following samples show how to import the library and fetch national FluView data for epiweeks `201440` and `201501-201510` (11 weeks total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.fluview(callback, ['nat'], [201440, Epidata.range(201501, 201510)])
````

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="jquery.js"></script>
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  var callback = function(result, message, epidata) {
    console.log(result, message, epidata != null ? epidata.length : void 0);
  };
  Epidata.fluview(callback, ['nat'], [201440, Epidata.range(201501, 201510)]);
</script>
````

### Python

````python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.fluview(['nat'], [201440, Epidata.range(201501, 201510)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$fluview(list('nat'), list(201440, Epidata$range(201501, 201510)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````

# References

 - Cook, Samantha, et al. "Assessing Google flu trends performance in the United States during the 2009 influenza virus A (H1N1) pandemic." PloS one 6.8 (2011): e23610.
 - Broniatowski, David A., Michael J. Paul, and Mark Dredze. "National and local influenza surveillance through Twitter: an analysis of the 2012-2013 influenza epidemic." (2013): e83672.
 - Dredze, Mark, et al. "HealthTweets. org: A Platform for Public Health Surveillance using Twitter." AAAI Conference on Artificial Intelligence. 2014.
 - Generous, Nicholas, et al. "Global disease monitoring and forecasting with Wikipedia." (2014): e1003892.
 - Hickmann, Kyle S., et al. "Forecasting the 2013–2014 Influenza Season Using Wikipedia." (2015): e1004239.
 - McIver, David J., and John S. Brownstein. "Wikipedia usage estimates prevalence of influenza-like illness in the United States in near real-time." PLoS Comput Biol 10.4 (2014): e1003581.
