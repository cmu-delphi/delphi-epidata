---
title: NCHS Mortality Data
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# NCHS Mortality Data
{: .no_toc}

* **Source name:** `nchs-mortality`
* **First issued:** Epiweek 50 2020 (6-12 December 2020)
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week (see [date format docs](../covidcast_times.md))
* **License:** [NCHS Data Use Agreement](https://www.cdc.gov/nchs/data_access/restrictions.htm)

This data source of national provisional death counts is based on death
certificate data received and coded by the National Center for Health Statistics
[(NCHS)](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm). This data is
different from the death data available from [USAFacts](usa-facts.md) and [JHU
CSSE](jhu-csse.md): deaths are reported by the date they occur, not the date
they are reported by local health departments, and data is frequently reissued
as additional death certificates from recent weeks are received and tabulated.

| Signal | Description |
| --- | --- |
| `deaths_covid_incidence_num` | Number of weekly new deaths with confirmed or presumed COVID-19 |
| `deaths_covid_incidence_prop` | Number of weekly new deaths with confirmed or presumed COVID-19, per 100,000 population |
| `deaths_allcause_incidence_num` | Number of weekly new deaths from all causes |
| `deaths_allcause_incidence_prop` | Number of weekly new deaths from all causes, per 100,000 population |
| `deaths_flu_incidence_num` | Number of weekly new deaths involving Influenza and at least one of (Pneumonia, COVID-19)|
| `deaths_flu_incidence_prop` | Number of weekly new deaths involving Influenza and at least one of (Pneumonia, COVID-19), per 100,000 population |
| `deaths_pneumonia_notflu_incidence_num` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths |
| `deaths_pneumonia_notflu_incidence_prop` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths, per 100,000 population |
| `deaths_covid_and_pneumonia_notflu_incidence_num`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza |
| `deaths_covid_and_pneumonia_notflu_incidence_prop`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza, per 100,000 population |
|`deaths_pneumonia_or_flu_or_covid_incidence_num`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19|
|`deaths_pneumonia_or_flu_or_covid_incidence_prop`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19, per 100,000 population|
|`deaths_percent_of_expected`| Number of weekly new deaths for all causes in 2020 compared to the average number across the same week in 2017–2019|

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Calculation

These signals are taken directly from [Table
1](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm) without
changes. National provisional death counts include deaths occurring within the
50 states and the District of Columbia that have been received and coded as of
the date specified during a given time period. The deaths are classified based
on a new ICD-10 code. (Note that the classification is based on all the codes on
the death certificate, not just the primary cause of death). The codes that are
considered for each signals are described in detail
[here](https://github.com/cmu-delphi/covidcast-indicators/blob/main/nchs_mortality/DETAILS.md#metrics-level-1-m1). We
export the state-level data as-is in a weekly format.

## Geographical Exceptions

New York City is listed as its own region in the NCHS Mortality data, but
we don't consider NYC separately. The death counts for NYC are included in New
York State in our reports.

## Report Using Epiweeks

We report the NCHS Mortality data in a weekly format (`time_type=week` &
`time_value={YYYYWW}`, where `YYYYWW` refers to an epiweek). The CDC defines
the [epiweek](https://wwwn.cdc.gov/nndss/document/MMWR_Week_overview.pdf) as
seven days, from Sunday to Saturday. We check the week-ending dates provided in
the NCHS morality data and use Python package
[epiweeks](https://pypi.org/project/epiweeks/) to convert them into epiweek
format.

## Missingness

NCHS suppresses some data to protect individual privacy and avoid publishing
low-confidence figures. This includes data for jurisdictions where counts are
between 1 and 9, and data for weeks where the counts are less than 50% of the
expected number, since these provisional counts are highly incomplete and
potentially misleading.

## Lag and Backfill

There is a lag in time between when the death occurred and when the death
certificate is completed, submitted to NCHS, and processed for reporting
purposes. The death counts for recent weeks are continually revised and may
increase or decrease as new and updated death certificate data are received from
the states by NCHS. This delay can range from 1 to 8 weeks or even more.
Some states report deaths on a daily basis, while other states report deaths weekly
or monthly. State vital record reporting may also be affected or delayed by
COVID-19 related response activities which make death counts not comparable
across states. We check for updates reported by NCHS every weekday but will
report the signals weekly (on Monday).

## Source and Licensing

This data was originally published by the National Center for Health Statistics,
and is made available here as a convenience to the forecasting community under
the terms of the original license. The NCHS places restrictions on how this
dataset may be used: you may not attempt to identify any individual included in
the data, whether by itself or through linking to other
individually identifiable data; you may only use the dataset for statistical
reporting and analysis. The full text of the [NCHS Data Use
Agreement](https://www.cdc.gov/nchs/data_access/restrictions.htm) is available
from their website.
