---
title: <i>inactive</i> NIDSS Flu
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# NIDSS Flu

This is the documentation of the API for accessing the Taiwan National Infectious Disease Statistics System Flu (`nidss_flu`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## NIDSS Flu Data

Outpatient ILI from Taiwan's National Infectious Disease Statistics System (NIDSS).
 - Source: [Taiwan CDC](http://nidss.cdc.gov.tw/en/CDCWNH01.aspx?dc=wnh)
 - Temporal Resolution: Weekly* from 2008w14
 - Spatial Resolution: By [hexchotomy region](https://en.wikipedia.org/wiki/Regions_of_Taiwan#Hexchotomy) ([6+1](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/nidss_regions.txt))
 - Open access

\* Data is usually released on Tuesday

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/nidss_flu/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `regions` | regions | `list` of [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/nidss_regions.txt) labels |

### Optional

| Parameter | Description                                | Type               |
|-----------|--------------------------------------------|--------------------|
| `issues`  | issues                                     | `list` of epiweeks |
| `lag`     | # weeks between each epiweek and its issue | integer            |

Notes:
- If both `issues` and `lag` are specified, only `issues` is used.
If neither is specified, the current issues are used.

## Response

| Field                    | Description                                                     | Type             |
|--------------------------|-----------------------------------------------------------------|------------------|
| `result`                 | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`                | list of results                                                 | array of objects |
| `epidata[].release_date` | date when record was first published (yyyy-MM-dd)               | string           |
| `epidata[].region`       | region                                                          | string           |
| `epidata[].issue`        | epiweek of publication                                          | integer          |
| `epidata[].epiweek`      | epiweek during which the data was collected                     | integer          |
| `epidata[].lag`          | number of weeks between `epiweek` and `issue`                   | integer          |
| `epidata[].visits`       | total number of patients with ILI                               | integer          |
| `epidata[].ili`          | percent ILI                                                     | float            |
| `message`                | `success` or error message                                      | string           |

# Example URLs

### NIDSS Flu on 2015w01 (nationwide)
https://api.delphi.cmu.edu/epidata/nidss_flu/?regions=nationwide&epiweeks=201501

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

Libraries are available for [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js), [Python](https://pypi.org/project/delphi-epidata/), and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch national NIDSS Flu data for epiweeks `201440` and `201501-201510` (11 weeks total).

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.nidss_flu('nationwide', [201440, EpidataAsync.range(201501, 201510)]).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });;
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

# Source and Licensing

The full text of the NIDSS Flu license information is available on the Taiwan Digital Development Department's [website](https://data.gov.tw/license).