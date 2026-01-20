---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: NoroSTAT
---

# NoroSTAT
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `norostat` |
| **Data Source** | [CDC NoroSTAT](https://www.cdc.gov/norovirus/php/reporting/norostat-data.html) metadata endpoint (requires authentication) |
| **Dataset Type** | Surveillance (Inactive) |
| **Geographic Levels** | Only a specific list of full state names are permitted. See the `locations` output of the [meta_norostat](norostat_meta.md#norostat-metadata-1) endpoint for the allowed values. |
| **Temporal Granularity** | Weekly (Epiweek) |
| **Reporting Cadence** | Inactive - No longer updated since 2020w30. |
| **Temporal Scope Start** | 2012w31 |
| **License** | [Publicly Accessible US Government](https://www.usa.gov/government-works) |

## Overview
{: .no_toc}

This data source provides norovirus surveillance data for US states, collected through the NoroSTAT system via the US CDC.

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

## Estimation

NoroSTAT data is derived from the CDC's sentinel surveillance system, which tracks norovirus outbreaks in participating states. The `value` field represents raw outbreak counts.

Outbreak reports are aggregated weekly. No additional smoothing or statistical adjustments are applied by Delphi.

## Lag and Backfill

*   **Lag:** Historically, data was released with a lag of several weeks.
*   **Backfill:**  NoroSTAT data was subject to revisions as new reports were finalized or historical data was updated by participating states. The API tracks these revisions via the `release_date`.

## Limitations

*   Data is only available for specific lists of participating states. Use the [NoroSTAT Metadata](norostat_meta.md) endpoint to check available locations.


# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/norostat/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.html)) | `list` of epiweeks |
| `location` | Location string. Must be an exact match from the `location` field of the [NoroSTAT Metadata](norostat_meta.md) endpoint. | string |

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
<https://api.delphi.cmu.edu/epidata/norostat/?auth=...&location=Minnesota%2C%20Ohio%2C%20Oregon%2C%20Tennessee%2C%20and%20Wisconsin&epiweeks=201233>

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
res = epidata.pvt_norostat(auth='auth_token', locations=['Minnesota, Ohio, Oregon, Tennessee, and Wisconsin'], epiweeks=[201501])
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_norostat(auth = 'auth_token', locations = 'Minnesota, Ohio, Oregon, Tennessee, and Wisconsin', epiweeks = 201501)
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
res = Epidata.norostat('auth_token', ['Minnesota, Ohio, Oregon, Tennessee, and Wisconsin'], [201501])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$norostat(auth = "auth_token", locations = list("Minnesota, Ohio, Oregon, Tennessee, and Wisconsin"), epiweeks = list(201501))
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
  EpidataAsync.norostat('nat', [EpidataAsync.range(201501, 201510)]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
