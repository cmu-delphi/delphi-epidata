---
title: NCHS Mortality Data
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# NCHS Mortality Data
{: .no_toc}

* **Source name:** `nchs_mortality`
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** state (see [geography coding docs](../covidcast_geography.md))

This data source of national provisional death counts is based on death certificate data received and coded by the National Center for Health Statistics [(NCHS)](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm). 

| Signal | Description |
| --- | --- |
| `deaths_covid_incidence_num` | Number of weekly new deaths with confirmed or presumed COVID-19 |
| `deaths_covid_incidence_prop` | Number of weekly new deaths with confirmed or presumed COVID-19, per 100,000 population |
| `deaths_allcause_incidence_num` | Number of weekly new deaths from all causes |
| `deaths_allcause_incidence_prop` | Number of weekly new deaths from all causes, per 100,000 population |
| `deaths_flu_incidence_num` | Number of weekly new deaths involving Influenza |
| `deaths_flu_incidence_prop` | Number of weekly new deaths involving Influenza, per 100,000 population |
| `deaths_pneumonia_notflu_incidence_num` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths |
| `deaths_pneumonia_notflu_incidence_prop` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths, per 100,000 population |
| `deaths_covid_and_pneumonia_notflu_incidence_num`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza |
| `deaths_covid_and_pneumonia_notflu_incidence_prop`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza, per 100,000 population |
|`deaths_pneumonia_or_flu_or_covid_incidence_num`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19|
|`deaths_pneumonia_or_flu_or_covid_incidence_prop`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19, per 100,000 population|
|`deaths_percent_of_expected`| The number of weekly new deaths for all causes in 2020 compared to the average number across the same week in 2017–2019|

These signals are taken directly from [Table 1](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm) without changes. National provisional death counts include deaths occurring within the 50 states and the District of Columbia that have been received and coded as of the date specified during a given time period. The deaths are classified based on a new ICD-10 code. (Note that, the classification is based on all the codes on the death certificate, but not the primary cause of death). The codes that are considered for each signals are described in details [here](https://github.com/cmu-delphi/covidcast-indicators/blob/nchs_mortality/nchs_mortality/DETAILS.md#metrics-level-1-m1). We export the state-level data as-is in a weekly format. 

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Geographical Exceptions

New York City is considered as a special state in the NCHS Mortality data, but we don't consider NYC separately. The death counts for NYC are included in New York State in our reports.

## Report Using Epiweeks

We report the NCHS Mortality data in a weekly format (`time_type=week` \& `time_value=\{YYYYWW\}`, where `YYYYWW` refers to an epiweek). The CDC defines the [epiweek](https://wwwn.cdc.gov/nndss/document/MMWR_Week_overview.pdf) as seven days, from Sunday to Saturday. We check the week-ending dates provided in the NCHS morality data and use Python package [epiweeks](https://pypi.org/project/epiweeks/) to convert them into epiweek format.

## Lag and Backfill
There is a lag in time between the death occurred and when the death certificate is completed, submitted to NCHS and processed for reporting purposes. The death counts for earlier weeks are continually revised and may increase or decrease as new and updated death certificate data are received from the states by NCHS.  This delay can range from 1 week to 8 weeks or even more. We check for updates every weekday as they are reported by NCHS, but will report the signals weekly (on Mondays). The changes in the data due to backfill made over the past week can be fetched from our API.
