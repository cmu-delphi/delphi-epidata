---
title: <i>inactive</i> CDC
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# CDC
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `cdc` |
| **Data Source** | CDC influenza surveillance data |
| **Geographic Coverage** | National, HHS regions, Census divisions, and US states (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated |
| **Earliest Date** | 2013w02 (2013-01-06) |

<!-- | **License** | | -->

## Overview
{: .no_toc}

This data source provides CDC-collected influenza surveillance data from various sources.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}



# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/cdc/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of location codes: `nat` (national), HHS regions (`hhs1`-`hhs10`), Census divisions (`cen1`-`cen9`), or state codes (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |

## Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].num1`      | number of hits for datasource 1                                 | integer          |
| `epidata[].num2`      | number of hits for datasource 2                                 | integer          |
| `epidata[].num3`      | number of hits for datasource 3                                 | integer          |
| `epidata[].num4`      | number of hits for datasource 4                                 | integer          |
| `epidata[].num5`      | number of hits for datasource 5                                 | integer          |
| `epidata[].num6`      | number of hits for datasource 6                                 | integer          |
| `epidata[].num7`      | number of hits for datasource 7                                 | integer          |
| `epidata[].num8`      | number of hits for datasource 8                                 | integer          |
| `epidata[].total`     | total page hits across all datasources                          | integer          |
| `epidata[].value`     | computed value (may be null)                                    | float or null    |
| `message`             | `success` or error message                                      | string           |

# Example URLs

### CDC Page Hits on 2015w01 (national)
<https://api.delphi.cmu.edu/epidata/cdc/?auth=...&locations=nat&epiweeks=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nat",
      "epiweek": 201501,
      "num1": 91858,
      "num2": 81121,
      "num3": 89511,
      "num4": 52278,
      "num5": 16219,
      "num6": 87327,
      "num7": 38310,
      "num8": 51461,
      "total": 4252190,
      "value": null
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch CDC data for national level for epiweek `201501`.

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
res = epidata.pvt_cdc(auth='auth_token', locations=['nat'], epiweeks=[201501])
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_cdc(auth = 'auth_token', locations = 'nat', epiweeks = 201501)
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
res = Epidata.cdc('auth_token', [201501], ['nat'])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$cdc(auth = "auth_token", epiweeks = list(201501), locations = list("nat"))
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
  EpidataAsync.cdc('auth_token', [201501], 'nat').then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
