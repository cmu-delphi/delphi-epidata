---
title: Google Symptoms
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Google Symptoms
{: .no_toc}

* **Source name:** `google-symptoms`
* **First issued:** 30 November 2020
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, MSA, HRR, state (see [geography coding docs](../covidcast_geography.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

This data source is based on [COVID-19 Search Trends symptoms dataset](https://github.com/google-research/open-covid-19-data/tree/master/data/exports/search_trends_symptoms_dataset). Using this search data, we estimate the volume of searches mapped to symptoms related to COVID-19 such as _anosmia_ (lack of smell) and _ageusia_(lack of taste). The resulting daily dataset for each region shows the relative frequency of searches for each symptom. The signals are measured in arbitrary units that are normalized for population and scaled by the maximum value of the normalized popularity within a 
geographic region across a specific time range. **Thus, values are NOT 
comparable across geographic regions**. Larger numbers represent higher numbers of symptom-related searches.

| Signal | Description |
| --- | --- |
| `anosmia_raw_search` |  Google search volume for anosmia-related searches, in arbitrary units that are normalized for population |
| `anosmia_smoothed_search` | Google search volume for anosmia-related searches, in arbitrary units that are normalized for population, smoothed by 7-day average |
| `ageusia_raw_search` | Google search volume for ageusia-related searches, in arbitrary units that are normalized for population |
| `ageusia_smoothed_search` |  Google search volume for ageusia-related searches, in arbitrary units that are normalized for population, smoothed by 7-day average |
| `sum_anosmia_ageusia_raw_search` | The sum of Google search volume for anosmia and ageusia related searches, in an arbitrary units that are normalized for population |
| `sum_anosmia_ageusia_smoothed_search` | The sum of Google search volume for anosmia and ageusia related searches, in an arbitrary units that are normalized for population, smoothed by 7-day average |


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}
## Estimation
The `sum_anosmia_ageusia_raw_search` signals are simply the raw sum of the values of `anosmia_raw_search`
 and `ageusia_raw_search`, but not the union of anosmia and ageusia related searches. This is because the data volume is calculated based on search queries. A single search query can be mapped to more than one symptom. Currently, Google does not provide _intersection/union_ data. Users should be careful when considering such signals.

## Limitation 
When daily volume in a region does not meet quality or privacy thresholds, set by Google, no value
will be reported. Since Google uses differential privacy, there is artificial noise added to the raw 
datasets to avoid identifying any individual persons without affecting the quality of results. 

The data is normalized by the total number of Search users in certain regions for a certain time period and is scaled considering the maximum value of the normalized
popularity across the entire published time range for that region over all symptoms. The values
of symptom popularity are **NOT** comparable across geographic regions. Due to the scaling step, 
most of the values should be in the range 0-1. However, since the scaling factor is calculated and stored at a certain time point, the symptom popularity released after that time point is likely to exceed the previously-observed maximum value which results in values larger than 1.


## Geographical Aggregation
The state-level and county-level `raw_search` signals for specific symptoms such as _anosmia_ and _ageusia_ are taken directly from the [COVID-19 Search Trends symptoms dataset](https://github.com/google-research/open-covid-19-data/tree/master/data/exports/search_trends_symptoms_dataset) without changes. We aggregate the county-level data to the MSA and HRR levels using the population-weighted average. For MSAs/HRRs with part of the counties with no data provided due to quality of privacy issue for a certain day, we simply assume the values to be 0 during aggregation. The values for MSAs/HRRs with no counties having non-NaN values will not be reported. Thus, the resulting MSA/HRR level data does not fully match the _actual_ MSA/HRR level data (which we are not provided).


## Lag and Backfill
Google does not update the search data daily, but has an uncertain update frequency. The delay can range from 1 day to 10 days or even more. We check for updates everyday and provide the most up-to-date data.
