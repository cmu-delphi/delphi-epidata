---
title: Google Health Trends
parent: Other Endpoints (COVID-19 and Other Diseases)
---

# Google Health Trends

This is the API documentation for accessing the Google Health Trends (`ght`)
endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Google Health Trends Data

Estimate of influenza activity based on volume of certain search queries. ... <!-- TODO -->

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/ght/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [state](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt) and/or `US` labels |
| `query` | search query or topic ID (see https://www.freebase.com/) | string |

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
