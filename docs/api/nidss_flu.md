---
title: <i>inactive</i> NIDSS Flu
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# NIDSS Flu
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nidss_flu` |
| **Source** | [Taiwan CDC](http://nidss.cdc.gov.tw/en/CDCWNH01.aspx?dc=wnh) |
| **Geographic Coverage** | Taiwan regions (see [Geographic Codes](geographic_codes.html#taiwan-regions)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated since 2018w10 |
| **Earliest Date** | 2008w14 |
| **License** | [Open Access](https://data.gov.tw/license) |

## Overview
{: .no_toc}

This data source provides weekly influenza case counts for Taiwan, as reported by the National Infectious Disease Statistics System (NIDSS).

This is the documentation of the API for accessing the Taiwan National Infectious Disease Statistics System Flu (`nidss_flu`) endpoint of
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

The base URL is: <https://api.delphi.cmu.edu/epidata/nidss_flu/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `regions` | regions | `list` of Taiwan region labels (see [Geographic Codes](geographic_codes.html#taiwan-regions)) |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

Notes:
- If both `issues` and `lag` are specified, only `issues` is used.
If neither is specified, the current issues are used.

## Response

| Field                    | Description                                                     | Type             |
|--------------------------|-----------------------------------------------------------------|------------------|
| `result`                 | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                | list of results                                                 | array of objects |
| `epidata[].release_date` | date when record was first published (yyyy-MM-dd)               | string           |
| `epidata[].region`       | region                                                          | string           |
| `epidata[].issue`        | epiweek of publication                                          | integer          |
| `epidata[].epiweek`      | epiweek during which the data was collected                     | integer          |
| `epidata[].lag`          | number of weeks between `epiweek` and `issue`                   | integer          |
| `epidata[].visits`       | total number of patients with ILI                               | integer          |
| `epidata[].ili`          | percent ILI                                                     | float            |
| `message`                | `success` or error message                                      | string           |

# Example URLs

### NIDSS Flu on 2015w01 (nationwide)
<https://api.delphi.cmu.edu/epidata/nidss_flu/?regions=nationwide&epiweeks=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2016-01-05",
      "region": "Nationwide",
      "issue": 201552,
      "epiweek": 201501,
      "lag": 51,
      "visits": 65685,
      "ili": 1.21
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national NIDSS Flu data for epiweeks `201501-201510` (10 weeks total).

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
res = epidata.pub_nidss_flu(regions=['nationwide'], epiweeks=EpiRange(201501, 201510))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_nidss_flu(regions = 'nationwide', epiweeks = epirange(201501, 201510))
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
res = Epidata.nidss_flu(['nationwide'], Epidata.range(201501, 201510))
print(res['result'], res['message'], len(res['epidata']))
```

# Source and Licensing

The full text of the NIDSS Flu license information is available on the Taiwan Digital Development Department's [website](https://data.gov.tw/license).
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$nidss_flu(regions = list("nationwide"), epiweeks = Epidata$range(201501, 201510))
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
  EpidataAsync.nidss_flu('nationwide', EpidataAsync.range(201501, 201510)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
