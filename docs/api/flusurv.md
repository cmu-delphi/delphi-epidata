---
title: Flusurv
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# FluSurv
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `flusurv` |
| **Data Source** | [Laboratory-Confirmed Influenza Hospitalizations](https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html) |
| **Geographic Coverage** | See [Geographic Codes](geographic_codes.html#flusurv-locations) for full list |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Earliest Date** | 2003w40 |

<!--| **Update Frequency** | Weekly |
| **License** | Open Access | -->



## Overview
{: .no_toc}

This data source provides laboratory-confirmed influenza hospitalization rates from the FluSurv-NET surveillance system. The data includes age-stratified hospitalization rates and rates by race, sex, and flu type, when available.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

See also:
  - <https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html>
  - <https://wwwnc.cdc.gov/eid/article/21/9/14-1912_article>
  - Chaves, S., Lynfield, R., Lindegren, M., Bresee, J., & Finelli, L. (2015).
    The US Influenza Hospitalization Surveillance Network. Emerging Infectious
    Diseases, 21(9), 1543-1550. <https://dx.doi.org/10.3201/eid2109.141912>.

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/flusurv/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of location labels (see [Geographic Codes](geographic_codes.html#flusurv-locations)) |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

{: .note}
> **Notes:**
> - If both `issues` and `lag` are specified, only `issues` is used.
> - If neither is specified, the current issues are used.

## Response

| Field | Description | Type |
|---|---|---|
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].release_date` | the date when this record was first received by Delphi | string |
| `epidata[].location` | the name of the catchment (e.g. 'network_all', 'CA', 'NY_albany' | string |
| `epidata[].issue` | the epiweek of receipt by Delphi (e.g. issue 201453 includes epiweeks up to and including 2014w53, but not 2015w01 or following) | integer |
| `epidata[].epiweek` | the epiweek during which the data was collected | integer |
| `epidata[].lag` | number of weeks between `epiweek` and `issue` | integer |
| `epidata[].rate_age_0` | hospitalization rate for ages 0-4 | float |
| `epidata[].rate_age_1` | hospitalization rate for ages 5-17 | float |
| `epidata[].rate_age_2` | hospitalization rate for ages 18-49 | float |
| `epidata[].rate_age_3` | hospitalization rate for ages 50-64 | float |
| `epidata[].rate_age_4` | hospitalization rate for ages 65+ | float |
| `epidata[].rate_overall` | overall hospitalization rate | float |
| `epidata[].rate_age_5` | hospitalization rate for ages 65-74 | float |
| `epidata[].rate_age_6` | hospitalization rate for ages 75-84 | float |
| `epidata[].rate_age_7` | hospitalization rate for ages 85+ | float |
| `epidata[].rate_age_18t29` | hospitalization rate for ages 18 to 29 | float |
| `epidata[].rate_age_30t39` | hospitalization rate for ages 30 to 39 | float |
| `epidata[].rate_age_40t49` | hospitalization rate for ages 40 to 49 | float |
| `epidata[].rate_age_5t11` | hospitalization rate for ages 5 to 11 | float |
| `epidata[].rate_age_12t17` | hospitalization rate for ages 12 to 17 | float |
| `epidata[].rate_age_lt18` | hospitalization rate for ages <18 | float |
| `epidata[].rate_age_gte18` | hospitalization rate for ages >=18 | float |
| `epidata[].rate_age_0tlt1` | hospitalization rate for ages 0-1 | float |
| `epidata[].rate_age_1t4` | hospitalization rate for ages 1-4 | float |
| `epidata[].rate_age_gte75` | hospitalization rate for ages >=75 | float |
| `epidata[].rate_race_white` | hospitalization rate for white people | float |
| `epidata[].rate_race_black` | hospitalization rate for black people | float |
| `epidata[].rate_race_hisp` | hospitalization rate for Hispanic/Latino people | float |
| `epidata[].rate_race_asian` | hospitalization rate for Asian people | float |
| `epidata[].rate_race_natamer` | hospitalization rate for American Indian/Alaskan Native people | float |
| `epidata[].rate_sex_male` | hospitalization rate for males | float |
| `epidata[].rate_sex_female` | hospitalization rate for females | float |
| `epidata[].rate_flu_a` | hospitalization rate for inflenza A | float |
| `epidata[].rate_flu_b` | hospitalization rate for inflenza B | float |
| `epidata[].season` | indicates the start and end years of the winter flu season in the format YYYY-YY (e.g. 2022-23 indicates the flu season running late 2022 through early 2023) | string |
| `message` | `success` or error message | string |

{: .note}
> **Note:**
> * The `flusurv` age groups are, in general, not the same as the ILINet
(`fluview`) age groups. However, the following groups are equivalent:
>   - flusurv age_0 == fluview age_0  (0-4 years)
>   - flusurv age_3 == fluview age_4  (50-64 years)
>   - flusurv age_4 == fluview age_5  (65+ years)

# Example URLs

### FluSurv on 2020w01 (CA)
<https://api.delphi.cmu.edu/epidata/flusurv/?locations=ca&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2020-04-10",
      "location": "CA",
      "issue": 202014,
      "epiweek": 202001,
      "lag": 13,
      "rate_age_0": 8.4,
      "rate_age_1": 0.8,
      "rate_age_2": 1.6,
      "rate_age_3": 5.6,
      "rate_age_4": 16.5,
      "rate_overall": 4.8
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch CA FluView Clinical data for epiweeks `201701-201801`.

### R

```R
library(epidatr)
# Fetch data
res <- pub_flusurv(locations = "CA", epiweeks = epirange(201701, 201801))
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
res = epidata.pub_flusurv(locations="CA", epiweeks=EpiRange(201701, 201801))
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.flusurv('CA', [EpidataAsync.range(201701, 201801)]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$flusurv(locations = list("CA"), epiweeks = list(Epidata$range(201701, 201801)))
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
res = Epidata.flusurv(['CA'], [Epidata.range(201701, 201801)])
print(res['result'], res['message'], len(res['epidata']))
```
```
