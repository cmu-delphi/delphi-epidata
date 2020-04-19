# About

This is the documentation of the API for accessing the Delphi's COVID-19 Surveillance Streams (`covidcast`)
data source of the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

## Delphi's COVID-19 Surveillance Streams Data

... <!-- TODO -->

## Contributing

If you are interested in contributing:

- For development of the API itself, see the
  [development guide](docs/epidata_development.md).
- To suggest changes, additions, or other ways to improve,
  [open an issue](https://github.com/cmu-delphi/delphi-epidata/issues/new)
  describing your idea.

## Citing

We hope that this API is useful to others outside of our group, especially for
epidemiological and other scientific research. If you use this API and would
like to cite it, we would gratefully recommend the following copy:

> David C. Farrow,
> Logan C. Brooks,
> Aaron Rumack,
> Ryan J. Tibshirani,
> Roni Rosenfeld
> (2015).
> _Delphi Epidata API_.
> https://github.com/cmu-delphi/delphi-epidata

## Data licensing

Any data which is produced novelly by Delphi and is intentionally and openly
surfaced by Delphi through this API is hereby licensed
[CC-BY](https://creativecommons.org/licenses/by/4.0/). The `covidcast` endpoint
is known to wholly or partially serve data under this license.

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)


# The API

The base URL is: https://delphi.midas.cs.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `data_source` | name of upstream data souce | string |
| `signal` | name of signal derived from upstream data | string |
| `time_type` | temporal resolution of the signal (e.g., `day`, `week`) | string |
| `geo_type` | spatial resolution of the signal (e.g., `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `time_values` | time unit (e.g., date) over which underlying events happened | `list` of time values (e.g., 20200401) |
| `geo_value` | unique code for each location, depending on `geo_type` (county -> FIPS 6-4 code, HRR -> HRR number, MSA -> CBSA code, DMA -> DMA code, state -> two-letter [state](../../labels/states.txt) code), or `*` for all | string |

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

### Delphi's COVID-19 Surveillance Streams from Facebook Survey ILI on 2020-04-06 - 2020-04-10 (county 06001)
https://delphi.midas.cs.cmu.edu/epidata/api.php?source=covidcast&data_source=fb_survey&signal=ili&time_type=day&geo_type=county&time_values=20200406-20200410&geo_value=06001
```json
{
  "result": 1,
  "epidata": [
    {
      "geo_value": "06001",
      "time_value": 20200406,
      "direction": 0,
      "value": 0,
      "stderr": null,
      "sample_size": 417.2392
    },
    ...
  ],
  "message": "success"
}
```

## Delphi's COVID-19 Surveillance Streams from Facebook Survey ILI on 2020-04-06 (all counties)
https://delphi.midas.cs.cmu.edu/epidata/api.php?source=covidcast&data_source=fb_survey&signal=ili&time_type=day&geo_type=county&time_values=20200406&geo_value=*

# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19 Surveillance Streams from Facebook Survey ILI for county 06001 and days `20200401` and `20200405-20200414` (11 days total).

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.covidcast(callback, 'fb_survey', 'ili', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
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
  Epidata.covidcast(callback, 'fb_survey', 'ili', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001');
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
res = Epidata.covidcast('fb_survey', 'ili', 'day', 'county', [20200401, Epidata.range(20200405, 20200414)], '06001')
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast('fb_survey', 'ili', 'day', 'county', list(20200401, Epidata$range(20200405, 20200414)), '06001')
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
