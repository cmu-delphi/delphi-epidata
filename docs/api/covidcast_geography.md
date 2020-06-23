---
title: Geographic Coding
parent: COVIDcast API
nav_order: 4
---

# COVIDcast Geographic Coding

The `geo_value` field returned by the API specifies the geographic location
whose estimate is being reported. Estimates are available for several possible
`geo_type`s:

* `county`: County-level estimates are reported by the county's five-digit [FIPS
  code](https://en.wikipedia.org/wiki/FIPS_county_code). All FIPS codes are
  reported using pre-2015 FIPS code assignments, *except* for FIPS codes used by
  the `jhu-csse` source. These are reported exactly as JHU reports their data;
  [see below](#fips-exceptions-in-jhu-data).
* `hrr`: Hospital Referral Region, units designed to represent regional health
  care markets. There are roughly 300 HRRs in the United States. A map is
  available
  [here](https://hub.arcgis.com/datasets/fedmaps::hospital-referral-regions). We
  report HRRs by their number (non-consecutive, between 1 and 457).
* `msa`: Metropolitan Statistical Area, as defined by the Office of Management
  and Budget. The Census Bureau provides [detailed definitions of these
  regions](https://www.census.gov/programs-surveys/metro-micro/about.html). We
  report MSAs by their CBSA ID number.
* `dma`: Designated Market Areas represent geographic regions with their own
  media markets, as [defined by
  Nielsen](https://www.nielsen.com/us/en/intl-campaigns/dma-maps/).
* `state`: The 50 states, identified by their two-digit postal abbreviation (in
  lower case). Estimates for Puerto Rico are available as state `pr`; Washington, D.C. is available as state `dc`.

Some signals are not available for all `geo_type`s, since they may be reported
from their original sources with different levels of aggregation.

1. toc
{:toc}

## Small Sample Sizes and "Megacounties"

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


## FIPS Exceptions in JHU Data

At the County (FIPS) level, we report the data _exactly_ as JHU reports their
data, to prevent confusing public consumers of the data. JHU FIPS reporting
matches that used in the other signals, except for the following exceptions.

### New York City
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

### Kansas City, Missouri

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

### Dukes and Nantucket Counties, Massachusetts

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

### Mismatched FIPS Codes

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
