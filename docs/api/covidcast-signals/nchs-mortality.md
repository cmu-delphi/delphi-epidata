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

This data source of Provisional Death Counts for COVID-19 is based on reports made
available by National Center for Health statistics [(NCHS)](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm).

| Signal | Description |
| --- | --- |
| `covid_deaths_num` | Number of all the weekly new deaths with confirmed or presumed COVID-19 |
| `covid_deaths_prop` | Number of all the weekly new deaths with confirmed or presumed COVID-19 per 100,000 population |
| `total_deaths_num` | Number of weekly new deaths from all causes |
| `total_deaths_prop` | Number of weekly new deaths from all causes per 100,000 population |
| `influenza_deaths_num` | Number of weekly new deaths involving Influenza |
| `influenza_deaths_prop` | Number of weekly new deaths involving Influenza per 100,000 population |
| `pneumonia_deaths_num` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths |
| `pneumonia_deaths_prop` | Number of weekly new deaths involving Pneumonia, excluding Influenza deaths per 100,000 population |
| `pneumonia_and_covid_deaths_num`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza |
|`pneumonia_and_covid_deaths_prop`| Number of weekly new deaths involving COVID-19 and Pneumonia, excluding Influenza per 100,000 population |
|`pneumonia_influenza_or_covid_19_deaths_num`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19|
|`pneumonia_influenza_or_covid_19_deaths_prop`| Number of weekly new deaths involving Pneumonia, Influenza, or COVID-19 per 100,000 population|
|`percent_of_expected_deaths`| The number of weekly new deaths for all causes in 2020 compared to the average number across the same week in 2017–2019|

These signals are taken directly from [Table 1](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm) without changes. National provisional counts include deaths occurring within the 50 states and the District of Columbia that have been received and coded as of the date specified. The deaths are classified based on a new ICD-10 code. The codes that are considered for each signals are described in details [here](https://github.com/cmu-delphi/covidcast-indicators/blob/nchs_mortality/nchs_mortality/DETAILS.md#metrics-level-1-m1). We export the state-level data as-is in a weekly format. 

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Geographical Exceptions

New York City is considered as a special state in the NCHS Mortality data, but we don't consider NYC separately. The death counts for NYC would be included in New York State in our reports.

## Report Using Epiweeks

We report the NCHS Mortality data in a weekly format (weekly_YYYYWW, where YYYYWW refers to an epiweek). However, NCHS reports their weekly data from Saturday to Saturday. We assume there is a one day shift. For example, they report a death counts for Alaska in a week starting from date D, we will report the timestamp of this report as the corresponding epiweek of date(D + 1).

## Data Versioning
Data versions are tracked on both a daily and weekly level. On a daily level, we check for updates for NCHS mortality data every weekday as how it is reported by CDC and stash these daily updates on S3, but not our API. On a weekly level (on Mondays), we additionally upload the changes to the data made over the past week (due to backfill) to our API.

## Lag and Backfill
There is a lag in time between the death occurred and when the death certificate is completed, submitted to NCHS and processed for reporting purposes. This delay can range from 1 week to 8 weeks or even more, as described by NCHS. 


