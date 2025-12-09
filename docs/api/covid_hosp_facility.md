---
title: <i>inactive</i> COVID-19 Reported Patient Impact and Hospital Capacity by Facility
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# COVID-19 Hospitalization by Facility
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `covid_hosp_facility` |
| **Data Source** | [US Department of Health & Human Services](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u) |
| **Geographic Levels** | Healthcare facility |
| **Temporal Granularity** | Weekly (Friday -- Thursday) |
| **Reporting Cadence** | Inactive - No longer updated since 2024w08 |
| **Temporal Scope Start** | 2020-07-31 |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

## Overview
{: .no_toc}

This data source provides various measures of COVID-19 burden on patients and healthcare facilities in the US. It is a mirror of the "COVID-19 Reported Patient Impact and Hospital Capacity by Facility" dataset provided by HHS via healthdata.gov.

HHS performs up to four days of forward-fill for missing values.

Starting October 1, 2022, some facilities are only required to report annually.

See the
[official description and data dictionary at healthdata.gov](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u)
for more information. The data elements, cadence, and how the data are being used in the
federal response are documented in
[a FAQ published by Health & Human Services](https://www.hhs.gov/sites/default/files/covid-19-faqs-hospitals-hospital-laboratory-acute-care-facility-data-reporting.pdf).


General topics not specific to any particular data source are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing) and [citing](README.md#citing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/covid_hosp_facility/>

See [this documentation](README.md) for details on specifying locations and dates.

## Parameters

### Required

| Parameter          | Description                 | Type                           |
|--------------------|-----------------------------|--------------------------------|
| `hospital_pks`     | facility unique identifiers | `list` of identifiers          |
| `collection_weeks` | dates                       | `list` of dates or date ranges |


{: .note}
> **NOTES:** 
> - [`covid_hosp_facility_lookup` endpoint](covid_hosp_facility_lookup.md) can > be used to lookup facility identifiers in a variety of ways.
> - A collection week spans Friday -- Thursday, and weeks are identified by
>  the date corresponding to the Friday at the start of the week. Therefore, the
> `collection_weeks` parameter is formatted as a `YYYYMMDD` date (or list of
>  dates) rather than an "epiweek" as in other endpoints.

### Optional

| Parameter           | Description         | Type                                   |
|---------------------|---------------------|----------------------------------------|
| `publication_dates` | date of publication | `list` of "issue" dates or date ranges |

If `publication_dates` is not specified, then the most recent issue is used by
default.

NOTE: The `publication_dates` parameter is semantically equivalent to the
`issues` parameter in the related [`covid_hosp` endpoint](covid_hosp.md). It
has been renamed here for clarity.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].hospital_pk` | facility identified by this row | string |
| `epidata[].collection_week` | Friday's date in the week pertaining to this row | integer |
| `epidata[].publication_date` | the date on which the dataset containing this row was published | integer |
| `epidata[].*` | see the [data dictionary](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u) |  |
| `message` | `success` or error message | string |

# Example URLs

### Moses Taylor Hospital (Scranton, PA) on the first collection week of December 2020 (per most recent issue)
<https://api.delphi.cmu.edu/epidata/covid_hosp_facility/?hospital_pks=390119&collection_weeks=20201201-20201207>

```json
{
    "result": 1,
    "epidata": [
        {
            "hospital_pk": "390119",
            "state": "PA",
            "ccn": "390119",
            "hospital_name": "MOSES TAYLOR HOSPITAL",
            "address": "700 QUINCY AVENUE",
            "city": "SCRANTON",
            "zip": "18510",
            "hospital_subtype": "Short Term",
            "fips_code": "42069",
            "publication_date": 20201221,
            "collection_week": 20201204,
            "is_metro_micro": 1,
            "total_beds_7_day_sum": 860,
            "all_adult_hospital_beds_7_day_sum": 734,
            "all_adult_hospital_inpatient_beds_7_day_sum": 734,
            "inpatient_beds_used_7_day_sum": 807,
            "all_adult_hospital_inpatient_bed_occupied_7_day_sum": 727,
            "total_adult_patients_hosp_confirmed_suspected_covid_7d_sum": -999999,
            "total_adult_patients_hospitalized_confirmed_covid_7_day_sum": 0,
            "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_sum": -999999,
            "total_pediatric_patients_hospitalized_confirmed_covid_7_day_sum": 0,
            "inpatient_beds_7_day_sum": 860,
            "total_icu_beds_7_day_sum": 116,
            "total_staffed_adult_icu_beds_7_day_sum": 48,
            "icu_beds_used_7_day_sum": 94,
            "staffed_adult_icu_bed_occupancy_7_day_sum": 46,
            "staffed_icu_adult_patients_confirmed_suspected_covid_7d_sum": 0,
            "staffed_icu_adult_patients_confirmed_covid_7_day_sum": 0,
            "total_patients_hospitalized_confirmed_influenza_7_day_sum": 0,
            "icu_patients_confirmed_influenza_7_day_sum": 0,
            "total_patients_hosp_confirmed_influenza_and_covid_7d_sum": 0,
            "total_beds_7_day_coverage": 7,
            "all_adult_hospital_beds_7_day_coverage": 7,
            "all_adult_hospital_inpatient_beds_7_day_coverage": 7,
            "inpatient_beds_used_7_day_coverage": 7,
            "all_adult_hospital_inpatient_bed_occupied_7_day_coverage": 7,
            "total_adult_patients_hosp_confirmed_suspected_covid_7d_cov": 7,
            "total_adult_patients_hospitalized_confirmed_covid_7_day_coverage": 7,
            "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_cov": 7,
            "total_pediatric_patients_hosp_confirmed_covid_7d_cov": 7,
            "inpatient_beds_7_day_coverage": 7,
            "total_icu_beds_7_day_coverage": 7,
            "total_staffed_adult_icu_beds_7_day_coverage": 7,
            "icu_beds_used_7_day_coverage": 7,
            "staffed_adult_icu_bed_occupancy_7_day_coverage": 7,
            "staffed_icu_adult_patients_confirmed_suspected_covid_7d_cov": 7,
            "staffed_icu_adult_patients_confirmed_covid_7_day_coverage": 7,
            "total_patients_hospitalized_confirmed_influenza_7_day_coverage": 7,
            "icu_patients_confirmed_influenza_7_day_coverage": 7,
            "total_patients_hosp_confirmed_influenza_and_covid_7d_cov": 7,
            "previous_day_admission_adult_covid_confirmed_7_day_sum": -999999,
            "previous_day_admission_adult_covid_confirmed_18_19_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_20_29_7_day_sum": -999999,
            "previous_day_admission_adult_covid_confirmed_30_39_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_40_49_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_50_59_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_60_69_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_70_79_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_80plus_7_day_sum": 0,
            "previous_day_admission_adult_covid_confirmed_unknown_7_day_sum": 0,
            "previous_day_admission_pediatric_covid_confirmed_7_day_sum": -999999,
            "previous_day_covid_ed_visits_7_day_sum": 62,
            "previous_day_admission_adult_covid_suspected_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_18_19_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_20_29_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_30_39_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_40_49_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_50_59_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_60_69_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_70_79_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_80plus_7_day_sum": 0,
            "previous_day_admission_adult_covid_suspected_unknown_7_day_sum": 0,
            "previous_day_admission_pediatric_covid_suspected_7_day_sum": 0,
            "previous_day_total_ed_visits_7_day_sum": 495,
            "previous_day_admission_influenza_confirmed_7_day_sum": 0,
            "total_beds_7_day_avg": 122.9,
            "all_adult_hospital_beds_7_day_avg": 104.9,
            "all_adult_hospital_inpatient_beds_7_day_avg": 104.9,
            "inpatient_beds_used_7_day_avg": 115.3,
            "all_adult_hospital_inpatient_bed_occupied_7_day_avg": 103.9,
            "total_adult_patients_hosp_confirmed_suspected_covid_7d_avg": -999999,
            "total_adult_patients_hospitalized_confirmed_covid_7_day_avg": 0,
            "total_pediatric_patients_hosp_confirmed_suspected_covid_7d_avg": -999999,
            "total_pediatric_patients_hospitalized_confirmed_covid_7_day_avg": 0,
            "inpatient_beds_7_day_avg": 122.9,
            "total_icu_beds_7_day_avg": 16.6,
            "total_staffed_adult_icu_beds_7_day_avg": 6.9,
            "icu_beds_used_7_day_avg": 13.4,
            "staffed_adult_icu_bed_occupancy_7_day_avg": 6.6,
            "staffed_icu_adult_patients_confirmed_suspected_covid_7d_avg": 0,
            "staffed_icu_adult_patients_confirmed_covid_7_day_avg": 0,
            "total_patients_hospitalized_confirmed_influenza_7_day_avg": 0,
            "icu_patients_confirmed_influenza_7_day_avg": 0,
            "total_patients_hosp_confirmed_influenza_and_covid_7d_avg": 0
        }
    ],
    "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following sample shows how to import the library and fetch Moses Taylor
Hospital (Scranton, PA) on the first collection week of December 2020 (per most
recent issue).

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

Install the package using pip:
```bash
pip install -e "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"
```

```python
# Import
from epidatpy import CovidcastEpidata, EpiDataContext, EpiRange
# Fetch data
epidata = EpiDataContext()
res = epidata.pub_covid_hosp_facility(hospital_pks="390119", collection_weeks=EpiRange(20201201, 20201207))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_covid_hosp_facility(hospital_pks = "390119", collection_weeks = epirange(20201201, 20201207))
print(res)
```
  </div>

</div>

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

Optionally install the package using pip(env):
```bash
pip install delphi-epidata
```

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.covid_hosp_facility('390119', Epidata.range(20201201, 20201207))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$covid_hosp_facility(hospital_pks = list("390119"), collection_weeks = list(Epidata$range(20201201, 20201207)))
print(res$message)
print(length(res$epidata))
```
  </div>

</div>
