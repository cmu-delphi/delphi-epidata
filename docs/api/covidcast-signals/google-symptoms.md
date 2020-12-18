---
title: Google Search Trends symptoms dataset
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Google Symptoms
{: .no_toc}

* **Source name:** `google-search-trends-symptoms-dataset`
* **First issued:** 30 November 2020
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, MSA, HRR, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** To download or use the data, you must agree to the Google [Terms of Service](https://policies.google.com/terms)

This data source is based on the [COVID-19 Search Trends symptoms
dataset](http://goo.gle/covid19symptomdataset). Using
this search data, we estimate the volume of searches mapped to symptoms related
to COVID-19 such as _anosmia_ (lack of smell) and _ageusia_(lack of taste). The
resulting daily dataset for each region shows the relative frequency of searches
for each symptom. The signals are measured in arbitrary units that are
normalized for overall search users in the region and scaled by the maximum value of the normalized
popularity within a geographic region across a specific time range. **Thus,
values are NOT comparable across geographic regions**. Larger numbers represent
increased releative popularity of symptom-related searches.

| Signal | Description |
| --- | --- |
| `anosmia_raw_search` |  Google search volume for anosmia-related searches, in arbitrary units that are normalized for overall search users |
| `anosmia_smoothed_search` | Google search volume for anosmia-related searches, in arbitrary units that are normalized for overall search users, smoothed by 7-day average |
| `ageusia_raw_search` | Google search volume for ageusia-related searches, in arbitrary units that are normalized for overall search users |
| `ageusia_smoothed_search` |  Google search volume for ageusia-related searches, in arbitrary units that are normalized for overall search users, smoothed by 7-day average |
| `sum_anosmia_ageusia_raw_search` | The sum of Google search volume for anosmia and ageusia related searches, in an arbitrary units that are normalized for overall search users |
| `sum_anosmia_ageusia_smoothed_search` | The sum of Google search volume for anosmia and ageusia related searches, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average |


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}
## Estimation
The `sum_anosmia_ageusia_raw_search` signals are simply the raw sum of the
 values of `anosmia_raw_search` and `ageusia_raw_search`, but not the union of
 anosmia and ageusia related searches. This is because the data volume is
 calculated based on search queries. A single search query can be mapped to more
 than one symptom. Currently, Google does not provide _intersection/union_
 data. Users should be careful when considering such signals.

## Properties and limitations 
WTo learn more about the dataset, how it is generated it and its limitations, 
read the [dataset documentation](https://storage.googleapis.com/gcp-public-data-symptom-search/COVID-19%20Search%20Trends%20symptoms%20dataset%20documentation%20.pdf).

## Geographical Aggregation
The state-level and county-level `raw_search` signals for specific symptoms such
as _anosmia_ and _ageusia_ are taken directly from the [COVID-19 Search Trends
symptoms
dataset](https://github.com/google-research/open-covid-19-data/tree/master/data/exports/search_trends_symptoms_dataset)
without changes. We aggregate the county-level data to the MSA and HRR levels
using the population-weighted average. For MSAs/HRRs that include counties that
have no data provided due to quality or privacy issues for a certain day, we
simply assume the values to be 0 during aggregation. The values for MSAs/HRRs
with no counties having non-NaN values will not be reported. Thus, the resulting
MSA/HRR level data does not fully match the _actual_ MSA/HRR level data (which
we are not provided).


## Lag and Backfill
Google does not currently update the search data daily, but usually twice a week.
Each update will usually the coverage to within three days of the day of the update.
As a result the delay can range from 3 to 10 days or even more. We check for
updates every day and provide the most up-to-date data.
