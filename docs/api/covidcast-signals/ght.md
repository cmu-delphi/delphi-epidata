---
title: Google Health Trends
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Google Health Trends

* **Source name:** `ght`
* **First issued:** TODO
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never

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
