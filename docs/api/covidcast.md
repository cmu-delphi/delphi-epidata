# Delphi's COVIDcast API

This is the documentation of the API for accessing the Delphi's COVID-19
Surveillance Streams (`covidcast`) endpoint of
[Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular data source are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

### Data Signals

Currently, there are 7 data sources available in the API: `doctor-visits`,
`fb-survey`, `google-survey`, `ght`, `quidel`, `indicator-combination`, and
`jhu-csse`. Each of these data sources has several associated data signals: for
example, for `doctor-visits`, includes `smoothed_cli` and `smoothed_adj_cli`.  A
separate [COVIDcast signals document](covidcast_signals.md) describes all
available sources and signals. Furthermore, our [COVIDcast
site](https://covidcast.cmu.edu) provides an interactive visualization of a
select set of these data signals.

### Parameters

#### Required

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

#### Optional

The default API behavior is to return the most recently issued value for each `time_value` selected.

We also provide access to previous versions of data using the optional parameters below.

| Parameter | Description | Type |
| --- | --- | --- |
| `as_of` | maximum time unit (e.g., date) when the signal data were published (return most recent for each `time_value`) | time value (e.g., 20200401) |
| `issues` | time unit (e.g., date) when the signal data were published (return all matching records for each `time_value`) | `list` of time values (e.g., 20200401) |
| `lag` | time delta (e.g. days) between when the underlying events happened and when the data were published | integer |

Use cases:

* To pretend like you queried the API on June 1, such that the returned results
  do not include any updates which became available after June 1, use
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

NB: Each issue in the versioning system contains only the records that were
added or updated during that time unit; we exclude records whose values remain
the same as a previous issue. If you have a research problem that would require
knowing when an unchanged value was last confirmed, please get in touch.

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
| `epidata[].issue` | time unit (e.g. date) when this statistic was published | integer |
| `epidata[].lag` | time delta (e.g. days) between when the underlying events happened and when this statistic was published | integer |
| `message` | `success` or error message | string |

**Note:** `result` code 2, "too many results", means that the number of results
you requested was greater than the API's maximum results limit. Results will be
returned, but not all of the results you requested. API clients should check the
results code, and should consider breaking up their requests across multiple API
calls, such as by breaking a request for a large time interval into multiple
requests for smaller time intervals.


## Geographic Coding

The `geo_value` field specifies the geographic location whose estimate is being
reported. County-level estimates are reported by the county FIPS code. All FIPS
codes are reported using pre-2015 FIPS code assignments, *except* for FIPS codes
used by the `jhu-csse` source. These are reported exactly as JHU reports their
data; see below.

Other possible `geo_type`s include:

* `hrr`: Hospital Referral Region, units designed to represent regional health
  care markets. There are roughly 300 HRRs in the United States. A map is
  available
  [here](https://hub.arcgis.com/datasets/fedmaps::hospital-referral-regions).
* `msa`: Metropolitan Statistical Area, as defined by the Office of Management
  and Budget. The Census Bureau provides [detailed definitions of these
  regions](https://www.census.gov/programs-surveys/metro-micro/about.html).
* `dma`: Designated Market Areas represent geographic regions with their own
  media markets, as [defined by
  Nielsen](https://www.nielsen.com/us/en/intl-campaigns/dma-maps/).
* `state`: The 50 states.

Some signals are not available for all `geo_type`s, since they may be reported
from their original sources with different levels of aggregation.

### Small Sample Sizes and "Megacounties"

Most sources do not report the same amount of data for every county; for
example, the survey sources rely on survey responses each day, and many counties
may have comparatively few survey responses. We do not report individual county
estimates when small sample sizes would make estimates unreliable or would allow
identification of respondents, violating privacy and confidentiality agreements.
Additional considerations for specific signals are discussed in the [source and
signal documentation](covidcast_signals.md).

In each state, we collect together the data from all counties with insufficient
data to be individually reported. These counties are combined into a single
"megacounty". For example, if only five counties in a state have sufficient data
to be reported, the remaining counties will form one megacounty representing the
rest of that state. As sample sizes vary from day to day, the counties composing
the megacounty can vary daily; the geographic area covered by the megacounty is
simply the state minus the counties reported for that day.

Megacounty estimates are reported with a FIPS code ending with 000, which is
never a FIPS code for a real county. For example, megacounty estimates for the
state of New York are reported with FIPS code 36000, since 36 is the FIPS code
prefix for New York.


### FIPS Exceptions in JHU Data

At the County (FIPS) level, we report the data _exactly_ as JHU reports their
data, to prevent confusing public consumers of the data. JHU FIPS reporting
matches that used in the other signals, except for the following exceptions.

#### New York City
New York City comprises of five boroughs:

|Borough Name       |County Name        |FIPS Code      |
|-------------------|-------------------|---------------|
|Manhattan          |New York County    |36061          |
|The Bronx          |Bronx County       |36005          |
|Brooklyn           |Kings County       |36047          |
|Queens             |Queens County      |36081          |
|Staten Island      |Richmond County    |36085          |

**Data from all five boroughs are reported under New York County,
FIPS Code 36061.**  The other four boroughs are included in the dataset
and show up in our API, but they should be uniformly zero.

All NYC counts are mapped to the MSA with CBSA ID 35620, which encompasses all
five boroughs. All NYC counts are mapped to HRR 303, which intersects all five
boroughs (297 also intersects the Bronx, 301 also intersects Brooklyn and
Queens, but absent additional information, we chose to leave all counts in 303).

#### Kansas City, Missouri

Kansas City intersects the following four counties, which themselves report
confirmed case and deaths data:

|County Name        |FIPS Code      |
|-------------------|---------------|
|Jackson County     |29095          |
|Platte County      |29165          |
|Cass County        |29037          |
|Clay County        |29047          |

**Data from Kansas City is given its own dedicated line, with FIPS
code 70003.**  This is how JHU encodes their data.  However, the data in
the four counties that Kansas City intersects is not necessarily zero.

For the mapping to HRR and MSA, the counts for Kansas City are dispersed to
these four counties in equal proportions.

#### Dukes and Nantucket Counties, Massachusetts

**The counties of Dukes and Nantucket report their figures together,
and we (like JHU) list them under FIPS Code 70002.**  Here are the FIPS codes
for the individual counties:

|County Name        |FIPS Code      |
|-------------------|---------------|
|Dukes County       |25007          |
|Nantucket County   |25019          |

For the mapping to HRR and MSA, the counts for Dukes and Nantucket are
dispersed to the two counties in equal proportions.

The data in the individual counties is expected to be zero.

#### Mismatched FIPS Codes

Finally, there are two FIPS codes that were changed in 2015 (see the [Census
Bureau
documentation](https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.html)),
leading to mismatch between us and JHU. We report the data using the FIPS code
used by JHU, again to promote consistency and avoid confusion by external users
of the dataset. For the mapping to MSA, HRR, these two counties are included
properly.

|County Name        |State          |"Our" FIPS         |JHU FIPS       |
|-------------------|---------------|-------------------|---------------|
|Oglala Lakota      |South Dakota   |46113              |46102          |
|Kusilvak           |Alaska         |02270              |02158          |

## Example URLs

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

## Code Samples

Libraries are available for
[CoffeeScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.coffee),
[JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.js),
[Python](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.py),
and
[R](https://github.com/cmu-delphi/delphi-epidata/blob/master/src/client/delphi_epidata.R).
The following samples show how to import the library and fetch Delphi's COVID-19
Surveillance Streams from Facebook Survey CLI for county 06001 and days
`20200401` and `20200405-20200414` (11 days total).

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

Optionally install the [package from PyPI](https://pypi.org/project/delphi-epidata/) using pip(env):
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
