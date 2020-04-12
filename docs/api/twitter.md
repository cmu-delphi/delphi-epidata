# About

This is the documentation of the API for accessing the Twitter Stream (`twitter`) data source of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

## Twitter Stream Data

Estimate of influenza activity based on analysis of language used in tweets.
 - Data source: [HealthTweets](http://www.healthtweets.org/)
 - Temporal Resolution: Daily and weekly from 2011-12-01 (2011w48)
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), and [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](labels/regions.txt)); and by state/territory ([51](labels/states.txt))
 - Restricted access: Delphi doesn't have permission to share this dataset

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

The data surfaced through this API is just a carefully curated mirror of data acquired from .... <!-- TODO -->
It is subject to its original licensing, .... <!-- TODO -->

# The API

The base URL is: https://delphi.midas.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `locations` | locations | `list` of [region](labels/regions.txt)/[state](labels/states.txt) labels |
| `dates` | dates | `list` of dates |
| `epiweeks` | epiweeks | `list` of epiweeks |

Note:
- Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| ... | ... | ... | <!-- TODO -->
| `message` | `success` or error message | string |

# Example URLs

### Twitter on 2015w01 (national)
https://delphi.cmu.edu/epidata/api.php?source=twitter&auth=...&locations=nat&epiweeks=201501

```json
{
  "result":1,
  "epidata":[...],
  "message":"success"
}
```

<!-- TODO: fix -->

# Code Samples

<!-- TODO: fix -->
