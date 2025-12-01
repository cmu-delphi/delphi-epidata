---
title: <i>inactive</i> Dengue Nowcast
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Delphi's Dengue Nowcast
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `dengue_nowcast` |
| **Data Source** | [Delphi](https://delphi.cmu.edu/) |
| **Geographic Coverage** | Countries and territories in the Americas (see [Geographic Codes](geographic_codes.html#countries-and-territories-in-the-americas)) <br> *Note: Data availability varies by country.* |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated |
| **Earliest Date** | 2014w09 |
| **License** | [CC BY](https://creativecommons.org/licenses/by/4.0/ |


## Overview
{: .no_toc}

This endpoint provides nowcast esimtates of dengue incidence, based on historical data and reported case counts.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/dengue_nowcast/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of location labels (see [Geographic Codes](geographic_codes.html#countries-and-territories-in-the-americas)) |

## Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].value`     | nowcast value                                                   | float            |
| `epidata[].std`       | standard deviation                                              | float            |
| `message`             | `success` or error message                                      | string           |

# Example URLs

### Dengue Nowcast on 2015w01 (Puerto Rico)
<https://api.delphi.cmu.edu/epidata/dengue_nowcast/?locations=pr&epiweeks=201401-202301>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "pr",
      "epiweek": 201501,
      "value": 12.34,
      "std": 1.23
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Dengue Nowcast data for Puerto Rico for epiweeks `201401` to `202301`.

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
res = epidata.dengue_nowcast(['pr'], EpiRange(201401, 202301))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_dengue_nowcast(locations = 'pr', epiweeks = epirange(201401, 202301))
print(res)
```
  </div>

</div>

### Legacy Clients

For modern clients, we recommend using [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/). The following clients are considered legacy: [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js), [Python](https://pypi.org/project/delphi-epidata/), and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

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
res = Epidata.dengue_nowcast(['pr'], [201501])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$dengue_nowcast(locations = list("pr"), epiweeks = list(201501))
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
  EpidataAsync.dengue_nowcast('pr', [201501]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
