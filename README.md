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

# Examples

### FluView/GFT/Twitter on 2015w01 (national)
 - http://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201501

        {"result":1,"epidata":[{"release_date":"2015-07-31","region":"nat","issue":201529,"epiweek":201501,"lag":-28,"num_ili":31834,"num_patients":777188,"num_providers":1977,"num_age_0":7177,"num_age_1":9694,"num_age_2":0,"num_age_3":8221,"num_age_4":3670,"num_age_5":3072,"wili":4.2403781703231,"ili":4.0960488324575}],"message":"success"}

 - http://delphi.midas.cs.cmu.edu/epidata/api.php?source=gft&locations=nat&epiweeks=201501

        {"result":1,"epidata":[{"location":"nat","epiweek":201501,"num":4647}],"message":"success"}

 - http://delphi.midas.cs.cmu.edu/epidata/api.php?source=twitter&auth=XXXXX&locations=nat&epiweeks=201501

        {"result":1,"epidata":[ ... ],"message":"success"}

### Wiki article "influenza" on 2015w01

http://delphi.midas.cs.cmu.edu/epidata/api.php?source=wiki&articles=influenza&epiweeks=201501

    {"result":1,"epidata":[{"article":"influenza","count":30819,"hour":-1,"epiweek":201501}],"message":"success"}

### FluView in HHS Region 6 for the 2014/2015 flu season

http://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201440-201520

### Updates to FluView on 2014w53, reported from 2015w01 through 2015w10 (national)

http://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201453&issues=201501-201510

# References

 - Cook, Samantha, et al. "Assessing Google flu trends performance in the United States during the 2009 influenza virus A (H1N1) pandemic." PloS one 6.8 (2011): e23610.
 - Broniatowski, David A., Michael J. Paul, and Mark Dredze. "National and local influenza surveillance through Twitter: an analysis of the 2012-2013 influenza epidemic." (2013): e83672.
 - Dredze, Mark, et al. "HealthTweets. org: A Platform for Public Health Surveillance using Twitter." AAAI Conference on Artificial Intelligence. 2014.
 - Generous, Nicholas, et al. "Global disease monitoring and forecasting with Wikipedia." (2014): e1003892.
 - Hickmann, Kyle S., et al. "Forecasting the 2013–2014 Influenza Season Using Wikipedia." (2015): e1004239.
 - McIver, David J., and John S. Brownstein. "Wikipedia usage estimates prevalence of influenza-like illness in the United States in near real-time." PLoS Comput Biol 10.4 (2014): e1003581.
