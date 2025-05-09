---
title: <i>inactive</i> NoroSTAT Metadata
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
permalink: api/meta_norostat.html
---

# NoroSTAT Metadata

This is the documentation of the API for accessing the NoroSTAT Metadata (`meta_norostat`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## NoroSTAT Metadata

... <!-- TODO -->

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/meta_norostat/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

<!-- TODO -->

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
