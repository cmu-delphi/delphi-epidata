# About

This is the home of [Delphi](https://delphi.cmu.edu/)'s epidemiological data
API.

## Contributing

If you are interested in contributing:

- For development of the API itself, see the
  [development guide](docs/epidata_development.md).
- To suggest changes, additions, or other ways to improve,
  [open an issue](https://github.com/cmu-delphi/delphi-epidata/issues/new)
  describing your idea.

## Citing

We hope that this API is useful to others outside of our group, especially for
epidemiological and other scientific research. If you use this API and would
like to cite it, we would gratefully recommend the following copy:

> David C. Farrow,
> Logan C. Brooks,
> Aaron Rumack,
> Ryan J. Tibshirani,
> Roni Rosenfeld
> (2015).
> _Delphi Epidata API_.
> https://github.com/cmu-delphi/delphi-epidata

## Data licensing

The majority of the data surfaced through this API is more or less just a
carefully curated mirror of data acquired from various external parties. Such
data is subject to its original licensing, where applicable.

---

Any data which is produced novelly by Delphi and is intentionally and openly
surfaced by Delphi through this API is hereby licensed
[CC-BY](https://creativecommons.org/licenses/by/4.0/). Endpoints, as specified
by the `source` parameter, which are known to wholly or partially serve data
under this license include:

- `delphi`
- `sensors`
- `nowcast`
- `covidcast`
- `covidcast_meta`
- `meta*`

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

---

# The API

The base URL is: https://delphi.midas.cs.cmu.edu/epidata/api.php

## Specifying Epiweeks, Dates, and Lists

Epiweeks use the U.S. definition. That is, the first epiweek each year is the week, starting on a Sunday, containing January 4.
See [this page](http://www.cmmcp.org/epiweek.htm) for more information.

Formatting for epiweeks is YYYYWW and for dates is YYYYMMDD.

`list` parameters consist of a comma-separated list of individual values or, for numeric parameters, a hyphenated range of values. Examples include:
 - `param=201530` *(A single epiweek)*
 - `param=201401,201501,201601` *(Several epiweeks)*
 - `param=200501-200552` *(A range of epiweeks)*
 - `param=201440,201501-201510` *(Several epiweeks, including a range)*
 - `param=20070101-20071231` *(A range of dates)*

## Universal Parameters

The only universally required parameter is `source`, which must be one of the supported source names listed below, e.g., `fluview`.

## Source-Specific Parameters

The parameters available for each source are documented in each linked source-specific API page.

<!-- TODO: check existing descriptions -->

### COVID-19 Data

| Source | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`covidcast`](covidcast.md) | COVIDCast | Delphi's COVID-19 surveillance streams. | no |
| [`covidcast_meta`](covidcast_meta.md) | COVIDCast Metadata | Metadata for Delphi's COVID-19 surveillance streams. | no |

### Influenza Data

| Source | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`afhsb`](ahfsb.md) | AFHSB | ... <!-- TODO --> | yes |
| [`cdc`](cdc.md) | CDC Page Hits | ... <!-- TODO --> | yes |
| [`delphi`](delphi.md) | Delphi's Forecast | ... <!-- TODO --> | no |
| [`ecdc_ili`](ecdc_ili.md) | ECDC ILI | ECDC ILI data from the ECDC website. | no |
| [`flusurv`](flusurv.md) | FluSurv | FluSurv-NET data (flu hospitaliation rates) from CDC. | no |
| [`fluview`](fluview.md) | FluView | Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet). | no |
| [`fluview_clinical`](fluview_clinical.md) | FluView Clinical | ... <!-- TODO --> | no |
| [`gft`](gft.md) | Google Flu Trends | Estimate of influenza activity based on volume of certain search queries. Google has discontinued Flu Trends, and this is now a static data source. | no |
| [`ght`](ght.md) | Google Health Trends | Estimate of influenza activity based on volume of certain search queries. | yes |
| [`kcdc_ili`](kcdc_ili.md) | KCDC ILI | KCDC ILI data from KCDC website. | no |
| [`meta`](meta.md) | API Metadata | Metadata for `fluview`, `twitter`, `wiki`, and `delphi`. | no |
| [`meta_afhsb`](meta_afhsb.md) | AFHSB Metadata | ... <!-- TODO --> | yes |
| [`nidss_flu`](nidss_flu.md) | NIDSS Flu | Outpatient ILI from Taiwan's National Infectious Disease Statistics System (NIDSS). | no |
| [`nowcast`](nowcast.md) | ILI Nearby | A nowcast of U.S. national, regional, and state-level (weighted) percent ILI, available seven days (regionally) or five days (state-level) before the first ILINet report for the corresponding week. | no |
| [`quidel`](quidel.md) | Quidel | Data provided by Quidel Corp., which contains flu lab test results. | yes |
| [`sensors`](sensors.md) | Delphi's Digital Surveillance Sensors | ... <!-- TODO --> | no |
| [`twitter`](twitter.md) | Twitter Stream | Estimate of influenza activity based on analysis of language used in tweets from [HealthTweets](http://HealthTweets.org/). | yes |
| [`wiki`](wiki.md) | Wikipedia Access Logs | Number of page visits for selected English, Influenza-related wikipedia articles. | no |

### Dengue Data

| Source | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`dengue_nowcast`](dengue_nowcast.md) | Delphi's Dengue Nowcast | ... <!-- TODO --> | ... <!-- TODO --> |
| [`dengue_sensors`](dengue_sensors.md) | Delphi's Dengue Digital Surveillance Sensors | ... <!-- TODO --> | ... <!-- TODO --> |
| [`nidss_dengue`](nidss_dengue.md) | NIDSS Dengue | Counts of confirmed dengue cases from Taiwan's NIDSS. | no |
| [`paho_dengue`](paho_dengue.md) | PAHO Dengue | ... <!-- TODO --> | ... <!-- TODO --> |

### Norovirus Data

| Source | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`meta_norostat`](meta_norostat.md) | NoroSTAT Metadata | ... <!-- TODO --> | ... <!-- TODO --> |
| [`norostat`](norostat.md) | NoroSTAT | Suspected and confirmed norovirus outbreaks reported by state health departments to the CDC. | ... <!-- TODO --> |

### Deprecated
* `ilinet` - replaced by [`fluview`](fluview.md)
* `signals` - replaced by [`sensors`](sensors.md)
* `stateili` - replaced by [`fluview`](fluview.md)

# Example URLs

### FluView on 2015w01 (national)
https://delphi.midas.cs.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2017-10-24",
      "region": "nat",
      "issue": 201740,
      "epiweek": 201501,
      "lag": 143,
      "num_ili": 31483,
      "num_patients": 771835,
      "num_providers": 1958,
      "num_age_0": 7160,
      "num_age_1": 9589,
      "num_age_2": null,
      "num_age_3": 8072,
      "num_age_4": 3614,
      "num_age_5": 3048,
      "wili": 4.21374,
      "ili": 4.07898
    }
  ],
  "message": "success"
}
```

### Wikipedia Access article "influenza" on 2020w01
https://delphi.midas.cs.cmu.edu/epidata/api.php?source=wiki&language=en&articles=influenza&epiweeks=202001

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "count": 6516,
      "total": 663604044,
      "hour": -1,
      "epiweek": 202001,
      "value": 9.81910834
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R). The following samples show how to import the library and fetch national FluView data for epiweeks `201440` and `201501-201510` (11 weeks total).

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

Optionally install the package using pip(env):
````bash
pip install delphi-epidata
````

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

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

# Related work

 - Cook, Samantha, et al. "Assessing Google flu trends performance in the United States during the 2009 influenza virus A (H1N1) pandemic." PloS one 6.8 (2011): e23610.
 - Broniatowski, David A., Michael J. Paul, and Mark Dredze. "National and local influenza surveillance through Twitter: an analysis of the 2012-2013 influenza epidemic." (2013): e83672.
 - Dredze, Mark, et al. "HealthTweets. org: A Platform for Public Health Surveillance using Twitter." AAAI Conference on Artificial Intelligence. 2014.
 - Generous, Nicholas, et al. "Global disease monitoring and forecasting with Wikipedia." (2014): e1003892.
 - Hickmann, Kyle S., et al. "Forecasting the 2013–2014 Influenza Season Using Wikipedia." (2015): e1004239.
 - McIver, David J., and John S. Brownstein. "Wikipedia usage estimates prevalence of influenza-like illness in the United States in near real-time." PLoS Comput Biol 10.4 (2014): e1003581.
