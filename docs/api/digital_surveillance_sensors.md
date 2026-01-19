---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: Digital Surveillance Sensors
permalink: api/sensors.html
---

# Digital Surveillance Sensors
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `sensors` |
| **Data Source** | Various digital data streams |
| **Geographic Levels** | National, Department of Health & Human Services (HHS) Regions, Census Divisions, State (see [Geographic Codes](geographic_codes.md#us-regions-and-states)) |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2022w36 |
| **Temporal Scope Start** | 2010w40 |
| **License** | [CC BY](https://creativecommons.org/licenses/by/4.0/) |

## Overview
{: .no_toc}

This endpoint provides access to Delphi's digital surveillance sensor estimates for seasonal influenza-like illness (ILI). It aggregates signals from multiple digital sources, including Google Health Trends, Wikipedia access counts, Twitter posts, and CDC web traffic, to provide real-time indicators of flu activity before official clinical reports are finalized.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

{: .note}
> **Note:** This repository was built to support modelling and forecasting efforts
> surrounding dengue and seasonal influenza.
> Syndromic surveillance data, like ILI data (influenza-like illness) through
> FluView, will likely prove very useful for understanding disease in
> the time period that includes the COVID-19 pandemic.
> However, **we urge caution to users examining the digital surveillance sensors**,
> like ILI Nearby, Google Flu
> Trends, etc., during that same date range, because these were designed to track
> ILI as driven by _seasonal_ influenza, and were NOT designed to track ILI during
> the COVID-19 pandemic.


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Signal Data Sources

The endpoint aggregates data from the following sources.

| Signal | Name | Description | Documentation |
|:---|:---|:---|:---|
| `cdc` | **CDC Webpage Visits** | Count of hits to CDC flu-related pages | [Docs](cdc.md) |
| `gft` | **Google Flu Trends** | Estimated ILI cases | [Docs](gft.md) |
| `ght` | **Google Health Trends** | Search volume for flu terms | [Docs](ght.md) |
| `twtr` | **Twitter Stream** | Percentage of tweets related to ILI | [Docs](twitter.md) |
| `wiki` | **Wikipedia Access** | Page view counts for flu articles | [Docs](wiki.md) |
| `quid` | **Quidel** | Positive influenza lab tests | [Docs](quidel.md) |
| `sar3` | **Seasonal Auto-Regressive model (v3)** | SAR3 is a regression model that, given the current week number and preliminary wILI values of the past three weeks, provides an estimate of the final wILI value of the current week. | [Reference (Subsection 4.3.2: Predictions)](http://reports-archive.adm.cs.cmu.edu/anon/cbd/CMU-CB-16-101.pdf) |
| `epic` | **Epicast** | A web-based system that collects and aggregates epidemic predictions from human participants to leverage collective human judgment. | [Reference](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005248) |
| `arch` | **Archefilter** | Builds an archetype influenza trajectory by splitting, smoothing, centering, and averaging historical wILI trajectories to estimate the current season's curve. | [Reference (Appendix B: The Archefilter)](http://reports-archive.adm.cs.cmu.edu/anon/cbd/CMU-CB-16-101.pdf) |


# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/sensors/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `locations` | locations | `list` of location codes: `nat`, HHS regions, Census divisions, or state codes (see [Geographic Codes](geographic_codes.md#us-regions-and-states)) |
| `names` | sensor names | `list` of string |

{: .note}
> **Note:** Restricted access: Some component signals require authentication.
> - **Publicly-accessible sensors:** `sar3`, `epic`, `arch` (no `auth` required)
> - **Private sensors:** `twtr`, `gft`, `ght`, `ghtj`, `cdc`, `quid`, `wiki` (require `auth` token)

### Optional

| Parameter | Description                                                                        | Type             |
|-----------|-------------------------------------------------------------------------------------|------------------|
| `auth`    | sensor authentication tokens (currently restricted to 1); can be global or granular | `list` of string |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].name`     | sensor name                                                     | string           |
| `epidata[].location` | location code                                                   | string           |
| `epidata[].epiweek`  | epiweek                                                         | integer          |
| `epidata[].value`    | signal value (varies by sensor)                  | float            |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### Delphi's Digital Surveillance SAR3 Sensor on 2020w01 (national)
<https://api.delphi.cmu.edu/epidata/sensors/?auth=...&names=sar3&locations=nat&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "name": "sar3",
      "location": "nat",
      "epiweek": 202001,
      "value": 6.2407
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national Delphi's Digital Surveillance SAR3 Sensor data for epiweeks `201501-202001`.

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
res = epidata.sensors(['nat'], ['sar3'], EpiRange(201501, 202001))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_sensors(auth = 'SECRET_API_AUTH_SENSORS', locations = 'nat',
names = 'sar3', epiweeks = epirange(201501, 202001))
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
res = Epidata.sensors(['nat'], ['sar3'], Epidata.range(201501, 202001))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$sensors(locations = list("nat"), sensors = list("sar3"), epiweeks = Epidata$range(201501, 202001))
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
  EpidataAsync.sensors('nat', 'sar3', EpidataAsync.range(201501, 202001)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
