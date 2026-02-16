---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: Google Health Trends
---

# Google Health Trends
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `ght` |
| **Data Source** | Google Health Trends |
| **Geographic Levels** | National, State (see [Geographic Codes](geographic_codes.md#us-states-and-territories)) |
| **Temporal Granularity** | Weekly (Epiweek) | 
| **Reporting Cadence** | Inactive - No longer updated since 2022w36 |
| **Temporal Scope Start** | 1993w01 |
| **License** | [Google Terms of Service](https://policies.google.com/terms) |

## Overview
{: .no_toc}

The `ght` endpoint provides access to Google Health Trends data, which tracks the aggregated volume of search queries related to specific influenza symptoms and treatments.

{: .note}
> **Notes:**
> - This data source tracks the search interest for specific terms (e.g., "flu symptoms", "thermometer") rather than model estimates. It is distinct from Google Flu Trends (GFT) which provided modeled ILI rates.
> - Restricted access: This endpoint requires authentication.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

This data may be useful for real-time monitoring of diseases, as in:
- Herman Anthony Carneiro, Eleftherios Mylonakis. [Google Trends: A Web-Based Tool for Real-Time Surveillance of Disease Outbreaks](https://doi.org/10.1086/630200). Clinical Infectious Diseases, Volume 49, Issue 10, 15 November 2009, Pages 1557–1564. 
- Abel Brodeur, Andrew E. Clark, Sarah Fleche, Nattavudh Powdthavee.
[COVID-19, lockdowns and well-being: Evidence from Google Trends](https://doi.org/10.1016/j.jpubeco.2020.104346). Journal of Public Economics, Volume 193, 2021, 104346.
- Sudhakar V. Nuti, Brian Wayda, Isuru Ranasinghe, Sisi Wang, Rachel P. Dreyer, Serene I. Chen, Karthik Murugiah. [The Use of Google Trends in Health Care Research: A Systematic Review](https://doi.org/10.1371/journal.pone.0109583), October 2014.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Values represent the relative search volume for a specific query or topic within a geographic region.

<!-- Source code: src/acquisition/ght/ght_update.py -->


## The API

The base URL is: <https://api.delphi.cmu.edu/epidata/ght/>


### Parameters

#### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.md)) | `list` of epiweeks |
| `locations` | locations | `list` of state codes (see [Geographic Codes](geographic_codes.md#us-states-and-territories)) and/or `US` |
| `query` | search query or topic ID (see [Valid Queries](#valid-queries)) | string |

##### Valid Queries

<details markdown="1">
<summary>Click to expand full list of valid queries</summary>

*   `/m/0cycc`
*   `influenza type a`
*   `flu duration`
*   `flu fever`
*   `treating flu`
*   `fever flu`
*   `flu recovery`
*   `braun thermoscan`
*   `oscillococcinum`
*   `treating the flu`
*   `cold or flu`
*   `flu versus cold`
*   `flu remedies`
*   `contagious flu`
*   `type a influenza`
*   `flu or cold`
*   `duration of flu`
*   `cold versus flu`
*   `flu cough`
*   `flu headache`
*   `thermoscan`
*   `influenza incubation period`
*   `flu lasts`
*   `length of flu`
*   `flu stomach`
*   `cold vs flu`
*   `flu and fever`
*   `getting over the flu`
*   `influenza a`
*   `treatment for flu`
*   `flu length`
*   `treatment for the flu`
*   `influenza symptoms`
*   `over the counter flu`
*   `flu complications`
*   `cold and flu symptoms`
*   `influenza incubation`
*   `treatment of flu`
*   `human temperature`
*   `low body`
*   `flu contagious`
*   `robitussin ac`
*   `flu how long`
*   `ear thermometer`
*   `flu contagious period`
*   `treat flu`
*   `cough flu`
*   `low body temperature`
*   `expectorant`
*   `flu and cold`
*   `rapid flu`
*   `flu vs. cold`
*   `how to treat the flu`
*   `how long does the flu last?`
*   `viral pneumonia`
*   `flu in kids`
*   `type a flu`
*   `influenza treatment`
*   `fighting the flu`
*   `flu relief`
*   `treat the flu`
*   `flu medicine`
*   `dangerous fever`
*   `what is influenza`
*   `tussin`
*   `low body temp`
*   `flu care`
*   `flu in infants`
*   `flu dizziness`
*   `feed a fever`
*   `flu vs cold`
*   `flu vomiting`
*   `bacterial pneumonia`
*   `flu activity`
*   `flu chills`
*   `anas barbariae`
*   `flu germs`
*   `tylenol cold`
*   `how to get over the flu`
*   `flu in children`
*   `influenza a and b`
*   `duration of the flu`
*   `cold symptoms`
*   `flu report`
*   `rapid flu test`
*   `flu relapse`
*   `get over the flu`
*   `flu during pregnancy`
*   `flu recovery time`
*   `cure for flu`
*   `tamiflu and breastfeeding`
*   `flu chest pain`
*   `flu treatment`
*   `flu nausea`
*   `remedies for the flu`
*   `tamiflu in pregnancy`
*   `side effects of tamiflu`
*   `how to treat flu`
*   `viral bronchitis`
*   `flu how long contagious`
*   `flu remedy`

</details>

### Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].query`     | search query                                                    | string           |
| `epidata[].value`     | search volume                                                   | float            |
| `message`             | `success` or error message                                      | string           |

## Example URLs

### Google Health Trends for "how to get over the flu" on 2015w01 (US)
<https://api.delphi.cmu.edu/epidata/ght/?auth=...&locations=US&epiweeks=201501&query=how%20to%20get%20over%20the%20flu>

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "US",
      "epiweek": 201501,
      "value": 9.113
    }
  ],
  "message": "success"
}
```

## Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch GHT data for "how to get over the flu" in the US for epiweek `201501`.

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
from epidatpy import EpiDataContext
# Fetch data
epidata = EpiDataContext()
res = epidata.pvt_ght('auth_token', ['US'], [201501], 'how to get over the flu')
print(res.df())
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pvt_ght(auth = 'auth_token', locations = 'US', epiweeks = 201501,
               query = "how to get over the flu")
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
res = Epidata.ght('auth_token', ['US'], [201501], 'how to get over the flu')
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$ght(auth = "auth_token", locations = list("US"), epiweeks = list(201501), query = "how to get over the flu")
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
  EpidataAsync.ght('auth_token', ['US', 'CN'], EpidataAsync.range(201501, 201510), 'g').then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
