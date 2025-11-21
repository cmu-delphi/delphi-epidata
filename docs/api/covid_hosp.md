---
title: <i>inactive</i> COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# COVID-19 Hospitalization by State
{: .no_toc}

* **Source name:** `covid_hosp_state_timeseries`
* **Data source:** [US Department of Health & Human Services](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh) 
* **Earliest issue available:** 2020-01-01
* **Temporal Resolution:** Daily
* **Spatial Resolution:** US States plus DC, PR, and VI
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

## Overview
{: .no_toc}

This data source provides various measures of COVID-19 burden on patients and healthcare facilities in the US. It is a mirror of the "COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries" and "COVID-19 Reported Patient Impact and Hospital Capacity by State" datasets provided by HHS via healthdata.gov. The latter provides more frequent updates, so it is combined with the former to create a single dataset which is as recent as possible.

HHS performs up to four days of forward-fill for missing values in the
[facility-level data](covid_hosp_facility.md) which are aggregated to make this
state-level dataset. This sometimes results in repeated values in the state-level data.
A sequence of two repeated values is extremely common, and longer sequences are rare.
Repeated values added in this way are sometimes updated if the underlying missing data can
be completed at a later date.

Starting October 1, 2022, some facilities are only required to report annually.

For more information, see the
[official description and data dictionary at healthdata.gov](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh)
for "COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries,"
as well as the [official description](https://healthdata.gov/dataset/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/6xf2-c3ie)
for "COVID-19 Reported Patient Impact and Hospital Capacity by State." The data elements,
cadence, and how the data are being used in the federal response are documented in
[a FAQ published by Health & Human Services](https://www.hhs.gov/sites/default/files/covid-19-faqs-hospitals-hospital-laboratory-acute-care-facility-data-reporting.pdf).

General topics not specific to any particular data source are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing) and [citing](README.md#citing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/covid_hosp_state_timeseries/

See [this documentation](README.md) for details on specifying locations and dates.

## Parameters

### Required

| Parameter | Description                    | Type                           |
|-----------|--------------------------------|--------------------------------|
| `states`  | two-letter state abbreviations | `list` of states               |
| `dates`   | dates                          | `list` of dates or date ranges |

### Optional

| Parameter | Description | Type                                   |
|-----------|-------------|----------------------------------------|
| `issues`  | issues      | `list` of "issue" dates or date ranges |

If `issues` is not specified, then the most recent issue is used by default.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].state` | state pertaining to this row | string |
| `epidata[].date` | date pertaining to this row | integer |
| `epidata[].issue` | the date on which the dataset containing this row was published | integer |
| `epidata[].*` | see the [data dictionary](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh). Last synced: 2021-10-21 |  |
| `message` | `success` or error message | string |

# Example URLs

### MA on 2020-05-10 (per most recent issue)
https://api.delphi.cmu.edu/epidata/covid_hosp_state_timeseries/?states=MA&dates=20200510

```json
{
    "epidata":
    [
        {
            "state": "MA",
            "geocoded_state": null,
            "issue": 20240503,
            "date": 20200510,
            "critical_staffing_shortage_today_yes": 0,
            "critical_staffing_shortage_today_no": 0,
            "critical_staffing_shortage_today_not_reported": 84,
            "critical_staffing_shortage_anticipated_within_week_yes": 0,
            "critical_staffing_shortage_anticipated_within_week_no": 0,
            "critical_staffing_shortage_anticipated_within_week_not_reported": 84,
            "hospital_onset_covid": 53,
            "hospital_onset_covid_coverage": 84,
            "inpatient_beds": 15691,
            "inpatient_beds_coverage": 73,
            "inpatient_beds_used": 12427,
            "inpatient_beds_used_coverage": 83,
            "inpatient_beds_used_covid": 3625,
            "inpatient_beds_used_covid_coverage": 84,
            "previous_day_admission_adult_covid_confirmed": null,
            "previous_day_admission_adult_covid_confirmed_coverage": 0,
            "previous_day_admission_adult_covid_suspected": null,
            "previous_day_admission_adult_covid_suspected_coverage": 0,
            "previous_day_admission_pediatric_covid_confirmed": null,
            "previous_day_admission_pediatric_covid_confirmed_coverage": 0,
            "previous_day_admission_pediatric_covid_suspected": null,
            "previous_day_admission_pediatric_covid_suspected_coverage": 0,
            "staffed_adult_icu_bed_occupancy": null,
            "staffed_adult_icu_bed_occupancy_coverage": 0,
            "staffed_icu_adult_patients_confirmed_suspected_covid": null,
            "staffed_icu_adult_patients_confirmed_suspected_covid_coverage": 0,
            "staffed_icu_adult_patients_confirmed_covid": null,
            "staffed_icu_adult_patients_confirmed_covid_coverage": 0,
            "total_adult_patients_hosp_confirmed_suspected_covid": null,
            "total_adult_patients_hosp_confirmed_suspected_covid_coverage": 0,
            "total_adult_patients_hosp_confirmed_covid": null,
            "total_adult_patients_hosp_confirmed_covid_coverage": 0,
            "total_pediatric_patients_hosp_confirmed_suspected_covid": null,
            "total_pediatric_patients_hosp_confirmed_suspected_covid_coverage": 0,
            "total_pediatric_patients_hosp_confirmed_covid": null,
            "total_pediatric_patients_hosp_confirmed_covid_coverage": 0,
            "total_staffed_adult_icu_beds": null,
            "total_staffed_adult_icu_beds_coverage": 0,
            "inpatient_beds_utilization_coverage": 72,
            "inpatient_beds_utilization_numerator": 10876,
            "inpatient_beds_utilization_denominator": 15585,
            "percent_of_inpatients_with_covid_coverage": 83,
            "percent_of_inpatients_with_covid_numerator": 3607,
            "percent_of_inpatients_with_covid_denominator": 12427,
            "inpatient_bed_covid_utilization_coverage": 73,
            "inpatient_bed_covid_utilization_numerator": 3304,
            "inpatient_bed_covid_utilization_denominator": 15691,
            "adult_icu_bed_covid_utilization_coverage": null,
            "adult_icu_bed_covid_utilization_numerator": null,
            "adult_icu_bed_covid_utilization_denominator": null,
            "adult_icu_bed_utilization_coverage": null,
            "adult_icu_bed_utilization_numerator": null,
            "adult_icu_bed_utilization_denominator": null,
            "deaths_covid": 48,
            "deaths_covid_coverage": 73,
            "icu_patients_confirmed_influenza": null,
            "icu_patients_confirmed_influenza_coverage": 0,
            "on_hand_supply_therapeutic_a_casirivimab_imdevimab_courses": null,
            "on_hand_supply_therapeutic_b_bamlanivimab_courses": null,
            "on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses": null,
            "previous_day_admission_adult_covid_confirmed_18_19": null,
            "previous_day_admission_adult_covid_confirmed_18_19_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_20_29": null,
            "previous_day_admission_adult_covid_confirmed_20_29_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_30_39": null,
            "previous_day_admission_adult_covid_confirmed_30_39_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_40_49": null,
            "previous_day_admission_adult_covid_confirmed_40_49_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_50_59": null,
            "previous_day_admission_adult_covid_confirmed_50_59_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_60_69": null,
            "previous_day_admission_adult_covid_confirmed_60_69_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_70_79": null,
            "previous_day_admission_adult_covid_confirmed_70_79_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_80plus": null,
            "previous_day_admission_adult_covid_confirmed_80plus_coverage": 0,
            "previous_day_admission_adult_covid_confirmed_unknown": null,
            "previous_day_admission_adult_covid_confirmed_unknown_coverage": 0,
            "previous_day_admission_adult_covid_suspected_18_19": null,
            "previous_day_admission_adult_covid_suspected_18_19_coverage": 0,
            "previous_day_admission_adult_covid_suspected_20_29": null,
            "previous_day_admission_adult_covid_suspected_20_29_coverage": 0,
            "previous_day_admission_adult_covid_suspected_30_39": null,
            "previous_day_admission_adult_covid_suspected_30_39_coverage": 0,
            "previous_day_admission_adult_covid_suspected_40_49": null,
            "previous_day_admission_adult_covid_suspected_40_49_coverage": 0,
            "previous_day_admission_adult_covid_suspected_50_59": null,
            "previous_day_admission_adult_covid_suspected_50_59_coverage": 0,
            "previous_day_admission_adult_covid_suspected_60_69": null,
            "previous_day_admission_adult_covid_suspected_60_69_coverage": 0,
            "previous_day_admission_adult_covid_suspected_70_79": null,
            "previous_day_admission_adult_covid_suspected_70_79_coverage": 0,
            "previous_day_admission_adult_covid_suspected_80plus": null,
            "previous_day_admission_adult_covid_suspected_80plus_coverage": 0,
            "previous_day_admission_adult_covid_suspected_unknown": null,
            "previous_day_admission_adult_covid_suspected_unknown_coverage": 0,
            "previous_day_admission_influenza_confirmed": null,
            "previous_day_admission_influenza_confirmed_coverage": 0,
            "previous_day_deaths_covid_and_influenza": null,
            "previous_day_deaths_covid_and_influenza_coverage": 0,
            "previous_day_deaths_influenza": null,
            "previous_day_deaths_influenza_coverage": 0,
            "previous_week_therapeutic_a_casirivimab_imdevimab_courses_used": null,
            "previous_week_therapeutic_b_bamlanivimab_courses_used": null,
            "previous_week_therapeutic_c_bamlanivimab_etesevimab_courses_used": null,
            "total_patients_hospitalized_confirmed_influenza": null,
            "total_patients_hospitalized_confirmed_influenza_coverage": 0,
            "total_patients_hospitalized_confirmed_influenza_covid": null,
            "total_patients_hospitalized_confirmed_influenza_covid_coverage": null,
            "inpatient_beds_utilization": 0.697850497273019,
            "percent_of_inpatients_with_covid": 0.290255089723988,
            "inpatient_bed_covid_utilization": 0.210566566821745,
            "adult_icu_bed_covid_utilization": null,
            "adult_icu_bed_utilization": null
        }
    ],
    "result": 1,
    "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following sample shows how to import the library and fetch MA on 2020-05-10
(per most recent issue).

### R

```R
library(epidatr)
# Fetch data
res <- pub_covid_hosp_state_timeseries(states = "MA", dates = 20200510)
print(res)
```

### Python

Install the package using pip:
```bash
pip install -e "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"
```

```python
# Import
from epidatpy import CovidcastEpidata, EpiDataContext, EpiRange
# Fetch data
epidata = EpiDataContext()
res = epidata.pub_covid_hosp(states="MA", dates=20200510)
print(res)
```

### Legacy Clients

We recommend using our modern client libraries: [epidatr](https://cmu-delphi.github.io/epidatr/) for R and [epidatpy](https://cmu-delphi.github.io/epidatpy/) for Python. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$covid_hosp(states = list("MA"), dates = list(20200510))
print(res$message)
print(length(res$epidata))
```

#### Python (Legacy)

Optionally install the package using pip(env):
```bash
pip install delphi-epidata
```

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.covid_hosp('MA', 20200510)
print(res['result'], res['message'], len(res['epidata']))
```

# Repair Log

If we ever need to repair the data record due to a bug in our code (not at the
source), we will update the list below.

## October 21, 2021

All issues between 20210430 and 20211021 were re-uploaded to include new columns added by
HHS. If you pulled these issues before October 21, the data you received was correct, but
was missing the added columns.

## January 22, 2021

The following issues were repaired:

* 20210113
* 20210118

These issues had been imported using the wrong column order due to an imprecise
database migration. If you pulled these issues before January 22, you will want
to discard that data.
