---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: Google Flu Trends
---

# Google Flu Trends
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `gft` |
| **Data Source** | [Google Flu Trends Estimates](https://www.google.com/publicdata/explore?ds=z3bsqef7ki44ac_) ([context](https://en.wikipedia.org/wiki/Google_Flu_Trends)) |
| **Geographic Levels** | National, Department of Health & Human Services (HHS) Regions, State (see [Geographic Codes](geographic_codes.md#us-regions-and-states)), Selected US Cities (see [Selected US Cities](geographic_codes.md#selected-us-cities)) |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2015w32 |
| **Temporal Scope Start** | 2003w40 |
| **License** | [Google Terms of Service](https://policies.google.com/terms) |


## Overview
{: .no_toc}

This data source provides a historical estimate of influenza activity based on the aggregated volume of search queries related to flu symptoms, treatments, and related topics. The data is sourced from Google Flu Trends (GFT), which used these query volumes to model ILI rates.

We offer similar search query-based disease tracking that is more up to date: [Google Health Trends](ght.md), available through mid 2022, and [Google Symptoms](covidcast-signals/google-symptoms.md), available through late 2025.
Although these datasets are all based on search query volume, the processing and privacy handling differs such that reported values may not be comparable between sources.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/gft/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `locations` | Locations to fetch. National, HHS regions, US states (see [US Regions and States](geographic_codes.md#us-regions-and-states)), and select cities (see [Selected US Cities](geographic_codes.md#selected-us-cities)). | `list` of strings |
| `epiweeks` | Epiweeks to fetch. Supports [`epirange()`] and defaults to all ("*") dates. | `list` of epiweeks |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].location` | location                                                        | string           |
| `epidata[].epiweek`  | epiweek                                                         | integer          |
| `epidata[].num`      | GFT estimate (estimated ILI cases per 100,000 physician visits) | integer          |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### Google Flu Trends on 2015w01 (national)
<https://api.delphi.cmu.edu/epidata/gft/?locations=nat&epiweeks=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nat",
      "epiweek": 201501,
      "num": 4647
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Google Flu Trends data for epiweeks `201501-201510`.

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
res = epidata.pub_gft(locations='nat', epiweeks=EpiRange(201501, 201510))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_gft(locations = 'nat', epiweeks = epirange(201501, 201510))
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
res = Epidata.gft(['nat'], Epidata.range(201501, 201510))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$gft(locations = list("nat"), epiweeks = Epidata$range(201501, 201510))
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
  EpidataAsync.gft('nat', EpidataAsync.range(201501, 201510)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
