---
title: AFHSB
parent: Epidata API (Other Diseases)
---

# AFHSB

This is the API documentation for accessing the AFHSB (`afhsb`) endpoint of
[Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## AFHSB Data

... <!-- TODO -->

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [region](../../labels/regions.txt), [state](../../labels/states.txt), or 3-letter country code labels |
| `flu_types` | flu types | `list` of disjoint (`flu1`, `flu2-flu1`, `flu3-flu2`, `ili-flu3`) or subset (`flu2`, `flu3`, `ili`) flu type labels |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| ... | ... | ... | <!-- TODO -->
| `message` | `success` or error message | string |

# Example URLs

<!-- TODO: fix -->

# Code Samples

<!-- TODO: fix -->
