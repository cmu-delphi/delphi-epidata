---
title: Flusurv
parent: Epidata API (Other Diseases)
---

# FluSurv

This is the API documentation for accessing the FluSurv (`flusurv`) endpoint of
[Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## FluSurv Data

FluSurv-NET data (flu hospitaliation rates) from CDC.

See also:
  - https://gis.cdc.gov/GRASP/Fluview/FluHospRates.html
  - https://wwwnc.cdc.gov/eid/article/21/9/14-1912_article
  - Chaves, S., Lynfield, R., Lindegren, M., Bresee, J., & Finelli, L. (2015).
    The US Influenza Hospitalization Surveillance Network. Emerging Infectious
    Diseases, 21(9), 1543-1550. https://dx.doi.org/10.3201/eid2109.141912.

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [location](../../labels/flusurv_locations.txt) labels |

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
| `epidata[].release_date` | | string |
| `epidata[].location` | | string |
| `epidata[].issue` | | integer |
| `epidata[].epiweek` | | integer |
| `epidata[].lag` | | integer |
| `epidata[].rate_age_0` | | float |
| `epidata[].rate_age_1` | | float |
| `epidata[].rate_age_2` | | float |
| `epidata[].rate_age_3` | | float |
| `epidata[].rate_age_4` | | float |
| `epidata[].rate_overall` | | float |
| `message` | `success` or error message | string |

Notes:
* The `flusurv` age groups are, in general, not the same as the ILINet
(`fluview`) age groups. However, the following groups are equivalent:
  - flusurv age_0 == fluview age_0  (0-4 years)
  - flusurv age_3 == fluview age_4  (50-64 years)
  - flusurv age_4 == fluview age_5  (65+ years)

# Example URLs

### FluSurv on 2020w01 (CA)
https://delphi.cmu.edu/epidata/api.php?source=flusurv&locations=ca&epiweeks=202001

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2020-04-10",
      "location": "CA",
      "issue": 202014,
      "epiweek": 202001,
      "lag": 13,
      "rate_age_0": 8.4,
      "rate_age_1": 0.8,
      "rate_age_2": 1.6,
      "rate_age_3": 5.6,
      "rate_age_4": 16.5,
      "rate_overall": 4.8
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch CA FluView Clinical data for epiweeks `201940` and `202001-202010` (11 weeks total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.flusurv(callback, ['ca'], [201940, Epidata.range(202001, 202010)])
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
  Epidata.flusurv(callback, ['ca'], [201940, Epidata.range(202001, 202010)]);
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
res = Epidata.flusurv(['ca'], [201940, Epidata.range(202001, 202010)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$flusurv(list('ca'), list(201940, Epidata$range(202001, 202010)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
