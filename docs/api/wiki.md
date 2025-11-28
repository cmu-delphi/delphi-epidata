---
title: <i>inactive</i> Wikipedia Access
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Wikipedia Access
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `wiki` |
| **Data Source** | [Wikimedia pageviews](https://dumps.wikimedia.org/other/pagecounts-raw/) for health-related Wikipedia articles |
| **Dataset Type** | Surveillance (Inactive) |
| **Geographic Coverage** | Not applicable (article-based) |
| **Temporal Resolution** | Hourly, Daily, and Weekly (Epiweek) |
| **Available Articles** | [54 health-related articles](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/articles.txt) |
| **Update Frequency** | Inactive - No longer updated |
| **License** | Open Access |

<!----| **Earliest Date** | 2007w50 (2007-12-09) |---->

## Overview
{: .no_toc}

This data source provides pageview counts for Influenza-related Wikipedia articles, which can serve as indicators of public health interest and awareness.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/wiki/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `articles` | articles | list of [articles](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/articles.md) |
| `language` | language (currently `en`, `es`, and `pt` supported) | string |
| `dates` | dates | `list` of dates |
| `epiweeks` | epiweeks | `list` of epiweeks |


### Optional

| Parameter | Description | Type                   |
|-----------|-------------|------------------------|
| `hours`   | hours       | `list` of hours (0-23) |

{: .note}
> **Notes:** 
> - Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.
> - `dates`, `epiweeks`, and `hours` are `None` by default.
> - `language` is `en` by default.

## Response

| Field               | Description                                                     | Type             |
|---------------------|-----------------------------------------------------------------|------------------|
| `result`            | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`           | list of results                                                 | array of objects |
| `epidata[].article` | Wikipedia article name                                          | string           |
| `epidata[].count`   | number of pageviews                                             | integer          |
| `epidata[].total`   | total pageviews                                                 | integer          |
| `epidata[].hour`    | hour (-1 if `hour` not used)                                   | integer          |
| `epidata[].date`    | date (yyyy-MM-dd) (only included if `date` used)                | string           |
| `epidata[].epiweek` | epiweek (only included if `epiweek` used)                       | integer          |
| `epidata[].value`   | normalized pageview count                                       | float            |
| `message`           | `success` or error message                                      | string           |

# Example URLs

### Wikipedia Access article "influenza" on 2020w01
<https://api.delphi.cmu.edu/epidata/wiki/?language=en&articles=influenza&epiweeks=202001>

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

### Wikipedia Access article "influenza" on date 2020-01-01
<https://api.delphi.cmu.edu/epidata/wiki/?language=en&articles=influenza&dates=20200101>

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "date": "2020-01-01",
      "count": 676,
      "total": 82359844,
      "hour": -1,
      "value": 8.20788344
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Wikipedia Access data for article "influenza" in English for epiweeks `202001-202010` (10 weeks total) and hours 0 and 12.

### R

```R
library(epidatr)
# Fetch data
res <- pub_wiki(articles = "influenza", time_values = epirange(202001, 202010),
                time_type = "week", language = "en", hours = c(0, 12))
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
res = epidata.pub_wiki(articles=['influenza'], time_values=EpiRange(202001, 202010), time_type='week', language='en', hours=[0, 12])
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.wiki('influenza', EpidataAsync.range(202001, 202010), {time_type: 'week', language: 'en', hours: [0, 12]}).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$wiki(articles = list("influenza"), time_values = Epidata$range(202001, 202010), time_type = "week", options = list(language = "en", hours = list(0, 12)))
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
res = Epidata.wiki(['influenza'], Epidata.range(202001, 202010), {'time_type': 'week', 'language': 'en', 'hours': [0, 12]})
print(res['result'], res['message'], len(res['epidata']))
```
