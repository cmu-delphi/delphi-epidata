---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: NoroSTAT Metadata
permalink: api/meta_norostat.html
---

# NoroSTAT Metadata
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `meta_norostat` |
| **Data Source** | [CDC NoroSTAT](https://www.cdc.gov/norovirus/php/reporting/norostat-data.html) |
| **Reporting Cadence** | Inactive - Delphi stopped stopped acquiring data from this data source in November 2020. |

<!-- | **License** | Open Access | -->

## Overview
{: .no_toc}

This endpoint is a companion data source to the [NoroSTAT](norostat.md) endpoint.
It describes when the NoroSTAT endpoint was last updated and for which locations.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

{: .note}
> **Note:** Restricted access: This endpoint requires authentication.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}


## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/meta_norostat/>


### Parameters

#### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |

### Response

| Field                         | Description                                                     | Type             |
|-------------------------------|-----------------------------------------------------------------|------------------|
| `result`                      | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                     | metadata object containing locations and releases               | object           |
| `epidata.locations`           | list of location sets available over time                       | array of objects |
| `epidata.locations[].location`| comma-separated list of state names available in this release   | string           |
| `epidata.releases`            | list of data release dates                                      | array of objects |
| `epidata.releases[].release_date` | date when data was released (YYYY-MM-DD)                    | string           |
| `message`                     | `success` or error message                                      | string           |

## Example URLs

### NoroSTAT Metadata
<https://api.delphi.cmu.edu/epidata/meta_norostat/?auth=...>

```json
{
  "result": 1,
  "epidata": {
    "locations": [
      {
        "location": "Massachusetts, Michigan, Minnesota, Nebraska, New Mexico, Ohio, Oregon, South Carolina, Tennessee, Virginia, Wisconsin, and Wyoming"
      },
      {
        "location": "Massachusetts, Michigan, Minnesota, New Mexico, Ohio, Oregon, South Carolina, Tennessee, Virginia, Wisconsin, and Wyoming"
      },
      {
        "location": "Massachusetts, Michigan, Minnesota, Ohio, Oregon, South Carolina, Tennessee, Virginia, and Wisconsin"
      },
      {
        "location": "Michigan, Minnesota, Ohio, Oregon, South Carolina, Tennessee, and Wisconsin"
      },
      {
        "location": "Minnesota, Ohio, Oregon, Tennessee, and Wisconsin"
      }
    ],
    "releases": [
      {"release_date": "2014-10-21"},
      {"release_date": "2015-03-30"},
      ...]
  },
  "message": "success"
}
```

## Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch NoroSTAT Metadata.

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
res = epidata.pvt_meta_norostat(auth='auth_token')
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_meta_norostat(auth = 'auth_token')
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
res = Epidata.meta_norostat('auth_token')
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$meta_norostat(auth = "auth_token")
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
  EpidataAsync.norostat_meta('auth_token').then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
