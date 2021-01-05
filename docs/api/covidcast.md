---
title: COVIDcast Epidata API
has_children: true
nav_order: 1
---

# COVIDcast Epidata API

This is the documentation for accessing Delphi's COVID-19 indicators via the `covidcast` endpoint of [Delphi](https://delphi.cmu.edu/)'s
epidemiological data API. This API provides data on the spread and impact of the COVID-19 pandemic across the United States, most of which is available at the
county level and updated daily. This data powers our public [COVIDcast
map](https://covidcast.cmu.edu/) which includes testing, cases, and death data,
as well as unique healthcare and survey data Delphi acquires through its
partners. The API allows users to select specific signals and download data for
selected geographical areas---counties, states, metropolitan statistical areas,
and other divisions.


<div style="background-color:#FCC; padding: 10px 30px;"><strong>Get
updates:</strong> Delphi operates a <a
href="https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api">mailing
list</a> for users of the COVIDcast API. We will use the list to announce API
changes, corrections to data, and new features; API users may also use the
mailing list to ask general questions about its use. If you use the API, we
strongly encourage you to <a
href="https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api">subscribe</a>.
</div>

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Licensing
Like all other Delphi Epidata datasets, our COVIDcast data is freely available to the public. However, our COVID-19 indicators include data from many different sources, with data licensing handled separately for each source. For a summary of the licenses used and a list of the indicators each license applies to, we suggest users visit our [COVIDcast licensing](covidcast_licensing.md) page. Licensing information is also summarized on each indicator's details page.
We encourage academic users to [cite](README.md#citing) the data if they
use it in any publications. Our [data ingestion
code](https://github.com/cmu-delphi/covidcast-indicators) and [API server
code](https://github.com/cmu-delphi/delphi-epidata) is open-source, and
contributions are welcome. Further documentation on Delphi's APIs is available
in the [API overview](README.md).

## Accessing the Data

Our [COVIDcast site](https://covidcast.cmu.edu) provides an interactive
visualization of a select set of the data signals available in the COVIDcast
API, and provides a data export feature to download any data range as a
CSV file.

Several [API clients are available](covidcast_clients.md) for common programming
languages, so you do not need to construct API calls yourself to obtain
COVIDcast data. Once you install the appropriate client for your programming
language, accessing data is as easy as, in [R](https://www.r-project.org/):

```r
library(covidcast)

data <- covidcast_signal("fb-survey", "smoothed_cli", start_day = "2020-05-01",
                         end_day = "2020-05-07")
```

or, in [Python](https://www.python.org):

```python
import covidcast
from datetime import date

data = covidcast.signal("fb-survey", "smoothed_cli", date(2020, 5, 1), date(2020, 5, 7),
                        "county")
```

[The API clients](covidcast_clients.md) have extensive documentation providing
further examples.

Alternately, to construct URLs and parse responses to access data manually, [see
below](#constructing-api-queries) for details.

## Data Sources and Signals

The API provides multiple data sources, each with several signals. Each source
represents one provider of data, such as a medical testing provider or a symptom
survey, and each signal represents one quantity computed from data provided by
that source. Our sources provide detailed data about COVID-related topics,
including confirmed cases, symptom-related search queries, hospitalizations,
outpatient doctor's visits, and other sources. Many of these are publicly
available *only* through the COVIDcast API.

The [signals documentation](covidcast_signals.md) describes all available
sources and signals.

## Constructing API Queries

The COVIDcast API is based on HTTP GET queries and returns data in JSON form.
The base URL is `https://api.covidcast.cmu.edu/epidata/api.php`.  The covidcast
endpoint is `https://api.covidcast.cmu.edu/epidata/api.php?source=covidcast`.

See [this documentation](README.md) for details on specifying epiweeks, dates,
and lists.

### Query Parameters

#### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `data_source` | name of upstream data source (e.g., `doctor-visits` or `fb-survey`; [see full list](covidcast_signals.md)) | string |
| `signal` | name of signal derived from upstream data (see notes below) | string |
| `time_type` | temporal resolution of the signal (e.g., `day`, `week`; see [date coding details](covidcast_times.md)) | string |
| `geo_type` | spatial resolution of the signal (e.g., `county`, `hrr`, `msa`, `dma`, `state`) | string |
| `time_values` | time unit (e.g., date) over which underlying events happened | `list` of time values (e.g., 20200401) |
| `geo_value` | unique code for each location, depending on `geo_type` (see [geographic coding details](covidcast_geography.md)), or `*` for all | string |

The current set of signals available for each data source is returned by the
[`covidcast_meta`](covidcast_meta.md) endpoint.

#### Optional

Estimates for a specific `time_value` and `geo_value` are sometimes updated
after they are first published. Many of our data sources issue corrections or
backfill estimates as data arrives; see the [documentation for each source](covidcast_signals.md)
for details.

The default API behavior is to return the most recently issued value for each
`time_value` selected.

We also provide access to previous versions of data using the optional query
parameters below.

| Parameter | Description | Type |
| --- | --- | --- |
| `as_of` | maximum time unit (e.g., date) when the signal data were published (return most recent for each `time_value`) | time value (e.g., 20200401) |
| `issues` | time unit (e.g., date) when the signal data were published (return all matching records for each `time_value`) | `list` of time values (e.g., 20200401) |
| `lag` | time delta (e.g. days) between when the underlying events happened and when the data were published | integer |

Use cases:

* To pretend like you queried the API on June 1, such that the returned results
  do not include any updates that became available after June 1, use
  `as_of=20200601`.
* To retrieve only data that was published or updated on June 1, and exclude
  records whose most recent update occured earlier than June 1, use
  `issues=20200601`.
* To retrieve all data that was published between May 1 and June 1, and exclude
  records whose most recent update occured earlier than May 1, use
  `issues=20200501-20200601`. The results will include all matching issues for
  each `time_value`, not just the most recent.
* To retrieve only data that was published or updated exactly 3 days after the
  underlying events occurred, use `lag=3`.

You should specify only one of these three parameters in any given query.

**Note:** Each issue in the versioning system contains only the records added or updated during that time unit; we exclude records whose values
remain the same as a previous issue. If you have a research problem that would
require knowing when we last confirmed an unchanged value, please get in touch.

### Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results, 1 per geo/time pair | array of objects |
| `epidata[].geo_value` | location code, depending on `geo_type` | string |
| `epidata[].time_value` | time unit (e.g. date) over which underlying events happened (see [date coding details](covidcast_times.md)) | integer |
| `epidata[].direction` | trend classifier (+1 -> increasing, 0 -> steady or not determined, -1 -> decreasing) | integer |
| `epidata[].value` | value (statistic) derived from the underlying data source | float |
| `epidata[].stderr` | approximate standard error of the statistic with respect to its sampling distribution, `null` when not applicable | float |
| `epidata[].sample_size` | number of "data points" used in computing the statistic, `null` when not applicable | float |
| `epidata[].issue` | time unit (e.g. date) when this statistic was published | integer |
| `epidata[].lag` | time delta (e.g. days) between when the underlying events happened and when this statistic was published | integer |
| `message` | `success` or error message | string |

**Note:** `result` code 2, "too many results", means that the number of results
you requested was greater than the API's maximum results limit. Results will be
returned, but not all of the results you requested. API clients should check the
results code and consider breaking up requests for e.g. large time intervals into multiple
API calls.

## Example URLs

### Facebook Survey CLI on 2020-04-06 to 2010-04-10 (county 06001)

https://api.covidcast.cmu.edu/epidata/api.php?source=covidcast&data_source=fb-survey&signal=smoothed_cli&time_type=day&geo_type=county&time_values=20200406-20200410&geo_value=06001

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

https://api.covidcast.cmu.edu/epidata/api.php?source=covidcast&data_source=fb-survey&signal=smoothed_cli&time_type=day&geo_type=county&time_values=20200406&geo_value=*

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
