# About

This is the documentation of the API for accessing the Delphi's COVID-19
Surveillance Streams (`covidcast`) data source of the
[Delphi](https://delphi.cmu.edu/)'s epidemiological data. 

For an interactive visualization of many of these data signals, visit our 
[**COVIDcast site**](https://covidcast.cmu.edu).

General topics not specific to any particular data source are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Delphi's COVID-19 Surveillance Streams Data

Delphi's COVID-19 Surveillance Streams data includes the following data sources:
* `doctor-visits`: Data based on outpatient visits, provided to us by a national
health system.  Using this outpatient data, we estimate the percentage of
covid-related doctor's visits in a given location, on a given day.
* `fb-survey`: Data signal based on CMU-run symptom surveys, advertised through
Facebook.  These surveys are voluntary, and no individual survey responses are
shared back to Facebook. Using this survey data, we estimate the percentage of
people in a given location, on a given day that have CLI (covid-like illness =
fever, along with cough, or shortness of breath, or difficulty breathing), and
separately, that have ILI (influenza-like illness = fever, along with cough or
sore throat).
* `google-survey`: Data signal based on Google-run symptom surveys, through
their Opinions Reward app, and similar applications.  These surveys are again
voluntary.  They are just one question long, and ask "Do you know someone in
your community who is sick (fever, along with cough, or shortness of breath, or
difficulty breathing) right now?"  Using this survey data, we estimate the
percentage of people in a given location, on a given day, that know somebody who
has CLI (covid-like illness = fever, along with cough, or shortness of breath,
or difficulty breathing).  Note that this is tracking a different quantity than
the surveys through Facebook, and (unsurprisingly) the estimates here tend to be
much larger.
* `ght`: Data signal based on Google searches, provided to us by Google Health
Trends.  Using this search data, we estimate the volume of covid-related
searches in a given location, on a given day.  This signal is measured in
arbitrary units (its scale is meaningless).
* `quidel`: Data signal based on flu lab tests, provided to us by Quidel, Inc.
When a patient (whether at a doctor’s office, clinic, or hospital) has
covid-like symptoms, standard practice currently is to perform a flu test to
rule out seasonal flu (influenza), because these two diseases have similar
symptoms. Using this lab test data, we estimate the total number of flu tests
per medical device (a measure of testing frequency), and the percentage of flu
tests that are *negative* (since ruling out flu leaves open another
cause---possibly covid---for the patient's symptoms), in a given location, 
on a given day. 

The data is expected to be updated daily. You can use the
[`covidcast_meta`](covidcast_meta.md) endpoint to get summary information about
the ranges of the different attributes for the different data sources currently
in the data.

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `data_source` | name of upstream data source (e.g., `fb-survey`, `google-survey`, `ght`, `quidel`, `doctor-visits`) | string |
| `signal` | name of signal derived from upstream data (see notes below) | string |
| `time_type` | temporal resolution of the signal (e.g., `day`, `week`) | string |
| `geo_type` | spatial resolution of the signal (e.g., `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `time_values` | time unit (e.g., date) over which underlying events happened | `list` of time values (e.g., 20200401) |
| `geo_value` | unique code for each location, depending on `geo_type` (county -> FIPS 6-4 code, HRR -> HRR number, MSA -> CBSA code, DMA -> DMA code, state -> two-letter [state](../../labels/states.txt) code), or `*` for all | string |

As of this writing, data sources have the following signals:
* `fb-survey` `signal` values include `raw_cli`, `raw_ili`, `raw_wcli`,
  `raw_wili`, and also four additional named with `raw_*` replaced by
  `smoothed_*` (e.g. `smoothed_cli`, etc).
* `google-survey` `signal` values include `raw_cli` and `smoothed_cli`.
* `ght` `signal` values include `raw_search` and `smoothed_search`.
* `quidel` `signal` values include `smoothed_pct_negative` and `smoothed_tests_per_device`.
* `doctor-visits` `signal` values include `smoothed_cli`.

More generally, the current set of signals available for each data source is
returned by the [`covidcast_meta`](covidcast_meta.md) endpoint.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results, 1 per geo/time pair | array of objects |
| `epidata[].geo_value` | location code, depending on `geo_type` | string |
| `epidata[].time_value` | time unit (e.g. date) over which underlying events happened | integer |
| `epidata[].direction` | trend classifier (+1 -> increasing, 0 steady or not determined, -1 -> decreasing) | integer |
| `epidata[].value` | value (statistic) derived from the underlying data source | float |
| `epidata[].stderr` | standard error of the statistic with respect to its sampling distribution, `null` when not applicable | float |
| `epidata[].sample_size` | number of "data points" used in computing the statistic, `null` when not applicable | float |
| `message` | `success` or error message | string |

# Example URLs

### Delphi's COVID-19 Surveillance Streams from Facebook Survey CLI on 2020-04-06 to 2010-04-10 (county 06001)
https://delphi.cmu.edu/epidata/api.php?source=covidcast&data_source=fb-survey&signal=raw_cli&time_type=day&geo_type=county&time_values=20200406-20200410&geo_value=06001

```json
{
  "result": 1,
  "epidata": [
    {
      "geo_value": "06001",
      "time_value": 20200407,
      "direction": null,
      "value": 1.1293550689064,
      "stderr": 0.53185454111042,
      "sample_size": 281.0245
    },
    ...
  ],
  "message": "success"
}
```

### Delphi's COVID-19 Surveillance Streams from Facebook Survey CLI on 2020-04-06 (all counties)
https://delphi.cmu.edu/epidata/api.php?source=covidcast&data_source=fb-survey&signal=raw_cli&time_type=day&geo_type=county&time_values=20200406&geo_value=*

# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19 Surveillance Streams from Facebook Survey CLI for county 06001 and days `20200401` and `20200405-20200414` (11 days total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.covidcast(callback, 'fb-survey', 'raw_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
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
  Epidata.covidcast(callback, 'fb-survey', 'raw_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001');
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
res = Epidata.covidcast('fb-survey', 'raw_cli', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast('fb-survey', 'raw_cli', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
