---
title: <i>inactive</i> NoroSTAT Metadata
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
permalink: api/meta_norostat.html
---

# NoroSTAT Metadata
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `meta_norostat` |
| **Data Source** | [CDC NoroSTAT](https://www.cdc.gov/norovirus/php/reporting/norostat-data.html) |
| **Update Frequency** | Inactive - Delphi stopped stopped acquiring data from this data source in November 2020. |

<!-- | **License** | Open Access | -->

This is the documentation of the API for accessing the NoroSTAT Metadata (`meta_norostat`) endpoint of
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

The base URL is: https://api.delphi.cmu.edu/epidata/meta_norostat/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |

## Response

| Field                         | Description                                                     | Type             |
|-------------------------------|-----------------------------------------------------------------|------------------|
| `result`                      | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                     | metadata object containing locations and releases               | object           |
| `epidata.locations`           | list of location sets available over time                       | array of objects |
| `epidata.locations[].location`| comma-separated list of state names available in this release   | string           |
| `epidata.releases`            | list of data release dates                                      | array of objects |
| `epidata.releases[].release_date` | date when data was released (YYYY-MM-DD)                    | string           |
| `message`                     | `success` or error message                                      | string           |

# Example URLs

### NoroSTAT Metadata
https://api.delphi.cmu.edu/epidata/meta_norostat/?auth=...

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

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch NoroSTAT Metadata.

### R

```R
library(epidatr)
# Fetch data
res <- pvt_meta_norostat(auth = 'auth_token')
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
res = epidata.pvt_meta_norostat(auth='auth_token')
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.meta_norostat('auth_token').then((res) => {
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
res <- Epidata$meta_norostat(auth = "auth_token")
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
res = Epidata.meta_norostat('auth_token')
print(res['result'], res['message'], len(res['epidata']))
```
