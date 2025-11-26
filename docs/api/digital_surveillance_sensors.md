---
title: <i>inactive</i> Digital Surveillance Sensors
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
permalink: api/sensors.html
---

# Digital Surveillance Sensors


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `sensors` |
| **Data Source** | Various digital data streams |
| **Geographic Coverage** | National, HHS regions, Census divisions, and US states (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| **Temporal Resolution** | Weekly (Epiweek) |
| **Update Frequency** | Inactive - No longer updated |
| **License** | [CC BY](https://creativecommons.org/licenses/by/4.0/) |

<!-- | **Earliest Date** | Variable | -->

This is the documentation of the API for accessing the Digital Surveillance Sensors (`sensors`) endpoint of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

{: .note}
> **Note:** this repository was built to support modelling and forecasting efforts
> surrounding seasonal influenza (and dengue).  In the current COVID-19 pandemic,
> syndromic surveillance data, like ILI data (influenza-like illness) through
> FluView, will likely prove very useful.  However, **we urge caution to users
> examining the digital surveillance sensors**, like ILI Nearby, Google Flu
> Trends, etc., during the COVID-19 pandemic, because these were designed to track
> ILI as driven by seasonal influenza, and were NOT designed to track ILI during
the COVID-19 pandemic.


# The API

The base URL is: https://api.delphi.cmu.edu/epidata/sensors/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of location codes: `nat`, HHS regions, Census divisions, or state codes (see [Geographic Codes](geographic_codes.html#us-regions-and-states)) |
| `names` | sensor names | `list` of string |

{: .note}
> **Notes:**
> * Names of open sensors (no `auth` token required): `sar3`, `epic`, `arch`
> * Names of sensors requiring `auth` token: `twtr`, `gft`, `ght`, `ghtj`, `cdc`, `quid`, `wiki`

### Optional

| Parameter | Description                                                                         | Type             |
|-----------|-------------------------------------------------------------------------------------|------------------|
| `auth`    | sensor authentication tokens (currently restricted to 1); can be global or granular | `list` of string |

## Response

| Field                | Description                                                     | Type             |
|----------------------|-----------------------------------------------------------------|------------------|
| `result`             | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`            | list of results                                                 | array of objects |
| `epidata[].name`     | sensor name                                                     | string           |
| `epidata[].location` |                                                                 | string           |
| `epidata[].epiweek`  |                                                                 | integer          |
| `epidata[].value`    |                                                                 | float            |
| `message`            | `success` or error message                                      | string           |

# Example URLs

### Delphi's Digital Surveillance SAR3 Sensor on 2020w01 (national)
https://api.delphi.cmu.edu/epidata/sensors/?auth=...&names=sar3&locations=nat&epiweeks=202001

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

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch national Delphi's Digital Surveillance SAR3 Sensor data for epiweeks `201501-202001`.


### R

```R
library(epidatr)
# Fetch data
res <- pvt_sensors(auth = 'SECRET_API_AUTH_SENSORS', locations = 'nat', 
names = 'sar3', epiweeks = epirange(201501, 202001))
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
res = epidata.sensors(['nat'], ['sar3'], EpiRange(201501, 202001))
print(res['result'], res['message'], len(res['epidata']))
```

### JavaScript (in a web browser)

The JavaScript client is available [here](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js).

```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.sensors('nat', 'sar3', EpidataAsync.range(201501, 202001)).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```

### Legacy Clients

We recommend using our modern client libraries: [epidatr](https://cmu-delphi.github.io/epidatr/) for R and [epidatpy](https://cmu-delphi.github.io/epidatpy/) for Python. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/) and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).

#### R (Legacy)

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$sensors(locations = list("nat"), sensors = list("sar3"), epiweeks = Epidata$range(201501, 202001))
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
res = Epidata.sensors(['nat'], ['sar3'], Epidata.range(201501, 202001))
print(res['result'], res['message'], len(res['epidata']))
```
