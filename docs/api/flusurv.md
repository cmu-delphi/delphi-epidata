---
title: Flusurv
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 3
---

# FluSurv
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `flusurv` |
| **Data Source** | [CDC FluSurv-NET](https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html) |
| **Geographic Levels** | Specific catchment areas (Network, State, or County-level catchments). See [Geographic Codes](geographic_codes.html#flusurv-locations) for full list |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Temporal Scope Start** | 2003w40 |
| **Reporting Cadence** | Weekly |
| **License** | [Publicly Accessible US Government](https://www.usa.gov/government-works) |




## Overview
{: .no_toc}

This data source provides laboratory-confirmed influenza hospitalization rates from the [CDC's Influenza Hospitalization Surveillance Network (FluSurv-NET)](https://www.cdc.gov/fluview/overview/influenza-hospitalization-surveillance.html?CDC_AAref_Val=https://www.cdc.gov/flu/weekly/influenza-hospitalization-surveillance.htm). The data includes age-stratified hospitalization rates and rates by race, sex, and flu type, when available.

{: .note}
> **Note:**
> FluSurv-NET age groups differ from ILINet. `age_0` matches ILINet's 0-4 years; `age_3` matches 50-64 years; `age_4` matches 65+ years.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

See also:
  - <https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html>
  - <https://wwwnc.cdc.gov/eid/article/21/9/14-1912_article>
  - Chaves, S., Lynfield, R., Lindegren, M., Bresee, J., & Finelli, L. (2015).
    The US Influenza Hospitalization Surveillance Network. Emerging Infectious
    Diseases, 21(9), 1543-1550. <https://dx.doi.org/10.3201/eid2109.141912>.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}


## Estimation

The rates provided in this dataset are pulled directly from the CDC's GRASP (Geospatial Research, Analysis, and Services Program) API.

For a specific location and stratum (e.g., Age 0-4), the rate represents the number of residents of the catchment area hospitalized with laboratory-confirmed influenza divided by the total population of that stratum in that catchment area, multiplied by 100,000.

### Processing Details
The Delphi pipeline scrapes the CDC GRASP API to emulate browser requests.
* **Duplicate Handling:** In rare instances where the source API provides two differing rates for the same location, epiweek, and demographic group, the pipeline is configured to retain the first value returned by the API.
* **Seasonality:** Data is processed based on "seasons" defined by the CDC, but is stored and served by Delphi indexed by Epiweek.

<!-- Source code: src/acquisition/flusurv/flusurv_update.py -->

## Strata Definitions

The signals are broken down into specific demographic groups. The suffix of the signal name corresponds to the groups below.

### Age Groups
The dataset includes both historical age groupings (0-4) and newer, more granular groupings (0tlt1, etc.) added in recent years.

| Signal Suffix | Age Group |
| :--- | :--- |
| `age_0` | 0-4 yr |
| `age_1` | 5-17 yr |
| `age_2` | 18-49 yr |
| `age_3` | 50-64 yr |
| `age_4` | 65+ yr |
| `age_5` | 65-74 yr |
| `age_6` | 75-84 yr |
| `age_7` | 85+ yr |
| `age_0tlt1` | 0 to <1 yr |
| `age_1t4` | 1-4 yr |
| `age_5t11` | 5-11 yr |
| `age_12t17` | 12-17 yr |
| `age_18t29` | 18-29 yr |
| `age_30t39` | 30-39 yr |
| `age_40t49` | 40-49 yr |
| `age_gte75` | >= 75 yr |
| `age_lt18` | < 18 yr |
| `age_gte18` | >= 18 yr |

### Race and Ethnicity
The dataset tracks 5 specific racial and ethnic groups.

| Signal Suffix | Group Description |
| :--- | :--- |
| `race_white` | White |
| `race_black` | Black |
| `race_hisp` | Hispanic/Latino |
| `race_asian` | Asian/Pacific Islander |
| `race_natamer` | American Indian/Alaska Native |

### Sex

| Signal Suffix | Group Description |
| :--- | :--- |
| `sex_male` | Male |
| `sex_female` | Female |

### Influenza Type

| Signal Suffix | Group Description |
| :--- | :--- |
| `flu_a` | Influenza A |
| `flu_b` | Influenza B |

## Lag and Backfill

FluSurv-NET data is subject to reporting lags and revisions. The CDC may update past weekly rates as more hospitalization data becomes available or is corrected.

The Delphi API tracks these changes via the `issue` date (inferred from the `loaddatetime` provided by the CDC API). When new data is fetched from the CDC, if a rate for a past week has changed, the database is updated to reflect the new value, allowing users to query historical versions of the data using the `lag` or `issues` parameters.

## Limitations

* This data does not cover the entire United States. It covers specific catchment areas within 13 states (EIP sites) and additional states participating in the IHSP. Rates are representative of these specific populations and may not perfectly generalize to the entire national population.
* As with all surveillance data, recent weeks may be subject to significant backfill.
* Not all strata (e.g., specific age bands or racial groups) may be available for all locations or all historical dates, depending on the data collection practices at the time.

## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/flusurv/>


### Parameters

#### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.html)) | `list` of epiweeks |
| `locations` | locations | `list` of location labels (see [Geographic Codes](geographic_codes.html#flusurv-locations)) |

#### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues (see [Date Formats](date_formats.html))                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

{: .note}
> **Notes:**
> - If both `issues` and `lag` are specified, only `issues` is used.
> - If neither is specified, the current issues are used.

### Response

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

## Example URLs

### FluSurv on 2020w01 (CA)
<https://api.delphi.cmu.edu/epidata/flusurv/?locations=ca&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2025-11-03",
      "location": "CA",
      "season": "2019-20",
      "issue": 202538,
      "epiweek": 202001,
      "lag": 298,
      "rate_age_0": 8.6,
      "rate_age_1": 0.8,
      "rate_age_2": 1.5,
      "rate_age_3": 5.7,
      "rate_age_4": 15.3,
      "rate_age_5": 11.5,
      "rate_age_6": 20.4,
      "rate_age_7": 20.8,
      "rate_age_0tlt1": 12.6,
      "rate_age_1t4": 7.6,
      "rate_age_5t11": 1.1,
      "rate_age_12t17": 0.4,
      "rate_age_18t29": 1.2,
      "rate_age_30t39": 1.6,
      "rate_age_40t49": 1.8,
      "rate_age_lt18": 2.9,
      "rate_age_gte18": 5.1,
      "rate_age_gte75": 20.5,
      "rate_race_white": 4.1,
      "rate_race_black": 8.1,
      "rate_race_hisp": 4.1,
      "rate_race_asian": 3.4,
      "rate_race_natamer": 0.0,
      "rate_sex_male": 4.7,
      "rate_sex_female": 4.7,
      "rate_flu_a": 3.6,
      "rate_flu_b": 1.0,
      "rate_overall": 4.7
    }
  ],
  "message": "success"
}
```

## Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch CA FluView Clinical data for epiweeks `201701-201801`.

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
res = epidata.pub_flusurv(locations="CA", epiweeks=EpiRange(201701, 201801))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_flusurv(locations = "CA", epiweeks = epirange(201701, 201801))
print(res)
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">

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
  </div>

</div>

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/), [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R), and [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.js).

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
    <button data-tab="js">JavaScript</button>
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
res = Epidata.flusurv(['CA'], [Epidata.range(201701, 201801)])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$flusurv(locations = list("CA"), epiweeks = list(Epidata$range(201701, 201801)))
print(res$message)
print(length(res$epidata))
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">



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
  </div>

</div>
