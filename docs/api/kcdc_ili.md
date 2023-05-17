---
title: KCDC ILI
parent: Other Endpoints (COVID-19 and Other Diseases)
---

# KCDC ILI

This is the API documentation for accessing the KCDC ILI (`kcdc_ili`) endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## KCDC ILI Data

KCDC ILI data from KCDC website. ... <!-- TODO -->

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/kcdc_ili/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter  | Description | Type               |
|------------|-------------|--------------------|
| `epiweeks` | epiweeks    | `list` of epiweeks |
| `regions`  | regions     | `ROK`              |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

Notes:
- If both `issues` and `lag` are specified, only `issues` is used.
If neither is specified, the current issues are used.

## Response

| Field     | Description                                                     | Type             |
|-----------|-----------------------------------------------------------------|------------------|
| `result`  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata` | list of results                                                 | array of objects |
| ...       | ...                                                             | ...              | <!-- TODO -->
| `message` | `success` or error message                                      | string           |

# Example URLs

<!-- TODO: fix -->

# Code Samples

<!-- TODO: fix -->
