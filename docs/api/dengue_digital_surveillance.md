---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: <i>inactive</i> Dengue Digital Surveillance
permalink: api/dengue_sensors.html
---

# Dengue Digital Surveillance Sensors
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `dengue_sensors` |
| **Data Source** | Various digital data streams |
| **Geographic Levels** | Countries and territories in the Americas (see [Geographic Codes](geographic_codes.md#countries-and-territories-in-the-americas)) <br> *Note: Data availability varies by country.* |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2020w32|
| **Temporal Scope Start** | 2014w04 |
| **License** | [CC BY](https://creativecommons.org/licenses/by/4.0/) |


## Overview
{: .no_toc}

This endpoint provides digital surveillance sensor estimates for dengue activity, derived from various data streams.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

### Available Signals

The following signals are available:

| Name | Description |
| :--- | :--- |
| `gft` | Google Flu Trends |
| `ght` | Google Health Trends |
| `twtr` | HealthTweets |
| `wiki` | Wikipedia access |
| `cdc` | CDC Page Hits |
| `epic` | Epicast 1-week-ahead point prediction |
| `quid` | Flu lab test data |
| `sar3` | Seasonal Autoregression (order 3) |
| `arch` | Best-fit Archetype at 1-week-ahead |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/dengue_sensors/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `name` | name | `list` of names (see [Available Signals](#available-signals)) | 
| `locations` | locations | `list` of location labels (see [Geographic Codes](geographic_codes.md#countries-and-territories-in-the-americas)) |


## Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].name`    | name                                                     | string           |
| `epidata[].value`     | value                                                    | float            |
| `message`             | `success` or error message                                      | string           |

# Example URLs

### Dengue Sensors on 2015w01 (Puerto Rico)
<https://api.delphi.cmu.edu/epidata/dengue_sensors/?auth=...&locations=pr&epiweeks=201501&names=ght>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "pr",
      "epiweek": 201501,
      "name": "ght",
      "value": 103.676
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Dengue Sensors data for Puerto Rico for epiweek `201501`.

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
res = epidata.dengue_sensors('auth_token', ['ght'], ['pr'], [201501])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_dengue_sensors(auth = 'auth_token', names = 'ght', locations = 'pr', epiweeks = 201501)
print(res)
```
  </div>

</div>

### Legacy Clients

We recommend using our client libraries: [epidatr](https://cmu-delphi.github.io/epidatr/) for R and [epidatpy](https://cmu-delphi.github.io/epidatpy/) for Python. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/), [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R), and [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.js).

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

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.dengue_sensors('auth_token', ['gft'], ['pr'], [201501])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$dengue_sensors(auth = "auth_token", sensors = list("gft"), locations = list("pr"), epiweeks = list(201501))
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
  EpidataAsync.dengue_sensors('auth_token', ['ght'], 'pr', [201501]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
