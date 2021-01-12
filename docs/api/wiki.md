---
title: Wikipedia Access
parent: Epidata API (Other Diseases)
---

# Wikipedia Access

This is the API documentation for accessing the Wikipedia Access (`wiki`)
endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Wikipedia Access Data

Number of page visits for selected English, Influenza-related wikipedia articles.
 - Source: [Wikimedia](https://dumps.wikimedia.org/other/pagecounts-raw/)
 - Temporal Resolution: Hourly, daily, and weekly from 2007-12-09 (2007w50)
 - Spatial Resolution: N/A
 - Other resolution: By article ([54](../../labels/articles.txt))
 - Open access

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `articles` | articles | list of [articles](../../labels/articles.md) |
| `language` | language (currently `en`, `es`, and `pt` supported) | string |
| `dates` | dates | `list` of dates |
| `epiweeks` | epiweeks | `list` of epiweeks |

Note:
- Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.

### Optional

| Parameter | Description | Type |
| --- | --- | --- |
| `hours` | hours | `list` of hours (0-23) |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].article` | | string |
| `epidata[].count` | | integer |
| `epidata[].total` | | integer |
| `epidata[].hour` | hour (-1 if `hour` not used) | integer |
| `epidata[].date` | date (yyyy-MM-dd) (only included if `date` used) | string |
| `epidata[].epiweek` | epiweek (only included if `epiweek` used) | integer |
| `epidata[].value` | | float |
| `message` | `success` or error message | string |

# Example URLs

### Wikipedia Access article "influenza" on 2020w01
https://delphi.cmu.edu/epidata/api.php?endpoint=wiki&language=en&articles=influenza&epiweeks=202001

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "count": 6516,
      "total": 663604044,
      "hour": -1,
      "epiweek": 202001,
      "value": 9.81910834
    }
  ],
  "message": "success"
}
```

### Wikipedia Access article "influenza" on date 2020-01-01
https://delphi.cmu.edu/epidata/api.php?endpoint=wiki&language=en&articles=influenza&dates=20200101

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "date": "2020-01-01",
      "count": 676,
      "total": 82359844,
      "hour": -1,
      "value": 8.20788344
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national Wikipedia Access data for article "influenza" on
epiweeks `201940` and `202001-202010` (11 weeks total) for hours 0 and 12 in English.

<!-- TODO: check syntax for optional arguments -->

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.fluview_clinical(callback, ['influenza'], undefined, [201940, Epidata.range(202001, 202010)], [0, 12])
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
  Epidata.fluview_clinical(callback, ['influenza'], null, [201940, Epidata.range(202001, 202010)], [0, 12]);
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
res = Epidata.wiki(['influenza'], None, [201940, Epidata.range(202001, 202010)], [0, 12])
print(res['result'], res['message'], len(res['epidata']))
````

Note:
- `dates`, `epiweeks`, and `hours` are `None` by default.
- `language` is `en` by default.

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$wiki(list('nat'), NULL, list(201940, Epidata$range(202001, 202010)), list(0, 12), 'en')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
