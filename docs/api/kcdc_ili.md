---
title: <i>inactive</i> KCDC ILI
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# KCDC ILI
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `kcdc_ili` |
| **Data Source** | [Korea Disease Control and Prevention Agency (KCDC) ILI surveillance](https://www.kdca.go.kr/) |
| **Geographic Coverage** | ROK (Republic of Korea) (see [Geographic Codes](geographic_codes.md#republic-of-korea)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated since 2020w44 |
| **Earliest Date** | 2004w36 |
| **License** | This was scraped from a publicly-accessible government website, but no explicit license terms were found. |

## Overview
{: .no_toc}

This data source provides weekly influenza-like illness (ILI) data for the Republic of Korea, as reported by the Korea Centers for Disease Control and Prevention (KCDC).

This is the API documentation for accessing the KCDC ILI (`kcdc_ili`) endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}


# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/kcdc_ili/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `regions` | Regions to fetch. See [Geographic Codes](geographic_codes.html#republic-of-korea). | `list` of strings |
| `epiweeks` | Epiweeks to fetch. Supports [`epirange()`] and defaults to all ("*") dates. | `list` of epiweeks |

### Optional

| Parameter | Description | Type |
| --- | --- | --- |
| `issues` | Optionally, the issue(s) of the data to fetch. See the "Data Versioning" section for details. | `list` of epiweeks |
| `lag` | Optionally, the lag of the issues to fetch. See the "Data Versioning" section for details. | integer |

{: .note}
> **Notes:**
> - If both `issues` and `lag` are specified, only `issues` is used.
> - If neither is specified, the current issues are used.

## Response

| Field                     | Description                                                     | Type             |
|---------------------------|-----------------------------------------------------------------|------------------|
| `result`                  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                 | list of results                                                 | array of objects |
| `epidata[].release_date`  | date of release                                                 | string           |
| `epidata[].region`        | region name                                                     | string           |
| `epidata[].issue`         | epiweek of issue                                                | integer          |
| `epidata[].epiweek`       | epiweek of data                                                 | integer          |
| `epidata[].lag`           | lag in weeks                                                    | integer          |
| `epidata[].ili`           | percent ILI                                                     | float            |
| `epidata[].visits`        | number of visits                                                | integer          |
| `message`                 | `success` or error message                                      | string           |

# Example URLs

### KCDC ILI in ROK on 2020w01
<https://api.delphi.cmu.edu/epidata/kcdc_ili/?regions=ROK&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2020-01-10",
      "region": "ROK",
      "issue": 202001,
      "epiweek": 202001,
      "lag": 44,
      "ili": 49.8,
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch KCDC ILI data for ROK for epiweeks `202001` and `202002`.

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
res = epidata.pub_kcdc_ili(regions=['ROK'], epiweeks=[202001, 202002])
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_kcdc_ili(regions = 'ROK', epiweeks = c(202001, 202002))
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
res = Epidata.kcdc_ili(['ROK'], [202001, 202002])
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$kcdc_ili(regions = list("ROK"), epiweeks = list(202001, 202002))
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
  EpidataAsync.kcdc_ili('ROK', [202001, 202002]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
