---
title: Data Sources and Signals
parent: COVIDcast Epidata API
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

To obtain many of these signals and update them daily, Delphi has written
extensive software to obtain data from various sources, aggregate the data,
calculate statistical estimates, and format the data to be shared through the
COVIDcast API. This code is [open source and available on
GitHub](https://github.com/cmu-delphi/covidcast-indicators), and contributions
are welcome.

## COVIDcast Map Signals

The following signals are currently displayed on [the public COVIDcast
map](https://covidcast.cmu.edu/):

| Kind             | Name                             | Source                                                                | Signal                           |
| ----             | ----                             | ------                                                                | ------                           |
| Public Behavior  | Away from Home 6hr+ a Day  | [`safegraph`](covidcast-signals/safegraph.md)                         | `full_time_work_prop`            |
| Public Behavior  | Away from Home 3-6hr a Day  | [`safegraph`](covidcast-signals/safegraph.md)                         | `part_time_work_prop`            |
| Public Behavior  | COVID Searches on Google           | [`ght`](covidcast-signals/ght.md)                                     | `smoothed_search`                |
| Early Indicators | COVID-Like Symptoms              | [`fb-survey`](covidcast-signals/fb-survey.md)                         | `smoothed_cli`                   |
| Early Indicators | COVID-Like Symptoms in Community | [`fb-survey`](covidcast-signals/fb-survey.md)                         | `smoothed_hh_cmnty_cli`          |
| Early Indicators | COVID-Related Doctor Visits                  | [`doctor-visits`](covidcast-signals/doctor-visits.md)                 | `smoothed_adj_cli`               |
| Early Indicators | COVID Indicator Combination                         | [`indicator-combination`](covidcast-signals/indicator-combination.md) | `nmf_day_doc_fbc_fbs_ght`        |
| Late Indicators  | COVID Antigen Test Positivity (Quidel)             | [`quidel`](covidcast-signals/quidel.md)                               | `covid_ag_smoothed_pct_positive` |
| Late Indicators  | COVID Hospital Admissions              | [`hospital-admissions`](covidcast-signals/hospital-admissions.md)     | `smoothed_adj_covid19_from_claims`           |
| Late Indicators  | Cases                            | [`indicator-combination`](covidcast-signals/indicator-combination.md) | `confirmed_7dav_incidence_num`   |
| Late Indicators  | Cases per 100,000 People         | [`indicator-combination`](covidcast-signals/indicator-combination.md) | `confirmed_7dav_incidence_prop`  |
| Late Indicators  | Deaths                           | [`indicator-combination`](covidcast-signals/indicator-combination.md) | `deaths_7dav_incidence_num`      |
| Late Indicators  | Deaths per 100,000 People        | [`indicator-combination`](covidcast-signals/indicator-combination.md) | `deaths_7dav_incidence_prop`     |

## All Available Sources and Signals

Beyond the signals available on the COVIDcast map, numerous other signals are
available directly through the API:
