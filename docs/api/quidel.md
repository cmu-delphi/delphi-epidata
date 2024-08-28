---
title: <i>inactive</i> Quidel
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Quidel

This is the documentation of the API for accessing the Quidel (`quidel`) endpoint of the Delphi’s epidemiological data.

General topics not specific to any particular endpoint are discussed in the [API overview](https://cmu-delphi.github.io/delphi-epidata/). Such topics include: [contributing](https://cmu-delphi.github.io/delphi-epidata/api/README.html#contributing), [citing](https://cmu-delphi.github.io/delphi-epidata/api/README.html#citing), and [data licensing](https://cmu-delphi.github.io/delphi-epidata/api/README.html#data-licensing).

## Quidel Data

Data provided by Quidel Corp., which contains flu lab test results.

## The API

The base URL is: https://api.delphi.cmu.edu/epidata/quidel/

See this [documentation](https://cmu-delphi.github.io/delphi-epidata/api/README.html) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of `hhs<#>` [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt) labels |

## Response

| Field     | Description                                                     | Type             |
|-----------|-----------------------------------------------------------------|------------------|
| `result`  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata` | list of results                                                 | array of objects |
| ...       | ...                                                             | ...              | <!-- TODO -->
| `message` | `success` or error message                                      | string           |