---
title: COVIDcast API
has_children: true
nav_order: 1
---

# Delphi's COVIDcast API

This is the documentation of the API for accessing the Delphi's COVID-19
Surveillance Streams (`covidcast`) endpoint of
[Delphi](https://delphi.cmu.edu/)'s epidemiological data. This API provides the
data used in our public [COVIDcast map](https://covidcast.cmu.edu/), and
includes other data sources and signals not currently shown on the map. The API
allows users to select specific signals and download data for selected
geographical areas---counties, states, metropolitan statistical areas, and other
divisions.

This data is freely available under our [licensing](README.md#data-licensing)
terms; we encourage academic users to [cite](README.md#citing) the data if they
use it in any publications. Further documentation on Delphi's APIs is available
in the [API overview](README.md).

**For users:** Delphi operates a [mailing
list](https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api) for
users of the COVIDcast API. We will use the list to announce API changes,
corrections to data, and new features; API users may also use the mailing list
to ask general questions about its use. If you use the API, we strongly
encourage you to
[subscribe](https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api).

## The API

The COVIDcast API is based on HTTP GET queries and returns data in JSON form.
The base URL is https://delphi.cmu.edu/epidata/api.php.

Several [API clients are available](#api-clients) for common programming
languages, so you do not need to construct API calls yourself. Alternately, [see
below](#example-urls) for example API URLs and query responses.

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

### Data Signals

Currently, there are 8 data sources available in the API: `doctor-visits`,
`fb-survey`, `safegraph`, `google-survey`, `ght`, `quidel`,
`indicator-combination`, and `jhu-csse`. Each of these data sources has several
associated data signals: for example, for `doctor-visits`, includes
`smoothed_cli` and `smoothed_adj_cli`. A separate [COVIDcast signals
document](covidcast_signals.md) describes all available sources and signals.
Furthermore, our [COVIDcast site](https://covidcast.cmu.edu) provides an
interactive visualization of a select set of these data signals.

### Parameters

| Parameter | Description | Type |
| --- | --- | --- |
| `data_source` | name of upstream data source (e.g., `doctor-visits` or `fb-survey`; [see full list](covidcast_signals.md)) | string |
| `signal` | name of signal derived from upstream data (see notes below) | string |
| `time_type` | temporal resolution of the signal (e.g., `day`, `week`) | string |
| `geo_type` | spatial resolution of the signal (e.g., `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `time_values` | time unit (e.g., date) over which underlying events happened | `list` of time values (e.g., 20200401) |
| `geo_value` | unique code for each location, depending on `geo_type` (county -> FIPS 6-4 code, HRR -> HRR number, MSA -> CBSA code, DMA -> DMA code, state -> two-letter [state](../../labels/states.txt) code), or `*` for all | string |

The current set of signals available for each data source is returned by the
[`covidcast_meta`](covidcast_meta.md) endpoint.

### Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results, 1 per geo/time pair | array of objects |
| `epidata[].geo_value` | location code, depending on `geo_type` | string |
| `epidata[].time_value` | time unit (e.g. date) over which underlying events happened | integer |
| `epidata[].direction` | trend classifier (+1 -> increasing, 0 -> steady or not determined, -1 -> decreasing) | integer |
| `epidata[].value` | value (statistic) derived from the underlying data source | float |
| `epidata[].stderr` | approximate standard error of the statistic with respect to its sampling distribution, `null` when not applicable | float |
| `epidata[].sample_size` | number of "data points" used in computing the statistic, `null` when not applicable | float |
| `message` | `success` or error message | string |

**Note:** `result` code 2, "too many results", means that the number of results
you requested was greater than the API's maximum results limit. Results will be
returned, but not all of the results you requested. API clients should check the
results code, and should consider breaking up their requests across multiple API
calls, such as by breaking a request for a large time interval into multiple
requests for smaller time intervals.

## Example URLs

### Facebook Survey CLI on 2020-04-06 to 2010-04-10 (county 06001)

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

### Facebook Survey CLI on 2020-04-06 (all counties)

https://delphi.cmu.edu/epidata/api.php?source=covidcast&data_source=fb-survey&signal=raw_cli&time_type=day&geo_type=county&time_values=20200406&geo_value=*

```json
{
  "result": 1,
  "epidata": [
    {
      "geo_value": "01000",
      "time_value": 20200406,
      "direction": null,
      "value": 1.1693378,
      "stderr": 0.1909232,
      "sample_size": 1451.0327
    },
    ...
  ],
  "message": "success"
}
```
