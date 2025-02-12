---
title: NHSN Respiratory Hospitalizations
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
nav_order: 1
---
# National Healthcare Safety Network Respiratory Hospitalizations
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
This dataset reports preliminary and finalized weekly hospital respiratory data and metrics aggregated to national and state/territory levels reported to the CDC’s National Health Safety Network (NHSN). Values are available for reference dates beginning August 2020.

Each signal below is derived from one of the two following datasets:

- Main: [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data)
- Preliminary: [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN) (Preliminary)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/mpgq-jmmr/about_data). Signals derived from the preliminary dataset have suffix `_prelim` in their signal names.

Both datasets started reporting data in late 2024.
For reference dates in May 2024, NHSN received data from 78% of US EDs.

State and nation-level values are pulled directly from the source; HHS-level values are aggregated up from the state level.


| Signal                          | Description                                                                                                                                                                         |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `confirmed_admissions_covid_ew`              | Total number of patients hospitalized with confirmed COVID-19 over the entire week (Sunday-Saturday). Only includes hospitalizations whose report was received before the Friday or Saturday of the following week. **Earliest date available:** 2020-08-08                                                                                                     |
| `confirmed_admissions_covid_ew_prelim`          | Total number of patients hospitalized with confirmed COVID-19 over the entire week (Sunday-Saturday). Only includes hospitalizations whose report was received before the Wednesday of the following week. <br/> **Earliest date available:** 2020-08-08  |
| `confirmed_admissions_flu_ew`           | Total number of patients hospitalized with confirmed influenza over the entire week (Sunday-Saturday). Only includes hospitalizations whose report was received before the Friday or Saturday of the following week.  <br/> **Earliest date available:** 2020-08-08                                                                                       |
| `confirmed_admissions_flu_ew_prelim`     | Total number of patients hospitalized with confirmed influenza over the entire week (Sunday-Saturday). Only includes hospitalizations whose report was received before the Wednesday of the following week. <br/> **Earliest date available:** 2020-08-08 |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

All data is weekly such that each reported value represents a total from Sunday to Saturday of the reference week.
The `confirmed_admissions_covid_ew` signal mirrors the `totalconfc19newadm` field for all geographic resolutions except HHS.
For `confirmed_admissions_flu_ew` signal mirrors the `totalconfflunewadm` field for all geographic resolutions except HHS.

We report both preliminary (`*_prelim`) and finalized signals.
Preliminary data is made available on the Wednesday following the end of the week being reported on. For example, the data for the week Dec 1-7, 2024 would first be available on 2024-12-11, the Wednesday of the following week.
Finalized data is made available on the Friday or Saturday following the end of the week being reported on.

Preliminary data is available 2 days earlier than finalized data. However, preliminary data will tend to underreport the true value since it is made available closer to the end of the week being reported on, allowing less time for hospitalization reports to be received.


### Geographic weighting

State and nation-level values are pulled directly from the source; HHS-level values are aggregated up from the state level by summing the values of member states.


## Missingness

Data is available for reference dates August 1, 2020 and later.

Data reported for reference dates December 1, 2020 or later are subject to thorough, routine data quality review procedures, including identifying and excluding invalid values and application of error correction methodology;
data for reference dates prior to this may be anomalous or invalid.

Data for reference dates through April 30, 2024 were reported during a federally-mandated reporting period
as specified by the Secretary of the Department of Health and Human Services.

Data for reference dates May 1, 2024-October 31, 2024 were voluntarily reported in the absence of a mandate.
As a result, during this period reported hospitalizations may not be fully representative.

Data for reference dates beginning November 1, 2024 were reported during the [current mandated reporting period](https://www.cms.gov/medicare/health-safety-standards/quality-safety-oversight-general-information/policy-memos-states-and-cms-locations/updates-condition-participation-cop-requirements-hospitals-and-critical-access-hospitals-cahs-report).
More information regarding the mandate beginning November 1, 2024, is available [from the CDC](https://www.cdc.gov/nhsn/psc/hospital-respiratory-reporting.html)

## Limitations

HHS collects data from state and territorial health departments about many, but not all, hospitals in the U.S.
Notably excluded from this dataset are psychiatric and rehabilitation facilities,and religious non-medical facilities.
Number of reporting hospitals is determined based on the NHSN unique hospital identifier and not aggregated to the CMS certification number (CCN).
Only hospitals indicated as active reporters in NHSN are included.

Between reference dates 2024-05-01 and 2024-10-31, reported hospitalizations may not be fully representative, since reporting was voluntary.
See the [missingness section](#missingness) for more information about voluntary and mandatory reporting periods.

Standard errors and sample sizes are not applicable to these metrics.


### Differences with HHS reports
An analysis comparing flu and COVID-19 data from the [HHS](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh/about_data) and NHSN datasets, for reference dates appearing in both sources, suggests that the data are largely equivalent. However, there are notable differences in a handful of states; GA (untill 2023), LA, NV, PR (late 2020-early 2021), and TN all have substantially lower values in HHS data than in NHSN.

Occasionally, data for a single geographic region will have a spike in NHSN or HHS that does not appear in the other source or in other geographic regions.

There may be other mismatches between the datasets, so exercise caution when comparing work based on NHSN data with work based on HHS data.


## Lag and Backfill

Finalized signals are currently updated weekly, generally on Friday or Saturday.
Preliminary signals are currently updated weekly, on Wednesday.
Each report adds data for the week prior.
For example, on Friday, 2024-04-19, the source added new data representing hospitalizations from the week ending 2024-04-13.
For finalized signals, this results in a reporting lag of 6-7 days from the end of the reference week.
For preliminary signals, this results in a reporting lag of 4 days from the end of the reference week.

As a result of continuous data quality checks and revisions to data for prior reference dates (also known as "backfill"), data may fluctuate or change week-over-week after initial posting.

In practice, revisions tend to happen within 2 months of the initial release; older data is unlikely to be revised.
Of values reported recently (reference date 2 months or less before the issue date), 20% were revisions.
Values that are revised tend to be revised a small number of times (once or twice). Revisions tend to increase values. Revisions tend to be small, with a median 2% (mean 5.4%) difference between highest and lowest values seen for a given reference date.

A handful of values have large revisions, for example, being revised from 10 to 100, but these are rare.

Texas has many more revisions than other states (7 times more than California during the analysis period). However Texas has the lowest median percent difference (0.08%) between high and low values seen for a given reference date. Idaho, New Hampshire, Hawaii, and North Dakota have some of the highest median percent differences.


## Source and Licensing

This source is derived from the CDC's [Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data) and
[Weekly Hospital Respiratory Data (HRD) Metrics by Jurisdiction, National Healthcare Safety Network (NHSN) (Preliminary)](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/mpgq-jmmr/about_data).

This data was originally published by the CDC, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).
