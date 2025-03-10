---
title: <i>inactive</i> NIDSS Dengue
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# NIDSS Dengue

This is the documentation of the API for accessing the Taiwan National Infectious Disease Statistics System Dengue (`nidss_dengue`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## NIDSS Dengue Data

Counts of confirmed dengue cases from Taiwan's National Infectious Disease Statistics System (NIDSS).
 - Data source: [Taiwan CDC](http://nidss.cdc.gov.tw/en/SingleDisease.aspx?dc=1&dt=4&disease=061&position=1)
 - Temporal Resolution: Weekly from 2003w01
 - Spatial Resolution: By [hexchotomy region](https://en.wikipedia.org/wiki/Regions_of_Taiwan#Hexchotomy) ([6+1](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/nidss_regions.txt)) and by [city/county](https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_Taiwan) ([22](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/nidss_locations.txt))
 - Open access

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/nidss_dengue/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/nidss_regions.txt) and/or [location](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/nidss_locations.txt) labels |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].location` | location                                                        | string           |
| `epidata[].epiweek`  | epiweek during which the data was collected                     | integer          |
| `epidata[].count`    | number of cases                                                 | integer          |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### NIDSS Dengue on 2015w01 (nationwide)
https://api.delphi.cmu.edu/epidata/nidss_dengue/?locations=nationwide&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nationwide",
      "epiweek": 201501,
      "count": 20
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js), [Python](https://pypi.org/project/delphi-epidata/), and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national NIDSS Dengue data for epiweeks `201440` and `201501-201510` (11 weeks total).

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.nidss_dengue('nationwide', [201440, EpidataAsync.range(201501, 201510)]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
````

### Python

Optionally install the package using pip(env):
````bash
pip install delphi-epidata
````

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

````python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.nidss_dengue(['nationwide'], [201440, Epidata.range(201501, 201510)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$nidss_dengue(list('nationwide'), list(201440, Epidata$range(201501, 201510)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````

# Source and Licensing

The full text of the NIDSS Dengue license information is available on the Taiwan Digital Development Department's [website](https://data.gov.tw/license).