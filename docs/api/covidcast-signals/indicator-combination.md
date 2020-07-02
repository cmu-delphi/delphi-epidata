---
title: Indicator Combination
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Indicator Combination

* **Source name:** `indicator-combination`
* **First issued:** 19 May 2020
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#indicator-combination)
* **Available for:** county, msa, state (see [geography coding docs](../covidcast_geography.md))

This source provides signals which are combinations of the other
sources, calculated and/or composed by Delphi. It is not a primary data source.

## Statistical combination signals 

* `nmf_day_doc_fbc_fbs_ght`: This signal uses a rank-1 approximation, from a
  nonnegative matrix factorization approach, to identify an underlying signal
  that best reconstructs the Doctor Visits (`smoothed_adj_cli`), Facebook
  Symptoms surveys (`smoothed_cli`), Facebook Symptoms in Community surveys
  (`smoothed_hh_cmnty_cli`), and Search Trends (`smoothed_search`) indicators.
  It does not include official reports (cases and deaths from the `jhu-csse`
  source). Higher values of the combined signal correspond to higher values of
  the other indicators, but the scale (units) of the combination is arbitrary.
  Note that the Search Trends source is not available at the county level, so
  county values of this signal do not use it.
* `nmf_day_doc_fbs_ght`: This signal is calculated in the same way as
  `nmf_day_doc_fbc_fbs_ght`, but does *not* include the Symptoms in Community
  survey signal, which was not available at the time this signal was introduced.
  It also uses `smoothed_cli` from the `doctor-visits` source instead of
  `smoothed_adj_cli`. This signal is deprecated and is no longer updated as of
  May 28, 2020.

## Compositional signals: Confirmed Cases and Deaths

These signals combine the cases and deaths data from JHU and USA Facts. This is
a straight composition: the signals below use the [JHU signal data](jhu-csse.md) for
Puerto Rico, and the [USA Facts signal data](usa-facts.md) everywhere else.

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumulative_num` | Cumulative number of confirmed COVID-19 cases |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumulative_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population |
| `confirmed_incidence_num` | `confirmed_7dav_incidence_num` | Number of new confirmed COVID-19 cases, daily |
| `confirmed_incidence_prop` | `confirmed_7dav_incidence_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily |
| `deaths_cumulative_num` | `deaths_7dav_cumulative_num` | Cumulative number of confirmed deaths due to COVID-19 |
| `deaths_cumulative_prop` | `deaths_7dav_cumulative_prop` | Cumulative number of confirmed due to COVID-19, per 100,000 population |
| `deaths_incidence_num` | `deaths_7dav_incidence_num` | Number of new confirmed deaths due to COVID-19, daily |
| `deaths_incidence_prop` | `deaths_7dav_incidence_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily |

