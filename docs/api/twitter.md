---
title: <i>inactive</i> Twitter Stream
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Twitter Stream
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `twitter` |
| **Data Source** | [HealthTweets](http://www.healthtweets.org/) |
| **Geographic Coverage** | National, HHS regions, Census divisions, and US states (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| **Temporal Resolution** | Daily and Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated |
| **Earliest Date** | 2011w48 (2011-11-27) |

<!-- | **License** |  | -->

## Overview
{: .no_toc}

Estimate of influenza activity based on analysis of language used in tweets.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

{: .note}
> **Note:** Restricted access: Delphi doesn't have permission to share this dataset.

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/twitter/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `locations` | locations | `list` of location codes: `nat`, HHS regions, Census divisions, or state codes (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| `dates` | dates | `list` of dates |
| `epiweeks` | epiweeks | `list` of epiweeks |

{: .note}
> **Note:** Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.

## Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].date`      | date (yyyy-MM-dd)                                               | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].num`       | number of tweets                                                | integer          |
| `epidata[].total`     | total tweets                                                    | integer          |
| `epidata[].percent`   | percent of tweets                                               | float            |
| `message`             | `success` or error message                                      | string           |

# Example URLs

### Twitter on 2015w01 (national)
https://api.delphi.cmu.edu/epidata/twitter/?auth=...&locations=nat&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nat",
      "num": 3067,
      "total": 443291,
      "epiweek": 201501,
      "percent": 0.6919
    }
  ],
  "message": "success"
}
```
# Citing the Survey
Researchers who use the Twitter Stream data for research are asked to credit and cite the survey in publications based on the data. Specifically, we ask that you cite our paper describing the survey:

  > Mark Dredze, Renyuan Cheng, Michael J Paul, David A Broniatowski. HealthTweets.org: A Platform for Public Health Surveillance using Twitter. AAAI Workshop on the World Wide Web and Public Health 
  > Intelligence, 2014.



# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Twitter data for national level for epiweek `201501`.

### R

```R
library(epidatr)
# Fetch data
res <- pvt_twitter(auth = 'auth_token', locations = 'nat',
                   time_type = "week", time_values = 201501)
print(res)
```

### Python

Install the package using pip:
```bash
pip install -e "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"
```

```python
# Import
from epidatpy import CovidcastEpidata, EpiDataContext, EpiRange
# Fetch data
epidata = EpiDataContext()
res = epidata.pvt_twitter(auth='auth_token', locations=['nat'], time_type="week", time_values=[201501])
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.twitter('auth_token', 'nat', 'week', [201501]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```

### Legacy Clients

We recommend using our modern client libraries: [epidatr](https://cmu-delphi.github.io/epidatr/) for R and [epidatpy](https://cmu-delphi.github.io/epidatpy/) for Python. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$twitter(auth = "auth_token", locations = list("nat"), time_type = "week", time_values = list(201501))
print(res$message)
print(length(res$epidata))
```

#### Python (Legacy)

Optionally install the package using pip(env):
```bash
pip install delphi-epidata
```

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.twitter('auth_token', ['nat'], time_type="week", time_values=[201501])  
print(res['result'], res['message'], len(res['epidata']))
```
