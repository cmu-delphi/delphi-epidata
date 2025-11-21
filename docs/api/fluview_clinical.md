---
title: FluView Clinical
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 1
---

# FluView Clinical
{: .no_toc}

* **Source name:** `fluview_clinical`
* **Earliest issue available:** 2010w40
* **Available for:** nat, hhs1-hhs10, and cen1-cen9 ([full list of regions](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt))
* **Time type available:** epiweek
* **License:** Open Access


## Overview
{: .no_toc}

This data source provides age-stratified clinical data on laboratory-confirmed influenza from the US Flu View system.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}



# The API

The base URL is: https://api.delphi.cmu.edu/epidata/fluview_clinical/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `regions` | regions | `list` of [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt) labels |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

Notes:
- If both `issues` and `lag` are specified, only `issues` is used.
If neither is specified, the current issues are used.

## Response

| Field                        | Description                                                     | Type             |
|------------------------------|-----------------------------------------------------------------|------------------|
| `result`                     | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                    | list of results                                                 | array of objects |
| `epidata[].release_date`     | date when data was released                                     | string           |
| `epidata[].region`           | region identifier                                               | string           |
| `epidata[].issue`            | epiweek of publication                                          | integer          |
| `epidata[].epiweek`          | epiweek for which data is valid                                 | integer          |
| `epidata[].lag`              | number of weeks between epiweek and issue                       | integer          |
| `epidata[].total_specimens`  | total number of specimens tested                                | integer          |
| `epidata[].total_a`          | total specimens positive for influenza A                        | integer          |
| `epidata[].total_b`          | total specimens positive for influenza B                        | integer          |
| `epidata[].percent_positive` | percentage of specimens testing positive for influenza          | float            |
| `epidata[].percent_a`        | percentage of specimens testing positive for influenza A        | float            |
| `epidata[].percent_b`        | percentage of specimens testing positive for influenza B        | float            |
| `message`                    | `success` or error message                                      | string           |

# Example URLs

### FluView Clinical on 2020w01 (national)
https://api.delphi.cmu.edu/epidata/fluview_clinical/?regions=nat&epiweeks=202001

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2021-10-08",
      "region": "nat",
      "issue": 202014,
      "epiweek": 202001,
      "lag": 13,
      "total_specimens": 64980,
      "total_a": 5651,
      "total_b": 9647,
      "percent_positive": 23.5426,
      "percent_a": 8.69652,
      "percent_b": 14.8461
    },
    ...
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national FluView Clinical data for epiweeks `201601-201701`.

### R

```R
library(epidatr)
# Fetch data
res <- pub_fluview_clinical(regions = "nat", epiweeks =  epirange(201601, 201701))
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
res = Epidata.fluview_clinical(['nat'], [Epidata.range(201601, 201701)])
print(res['result'], res['message'], len(res['epidata']))
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.fluview_clinical('nat', [EpidataAsync.range(201601, 201701)]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```

### Legacy Clients

We recommend using our modern client libraries: [epidatr](https://cmu-delphi.github.io/epidatr/) for R and [epidatpy](https://cmu-delphi.github.io/epidatpy/) for Python. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$fluview_clinical(regions = list("nat"), epiweeks = list(Epidata$range(201601, 201701)))
print(res$message)
print(length(res$epidata))
```

#### Python (Legacy)

Optionally install the package using pip(env):
```bash
pip install delphi-epidata
```

Place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.fluview_clinical(['nat'], [Epidata.range(201601, 201701)])
print(res['result'], res['message'], len(res['epidata']))
```
