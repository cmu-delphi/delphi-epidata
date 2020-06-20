---
title: Data Sources and Signals
parent: COVIDcast API
nav_order: 2
has_children: true
---

# Delphi's COVID-19 Data Sources and Signals

Delphi's COVID-19 Surveillance Streams data includes the following data sources.
Data from these sources is expected to be updated daily. You can use the
[`covidcast_meta`](covidcast_meta.md) API endpoint to get summary information
about the ranges of the different attributes for the different data sources.

The API for retrieving data from these sources is described in the
[COVIDcast API endpoint documentation](covidcast.md). Changes and corrections to
data in this API are listed in the [API changelog](covidcast_changelog.md).

## COVIDcast Map Signals

The following signals are currently displayed on [the public COVIDcast
map](https://covidcast.cmu.edu/):

| Name | Source | Signal |
| --- | --- | --- |
| Doctor's Visits | `doctor-visits` | `smoothed_adj_cli` |
| Symptoms (Facebook) | `fb-survey` | `smoothed_cli` |
| Symptoms in Community (Facebook) | `fb-survey` | `smoothed_hh_cmnty_cli` |
| Search Trends (Google) | `ght` | `smoothed_search` |
| Combined | `indicator-combination` | `nmf_day_doc_fbc_fbs_ght` |
| Cases | `jhu-csse` | `confirmed_incidence_num` |
| Cases per capita | `jhu-csse` | `confirmed_incidence_prop` |
| Deaths | `jhu-csse` | `deaths_incidence_num` |
| Deaths per capita | `jhu-csse` | `confirmed_incidence_prop` |
