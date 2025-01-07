---
title: NHSN ED Visits
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
nav_order: 1
---
# National Syndromic Surveillance Program Emergency Department Visits
{: .no_toc}

* **Source name:** `nhsn`
* **Earliest issue available:** November 19, 2024
* **Number of data revisions since 18 Nov 2024:** 0
* **Date of last change:** Never
* **Available for:** state, hhs, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

## Overview

[The National Healthcare Safety Network (NHSN)](https://www.cdc.gov/nhsn/index.html) is the nation’s most widely used healthcare-associated infection tracking system.
This dataset represents preliminary weekly hospital respiratory data and metrics aggregated to national and state/territory levels reported to CDC’s National Health Safety Network (NHSN) reference date beginning August 2020.

Each signal below is derived from one of two following datasets:

- Main: [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data)
- Preliminary: [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN) (Preliminary)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/mpgq-jmmr/about_data). Signals derived from the preliminary dataset have suffix `_prelim` in their signal names.

Both datasets started reporting data in late 2022.
As of May 2024, NHSN received data from 78% of US EDs.

State and nation-level values are pulled directly from the source; HHS-level values are aggregated up from the state level.


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

All data is weekly such that each reported value represents a total from Sunday to Saturday of the reference week.
The `output_signal_name` signal mirrors the `input signal name` field for all geographic resolutions except HHS.

### Geographic weighting

State and nation-level values are pulled directly from the source; HHS-level values are aggregated up from the state level by summing the values of member states.


## Missingness

Data prior to August 1, 2020, are unavailable. As a result of data quality implementation and submission of any backfilled data, data and metrics might fluctuate or change week-over-week after initial posting.
Data reported as of December 1, 2020 are subject to thorough, routine data quality review procedures, including identifying and excluding invalid values from metric calculations and application of error correction methodology; 
data prior to this date may have anomalies that are not yet resolved. 

Data for reference dates through April 30, 2024 were reported during a federally-mandated reporting period 
as specified by the Secretary of the Department of Health and Human Services.

Data for reference dates May 1, 2024 – October 31, 2024 were voluntarily reported in the absence of a mandate.
As a result, during this period the total number of hospitalized patients on a subsection of hospitals and may not be fully representative.

Data for reference dates beginning November 1, 2024 were reported during the [current mandated reporting period](https://www.cms.gov/medicare/health-safety-standards/quality-safety-oversight-general-information/policy-memos-states-and-cms-locations/updates-condition-participation-cop-requirements-hospitals-and-critical-access-hospitals-cahs-report).
More information regarding the mandate beginning November 1, 2024, is available [here](https://www.cdc.gov/nhsn/psc/hospital-respiratory-reporting.html)

## Limitations

Between reference dates 2024-05-01 and 2024-10-31, the total number of hospitalized patients on a subsection
of hospitals and may not be fully representative, since reporting was voluntary.
See the [missingness section](#missingness) for more context.

Standard errors and sample sizes are not applicable to these metrics.


### Differences with HHS reports

?


## Lag and Backfill

The signals are currently updated weekly, generally on Friday.
Each report adds data for the week prior.
For example, on Friday, 2024-04-19, the source added new data representing hospitalizations from the week ending 2024-04-13.
This results in a reporting lag of 6 days from the end of the reference week.


## Source and Licensing

This source is derived from the CDC's [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data) and
[Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN) (Preliminary)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/mpgq-jmmr/about_data).

This data was originally published by the CDC, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).
