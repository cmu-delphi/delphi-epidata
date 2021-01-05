---
title: NIDSS Flu
parent: Epidata API (Other Diseases)
---

# NIDSS Flu

This is the documentation of the API for accessing the NIDSS Flu (`nidss_flu`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## NIDSS Flu Data

Outpatient ILI from Taiwan's National Infectious Disease Statistics System (NIDSS).
 - Source: [Taiwan CDC](http://nidss.cdc.gov.tw/en/CDCWNH01.aspx?dc=wnh)
 - Temporal Resolution: Weekly* from 2008w14
 - Spatial Resolution: By [hexchotomy region](https://en.wikipedia.org/wiki/Regions_of_Taiwan#Hexchotomy) ([6+1](../../labels/nidss_regions.txt))
 - Open access

\* Data is usually released on Tuesday

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `regions` | regions | `list` of [region](../../labels/nidss_regions.txt) labels |

### Optional

| Parameter | Description | Type |
| --- | --- | --- |
| `issues` | issues | `list` of epiweeks |
| `lag` | # weeks between each epiweek and its issue | integer |

Notes:
- If both `issues` and `lag` are specified, only `issues` is used.
If neither is specified, the current issues are used.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].release_date` | date when record was first published (yyyy-MM-dd) | string |
| `epidata[].region` | region | string |
| `epidata[].issue` | epiweek of publication | integer |
| `epidata[].epiweek` | epiweek during which the data was collected | integer |
| `epidata[].lag` | number of weeks between `epiweek` and `issue` | integer |
| `epidata[].visits` | total number of patients with ILI | integer |
| `epidata[].ili` | percent ILI | float |
| `message` | `success` or error message | string |

# Example URLs

### NIDSS Flu on 2015w01 (nationwide)
https://delphi.cmu.edu/epidata/api.php?source=nidss_flu&regions=nationwide&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2016-01-05",
      "region": "Nationwide",
      "issue": 201552,
      "epiweek": 201501,
      "lag": 51,
      "visits": 65685,
      "ili": 1.21
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national NIDSS Flu data for epiweeks `201440` and `201501-201510` (11 weeks total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.nidss_flu(callback, ['nationwide'], [201440, Epidata.range(201501, 201510)])
````

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="jquery.js"></script>
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  var callback = function(result, message, epidata) {
    console.log(result, message, epidata != null ? epidata.length : void 0);
  };
  Epidata.nidss_flu(callback, ['nationwide'], [201440, Epidata.range(201501, 201510)]);
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
res = Epidata.nidss_flu(['nationwide'], [201440, Epidata.range(201501, 201510)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$nidss_flu(list('nationwide'), list(201440, Epidata$range(201501, 201510)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
