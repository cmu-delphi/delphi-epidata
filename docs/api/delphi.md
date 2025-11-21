---
title: <i>inactive</i> Delphi Forecasts
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Delphi Forecasts
{: .no_toc}

* **Source name:** `delphi`
* **Earliest issue available:** 2010w01  
* **Time type available:** epiweek
* **License:** [CC BY](https://creativecommons.org/licenses/by/4.0/)

## Overview
{: .no_toc}

This data source provides access to experimental and retrospective Delphi forecasting systems and nowcasting outputs.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/delphi/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type                                 |
|-----------|-------------|--------------------------------------|
| `system`  | system      | system name from (...) <!-- TODO --> |
| `epiweek` | epiweek     | epiweek when forecast was made       |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of single result | array of object |
| `epidata[].system` | system | string |
| `epidata[].epiweek` | epiweek | integer |
| `epidata[].forecast` | forecast structure | object |
| `epidata[].forecast.season` | year (yyyy) | integer |
| `epidata[].forecast.ili_bins` | | integer |
| `epidata[].forecast.data` | forecast data for each region | object |
| `epidata[].forecast.data.<region>` | forecast data for \<region\> | object |
| `epidata[].forecast.data.<region>.<distrib>` | distribution for \<distrib\> (`peak`, `peakweek`, `onset`, `x1`, `x2`, `x3`, `x4`) | object |
| ... | ... | ... | <!-- TODO -->
| `epidata[].forecast.name` | name = "delphi-epicast" | string |
| `epidata[].forecast.year_weeks` | number of weeks in year | integer |
| `epidata[].forecast.ili_bin_size` | float |
| `epidata[].forecast.season_weeks` | number of weeks in season | integer |
| `epidata[].forecast._version` | forecast version | integer |
| `epidata[].forecast.epiweek` | forecast epiweek | integer |
| `message` | `success` or error message | string |

# Example URLs

### Delphi on 2015w01 (EC)
https://api.delphi.cmu.edu/epidata/delphi/?system=ec&epiweek=201501

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

### R

```R
library(epidatr)
# Fetch data
res <- pub_delphi(system = 'ec', epiweek = 201501)
print(res)
```

### Python

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

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

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

### Legacy Clients

We recommend using our modern client libraries: [epidatr](https://cmu-delphi.github.io/epidatr/) for R and [epidatpy](https://cmu-delphi.github.io/epidatpy/) for Python. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$delphi(system = 'ec', epiweek = 201501)
print(res$message)
print(length(res$epidata))
```

#### Python (Legacy)

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
