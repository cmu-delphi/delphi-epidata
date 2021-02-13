---
title: Contingency Tables parent: COVID Symptom Survey nav_order: 4
---

# Contingency Tables
{: .no_toc}

This documentation describes the fine-resolution contingency tables produced by
grouping [COVID Symptom Survey](./index.md) individual responses by various
demographic features.

Please also take a look at the [individual response data](./survey-files.md),
and the coarse aggregates -- grouped only by region -- available [through the
COVIDcast API](../api/covidcast-signals/fb-survey.md) to find the data product
that best suits your needs.

Important updates for data users, including corrections to data or updates on
data processing delays, are posted as `OUTAGES.txt` in the directory where the
data is hosted.

## Table of contents
{: .no_toc .text-delta}

1. TOC {:toc}

## Available Data Files

We provide two types of data files, weekly and monthly. Users who need the most
up-to-date data or are interested in timeseries should use the weekly files,
while those who want to study groups with smaller sample sizes should use the
monthly files. Because monthly aggregates include more responses, they have
lower missingness when grouping by several features at a time.

## Dates
The included files provide estimates for various metrics of interest over a
period of either a full epiweek or a full month.

## Aggregation
The aggregates are filtered to only include estimates for a particular group if
there were 100 or more responses. Especially in the weekly aggregtes, many of
the state-level groups have been filtered out due to low sample size. In such
cases, the state marginal files, which group by a single demographic of interest
at a time, will likely provide more coverage.

## File format

### Naming

Each CSV is named as follows:

  {date}_{region}_{vars}.csv

Dates in of the form `YYYYmmdd`. `date` refers to the first day of the time
period survey responses were aggregated over, in the Pacific time zone (UTC -
7). Unless noted otherwise, this is always a complete month or epiweek. `region`
is the geographic level responses were aggregated over. At the moment, only
nation-wide and state groupings are available. `vars` is a list all other
grouping variables used in the aggregation, ordered alphabetically.

### Columns

Within a CSV, the first few columns are the grouping variables, ordered
alphabetically. Each aggregate reports four columns (unrounded):

* `val_<indicator name>`: the main value of interest, e.g., percent, average, or
  count
* `se_<indicator name>`: the standard error of `val_<indicator name>`
* `sample_size_<indicator name>`: the number of survey responses used to
  calculate `val_<indicator name>`
* `represented_<indicator name>`: the number of people in the population that
  `val_<indicator name>` represents over all days in the given time period. This
  is the sum of [participant weights](./weights.md) for all survey responses
  used.

All aggregates using the same set of grouping variables appear in a single CSV.

## Indicators

The files in this folder contain [weighted](./weights.md) estimates of percent
of respondents who fulfill one or several criteria. Estimates are broken out by
state, age, gender, race, and ethnicity.

| Signal | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccinated` | Estimated percentage of respondents who have already received a COVID vaccine. <br/> **Earliest date available:** 2021-01-01 | V1 |
| `pct_accepting` | Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_concerned_sideeffects` | Estimated percentage of respondents who are very or moderately concerned that they would "experience a side effect from a COVID-19 vaccination." (Asked of all respondents, including those who have already received one or more doses of a COVID-19 vaccine.) <br/> **Earliest date available:** 2021-01-01 | V9 |
| `pct_hesitant_sideeffects` | Estimated percentage of respondents who are very or moderately concerned that they would "experience a side effect from a COVID-19 vaccination" *and* would "definitely not" or "probably not" get a COVID-19 vaccine if offered. <br/> **Earliest date available:** 2021-01-01 | V9 and V3 |
| `pct_trust_fam` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by friends and family, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_trust_healthcare` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by local health workers, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_trust_who` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by the World Health Organization, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_trust_govt` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by government health officials, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_trust_politicians` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by politicians, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_hesitant_trust_fam` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by friends and family, among respondents who have not yet been vaccinated *and* would "definitely not" or "probably not" get a COVID-19 vaccine if offered. <br/> **Earliest date available:** 2021-01-01 | V3 and V4 |
| `pct_hesitant_trust_healthcare` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by local health workers, among respondents who have not yet been vaccinated *and* would "definitely not" or "probably not" get a COVID-19 vaccine if offered. <br/> **Earliest date available:** 2021-01-01 | V3 and V4 |
| `pct_hesitant_trust_who` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by the World Health Organization, among respondents who have not yet been vaccinated *and* would "definitely not" or "probably not" get a COVID-19 vaccine if offered. <br/> **Earliest date available:** 2021-01-01 | V3 and V4 |
| `pct_hesitant_trust_govt` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by government health officials, among respondents who have not yet been vaccinated *and* would "definitely not" or "probably not" get a COVID-19 vaccine if offered. <br/> **Earliest date available:** 2021-01-01 | V3 and V4 |
| `pct_trust_politicians` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by politicians, among respondents who have not yet been vaccinated *and* would "definitely not" or "probably not" get a COVID-19 vaccine if offered. <br/> **Earliest date available:** 2021-01-01 | V3 and V4 |

Note: CSVs for the month of January 2021 only use data from January 6-31 due to
a [definitional change](./coding.md#new-items-2) in a major vaccine item on
January 6.
