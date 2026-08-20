---
title: FluView Metadata
parent: Data Sources and Signals
grand_parent: Other Endpoints
nav_order: 1
---

# FluView Metadata
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `fluview_meta` |
| **Data Source** | [United States Centers for Disease Control and Prevention (CDC)](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) |
| **License** | [Publicly Accessible US Government](https://www.usa.gov/government-works) |

## Overview
{: .no_toc}

The FluView metadata (`fluview_meta`) endpoint is a companion data source to the [FluView](fluview.md) endpoint.
It describes when the FluView endpoint was last updated and how many records are available.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## FluView Metadata

Returns information about the [`fluview` endpoint](fluview.md).

## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/fluview_meta/>


### Parameters

There are no parameters for this endpoint.

### Response

| Field                     | Description                                                     | Type             |
|---------------------------|-----------------------------------------------------------------|------------------|
| `result`                  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                 | list of results                                                 | array of objects |
| `epidata[].latest_update` | date when data was last updated                                 | string           |
| `epidata[].latest_issue`  | most recent "issue" (epiweek) in the data                       | integer          |
| `epidata[].table_rows`    | total number of rows in the table                               | integer          |
| `message`                 | `success` or error message                                      | string           |

## Example URLs

### FluView Metadata
<https://api.delphi.cmu.edu/epidata/fluview_meta/>

```json
{
  "result": 1,
  "epidata": [
    {
      "latest_update": "2020-04-24",
      "latest_issue": 202016,
      "table_rows": 957673
    }
  ],
  "message": "success"
}
```

## Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch FluView metadata.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

```python
# Import
from epidatpy import EpiDataContext
# Fetch data
epidata = EpiDataContext()
res = epidata.pub_fluview_meta()
print(res.df())
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_fluview_meta()
print(res)
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
res = Epidata.fluview_meta()
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$fluview_meta()
print(res$epidata)
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.fluview_meta().then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
