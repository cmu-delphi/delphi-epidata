---
title: FluView
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 1
---

# FluView (ILINet)
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `fluview` |
| **Data Source** | [United States Centers for Disease Control and Prevention (CDC)](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) |
| **Geographic Coverage** | National, states, HHS regions, and Census divisions (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Weekly (typically Fridays) |
| **Earliest Date** | 1997w40 |
| **License** | Open Access / [CDC](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) | 

## Overview
{: .no_toc}

Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet).

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/fluview/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `regions` | regions | `list` of region labels: `nat`, states, `hhs1`-`hhs10`, `cen1`-`cen9` (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |
| `auth`    | password for private imputed data          | string             |

{: .note}
> **Notes:**
> - If both `issues` and `lag` are specified, only `issues` is used.
> - If neither is specified, the current issues are used.

## Response

| Field                     | Description                                                     | Type             |
|---------------------------|-----------------------------------------------------------------|---------------------|
| `result`                  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                 | list of results                                                 | array of objects |
| `epidata[].release_date`  | date when data was released                                     | string or null   |
| `epidata[].region`        | region identifier                                               | string           |
| `epidata[].issue`         | epiweek of publication                                          | integer          |
| `epidata[].epiweek`       | epiweek for which data is valid                                 | integer          |
| `epidata[].lag`           | number of weeks between epiweek and issue                       | integer          |
| `epidata[].num_ili`       | number of ILI cases                                             | integer          |
| `epidata[].num_patients`  | total number of patients                                        | integer          |
| `epidata[].num_providers` | number of reporting providers                                   | integer          |
| `epidata[].num_age_0`     | number of ILI cases for ages 0-4                                | integer or null  |
| `epidata[].num_age_1`     | number of ILI cases for ages 5-24                               | integer or null  |
| `epidata[].num_age_2`     | number of ILI cases for ages 25-49                              | integer or null  |
| `epidata[].num_age_3`     | number of ILI cases for ages 50-64                              | integer or null  |
| `epidata[].num_age_4`     | number of ILI cases for ages 65+                                | integer or null  |
| `epidata[].num_age_5`     | number of ILI cases with unknown age                            | integer or null  |
| `epidata[].wili`          | weighted percent influenza-like illness                         | float            |
| `epidata[].ili`           | percent influenza-like illness                                  | float            |
| `message`                 | `success` or error message                                      | string           |

{: .note}
> **Notes:**
> - If authorized via `auth`, private data is not included.

# Example URLs

### FluView on 2015w01 (national)
https://api.delphi.cmu.edu/epidata/fluview/?regions=nat&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2017-10-24",
      "region": "nat",
      "issue": 201740,
      "epiweek": 201501,
      "lag": 143,
      "num_ili": 31483,
      "num_patients": 771835,
      "num_providers": 1958,
      "num_age_0": 7160,
      "num_age_1": 9589,
      "num_age_2": null,
      "num_age_3": 8072,
      "num_age_4": 3614,
      "num_age_5": 3048,
      "wili": 4.21374,
      "ili": 4.07898
    }
  ],
  "message": "success"
}
```

### FluView in HHS Regions 4 and 6 for the 2014/2015 flu season

https://api.delphi.cmu.edu/epidata/fluview/?regions=hhs4,hhs6&epiweeks=201440-201520

### Updates to FluView on 2014w53, reported from 2015w01 through 2015w10 (national)

https://api.delphi.cmu.edu/epidata/fluview/?regions=nat&epiweeks=201453&issues=201501-201510


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national FluView data for epiweeks `201501-201510`.


### R

```R
library(epidatr)
# Fetch data
res <- pub_fluview(regions = "nat", epiweeks = epirange(201501, 201510))
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
res = epidata.pub_fluview(regions="nat", epiweeks=EpiRange(201501, 201510))
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.fluview('nat', [EpidataAsync.range(201501, 201510)]).then((res) => {
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
res <- Epidata$fluview(regions = list("nat"), epiweeks = list(Epidata$range(201501, 201510)))
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
res = Epidata.fluview(['nat'], [Epidata.range(201501, 201510)])
print(res['result'], res['message'], len(res['epidata']))
```
