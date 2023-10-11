---
title: ILI Nearby Nowcast
parent: Other Endpoints (COVID-19 and Other Diseases)
---

# ILI Nearby Nowcast

This is the documentation of the API for accessing the ILI Nearby (`nowcast`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## ILI Nearby Data

A nowcast of U.S. national, regional, and state-level (weighted) %ILI, available seven days (regionally) or five days (state-level) before the first ILINet report for the corresponding week.
 - Source: [Delphi's ILI Nearby system](https://delphi.cmu.edu/nowcast/)
 - Temporal Resolution: Weekly, from 2010w30*
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt)), and by state/territory ([51](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt))
 - Open access

\* Data is usually released on Friday and updated on Sunday and Monday

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/nowcast/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt)/[state](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt) labels |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].location` |                                                                 | string           |
| `epidata[].epiweek`  |                                                                 | integer          |
| `epidata[].value`    |                                                                 | float            |
| `epidata[].std`      |                                                                 | float            |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### ILI Nearby on 2020w01 (national)
https://api.delphi.cmu.edu/epidata/nowcast/?locations=nat&epiweeks=202001

```json
{
  "result": 1,
  "epidata": [
    {
      "location": "nat",
      "epiweek": 202001,
      "value": 6.08239,
      "std": 0.12595
    }
  ],
  "message": "success"
}
```


# Code Samples

Libraries are available for [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js), [Python](https://pypi.org/project/delphi-epidata/), and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national ILI Nearby data for epiweeks `201940` and `202001-202010` (11 weeks total).

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.nowcast('nat', [201940, EpidataAsync.range(202001, 202010)]).then((res) => {
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
res = Epidata.nowcast(['nat'], [201940, Epidata.range(202001, 202010)])
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$nowcast(list('nat'), list(201940, Epidata$range(202001, 202010)))
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
