---
title: Digital Surveillance Sensors
parent: Epidata API (Other Diseases)
---

# Digital Surveillance Sensors

This is the documentation of the API for accessing the Digital Surveillance Sensors (`sensors`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Delphi's Digital Surveillance Sensors Data

... <!-- TODO -->

**Note:** this repository was built to support modeling and forecasting efforts
surrounding seasonal influenza (and dengue).  In the current COVID-19 pandemic,
syndromic surveillance data, like ILI data (influenza-like illness) through
FluView, will likely prove very useful.  However, **we urge caution to users
examining the digital surveillance sensors**, like ILI Nearby, Google Flu
Trends, etc., during the COVID-19 pandemic, because these were designed to track
ILI as driven by seasonal influenza, and were NOT designed to track ILI during
the COVID-19 pandemic.


# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [region](../../labels/regions.txt)/[state](../../labels/states.txt) labels <!-- TODO: check --> |
| `names` | sensor names | `list` of string |

Notes:
* Names of open sensors (no `auth` token required): `sar3`, `epic`, `arch`
* Names of sensors requiring `auth` token: `twtr`, `gft`, `ght`, `ghtj`, `cdc`, `quid`, `wiki`

### Optional

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | sensor authentication tokens (currently restricted to 1); can be global or granular | `list` of string |

## Response

<!-- TODO: fix -->

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].name` | sensor name | string |
| `epidata[].location` | | string |
| `epidata[].epiweek` | | integer |
| `epidata[].value` | | float |
| `message` | `success` or error message | string |

# Example URLs

### Delphi's Digital Surveillance SAR3 Sensor on 2020w01 (national)
https://delphi.cmu.edu/epidata/api.php?source=sensors&names=sar3&locations=nat&epiweeks=202001

```json
{
  "result": 1,
  "epidata": [
    {
      "name": "sar3",
      "location": "nat",
      "epiweek": 202001,
      "value": 6.2407
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national Delphi's Digital Surveillance SAR3 Sensor data for epiweeks `201940` and `202001-202010` (11 weeks total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.sensors(callback, ['nat'], ['sar3'], [201940, Epidata.range(202001, 202010)])
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
  Epidata.sensors(callback, ['nat'], ['sar3'], [201940, Epidata.range(202001, 202010)]);
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
res = Epidata.sensors(['nat'], ['sar3'], [201940, Epidata.range(202001, 202010)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$sensors(list('nat'), list('sar3') list(201940, Epidata$range(202001, 202010)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
