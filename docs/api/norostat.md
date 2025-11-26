---
title: <i>inactive</i> NoroSTAT
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# NoroSTAT
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `norostat` |
| **Data Source** | [CDC NoroSTAT](https://www.cdc.gov/norovirus/php/reporting/norostat-data.html) metadata endpoint (requires authentication) |
| **Dataset Type** | Surveillance (Inactive) |
| **Geographic Coverage** | Only a specific list of full state names are permitted. See the `locations` output of the [meta_norostat](meta_norostat.html#norostat-metadata-1) endpoint for the allowed values. |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - Delphi stopped stopped acquiring data from this data source in November 2020. |
| **Earliest Date** | 2012w31 |

<!-- | **License** |  | -->

## Overview
{: .no_toc}

This data source provides norovirus surveillance data for US states, collected through the NoroSTAT system.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}


# The API

The base URL is: https://api.delphi.cmu.edu/epidata/norostat/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `string` with specific list of full state names |

## Response

| Field                     | Description                                                     | Type             |
|---------------------------|-----------------------------------------------------------------|------------------|
| `result`                  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                 | list of results                                                 | array of objects |
| `epidata[].release_date`  | date when data was released                                     | date (YYYY-MM-DD)|
| `epidata[].epiweek`       | epiweek for the data point                                      | integer          |
| `epidata[].value`         | count of norovirus outbreaks                                    | integer          |
| `message`                 | `success` or error message                                      | string           |

# Example URLs

### NoroSTAT on 2015w01
https://api.delphi.cmu.edu/epidata/norostat/?auth=...&location=Minnesota%2C%20Ohio%2C%20Oregon%2C%20Tennessee%2C%20and%20Wisconsin&epiweeks=201233

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2014-10-21",
      "epiweek": 201233,
      "value": 2
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch NoroSTAT data for the most recent available states for epiweek `201501`.

### R

```R
library(epidatr)
# Fetch data
res <- pvt_norostat(auth = 'auth_token', locations = 'Minnesota, Ohio, Oregon, Tennessee, and Wisconsin', epiweeks = 201501)
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
res = epidata.pvt_norostat(auth='auth_token', locations=['Minnesota, Ohio, Oregon, Tennessee, and Wisconsin'], epiweeks=[201501])
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.norostat('auth_token', ['Minnesota, Ohio, Oregon, Tennessee, and Wisconsin'], [201501]).then((res) => {
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
res <- Epidata$norostat(auth = "auth_token", locations = list("Minnesota, Ohio, Oregon, Tennessee, and Wisconsin"), epiweeks = list(201501))
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
res = Epidata.norostat('auth_token', ['Minnesota, Ohio, Oregon, Tennessee, and Wisconsin'], [201501])
print(res['result'], res['message'], len(res['epidata']))
```
