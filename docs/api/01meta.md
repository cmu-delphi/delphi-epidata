---
title: <i>inactive</i> Epidata Metadata
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
permalink: api/meta.html
---

# Epidata Metadata

This is the documentation of the API for accessing the API Metadata (`meta`) for `fluview`, `twitter`, `wiki`,
and `delphi` endpoints of the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## API Metadata

... <!-- TODO -->

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/meta/>

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

None.

## Response

| Field     | Description                                                     | Type             |
|-----------|-----------------------------------------------------------------|------------------|
| `result`  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata` | list of results                                                 | array of objects |
| ...       | ...                                                             | ...              | <!-- TODO -->
| `message` | `success` or error message                                      | string           |

# Example URLs

<https://api.delphi.cmu.edu/epidata/meta/>

```json
{
  "result": 1,
  "epidata": [
    {
      "fluview": [
        {
          "latest_update": "2020-04-10",
          "latest_issue": 202014,
          "table_rows": 945920
        }
      ],
      "twitter": [
        {
          "latest_update": "2020-04-11",
          "num_states": 41,
          "table_rows": 132712
        }
      ],
      "wiki": [
        {
          "latest_update": "2020-04-12 07:00:00",
          "table_rows": 131585
        }
      ],
      "delphi": [
        {
          "system": "af",
          "first_week": 201541,
          "last_week": 201619,
          "num_weeks": 31
        },
        {
          "system": "eb",
          "first_week": 201441,
          "last_week": 201519,
          "num_weeks": 32
        },
        {
          "system": "ec",
          "first_week": 201441,
          "last_week": 202013,
          "num_weeks": 171
        },
        {
          "system": "sp",
          "first_week": 201441,
          "last_week": 201519,
          "num_weeks": 32
        },
        {
          "system": "st",
          "first_week": 201542,
          "last_week": 201949,
          "num_weeks": 123
        }
      ]
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch API metadata.

### R

```R
library(epidatr)
# Fetch data
res <- pub_meta()
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
res = epidata.pub_meta()
print(res)
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.meta().then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$meta()
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
res = Epidata.meta()
print(res['result'], res['message'], len(res['epidata']))
```
