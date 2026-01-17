---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: PAHO Dengue
---

# PAHO Dengue
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `paho_dengue` |
| **Data Source** | [Pan American Health Organization (PAHO) Dengue surveillance](https://www.paho.org/en/arbo-portal/dengue-data-and-analysis) |
| **Geographic Levels** | Countries and territories in the Americas (see [Geographic Codes](geographic_codes.md#countries-and-territories-in-the-americas)) <br> *Note: Data availability varies by country.* |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2020w31 |
| **Temporal Scope Start** | 2014w01 |
| **License** | This was scraped from a publicly-accessible website, but no explicit license terms were found. |

## Overview
{: .no_toc}

This endpoint provides weekly dengue case counts for countries and territories in the Americas, as reported by the Pan American Health Organization (PAHO).

> [!IMPORTANT]
> Data acquisition is performed via web scraping of a Tableau dashboard, which renders the process fragile to website changes.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}



# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/paho_dengue/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `regions` | regions | `list` of region labels (see [Geographic Codes](geographic_codes.md#paho-dengue)) |

## Response

| Field                        | Description                                                     | Type             |
|------------------------------|-----------------------------------------------------------------|------------------|
| `result`                     | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                    | list of results                                                 | array of objects |
| `epidata[].release_date`     | date when data was released                                     | date (YYYY-MM-DD)|
| `epidata[].region`           | region label (ISO 3166-1 alpha-2 code)                          | string           |
| `epidata[].serotype`         | dengue serotype information                                     | string           |
| `epidata[].issue`            | epiweek when data was issued                                    | integer          |
| `epidata[].epiweek`          | epiweek for the data point                                      | integer          |
| `epidata[].lag`              | number of weeks between epiweek and issue                       | integer          |
| `epidata[].total_pop`        | total population (in thousands)                                 | integer          |
| `epidata[].num_dengue`       | total number of dengue cases                                    | integer          |
| `epidata[].num_severe`       | number of severe dengue cases                                   | integer          |
| `epidata[].num_deaths`       | number of dengue-related deaths                                 | integer          |
| `epidata[].incidence_rate`   | incidence rate per 100,000 population                           | float            |
| `message`                    | `success` or error message                                      | string           |

# Example URLs

### PAHO Dengue on 2015w01 (Canada)
<https://api.delphi.cmu.edu/epidata/paho_dengue/?regions=ca&epiweeks=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2020-08-07",
      "region": "CA",
      "serotype": "  ",
      "issue": 202032,
      "epiweek": 201501,
      "lag": 291,
      "total_pop": 0,
      "num_dengue": 0,
      "num_severe": 0,
      "num_deaths": 0,
      "incidence_rate": 0.0
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch PAHO Dengue data for Canada for epiweek `201501`.

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
res = epidata.pub_paho_dengue(regions=['ca'], epiweeks=[201501])
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_paho_dengue(regions = 'ca', epiweeks = 201501)
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

Place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.paho_dengue(['ca'], [201501])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$paho_dengue(regions = list("ca"), epiweeks = list(201501))
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
  EpidataAsync.paho_dengue('ca', [201501]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
