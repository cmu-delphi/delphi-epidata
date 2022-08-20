---
title: Department of Health & Human Services
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---

# Department of Health & Human Services
{: .no_toc}

* **Source name:** `hhs`
* **Earliest issue available:** November 16, 2020
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** state, hhs, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

The U.S. Department of Health & Human Services (HHS) publishes several
datasets on patient impact and hospital capacity. One of these
datasets is mirrored in Epidata at the following endpoint:

* [COVID-19 Hospitalization: States](../covid_hosp.md) - daily resolution, state aggregates

That dataset contains dozens of columns that break down hospital
resource usage in different ways.

This indicator makes available several commonly-used columns and combinations of
columns, aggregated geographically. In particular, we include the sum of all
adult and pediatric COVID-19 hospital admissions. This sum is used as the
"ground truth" for hospitalizations by the 
[COVID-19 Forecast Hub](https://github.com/reichlab/covid19-forecast-hub/blob/master/data-processed/README.md#hospitalizations).
We also include influenza hospital admissions.


|                                          Signal <br/> & <br/> 7-day average signal                                           |                                                                                                             Description                                                                                                              |
|:----------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                    `confirmed_admissions_covid_1d` <br/> **&** <br/> `confirmed_admissions_covid_1d_7dav`                    |                                                 Sum of adult and pediatric confirmed COVID-19 hospital admissions occurring each day. <br/> **Earliest date available:** 2019-12-31                                                  |
|               `confirmed_admissions_covid_1d_prop` <br/> **&** <br/> `confirmed_admissions_covid_1d_prop_7dav`               |                                     Sum of adult and pediatric confirmed COVID-19 hospital admissions occurring each day, per 100,000 population. <br/> **Earliest date available:** 2019-12-31                                      |
|      `sum_confirmed_suspected_admissions_covid_1d` <br/> **&** <br/> `sum_confirmed_suspected_admissions_covid_1d_7dav`      |                                          Sum of adult and pediatric confirmed and suspected COVID-19 hospital admissions occurring each day. <br/> **Earliest date available:** 2019-12-31                                           |
| `sum_confirmed_suspected_admissions_covid_1d_prop` <br/> **&** <br/> `sum_confirmed_suspected_admissions_covid_1d_prop_7dav` |                              Sum of adult and pediatric confirmed and suspected COVID-19 hospital admissions occurring each day, per 100,000 population. <br/> **Earliest date available:** 2019-12-31                               |
|                `confirmed_admissions_influenza_1d` <br/> **&** <br/> `confirmed_admissions_influenza_1d_7dav`                |             All confirmed influenza hospital admissions occurring each day. We made this signal available November 1, 2021. <br/> **Earliest issue available:** 2021-09-20 <br/> **Earliest date available:** 2020-01-02             |
|           `confirmed_admissions_influenza_1d_prop` <br/> **&** <br/> `confirmed_admissions_influenza_1d_prop_7dav`           | All confirmed influenza hospital admissions occurring each day, per 100,000 population. We made this signal available November 1, 2021. <br/> **Earliest issue available:** 2021-09-20 <br/> **Earliest date available:** 2020-01-02 |

*for all the above signals & 7-day average signals, their geography is state, and resolution is 1 day.

The 7-day average signals are computed by Delphi by calculating
moving averages of the preceding 7 days, so e.g. the signal for June 7 is the
average of the underlying data for June 1 through 7, inclusive.

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

This indicator mirrors and lightly aggregates data originally
published by the U.S. Department of Health & Human Services. 
As a work of the US government, the original data is in the 
[public domain](https://www.usa.gov/government-works).
