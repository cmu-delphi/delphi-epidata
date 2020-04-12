# About

This is the documentation of the API for accessing the COVIDCast Metadata (`covidcast_meta`)
data source of the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

## COVIDCast Metadata

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
[CC-BY](https://creativecommons.org/licenses/by/4.0/). The `covid_survey_hrr_daily` endpoint
is known to wholly or partially serve data under this license.

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)


# The API

The base URL is: https://delphi.midas.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

None.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results, one per name/geo_type pair | array of objects |
| `epidata[].name` | Data souce, and subtype if applicable (e.g. fb_survey_cli, fb_survey_ili) | string |
| `epidata[].geo_type` | geographic resolution (e.g. `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `epidata[].min_date` | minimum date (yyyy-MM-dd) | string |
| `epidata[].max_date` | maximum date (yyyy-MM-dd) | string |
| `epidata[].num_locations` | number of locations | integer |
| `message` | `success` or error message | string |

# Example URLs

https://delphi.midas.cs.cmu.edu/epidata/api.php?source=covidcast_meta

```json
{
  "result": 1,
  "epidata": [
    {
      "name": "fb_survey-cli",
      "geo_type": "county",
      "min_date": "2020-04-06",
      "max_date": "2020-04-13",
      "num_locations": 555
    },
    {
      "name": "fb_survey-cli",
      "geo_type": "hrr",
      "min_date": "2020-04-06",
      "max_date": "2020-04-13",
      "num_locations": 292
    },
    ...
    {
      "name": "fb_survey-ili",
      "geo_type": "county",
      "min_date": "2020-04-06",
      "max_date": "2020-04-13",
      "num_locations": 555
    },
    ...
    {
      "name": "ght-raw_search",
      "geo_type": "dma",
      "min_date": "2020-02-20",
      "max_date": "2020-04-12",
      "num_locations": 210
    },
    ...
    {
      "name": "ght-smoothed_search",
      "geo_type": "dma",
      "min_date": "2020-02-20",
      "max_date": "2020-04-12",
      "num_locations": 210
    },
    ...
    {
      "name": "google-survey-cli",
      "geo_type": "county",
      "min_date": "2020-04-11",
      "max_date": "2020-04-14",
      "num_locations": 599
    }
  ],
  "message": "success"
}
```

# Code Samples

<!-- TODO: fix -->
