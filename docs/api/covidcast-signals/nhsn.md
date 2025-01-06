---
title: NHSN ED Visits
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
nav_order: 1
---
# National Syndromic Surveillance Program Emergency Department Visits
{: .no_toc}

* **Source name:** `nhsn`
* **Earliest issue available:** August 08, 2020
* **Number of data revisions since 18 Nov 2024:** 0
* **Date of last change:** Never
* **Available for:** state, hhs, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

## Overview

[The National Healthcare Safety Network (NHSN)](https://www.cdc.gov/nhsn/index.html) is the nation’s most widely used healthcare-associated infection tracking system.
This dataset represents preliminary weekly hospital respiratory data and metrics aggregated to national and state/territory levels reported to CDC’s National Health Safety Network (NHSN) beginning August 2020.
Each signal below is derived from one of two following datasets:
- Main: [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data)
- Preliminary: [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN) (Preliminary)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/mpgq-jmmr/about_data). Signals derived from the preliminary dataset have suffix `_prelim` in their signal names.

Both datasets started reporting data in late 2022. As of May 2024, NHSN received data from 78% of US EDs.

| Signal                          | Description                                                                                                                                                                         |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `confirmed_admissions_covid_ew`              | Total number of patients hospitalized with confirmed COVID-19 captured for the Wednesday of the reporting week **Earliest date available:** 2020-08-08                                                                                                     |
| `confirmed_admissions_covid_ew_prelim`          | Total number of patients hospitalized with confirmed COVID-19 captured for the Wednesday of the reporting week preliminary data reported to NHSN for the previous reporting week (Sunday – Saturday). <br/> **Earliest date available:** 2020-08-08  |
| `confirmed_admissions_flu_ew`           | Total number of patients hospitalized with confirmed influenza captured for the Wednesday of the reporting week  <br/> **Earliest date available:** 2020-08-08                                                                                       |
| `confirmed_admissions_flu_ew_prelim`     | Total number of patients hospitalized with confirmed influenza captured for the Wednesday of the reporting week  preliminary data reported to NHSN for the previous reporting week (Sunday – Saturday).<br/> **Earliest date available:** 2020-08-08 |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation
Between the reference dates of 2024-05-01 and 2024-10-31, the total number of hospitalized patients on a subsection
of hospitals and may not be fully represenetative. See the [missingness section](#missingness) section below for more context.

### Geographic weighting
HHS values are computed from state-level data.


## Missingness
Data for reporting dates through April 30, 2024 represent data reported during a previous mandated reporting period as specified by the HHS Secretary.
Data for reporting dates May 1, 2024 – October 31, 2024 represent voluntarily reported data in the absence of a mandate. 
Data for reporting dates beginning November 1, 2024 represent data reported during a current mandated reporting period.
All data and metrics capturing information on respiratory syncytial virus (RSV) were voluntarily reported until November 1, 2024.


## Lag and Backfill

The weekly signal is primarily reported on Friday, adding data from the prior week.
For example, on Friday, 2024-04-19, the source added new data from the week ending 2024-04-13.

## Limitations


## Source and Licensing

This source is derived from the CDC's [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data) and
[Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN) (Preliminary)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/mpgq-jmmr/about_data).

This data was originally published by the CDC, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).
