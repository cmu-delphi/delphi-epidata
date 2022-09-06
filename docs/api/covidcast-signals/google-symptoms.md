---
title: Google Search Trends symptoms dataset
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---

# Google Symptoms
{: .no_toc}

* **Source name:** `google-symptoms`
* **Earliest issue available:** November 30, 2020
* **Number of data revisions since May 19, 2020:** 1
* **Date of last change:** January 20, 2022
* **Available for:** county, MSA, HRR, state, HHS, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** To download or use the data, you must agree to the Google [Terms of Service](https://policies.google.com/terms)

## Overview

This data source is based on the [COVID-19 Search Trends symptoms
dataset](http://goo.gle/covid19symptomdataset). Using
this search data, we estimate the volume of searches mapped to symptom sets related
to COVID-19. The resulting daily dataset for each region shows the average relative frequency of searches for each symptom set. The signals are measured in arbitrary units that are normalized for overall search users in the region and scaled by the maximum value of the normalized popularity within a geographic region across a specific time range. **Values are comparable across signals in the same location but NOT across geographic regions**. For example, within a state, we can compare `s01_smoothed_search` and `s02_smoothed_search`. However, we cannot compare `s01_smoothed_search` between states. Larger numbers represent increased relative popularity of symptom-related searches.

#### Symptom sets

* _s01_: Cough, Phlegm, Sputum, Upper respiratory tract infection
* _s02_: Nasal congestion, Post nasal drip, Rhinorrhea, Sinusitis, Rhinitis, Common cold
* _s03_: Fever, Hyperthermia, Chills, Shivering, Low grade fever
* _s04_: Shortness of breath, Wheeze, Croup, Pneumonia, Asthma, Crackles, Acute bronchitis, Bronchitis
* _s05_: Anosmia, Dysgeusia, Ageusia
* _s06_: Laryngitis, Sore throat, Throat irritation
* _scontrol_: Type 2 diabetes, Urinary tract infection, Hair loss, Candidiasis, Weight gain

The symptoms were combined in sets that showed positive correlation with cases, especially after Omicron was declared a variant of concern by the WHO. Note that symptoms in _scontrol_ are not COVID-19 related, and this symptom set can be used as a negative control.

Until January 20, 2022, we had separate signals for symptoms Anosmia, Ageusia, and their sum.

| Signal | Description |
| --- | --- |
| `s01_raw_search` | The average of Google search volume for related searches of symptom set _s01_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `s01_smoothed_search` | The average of Google search volume for related searches of symptom set _s01_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-01-07 |
| `s02_raw_search` | The average of Google search volume for related searches of symptom set _s02_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `s02_smoothed_search` | The average of Google search volume for related searches of symptom set _s02_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-01-07 |
| `s03_raw_search` | The average of Google search volume for related searches of symptom set _s03_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `s03_smoothed_search` | The average of Google search volume for related searches of symptom set _s03_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-01-07 |
| `s04_raw_search` | The average of Google search volume for related searches of symptom set _s04_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `s04_smoothed_search` | The average of Google search volume for related searches of symptom set _s04_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-01-07 |
| `s05_raw_search` | The average of Google search volume for related searches of symptom set _s05_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `s05_smoothed_search` | The average of Google search volume for related searches of symptom set _s05_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-01-07 |
| `s06_raw_search` | The average of Google search volume for related searches of symptom set _s06_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `s06_smoothed_search` | The average of Google search volume for related searches of symptom set _s06_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-01-07 |
| `scontrol_raw_search` | The average of Google search volume for related searches of symptom set _scontrol_, in an arbitrary units that are normalized for overall search users. <br/> **Earliest date available:** 2020-01-01 |
| `scontrol_smoothed_search` | The average of Google search volume for related searches of symptom set _scontrol_, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. <br/> **Earliest date available:** 2020-02-20 |
| `anosmia_raw_search` |  Google search volume for anosmia-related searches, in arbitrary units that are normalized for overall search users. _This signal is no longer updated as of 20 January, 2022._ <br/> **Earliest date available:** 2020-02-13 |
| `anosmia_smoothed_search` | Google search volume for anosmia-related searches, in arbitrary units that are normalized for overall search users, smoothed by 7-day average. _This signal is no longer updated as of 20 January, 2022._ <br/> **Earliest date available:** 2020-02-20 |
| `ageusia_raw_search` | Google search volume for ageusia-related searches, in arbitrary units that are normalized for overall search users. _This signal is no longer updated as of 20 January, 2022._ <br/> **Earliest date available:** 2020-02-13 |
| `ageusia_smoothed_search` |  Google search volume for ageusia-related searches, in arbitrary units that are normalized for overall search users, smoothed by 7-day average. _This signal is no longer updated as of 20 January, 2022._ <br/> **Earliest date available:** 2020-02-20 |
| `sum_anosmia_ageusia_raw_search` | The sum of Google search volume for anosmia and ageusia related searches, in an arbitrary units that are normalized for overall search users. _This signal is no longer updated as of 20 January, 2022._ <br/> **Earliest date available:** 2020-02-13 |
| `sum_anosmia_ageusia_smoothed_search` | The sum of Google search volume for anosmia and ageusia related searches, in an arbitrary units that are normalized for overall search users, smoothed by 7-day average. _This signal is no longer updated as of 20 January, 2022._ <br/> **Earliest date available:** 2020-02-20 |


## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation
Each signal is the average of the
 values of search trends for each symptom in the symptom set. For example, `s05_raw_search` is the average of the search trend values of anosmia, ageusia, and dysgeusia. Note that this is different from the union of
 anosmia, ageusia, and dysgeusia related searches divided by 3, because the data volume for each symptom is calculated based on search queries. A single search query can be mapped to more than one symptom. Currently, Google does not provide _intersection/union_
 data. Users should be careful when considering such signals.

 For each symptom set: when search trends for all symptoms are missing, the signal is reported as missing. When search trends are available for at least one of the symptoms, we fill the missing trends for other symptoms with 0 and compute the average. We use this approach because the missing observations in the Google Symptoms search trends dataset do not occur randomly; they represent low popularity and are censored for quality and/or privacy reasons. The same approach is used for smoothed signals. A 7 day moving average is used, and missing raw signals are filled with 0 as long as there is at least one day available within the 7 day window.



## Geographical Aggregation
The state-level and county-level `raw_search` signals for each symptoms set are the average of its individual symptoms search trends, taken directly from the [COVID-19 Search Trends
symptoms
dataset](https://github.com/google-research/open-covid-19-data/tree/master/data/exports/search_trends_symptoms_dataset).

We aggregate county and state data to other geographic levels using
population-weighted averaging.

| Source level | Aggregated level |
| ------------ | ---------------- |
| county       | MSA, HRR         |
| state        | HHS, nation      |

For aggregation purposes only, we assign a value of 0 to source regions that
have no data provided due to quality or privacy issues for a certain day (see
Limitations for details). We do not report aggregated regions if none of their
source regions have data. Because of this censoring behavior, the resulting data
for aggregated regions does not fully match the _actual_ search volume for these
regions (which is not provided to us).

## Lag and Backfill
Google does not currently update the search data daily, but usually twice a week.
Each update will usually extend the coverage to within three days of the day of the update.
As a result the delay can range from 3 to 10 days or even more. We check for
updates every day and provide the most up-to-date data.

## Limitations
When daily volume in a region does not meet quality or privacy thresholds, set
by Google, no daily value is reported. Weekly data may be available from Google
in these cases, but we do not yet support importation using weekly data.

Google uses differential privacy, which adds artificial noise to the raw
datasets to avoid identifying any individual persons without affecting the
quality of results.

Google normalizes and scales time series values to determine the relative
popularity of symptoms in searches within each geographical region individually.
This means that the resulting values of symptom set popularity are **NOT**
comparable across geographic regions, while the values of different symptom sets are comparable within the same location.

Standard errors and sample sizes are not available for this data source.

More details about the limitations of this dataset are available in [Google's Search
Trends symptoms dataset documentation](https://storage.googleapis.com/gcp-public-data-symptom-search/COVID-19%20Search%20Trends%20symptoms%20dataset%20documentation%20.pdf).

## Source and Licensing
This dataset is based on Google's [COVID-19 Search Trends symptoms dataset](http://goo.gle/covid19symptomdataset), which is licensed under Google's [Terms of Service](https://policies.google.com/terms).

To learn more about the source data, how it is generated and its limitations,
read [Google's Search Trends symptoms dataset documentation](https://storage.googleapis.com/gcp-public-data-symptom-search/COVID-19%20Search%20Trends%20symptoms%20dataset%20documentation%20.pdf).
