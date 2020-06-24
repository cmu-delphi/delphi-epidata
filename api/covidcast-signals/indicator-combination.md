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

This source provides signals which are statistical combinations of the other
sources, calculated by Delphi. It is not a primary data source.

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
