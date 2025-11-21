---
title: <i>inactive</i> Google Health Trends
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Google Health Trends
{: .no_toc}

* **Source name:** `ght`
* **Earliest issue available:** 2003w40
* **Available for:** US states([states list](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt)) and national level (US)
* **Time type available:** epiweek
* **License:** Restricted (requires auth)

This is the API documentation for accessing the [Google Health Trends](https://trends.google.com/trends/fullscreen/m/IN)  (`ght`)
endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}



- Herman Anthony Carneiro, Eleftherios Mylonakis. [Google Trends: A Web-Based Tool for Real-Time Surveillance of Disease Outbreaks](https://doi.org/10.1086/630200). Clinical Infectious Diseases, Volume 49, Issue 10, 15 November 2009, Pages 1557–1564. 
- Abel Brodeur, Andrew E. Clark, Sarah Fleche, Nattavudh Powdthavee.
[COVID-19, lockdowns and well-being: Evidence from Google Trends](https://doi.org/10.1016/j.jpubeco.2020.104346). Journal of Public Economics, Volume 193, 2021, 104346.
- Sudhakar V. Nuti, Brian Wayda, Isuru Ranasinghe, Sisi Wang, Rachel P. Dreyer, Serene I. Chen, Karthik Murugiah. [The Use of Google Trends in Health Care Research: A Systematic Review](https://doi.org/10.1371/journal.pone.0109583), October 2014.

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/ght/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [state](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt) and/or `US` labels |
| `query` | search query or topic ID (see https://www.freebase.com/) | string |

## Response

| Field                 | Description                                                     | Type             |
|-----------------------|-----------------------------------------------------------------|------------------|
| `result`              | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`             | list of results                                                 | array of objects |
| `epidata[].location`  | location label                                                  | string           |
| `epidata[].epiweek`   | epiweek                                                         | integer          |
| `epidata[].query`     | search query                                                    | string           |
| `epidata[].value`     | search volume                                                   | float            |
| `message`             | `success` or error message                                      | string           |

# Example URLs

### Google Health Trends for "how to get over the flu" on 2015w01 (US)
https://api.delphi.cmu.edu/epidata/ght/?auth=...&locations=US&epiweeks=201501&query=how%20to%20get%20over%20the%20flu

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "US",
      "epiweek": 201501,
      "query": "flu",
      "value": 9.113
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch GHT data for "how to get over the flu" in the US for epiweek `201501`.

### R

```R
library(epidatr)
# Fetch data
res <- pvt_ght(auth = 'auth_token', locations = 'US', epiweeks = 201501,
               query = "how to get over the flu")
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
res = epidata.ght('auth_token', ['US'], [201501], 'how to get over the flu')
print(res['result'], res['message'], len(res['epidata']))
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.ght('auth_token', 'US', [201501], 'how to get over the flu').then((res) => {
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
res <- Epidata$ght(auth = "auth_token", locations = list("US"), epiweeks = list(201501), query = "how to get over the flu")
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
res = Epidata.ght('auth_token', ['US'], [201501], 'how to get over the flu')
print(res['result'], res['message'], len(res['epidata']))
```
