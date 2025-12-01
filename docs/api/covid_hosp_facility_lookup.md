---
title: <i>inactive</i> COVID-19 Reported Patient Impact and Hospital Capacity - Facility lookup
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# COVID-19 Hospitalization: Facility Lookup
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `covid_hosp_facility_lookup` |
| **Data Source** | [US Department of Health & Human Services](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u) |
| **Geographic Coverage** | Healthcare facility ([state](geographic_codes.html#us-states-and-territories), ccn city, zip, fips) |
| **Update Frequency** | Inactive - No longer updated |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

<!-- | **Earliest Date** | N/A |
| **Temporal Resolution** | N/A -->

## Overview
{: .no_toc}

This endpoint is a companion to the [`covid_hosp_facility` endpoint](covid_hosp_facility.md). It provides a way to find unique identifiers and other metadata for facilities of interest.

Metadata is derived from the "COVID-19 Reported Patient Impact and Hospital Capacity by Facility" dataset provided by HHS via healthdata.gov.

See the
[official description and data dictionary at healthdata.gov](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u)
for more information.

General topics not specific to any particular data source are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing) and [citing](README.md#citing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/covid_hosp_facility_lookup/>

See [this documentation](README.md) for details on specifying locations and dates.

## Parameters

### Required

| Parameter   | Description                       | Type   |
|-------------|-----------------------------------|--------|
| `state`     | two-letter state abbreviation (see [Geographic Codes](geographic_codes.html#us-states-and-territories)) | string |
| `ccn`       | facility CMS Certification Number | string |
| `city`      | city name                         | string |
| `zip`       | 5-digit ZIP code                  | string |
| `fips_code` | 5-digit FIPS county code          | string |

{: .note}
> **NOTE:** Exactly one of the above parameters must be present in requests.
> Combinations of parameters (e.g. specifying both `city` and `state`) are not
> supported.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].hospital_pk` | unique identifier for this facility (will match CCN if CCN exists) | string |
| `epidata[].state` | two-letter state code | string |
| `epidata[].ccn` | CMS Certification Number for this facility | string |
| `epidata[].hospital_name` | facility name | string |
| `epidata[].address` | facility address | string |
| `epidata[].city` | facility city | string |
| `epidata[].zip` | 5-digit ZIP code | string |
| `epidata[].hospital_subtype` | one of: Childrens Hospitals, Critical Access Hospitals, Long Term, Psychiatric, Rehabilitation, Short Term  | string |
| `epidata[].fips_code` | 5-digit FIPS county code | string |
| `epidata[].is_metro_micro` | 1 if this facility serves a metropolitan or micropolitan area, 0 otherwise | integer |
| `message` | `success` or error message | string |

Use the `hospital_pk` value when querying
[the COVID-19 Reported Patient Impact and Hospital Capacity by Facility endpoint](covid_hosp_facility.md).

# Example URLs

### Lookup facilities in the city of Southlake (TX)
<https://api.delphi.cmu.edu/epidata/covid_hosp_facility_lookup/?city=southlake>

```json
{
    "result": 1,
    "epidata": [
        {
            "hospital_pk": "450888",
            "state": "TX",
            "ccn": "450888",
            "hospital_name": "TEXAS HEALTH HARRIS METHODIST HOSPITAL SOUTHLAKE",
            "address": "1545 E SOUTHLAKE BLVD",
            "city": "SOUTHLAKE",
            "zip": "76092",
            "hospital_subtype": "Short Term",
            "fips_code": "48439",
            "is_metro_micro": 1
        },
        {
            "hospital_pk": "670132",
            "state": "TX",
            "ccn": "670132",
            "hospital_name": "METHODIST SOUTHLAKE HOSPITAL",
            "address": "421 E STATE HIGHWAY 114",
            "city": "SOUTHLAKE",
            "zip": "76092",
            "hospital_subtype": "Short Term",
            "fips_code": "48439",
            "is_metro_micro": 1
        }
    ],
    "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following sample shows how to import the library and fetch facilities in
the city of Southlake (TX).

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
res = epidata.pub_covid_hosp_facility_lookup(city="southlake")
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_covid_hosp_facility_lookup(city = "southlake")
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
res = Epidata.covid_hosp_facility_lookup(city='southlake')
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$covid_hosp_facility_lookup(city = "southlake")
print(res$message)
print(length(res$epidata))
```
  </div>

</div>
