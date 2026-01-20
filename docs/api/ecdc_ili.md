---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: ECDC ILI
---

# ECDC ILI
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `ecdc_ili` |
| **Data Source** | [European Centre for Disease Prevention and Control (ECDC)](https://www.ecdc.europa.eu/en/home)  |
| **Geographic Levels** | European countries (see [Geographic Codes](geographic_codes.md#european-countries)) |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2020w12 |
| **Temporal Scope Start** | 2018w40 |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (with [attribution to ECDC](https://www.ecdc.europa.eu/en/copyright)) |


## Overview
{: .no_toc}

This endpoint provides weekly influenza-like illness (ILI) incidence rates for European countries. Data is sourced from the European Centre for Disease Prevention and Control (ECDC).

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Values represent ILI incidence rates (cases per 100,000 population) as reported and presented by the ECDC. Data is subject to backfill if the source provides historical revisions.

<!-- Source code: src/acquisition/ecdc/ecdc_ili.py, src/acquisition/ecdc/ecdc_db_update.py -->

## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/ecdc_ili/>


### Parameters

#### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `regions` | regions | `list` of European country labels (see [Geographic Codes](geographic_codes.md#european-countries)) |

#### Optional

| Parameter | Description | Type |
| --- | --- | --- |
| `issues` | issues (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `lag` | # weeks between each epiweek and its issue | integer |

{: .note}
> **Notes:**
> - If both `issues` and `lag` are specified, only `issues` is used.
> - If neither is specified, the current issues are used.

### Response

| Field                     | Description                                                     | Type             |
|---------------------------|-----------------------------------------------------------------|------------------|
| `result`                  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                 | list of results                                                 | array of objects |
| `epidata[].release_date`  | date of release                                                 | string           |
| `epidata[].region`        | region name                                                     | string           |
| `epidata[].issue`         | epiweek of issue                                                | integer          |
| `epidata[].epiweek`       | epiweek of data                                                 | integer          |
| `epidata[].lag`           | lag in weeks                                                    | integer          |
| `epidata[].incidence_rate`| ILI incidence rate (cases per 100,000 population)              | float            |
| `message`                 | `success` or error message                                      | string           |

## Example URLs

### ECDC ILI in Austria on 2020w01
<https://api.delphi.cmu.edu/epidata/ecdc_ili/?regions=austria&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date":"2020-03-26",
      "region": "Austria",
      "issue": 202012,
      "epiweek": 202001,
      "lag": 11,
      "incidence_rate": 406.60630449
    }
  ],
  "message": "success"
}
```

## Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch ECDC ILI data for Austria for epiweeks `202001` and `202002`.

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
res = epidata.ecdc_ili(['austria'], [202001, 202002])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_ecdc_ili(regions = 'austria', epiweeks = c(202001, 202002))
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
res = Epidata.ecdc_ili(['austria'], [202001, 202002])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$ecdc_ili(regions = list("austria"), epiweeks = list(202001, 202002))
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
  EpidataAsync.ecdc_ili('austria', [202001, 202002]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
