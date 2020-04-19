# About

This is the documentation of the API for accessing the Delphi's COVID-19 Surveillance Streams Metadata (`covidcast_meta`)
data source of the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

## Delphi's COVID-19 Surveillance Streams Metadata

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
[CC-BY](https://creativecommons.org/licenses/by/4.0/). The `covidcast_meta` endpoint
is known to wholly or partially serve data under this license.

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)


# The API

The base URL is: https://delphi.midas.cs.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

None.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results, one per name/geo_type pair | array of objects |
| `epidata[].data_source` | data souce | string |
| `epidata[].time_type` | temporal resolution of the signal (e.g., `day`, `week`) | string |
| `epidata[].geo_type` | geographic resolution (e.g. `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `epidata[].min_time` | minimum time (e.g., 20200406) | integer |
| `epidata[].max_time` | maximum time (e.g., 20200413) | integer |
| `epidata[].num_locations` | number of locations | integer |
| `message` | `success` or error message | string |

# Example URLs

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=covidcast_meta

```json
{
  "result": 1,
  "epidata": [
    {
      "data_source": "fb_survey",
      "signal": "cli",
      "time_type": "day",
      "geo_type": "county",
      "min_time": 20200406,
      "max_time": 20200413,
      "num_locations": 555,
      "min_value": 0,
      "max_value": 5.0805650596568
    },
    ...
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [CoffeeScript](../../src/client/delphi_epidata.coffee), [JavaScript](../../src/client/delphi_epidata.js), [Python](../../src/client/delphi_epidata.py), and [R](../../src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19 Surveillance Streams metadata.

### CoffeeScript (in Node.js)

````coffeescript
# Import
{Epidata} = require('./delphi_epidata')
# Fetch data
callback = (result, message, epidata) ->
  console.log(result, message, epidata?.length)
Epidata.covidcast_meta(callback)
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
  Epidata.covidcast_meta(callback);
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
res = Epidata.covidcast_meta()
print(res['result'], res['message'], len(res['epidata']))
````

### R

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast_meta()
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
