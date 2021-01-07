---
title: Delphi Forecasts
parent: Epidata API (Other Diseases)
---

# Delphi Forecasts

This is the documentation of the API for accessing the Delphi Forecast (`delphi`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Delphi Forecast Data

... <!-- TODO -->

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `system` | system | system name from (...) <!-- TODO --> |
| `epiweek` | epiweek | epiweek when forecast was made |

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

### Delphi on 2020w01 (EC)
https://delphi.cmu.edu/epidata/api.php?source=delphi&system=ec&epiweek=202001

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

<!-- TODO: fix -->
