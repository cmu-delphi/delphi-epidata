---
title: NCHS Mortality Data
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# NCHS Mortality Data
{: .no_toc}

* **Source name:** ``
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** state (see [geography coding docs](../covidcast_geography.md))

This data source of national provisional death counts are based on death certificate data received and coded by the National Center for Health Statistics [(NCHS)](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm). 

| Signal | Description |
| --- | --- |
| `covid_deaths_num` | Number of  weekly new deaths with confirmed or presumed COVID-19 |
| `covid_deaths_prop` | Number of weekly new deaths with confirmed or presumed COVID-19, per 100,000 population |
| `total_deaths_num` | Number of weekly new deaths from all causes |
| `total_deaths_prop` | Number of weekly new deaths from all causes, per 100,000 population |
| `influenza_deaths_num` | Number of weekly new deaths involving Influenza |
| `influenza_deaths_prop` | Number of weekly new deaths involving Influenza, per 100,000 population |
| `pneumonia_deaths_num` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths |
| `pneumonia_deaths_prop` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths, per 100,000 population |
| `pneumonia_and_covid_deaths_num`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza |
|`pneumonia_and_covid_deaths_prop`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza, per 100,000 population |
|`pneumonia_influenza_or_covid_19_deaths_num`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19|
|`pneumonia_influenza_or_covid_19_deaths_prop`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19, per 100,000 population|
|`percent_of_expected_deaths`| The number of weekly new deaths for all causes in 2020 compared to the average number across the same week in 2017–2019|

These signals are taken directly from [Table 1](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm) without changes. National provisional death counts include deaths occurring within the 50 states and the District of Columbia that have been received and coded as of the date specified during a given time period, especially for the more recent time periods. The deaths are classified based on a new ICD-10 code. The codes that are considered for each signals are described in details [here](https://github.com/cmu-delphi/covidcast-indicators/blob/nchs_mortality/nchs_mortality/DETAILS.md#metrics-level-1-m1). We export the state-level data as-is in a weekly format. 

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Geographical Exceptions

New York City is considered as a special state in the NCHS Mortality data, but we don't consider NYC separately. The death counts for NYC are included in New York State in our reports.

## Report Using Epiweeks

We report the NCHS Mortality data in a weekly format (`time_type=week` \& `time_value=\{YYYYWW\}`, where YYYYWW refers to an epiweek). However, NCHS reports their weekly data from Saturday to Saturday. We assume there is a one day shift. For example, they report a death counts for Alaska in a week starting from date D (a Saturday), out report will have `time_value` set to be the corresponding epiweek of date (D + 1).

## Lag and Backfill
There is a lag in time between the death occurred and when the death certificate is completed, submitted to NCHS and processed for reporting purposes. The death counts for earlier weeks are continually revised and my increase or decrease as new and updated death certificate data are received from the states by NCHS.  This delay can range from 1 week to 8 weeks or even more. We check for updates every weekday as how it is reported by NCHS but will report the signals weekly (on Mondays). The changes in the data due to backfill made over the past week can be fetched from our API.


