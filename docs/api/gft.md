---
title: Google Flu Trends
parent: Epidata API (Other Diseases)
---

# Google Flu Trends

This is the API documentation for accessing the Google Flu Trends (`gft`)
endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Google Flu Trends Data

Estimate of influenza activity based on volume of certain search queries. Google has discontinued Flu Trends, and this is now a static endpoint.
 - Source: [Google](https://www.google.org/flutrends/)
 - Temporal Resolution: Weekly from 2003w40 until 2015w32
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/) ([1+10](../../labels/regions.txt)); by state/territory ([50+1](../../labels/states.txt)); and by city ([97](../../labels/cities.txt))
 - Open access

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [region](../../labels/regions.txt)/[state](../../labels/states.txt)/[city](../../labels/cities.txt) labels |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].location` | location | string |
| `epidata[].epiweek` | epiweek | epiweek |
| `epidata[].num` | number | integer |
| `message` | `success` or error message | string |

# Example URLs

### Google Flu Trends on 2015w01 (national)
https://delphi.cmu.edu/epidata/api.php?source=gft&locations=nat&epiweeks=201501

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nat",
      "epiweek": 201501,
      "num": 4647
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Google Flu Trends data for epiweeks `201440` and `201501-201510` (11 weeks total).

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
  Epidata.gft(callback, ['nat'], [201440, Epidata.range(201501, 201510)]);
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
res = Epidata.gft(['nat'], [201440, Epidata.range(201501, 201510)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$gft(list('nat'), list(201440, Epidata$range(201501, 201510)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
