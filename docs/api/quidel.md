---
title: <i>inactive</i> Quidel
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Quidel
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `quidel` |
| **Data Source** | QuidelOrtho Corp. influenza testing data |
| **Geographic Coverage** | HHS regions (see [Geographic Codes](geographic_codes.html#hhs-regions)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated since 2020w15|
| **Earliest Date** | 2015w35 |

<!-- | **License** | Permission by QuidelOrtho | -->

## Overview
{: .no_toc}

This data source provides influenza testing data from Quidel Corporation, covering HHS health regions in the United States.

General topics not specific to any particular endpoint are discussed in the [API overview](https://cmu-delphi.github.io/delphi-epidata/). Such topics include: [contributing](https://cmu-delphi.github.io/delphi-epidata/api/README.html#contributing), [citing](https://cmu-delphi.github.io/delphi-epidata/api/README.html#citing), and [data licensing](https://cmu-delphi.github.io/delphi-epidata/api/README.html#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/quidel/>

See this [documentation](https://cmu-delphi.github.io/delphi-epidata/api/README.html) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of `hhs<#>` region labels (see [Geographic Codes](geographic_codes.html#hhs-regions)) |

## Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | HHS region label                                                | string           |
| `epidata[].epiweek`   | epiweek for the data point                                      | integer          |
| `epidata[].value`     | percentage of positive influenza tests                          | float            |
| `message`             | `success` or error message                                      | string           |

# Example URLs

### Quidel on 2015w35-2020w01 (HHS Region 1)
<https://api.delphi.cmu.edu/epidata/quidel/?auth=...&locations=hhs1&epiweeks=201535-202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "hhs1",
      "epiweek": 201535,
      "value": 2.0
    },
    {
      "location": "hhs1",
      "epiweek": 201536,
      "value": 6.16667
    },
    ...
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Quidel data for HHS Region 1 for epiweeks `201535-202001`.

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
res = epidata.pvt_quidel(auth='auth_token', locations=['hhs1'], epiweeks=EpiRange(201535, 202001))
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_quidel(auth = 'auth_token', locations = 'hhs1', epiweeks = epirange(201535, 202001))
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
res = Epidata.quidel('auth_token', ['hhs1'], Epidata.range(201535, 202001))
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$quidel(auth = "auth_token", locations = list("hhs1"), epiweeks = Epidata$range(201535, 202001))
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
  EpidataAsync.quidel('auth_token', ['hhs1'], Epidata.range(201535, 202001)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
