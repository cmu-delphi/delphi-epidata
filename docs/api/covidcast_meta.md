---
title: Metadata
parent: COVIDcast Main Endpoint
nav_order: 6
---

# COVIDcast Metadata

The COVIDcast metadata endpoint (endpoint `covidcast_meta`) provides a list of all
sources and signals available in the API, along with basic summary statistics
such as the dates they are available, their minimum and maximum values, and the
geographic levels at which they are reported.

## The API

The base URL is: https://api.covidcast.cmu.edu/epidata/covidcast_meta/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

### Parameters

None required.

### Response

| Field                     | Description                                                         | Type             |
|---------------------------|---------------------------------------------------------------------|------------------|
| `result`                  | result code: 1 = success, 2 = too many results, -2 = no results     | integer          |
| `epidata`                 | list of results, one per name/geo_type filter                       | array of objects |
| `epidata[].data_source`   | data source                                                         | string           |
| `epidata[].signal`        | signal name                                                         | string           |
| `epidata[].time_type`     | temporal resolution of the signal (e.g., `day`, `week`)             | string           |
| `epidata[].geo_type`      | geographic resolution (e.g. `county`, `hrr`, `msa`, `dma`, `state`) | string           |
| `epidata[].min_time`      | minimum observation time (e.g., 20200406)                           | integer          |
| `epidata[].max_time`      | maximum observation time (e.g., 20200413)                           | integer          |
| `epidata[].num_locations` | number of distinct geographic locations with data                   | integer          |
| `epidata[].min_value`     | minimum value                                                       | float            |
| `epidata[].max_value`     | maximum value                                                       | float            |
| `epidata[].mean_value`    | mean of value                                                       | float            |
| `epidata[].stdev_value`   | standard deviation of value                                         | float            |
| `epidata[].max_issue`     | most recent date data was issued (e.g., 20200710)                   | integer          |
| `epidata[].min_lag`       | smallest lag from observation to issue, in `time_type` units        | integer          |
| `epidata[].max_lag`       | largest lag from observation to issue, in `time_type` units         | integer          |
| `message`                 | `success` or error message                                          | string           |

## Example URLs

https://api.covidcast.cmu.edu/epidata/covidcast_meta/

```json
{
  "result": 1,
  "epidata": [
  {
      "data_source": "doctor-visits",
      "signal": "smoothed_adj_cli",
      "last_update": 1592707979,
      "stdev_value": 2.6647410028331,
      "num_locations": 2500,
      "time_type": "day",
      "max_value": 87.190476,
      "mean_value": 1.4439366759191,
      "geo_type": "county",
      "min_value": 0,
      "max_time": 20200617,
      "min_time": 20200201
    },
    ...
  ],
  "message": "success"
}
```

## Code Samples

Libraries are available for [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/main/src/client/delphi_epidata.js), [Python](https://pypi.org/project/delphi-epidata/), and [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19 Surveillance Streams metadata.

### JavaScript (in a web browser)

````html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.covidcast_meta().then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
````

### Python

Python users seeking to use the COVIDcast API to fetch data should instead
consider using the [dedicated API client](covidcast_clients.md), which provides
a `metadata()` method to return metadata as a data frame.

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

R users seeking to use the COVIDcast API to fetch data should instead consider
using the [dedicated API client](covidcast_clients.md), which provides a
`covidcast_meta()` function to return metadata as a data frame.

````R
# Import
source('delphi_epidata.R')
# Fetch data
res <- Epidata$covidcast_meta()
cat(paste(res$result, res$message, length(res$epidata), "\n"))
````
