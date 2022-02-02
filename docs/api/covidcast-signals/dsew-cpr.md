---
title: Data Strategy and Execution Workgroup Community Profile Report
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Data Strategy and Execution Workgroup Community Profile Report (CPR)
{: .no_toc}

* **Source name:** `dsew-cpr`
* **Earliest issue available:** 2022-01-28
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, msa, state, hhs, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

The Community Profile Report (CPR) is published by the Data Strategy and Execution Workgroup (DSEW) of the White House COVID-19 Team. For more information, see the [official description and data dictionary at healthdata.gov](https://healthdata.gov/Health/COVID-19-Community-Profile-Report/gqxm-d9w9) for "COVID-19 Community Profile Report".

This data source provides various COVID-19 related metrics, of which we report hospital admissions. Other sources of hospital admissions data in COVIDcast include [HHS](hhs.md) and [medical insurance claims](hospital-admissions.md). The CPR differs from these sources in that it is part of the public health surveillance stream (like HHS, unlike claims) but is available at a daily-county level (like claims, unlike HHS). CPR hospital admissions figures at the state level and above are meant to match those from HHS, but are known to differ. See the Limitations section for details.

County, MSA, state, and HHS-level values are pulled directly from CPR; nation-level values are aggregated up from the state level.

| Signal | Description |
| --- | --- |
| `confirmed_admissions_covid_1d_7dav` | Number of adult and pediatric confirmed COVID-19 hospital admissions occurring each day. Smoothed using a 7-day average.
Earliest date available: 2019-12-16 for state, HHS, and nation; 2021-01-06 for MSA and county |
| `confirmed_admissions_covid_1d_prop_7dav` | Number of adult and pediatric confirmed COVID-19 hospital admissions occurring each day, per 100,000 population. Smoothed using a 7-day average.
Earliest date available: 2019-12-16 for state, HHS, and nation; 2021-01-06 for MSA and county |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

For counts-based fields like hospital admissions, CPR reports rolling sums for the preceding 7 days. The 7-day average signals are computed by Delphi by dividing each sum by 7 and assigning it to the last date in the included range, so e.g. the signal for June 7 is the average of the underlying data for June 1 through 7, inclusive.

The `confirmed_admissions_covid_1d_7dav` signal mirrors the `Confirmed COVID-19 admissions - last 7 days` CPR field for all geographic resolutions except nation. Nation-level admissions is calculated by summing state-level values.

## Limitations

Nation-level estimates may be inaccurate since aggregations are done using state-level smoothed values instead of raw values. Ideally we would aggregate raw values before smoothing, but the raw values are not accessible in this case.

Because DSEW does not provide updates on weekends, estimates are not available for all dates.

### Differences with HHS reports

An analysis comparing the 
[CPR labeled January 5, 2022](https://healthdata.gov/api/views/gqxm-d9w9/files/14ee1150-edf1-4b54-b225-500c8954e6a8?download=true&filename=Community%20Profile%20Report%2020220105.xlsx) 
(newest file as of January 6, 2022) with the HHS 
[COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh) 
(downloaded January 6, 2022) suggests that the CPR undercounts the hospital admissions published by HHS by 10-15% or more. We are waiting from clarification from the data provider, but until then, exercise caution when comparing work based on the CPR with work based on HHS reports.

## Lag and Backfill

The report is currently updated daily, excluding weekends. However, this is subject to change; DSEW previously issued updates on a twice-weekly schedule. We check for updates daily.

Hospital admissions are reported with a lag of 2 days, but since the CPR is not updated on weekends, lag effectively varies from 2-4 days.

## Source and Licensing

This indicator mirrors and lightly aggregates data originally published by the Data Strategy and Execution Workgroup via [HealthData.gov](https://healthdata.gov/). As a work of the US government, the original data is in the [public domain](https://www.usa.gov/government-works).
