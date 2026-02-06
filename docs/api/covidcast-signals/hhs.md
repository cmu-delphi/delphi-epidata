---
parent: Inactive Sources
grand_parent: Data Sources and Signals
title: HHS Hospitalizations from NHSN
---

# Department of Health & Human Services Hospitalizations
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `hhs` |
| **Data Source** | U.S. Department of Health & Human Services |
| **Geographic Levels** | National, Department of Health & Human Services (HHS) Regions, State (see [geography coding docs](../covidcast_geography.md)) |
| **Temporal Granularity** | Daily (see [date format docs](../covidcast_times.md)) |
| **Reporting Cadence** | Inactive - no longer updated since 2024-04-30 |
| **Date of last data revision:** | Never (see [data revision docs](#changelog)) |
| **Temporal Scope Start** | 2019-12-31 |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

See [COVIDcast Signal Changes](../covidcast_changelog.md) for general information about how we track changes to signals.

No changes so far.

</details>

## Overview

The U.S. Department of Health & Human Services (HHS) publishes several
datasets on patient impact and hospital capacity. The data is made available
to HHS through the CDC’s National Healthcare Safety Network (NHSN). 
See [NHSN Respiratory Hospitalizations](nhsn.md) for the current data source.
One of these datasets is mirrored in Epidata at the following endpoint:

* [COVID-19 Hospitalization: States](../covid_hosp.md) - daily resolution, state aggregates

That dataset contains dozens of columns that break down hospital
resource usage in different ways.

These indicators make available several commonly-used columns and combinations of
columns, aggregated geographically. In particular, we include the sum of all
adult and pediatric COVID-19 hospital admissions. This sum is used as the
"ground truth" for hospitalizations by the
[COVID-19 Forecast Hub](https://github.com/reichlab/covid19-forecast-hub/blob/master/data-processed/README.md#hospitalizations).
We also include influenza hospital admissions.


Each metric below is available in four variants, with the relevant suffix added to the end of a base signal name, given in the table below.

1.  **Raw Count (daily) :** `_1d`
2.  **Smoothed (7-day average):** `_1d_7dav`
3.  **Population Proportion (per 100k):** `_1d_prop`
4.  **Smoothed Proportion:** `_1d_prop_7dav`

| Metric | Base Signal Name | Description |
| :--- | :--- | :--- |
| **Confirmed COVID-19** | `confirmed_admissions_covid` | **Sum of Adult + Pediatric.** Confirmed admissions only.<br><br>**Earliest Dates:**<br>• `_1d`: **2019-12-31**<br>• `_7dav`: **2020-01-06** |
| **Suspected + Confirmed** | `sum_confirmed_suspected_admissions_covid` | **Sum of Adult + Pediatric.** Combined count of confirmed and suspected cases.<br><br>**Earliest Dates:**<br>• `_1d`: **2019-12-31**<br>• `_7dav`: **2020-01-06** |
| **Influenza** | `confirmed_admissions_influenza` | All confirmed influenza hospital admissions.<br><br>**Earliest Dates:**<br>• `_1d`: **2020-01-02**<br>• `_7dav`: **2020-01-08** |


> **Note**
> * For all the above signals & 7-day average signals, their geography is state, and resolution is 1 day.
> * The 7-day average signals are computed by Delphi by calculating moving averages of the preceding 7 days, so e.g. the signal for June 7 is the average of the underlying data for June 1 through 7, inclusive.
{: .note }


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

### Statewise, daily resolution, COVID-19

Statewise daily resolution signals for COVID-19 use the following four columns from
the HHS state timeseries dataset:

* `previous_day_admission_[adult|pediatric]_covid_[confirmed|suspected]`

The `confirmed` signal is the sum of the two `confirmed` columns:

* adult
* pediatric

The `sum_confirmed_suspected` signal is the sum of all four columns:

* adult confirmed
* adult suspected
* pediatric confirmed
* pediatric suspected

The source data specifies that admissions occurred on the previous
day. We automatically adjust the date of each result so that
admissions are incident on that date.

### Statewise, daily resolution, influenza

Statewise daily resolution signals for influenza use the following column from
the HHS state timeseries dataset:

* `previous_day_admission_influenza_confirmed`

The source data specifies that admissions occurred on the previous day. We
automatically adjust the date of each result so that admissions are incident on
that date.

## Limitations

HHS collects data from state and territorial health departments about many, but
not all, hospitals in the U.S. Notably excluded from this dataset are
psychiatric and rehabilitation facilities, Indian Health Service (IHS)
facilities, U.S. Department of Veterans Affairs (VA) facilities, Defense Health
Agency (DHA) facilities, and religious non-medical facilities.

Standard errors and sample sizes are not applicable to these metrics.

## Lag and Backfill

HHS issues updates to this timeseries once a week, and occasionally more
often. We check for updates daily. Lag varies from 0 to 6 days.

Occasionally a value published in an early issue will be changed in a subsequent
issue when additional data becomes known. This effect is known as
backfill. Backfill is relatively uncommon in this dataset (80% of dates from
November 1, 2020 onward are never touched after their first issue) and most such
updates occur one to two weeks after information about a date is first
published. In rare instances, a value may be updated 10 weeks or more after it
is first published.

## Source and Licensing

These indicators mirror and lightly aggregate data originally
published by the U.S. Department of Health & Human Services.
As a work of the US government, the original data is in the
[public domain](https://www.usa.gov/government-works).
