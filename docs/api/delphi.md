---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: <i>inactive</i> Delphi Forecasts
---

# Delphi Forecasts
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `delphi` |
| **Data Source** | [Delphi](https://delphi.cmu.edu/) |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Systems available** | `af`, `eb`, `ec`, `sp`, `st` (see [details below](#forecasting-systems)) |
| **Reporting Cadence** | Inactive - No longer updated since 2020w19 |
| **Temporal Scope Start** | Varies by system (earliest 2014w41) |
| **License** | [CC BY](https://creativecommons.org/licenses/by/4.0/) |

## Overview
{: .no_toc}

This data source provides access to experimental and retrospective Delphi forecasting systems and nowcasting outputs.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

### Forecasting Systems

The following systems are available, representing different forecasting models for ILINet % weighted ILI:

| Code | Name | 
| :--- | :--- | 
| `af` | [Archefilter](http://reports-archive.adm.cs.cmu.edu/anon/cbd/CMU-CB-16-101.pdf#Appendix.1.B) | 
| `eb` | [Empirical Bayes](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004382) | 
| `ec` | [Epicast](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005248) | 
| `sp` | [Pinned Spline](http://reports-archive.adm.cs.cmu.edu/anon/cbd/CMU-CB-16-101.pdf#Appendix.1.A) | 
| `st` | [Delphi-Stat](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006134) 


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/delphi/>


## Parameters

### Required

| Parameter | Description | Type                                 |
|-----------|-------------|--------------------------------------|
| `system`  | system      | system name (`af`, `eb`, `ec`, `sp`, `st`) |
| `epiweek` | epiweek (see [Date Formats](date_formats.html))     | epiweek when forecast was made       |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of single result | array of object |
| `epidata[].system` | system | string |
| `epidata[].epiweek` | epiweek | integer |
| `epidata[].forecast` | forecast structure | object |
| `epidata[].forecast._version` | forecast version | integer |
| `epidata[].forecast.baselines` | baseline values for each region | object |
| `epidata[].forecast.baselines.<region>` | CDC %ILI baseline for \<region\> | float |
| `epidata[].forecast.data` | forecast data for each region | object |
| `epidata[].forecast.data.<region>` | forecast data for \<region\> | object |
| `epidata[].forecast.data.<region>.<distrib>` | distribution for \<distrib\> (`peak`, `peakweek`, `onset`, `x1`, `x2`, `x3`, `x4`) | object |
| `epidata[].forecast.data.<region>.<distrib>.dist` | probability distribution | array of float |
| `epidata[].forecast.data.<region>.<distrib>.point` | point estimate | float |
| `epidata[].forecast.data.<region>.<distrib>.none` | probability of "none" (if applicable) | float |
| `epidata[].forecast.epiweek` | forecast epiweek | integer |
| `epidata[].forecast.ili_bin_size` | size of ILI bins | float |
| `epidata[].forecast.ili_bins` | number of ILI bins | integer |
| `epidata[].forecast.name` | system name | string |
| `epidata[].forecast.season` | season year (yyyy) | integer |
| `epidata[].forecast.season_weeks` | number of weeks in season | integer |
| `epidata[].forecast.year_weeks` | number of weeks in year | integer |
| `message` | `success` or error message | string |

> [!TIP]
> **What is the CDC ILI Baseline?**
> The baseline marks when flu season begins in a region. It is calculated from historical low-activity periods and represents the expected ILI percentage when influenza is not actively circulating. See [CDC's U.S. Influenza Surveillance](https://www.cdc.gov/fluview/overview/index.html#:~:text=The%20baseline%20is%20developed%20by%20calculating%20the%20mean%20percentage%20of%20patient%20visits%20for%20ILI%20during%20non%2Dinfluenza%20weeks%20for%20the%20most%20recent%20three%20seasons) for more details.

# Example URLs

### Delphi on 2015w01 (EC)
<https://api.delphi.cmu.edu/epidata/delphi/?system=ec&epiweek=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "system": "ec",
      "epiweek": 202001,
      "forecast": {
        "season": 2019,
        "ili_bins": 131,
        "data": {
          "hhs5": {
            "peakweek": {
              "point": 52,
              "dist": [
                0.00021925496021215,
                ...
              ]
            },
            "onset": {
              "point": 48,
              "none": 0.0002,
              "dist": [
                0.00020000000000012,
                ...
              ]
            },
            "x2": {
              "point": 3.07298,
              "dist": [
                0.0010569913847139,
                ...
              ]
            },
            "x4": {
              "point": 2.85944,
              "dist": [
                0.0014449186313411,
                ...
              ]
            },
            "x3": {
              "point": 2.94803,
              "dist": [
                0.0012245906869107,
                ...
              ]
            },
            "peak": {
              "point": 4.5724227117742,
              "dist": [
                0.0010000000000028,
                ...
              ]
            },
            "x1": {
              "point": 3.35905,
              "dist": [
                0.0010036642441866,
                ...
              ]
            }
          },
          ...
        },
        "name": "delphi-epicast",
        "year_weeks": 52,
        "ili_bin_size": 0.1,
        "season_weeks": 33,
        "_version": 3,
        "epiweek": 202001
      }
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Delphi Forecast data for system `ec` on epiweek `201501`.

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
res = epidata.delphi('ec', 201501)
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_delphi(system = 'ec', epiweek = 201501)
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
res = Epidata.delphi('ec', 201501)
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$delphi(system = 'ec', epiweek = 201501)
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
  EpidataAsync.delphi('ec', 201501).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
