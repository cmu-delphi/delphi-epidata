---
title: FluView
parent: Epidata API (Other Diseases)
---

# FluView

This is the API documentation for accessing the FluView (`fluview`) endpoint of
[Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## FluView Data

Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet).
 - Data source: [United States Centers for Disease Control and Prevention](http://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) (CDC)
 - Temporal Resolution: Weekly* from 1997w40
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html), most States and Territories, and some Cities (full list [here](../../src/acquisition/fluview/fluview_locations.py))
 - Open access

\* Data is usually released on Friday

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `regions` | regions | `list` of [region](../../labels/regions.txt) labels |

### Optional

| Parameter | Description | Type |
| --- | --- | --- |
| `issues` | issues | `list` of epiweeks |
| `lag` | # weeks between each epiweek and its issue | integer |
| `auth` | password for private imputed data | string |

Notes:
- If both `issues` and `lag` are specified, only `issues` is used.
If neither is specified, the current issues are used.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].release_date` | | string or null |
| `epidata[].region` | | string |
| `epidata[].issue` | | integer |
| `epidata[].epiweek` | | integer |
| `epidata[].lag` | | integer |
| `epidata[].num_ili` | | integer |
| `epidata[].num_patients` | | integer |
| `epidata[].num_providers` | | integer |
| `epidata[].num_age_0` | | integer or null |
| `epidata[].num_age_1` | | integer or null |
| `epidata[].num_age_2` | | integer or null |
| `epidata[].num_age_3` | | integer or null |
| `epidata[].num_age_4` | | integer or null |
| `epidata[].num_age_5` | | integer or null |
| `epidata[].wili` | weighted percent influenza-like illness | float |
| `epidata[].ili` | percent influenza-like illness| float |
| `message` | `success` or error message | string |

Notes:
- If authorized via `auth`, private data is not included.

# Example URLs

### FluView on 2015w01 (national)
https://delphi.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2017-10-24",
      "region": "nat",
      "issue": 201740,
      "epiweek": 201501,
      "lag": 143,
      "num_ili": 31483,
      "num_patients": 771835,
      "num_providers": 1958,
      "num_age_0": 7160,
      "num_age_1": 9589,
      "num_age_2": null,
      "num_age_3": 8072,
      "num_age_4": 3614,
      "num_age_5": 3048,
      "wili": 4.21374,
      "ili": 4.07898
    }
  ],
  "message": "success"
}
```

### FluView in HHS Regions 4 and 6 for the 2014/2015 flu season

https://delphi.cmu.edu/epidata/api.php?source=fluview&regions=hhs4,hhs6&epiweeks=201440-201520

### Updates to FluView on 2014w53, reported from 2015w01 through 2015w10 (national)

https://delphi.cmu.edu/epidata/api.php?source=fluview&regions=nat&epiweeks=201453&issues=201501-201510


# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national FluView data for epiweeks `201440` and `201501-201510` (11 weeks total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.fluview(callback, ['nat'], [201440, Epidata.range(201501, 201510)])
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
  Epidata.fluview(callback, ['nat'], [201440, Epidata.range(201501, 201510)]);
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
res = Epidata.fluview(['nat'], [201440, Epidata.range(201501, 201510)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$fluview(list('nat'), list(201440, Epidata$range(201501, 201510)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
