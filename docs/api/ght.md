---
title: <i>inactive</i> Google Health Trends
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Google Health Trends

This is the API documentation for accessing the [Google Health Trends](https://trends.google.com/trends/fullscreen/m/IN)  (`ght`)
endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Google Health Trends Data

Estimate of influenza activity based on volume of certain search queries.
This data may be useful for real-time monitoring of diseases, as in:

- Herman Anthony Carneiro, Eleftherios Mylonakis. [Google Trends: A Web-Based Tool for Real-Time Surveillance of Disease Outbreaks](https://doi.org/10.1086/630200). Clinical Infectious Diseases, Volume 49, Issue 10, 15 November 2009, Pages 1557–1564. 
- Abel Brodeur, Andrew E. Clark, Sarah Fleche, Nattavudh Powdthavee.
[COVID-19, lockdowns and well-being: Evidence from Google Trends](https://doi.org/10.1016/j.jpubeco.2020.104346). Journal of Public Economics, Volume 193, 2021, 104346.
- Sudhakar V. Nuti, Brian Wayda, Isuru Ranasinghe, Sisi Wang, Rachel P. Dreyer, Serene I. Chen, Karthik Murugiah. [The Use of Google Trends in Health Care Research: A Systematic Review](https://doi.org/10.1371/journal.pone.0109583), October 2014.

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
