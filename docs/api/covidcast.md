# About

This is the documentation of the API for accessing the COVIDCast (`covidcast`)
data source of the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

## COVIDCast Data

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
| `name` | Data souce, and subtype if applicable (e.g. fb_survey_cli, fb_survey_ili) | string |
| `geo_type` | geographic resolution (e.g. `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `dates` | dates on which underlying events happened | `list` of dates |
| `geo_id` | a unique code for each location, depending on `geo_type` (county -> FIPS code, HRR -> HRR number, MSA -> CBSA code, DMA -> DMA code, state -> two-letter [state](../../labels/states.txt) code), or `*` for all | string |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results, 1 per date/geo-id pair | array of objects |
| `epidata[].date` | date (yyyy-MM-dd) | string |
| `epidata[].geo_id` | location id | string|
| `epidata[].direction` | trend classifier (+1 -> increasing, 0 stead or not determined, -1 -> decreasing) | integer |
| `epidata[].raw` | raw view of the data (e.g. contrast with `scaled`) | float |
| `epidata[].scaled` | view of the data centered and scaled relative to "normal" (mean = 0, standard deviation = 1)| float |
| `epidata[].sample_size` | number of "data points" used to produce the value in `raw`, `NULL` if not known or applicable | float |
| `epidata[].p_up` | | | <!-- TODO -->
| `epidata[].p_down` | | | <!-- TODO -->
| `message` | `success` or error message | string |

# Example URLs

### COVIDCast from Facebook Survey ILI on 2020-04-06 - 2010-04-10 (county 06001)
https://delphi.midas.cs.cmu.edu/epidata/api.php?source=covidcast&name=fb_survey-ili&geo_type=county&dates=20200406-20200410&geo_id=06001
```json
{
  "result": 1,
  "epidata": [
    {
      "date": "2020-04-06",
      "geo_id": "06001",
      "direction": 0,
      "raw": 0,
      "scaled": -1.5191456405295,
      "sample_size": 417.2392,
      "p_up": null,
      "p_down": null
    },
    ...
  ],
  "message": "success"
}
```

## CovidCast from Facebook Survey ILI on 2020-04-06 (all counties)
https://delphi.midas.cs.cmu.edu/epidata/api.php?source=covidcast&name=fb_survey-ili&geo_type=county&dates=20200406&geo_id=*


# Code Samples

No client support yet.
