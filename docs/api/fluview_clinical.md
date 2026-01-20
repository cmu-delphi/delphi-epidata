---
title: FluView Clinical
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# FluView Clinical
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `fluview_clinical` |
| **Data Source** | [United States Centers for Disease Control and Prevention (CDC)](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) |
| **Geographic Levels** | National, Department of Health & Human Services (HHS) Regions, Census Divisions, State (see [Geographic Codes](geographic_codes.md#us-regions-and-states)) |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Weekly (typically Fridays) |
| **Temporal Scope Start** | 2016w40 |
| **License** | [Publicly Accessible US Government](https://www.usa.gov/government-works) |


## Overview
{: .no_toc}

This data source provides age-stratified clinical data based on laboratory-confirmed influenza reports from the US FluView dashboard.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Values are sourced directly from the CDC's NREVSS (National Respiratory and Enteric Virus Surveillance System) clinical laboratories.

The metrics consist of weekly counts of influenza specimens (total tested and total positive for types A and B) and their corresponding positivity rates. Unlike the syndromic ILI data in the [FluView](fluview.html) endpoint, these metrics provide laboratory confirmation of influenza circulation.

### Percentages

The CDC calculates three percentage metrics:

* **`percent_positive`**: Percentage of total specimens that tested positive for influenza (A or B)
* **`percent_a`**: Percentage of total specimens that tested positive for influenza A
* **`percent_b`**: Percentage of total specimens that tested positive for influenza B

<!-- Source code: src/acquisition/fluview/fluview_update.py, src/server/endpoints/fluview_clinicial.py -->

## Lag and Backfill

The data is preliminary and subject to revision. Clinical labs may report data late or correct previously reported data. The `issues` and `lag` parameters allow access to historical versions of the data.

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/fluview_clinical/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `regions` | regions | `list` of region labels: `nat`, states, `hhs1`-`hhs10`, `cen1`-`cen9` (see [Geographic Codes](geographic_codes.md#us-regions-and-states)) |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues (see [Date Formats](date_formats.md))                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

{: .note}
> **Notes:**
> - If both `issues` and `lag` are specified, only `issues` is used.
> - If neither is specified, the current issues are used.

## Response

| Field                        | Description                                                     | Type             |
|------------------------------|-----------------------------------------------------------------|------------------|
| `result`                     | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                    | list of results                                                 | array of objects |
| `epidata[].release_date`     | date when data was released                                     | string           |
| `epidata[].region`           | region identifier                                               | string           |
| `epidata[].issue`            | epiweek of publication                                          | integer          |
| `epidata[].epiweek`          | epiweek for which data is valid                                 | integer          |
| `epidata[].lag`              | number of weeks between epiweek and issue                       | integer          |
| `epidata[].total_specimens`  | total number of specimens tested                                | integer          |
| `epidata[].total_a`          | total specimens positive for influenza A                        | integer          |
| `epidata[].total_b`          | total specimens positive for influenza B                        | integer          |
| `epidata[].percent_positive` | percentage of specimens testing positive for influenza          | float            |
| `epidata[].percent_a`        | percentage of specimens testing positive for influenza A        | float            |
| `epidata[].percent_b`        | percentage of specimens testing positive for influenza B        | float            |
| `message`                    | `success` or error message                                      | string           |

# Example URLs

### FluView Clinical on 2020w01 (national)
<https://api.delphi.cmu.edu/epidata/fluview_clinical/?regions=nat&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2021-10-08",
      "region": "nat",
      "issue": 202139,
      "epiweek": 202001,
      "lag": 91,
      "total_specimens": 65177,
      "total_a": 5645,
      "total_b": 9664,
      "percent_positive": 23.4883,
      "percent_a": 8.66103,
      "percent_b": 14.8273
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national FluView Clinical data for epiweeks `201601-201701`.

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
res = Epidata.fluview_clinical(['nat'], [Epidata.range(201601, 201701)])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_fluview_clinical(regions = "nat", epiweeks =  epirange(201601, 201701))
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

Place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.fluview_clinical(['nat'], [Epidata.range(201601, 201701)])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$fluview_clinical(regions = list("nat"), epiweeks = list(Epidata$range(201601, 201701)))
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
    EpidataAsync.fluview_clinical('nat', [EpidataAsync.range(201601, 201701)]).then((res) => {
      console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
    });
  </script>
  ```
  </div>

</div>
