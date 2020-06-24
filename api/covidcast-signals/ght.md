---
title: Google Health Trends
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Google Health Trends

* **Source name:** `ght`
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** dma, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source (`ght`) is based on Google searches, provided to us by Google
Health Trends. Using this search data, we estimate the volume of COVID-related
searches in a given location, on a given day. This signal is measured in
arbitrary units (its scale is meaningless); larger numbers represent higher
numbers of COVID-related searches. Note that this source is not available for
individual counties, as it is reported only for larger geographical areas, and
so county estimates are not available from the API.

| Signal | Description |
| --- | --- |
| `raw_search` | Google search volume for COVID-related searches, in arbitrary units that are normalized for population |
| `smoothed_search` | Google search volume for COVID-related searches, in arbitrary units that are normalized for population, smoothed in time using a local linear smoother with Gaussian kernel |

## Limitations

When query volume in a region is below a certain threshold, set by Google, it is
reported as 0. Areas with low query volume hence exhibit jumps and
zero-inflation, as small variations in the signal can cause it to be sometimes
truncated to 0 and sometimes reported at its actual level.

Google does not describe the units of its reported numbers, so the scale is
arbitrary.
