---
title: COVID-19 Reported Patient Impact and Hospital Capacity - Facility lookup
parent: Other Endpoints (COVID-19 and Other Diseases)
---

# COVID-19 Hospitalization: Facility Lookup

This endpoint is a companion to the
[`covid_hosp_facility` endpoint](covid_hosp_facility.md). It provides a way to
find unique identifiers and other metadata for facilities of interest.

Metadata is derived from the "COVID-19 Reported Patient Impact and Hospital
Capacity by Facility" dataset provided by the US Department of Health & Human
Services via healthdata.gov.

See the
[official description and data dictionary at healthdata.gov](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u)
for more information.

General topics not specific to any particular data source are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing) and [citing](README.md#citing).

## Metadata

This data source provides metadata about healthcare facilities in the US.
- Data source: [US Department of Health & Human Services](https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/anag-cw7u) (HHS)
- Total number of facilities: 4922
- Open Access: [Public Domain US Government](https://www.usa.gov/government-works)

# The API

The base URL is: https://delphi.cmu.edu/epidata/covid_hosp_facility_lookup/

See [this documentation](README.md) for details on specifying locations and dates.

## Parameters

| Parameter   | Description                       | Type   |
|-------------|-----------------------------------|--------|
| `state`     | two-letter state abbreviation     | string |
| `ccn`       | facility CMS Certification Number | string |
| `city`      | city name                         | string |
| `zip`       | 5-digit ZIP code                  | string |
| `fips_code` | 5-digit FIPS county code          | string |

NOTE: Exactly one of the above parameters must be present in requests.
Combinations of parameters (e.g. specifying both `city` and `state`) are not
supported.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].hospital_pk` | unique identifier for this facility (will match CCN if CCN exists) | string |
| `epidata[].state` | two-letter state code | string |
| `epidata[].ccn` | CMS Certification Number for this facility | string |
| `epidata[].hospital_name` |  | string |
| `epidata[].address` |  | string |
| `epidata[].city` |  | string |
| `epidata[].zip` | 5-digit ZIP code | string |
| `epidata[].hospital_subtype` | one of: Childrens Hospitals, Critical Access Hospitals, Long Term, Psychiatric, Rehabilitation, Short Term  | string |
| `epidata[].fips_code` | 5-digit FIPS county code | string |
| `epidata[].is_metro_micro` | 1 if this facility serves a metropolitan or micropolitan area, 0 otherwise | integer |
| `message` | `success` or error message | string |

# Example URLs

### Lookup facilities in the city of Southlake (TX)
https://delphi.cmu.edu/epidata/covid_hosp_facility_lookup/?city=southlake

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

Libraries are available for [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js), [Python](https://pypi.org/project/delphi-epidata/), and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).
The following sample shows how to import the library and fetch facilities in
the city of Southlake (TX).

### Python

Optionally install the package using pip(env):
````bash
pip install delphi-epidata
````

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

````python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.covid_hosp_facility_lookup(city='southlake')
print(res['result'], res['message'], len(res['epidata']))
````
