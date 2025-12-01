---
title: <i>inactive</i> NIDSS Dengue
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# NIDSS Dengue
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nidss_dengue` |
| **Data Source** | [Taiwan CDC](http://nidss.cdc.gov.tw/en/SingleDisease.aspx?dc=1&dt=4&disease=061&position=1)|
| **Geographic Coverage** | Taiwan regions and cities/counties (see [Geographic Codes](geographic_codes.html#nidss)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated |
| **Earliest Date** | 2003w01 |
| **License** | [Open Access](https://data.gov.tw/license) |

## Overview
{: .no_toc}

This is the documentation of the API for accessing the Taiwan National Infectious Disease Statistics System Dengue (`nidss_dengue`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}


# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/nidss_dengue/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of Taiwan region and/or location labels (see [Geographic Codes](geographic_codes.html#nidss)) |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].location` | location                                                        | string           |
| `epidata[].epiweek`  | epiweek during which the data was collected                     | integer          |
| `epidata[].count`    | number of cases                                                 | integer          |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### NIDSS Dengue on 2015w01 (nationwide)
<https://api.delphi.cmu.edu/epidata/nidss_dengue/?locations=nationwide&epiweeks=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nationwide",
      "epiweek": 201501,
      "count": 20
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national NIDSS Dengue data for epiweeks `201501-201510` (10 weeks total).

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
res = epidata.pub_nidss_dengue(locations=['nationwide'], epiweeks=EpiRange(201501, 201510))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_nidss_dengue(locations = 'nationwide', epiweeks = epirange(201501, 201510))
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
res = Epidata.nidss_dengue(['nationwide'], Epidata.range(201501, 201510))
print(res['result'], res['message'], len(res['epidata']))
```

# Source and Licensing

The full text of the NIDSS Dengue license information is available on the Taiwan Digital Development Department's [website](https://data.gov.tw/license).
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$nidss_dengue(regions = list("nationwide"), epiweeks = Epidata$range(201501, 201510))
print(res$message)
print(length(res$epidata))
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.nidss_dengue('nationwide', EpidataAsync.range(201501, 201510)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
