# About

This is the documentation of the API for accessing the Quidel (`quidel`) data source of
the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

## Quidel Data

Data provided by Quidel Corp., which contains flu lab test results.
 
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
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of `hhs<#>` [region](labels/regions.txt) labels |

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| ... | ... | ... | <!-- TODO -->
| `message` | `success` or error message | string |

# Example URLs

<!-- TODO: fix -->

# Code Samples

<!-- TODO: fix -->
