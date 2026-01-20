---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: Twitter Stream
---

# Twitter Stream
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `twitter` |
| **Data Source** | [HealthTweets](http://www.healthtweets.org/) |
| **Geographic Levels** | National, Department of Health & Human Services (HHS) Regions, Census Divisions, State (see [Geographic Codes](geographic_codes.md#us-regions-and-states)) |
| **Temporal Granularity** | Daily and Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2020w31 (2020-12-07)|
| **Temporal Scope Start** | 2011w48 (2011-11-27) |

<!-- | **License** |  | -->

## Overview
{: .no_toc}

This data source provides estimates of influenza activity derived from the content of public Twitter posts. The data was processed by HealthTweets.org using natural language processing (NLP) to classify tweets as flu-related.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

{: .note}
> **Note:** Restricted access: This endpoint requires authentication.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}


## Estimation

The classification and processing pipeline involves several stages to transform raw Twitter data into health trends:

1.  **Data Collection**: Two streams are collected via the Twitter Streaming API:
    *   **HEALTH Stream**: Capped at 1% of public tweets, filtered using 269 health-related keywords.
    *   **SAMPLE Stream**: A random 1% sample of all public tweets.
2.  **Classification**: A statistical classifier identifies health-related tweets within the HEALTH stream (estimated F1-score of 0.70). These are further processed to distinguish actual influenza reports from general awareness or concern.
3.  **Geolocation**: Every identified health tweet and every tweet from the SAMPLE stream is geolocated using **Carmen**, which resolves location down to the city level using profile data and geotags.
4.  **Normalization**: The volume of identified influenza infections (`num`) is normalized by the total volume of tweets from the same location in the SAMPLE stream (`total`) to calculate the prevalence (`percent`).
5.  **Gap Filling**: Missing data (e.g., due to network interruptions) is estimated based on adjacent days.

For more technical details, see the [research paper below](#citing-the-survey).

## Limitations

*   Highly dependent on Twitter's API access and terms of service, which have changed significantly.
*   Twitter users are not a representative sample of the general population.

## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/twitter/>


### Parameters

#### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `locations` | locations | `list` of location codes: `nat`, HHS regions, Census divisions, or state codes (see [Geographic Codes](geographic_codes.md#us-regions-and-states)) |
| `dates` | dates (see [Date Formats](date_formats.md)) | `list` of dates |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |

{: .note}
> **Note:** Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.

### Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].date`      | date (yyyy-MM-dd)                                               | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].num`       | number of flu-related tweets in the HEALTH stream (see [Methodology](#methodology)) | integer          |
| `epidata[].total`     | total number of tweets in the random SAMPLE stream for the same location | integer          |
| `epidata[].percent`   | flu-related tweets normalized based on the number
of tweets in SAMPLE                           | float            |
| `message`             | `success` or error message                                      | string           |

## Example URLs

### Twitter on 2015w01 (national)
<https://api.delphi.cmu.edu/epidata/twitter/?auth=...&locations=nat&epiweeks=201501>

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



## Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Twitter data for national level for epiweek `201501`.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>

  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

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
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_twitter(auth = 'auth_token', locations = 'nat',
                   time_type = "week", time_values = 201501)
print(res)
```
  </div>

</div>

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/), [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R), and [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.js).

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
    <button data-tab="js">JavaScript</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

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
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$twitter(auth = "auth_token", locations = list("nat"), time_type = "week", time_values = list(201501))
print(res$message)
print(length(res$epidata))
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">



```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.twitter('auth_token', ['nat'], EpidataAsync.range(201501, 201510)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
