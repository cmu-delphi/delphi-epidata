---
title: Geographic Coding
parent: COVIDcast Epidata API
nav_order: 4
---

# COVIDcast Geographic Coding
{: .no_toc}

The `geo_value` field returned by the API specifies the geographic location
whose estimate is being reported. Estimates are available for several possible
`geo_type`s:

* `county`: County-level estimates are labeled with the county's five-digit [FIPS
  code](https://en.wikipedia.org/wiki/FIPS_county_code). All FIPS codes are
  reported using pre-2015 FIPS code assignments, *except* for FIPS codes used by
  the `jhu-csse` and `usa-facts` sources. These are reported exactly as the
  sources report their data; [see below](#coding-exceptions). FIPS codes ending
  in `000` are not valid counties, and instead represent "megacounties" we
  construct; [see below](#small-sample-sizes-and-megacounties).
* `hrr`: Hospital Referral Region, units designed to represent regional health
  care markets. There are roughly 300 HRRs in the United States. A map is
  available
  [here](https://hub.arcgis.com/datasets/fedmaps::hospital-referral-regions). We
  report HRRs by their number (non-consecutive, between 1 and 457).
* `hhs`:  values that are accepted are the numbers 1-10, corresponding to the US [Department of Health & Human Services Regional Offices](https://www.hhs.gov/about/agencies/iea/regional-offices/index.html)
* `msa`: Metropolitan Statistical Area, as defined by the Office of Management
  and Budget. The Census Bureau provides [detailed definitions of these
  regions](https://www.census.gov/programs-surveys/metro-micro/about.html). We
  report MSAs by their CBSA ID number.
* `dma`: Designated Market Areas represent geographic regions with their own
  media markets, as [defined by
  Nielsen](https://www.nielsen.com/us/en/intl-campaigns/dma-maps/).
* `state`: The 50 states, identified by their two-digit postal abbreviation (in
  lower case). Estimates for Puerto Rico are available as state `pr`;
  Washington, D.C. is available as state `dc`.
* `nation`: accepted values are the ISO 3166-1 alpha-2 [country codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). Currently the only nation we have data on is `us`.

Some signals are not available for all `geo_type`s since they may be reported
by their original sources at geographic resolutions which are too coarse.

## Table of contents
{: .no_toc .text-delta}

1. toc
{:toc}

## Small Sample Sizes and "Megacounties"

Most sources do not report the same amount of data for every county; for
example, since the survey sources rely on survey responses submitted each day, counties with small populations 
may have comparatively few survey responses. We do not report individual county
estimates when small sample sizes would make estimates unreliable or would allow
identification of respondents, violating privacy and confidentiality agreements.
Additional considerations for specific signals are discussed in the [source and
signal documentation](covidcast_signals.md).

On each day, in each state, we collect the data from all counties with
insufficient data to be individually reported. These counties are combined into
a single "megacounty". For example, if only five counties in a state have
sufficient data to be reported, the remaining counties will form one megacounty
representing the rest of that state. Megacounty estimates are reported with a
FIPS code ending with `000`, which is never a FIPS code for a real county. For
example, megacounty estimates for the state of New York are reported with FIPS
code `36000`, since `36` is the FIPS code prefix for New York.

These megacounty estimates are used on our COVIDcast map and in the county maps
produced by our [API clients](covidcast_clients.md), to color in state backgrounds and graphically represent the "rest of" states whose counties are not
all individually reported.

**Warning:** As sample sizes vary from day to day, the counties composing the
megacounty can vary daily; the geographic area covered by the megacounty is
simply the state minus the counties reported for that day. The megacounty
construction also depends on the specific source and signal. For example, on one day,
megacounty `36000` may cover a different geographic area for the `doctor-visits`
source than it does for the `fb-survey` source. Do not try to compare megacounty
estimates across time or between signals.

## Coding Exceptions

1. The cases and deaths data from JHU CSSE has some geographic exceptions in its
   coding and reporting; see [its documentation](covidcast-signals/jhu-csse.md)
   for more details.
2. The cases and deaths data from USAFacts also has geographic exceptions; see
   [its documentation](covidcast-signals/usa-facts.md) for details.
