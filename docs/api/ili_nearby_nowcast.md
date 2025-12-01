---
title: <i>inactive</i> ILI Nearby Nowcast
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
permalink: api/nowcast.html
---

# ILI Nearby Nowcast
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nowcast` |
| **Data Source** | [Delphi's ILI Nearby system](https://delphi.cmu.edu/nowcast/) |
| **Dataset Type** | Predictive (Leading Indicator) |
| **Geographic Coverage** | National, HHS regions, Census divisions, and US states (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated since 2022w36 |
| **Earliest Date** | 2010w45 |
| **License** | [CC BY](https://creativecommons.org/licenses/by/4.0/) |

## Overview
{: .no_toc}

The ILI Nearby endpoint provides a "nowcast" predictive estimate of the percentage of outpatient visits due to Influenza-Like Illness (ILI).

This system uses a sensor-fusion approach to estimate the current level of flu activity before the official CDC reports are finalized. It is available:
* **National/Regional:** 7 days before the first official CDC ILINet report.
* **State-level:** 5 days before the first official CDC ILINet report.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).


# Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/nowcast/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of location codes: `nat`, HHS regions, Census divisions, or state codes (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].location` | location identifier (e.g., 'nat', state code, HHS region, census division) | string           |
| `epidata[].epiweek`  | epiweek for the nowcast estimate                                | integer          |
| `epidata[].value`    | nowcast estimate of %ILI (percentage of outpatient visits due to ILI) | float            |
| `epidata[].std`      | standard deviation of the nowcast estimate                      | float            |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### ILI Nearby on 2020w01 (national)
<https://api.delphi.cmu.edu/epidata/nowcast/?locations=nat&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nat",
      "epiweek": 202001,
      "value": 6.08239,
      "std": 0.12595
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national ILI Nearby data for epiweeks `202001-202010` (10 weeks total).

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
res = epidata.pub_nowcast(locations=['nat'], epiweeks=EpiRange(202001, 202010))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_nowcast(locations = 'nat', epiweeks = epirange(202001, 202010))
print(res)
```
  </div>

</div>

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

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
res = Epidata.nowcast(['nat'], Epidata.range(202001, 202010))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$nowcast(locations = list("nat"), epiweeks = Epidata$range(202001, 202010))
print(res$message)
print(length(res$epidata))
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.nowcast('nat', [EpidataAsync.range(201501, 201510)]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
```
