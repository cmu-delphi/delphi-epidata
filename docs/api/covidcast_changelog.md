---
title: Signal Changelog
parent: COVIDcast API
nav_order: 3
---

# COVIDcast Signal Changelog

When Delphi makes substantial changes to the computation of a signal, we will
typically publish it under a new name rather than revising the existing signal.
By contrast, the changes documented here are bug fixes, pipeline repairs, and
minor enhancements.

Changes are also announced via the [COVIDcast API mailing
list](https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api), and
we **strongly recommend** that anyone using the API to regularly download data
should subscribe to this list. The list will only be used to announce API
changes, data corrections, and other information relevant to API users.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Sources and Signals
### `doctor-visits`
### `fb-survey`

#### 3 June 2020

Duplicate survey weights had corrupted historical figures for the following signals and dates. The correct data has been restored to the API.
* `raw_wcli`
  * `county`: 20200406, 20200408, 20200410, 20200430
  * `hrr`: 20200406, 20200408-20200410, 20200430
  * `msa`: 20200408, 20200410, 20200430
  * `state`: 20200408-20200410, 20200430
* `smoothed_wcli`
  * `county`: 20200406, 20200408-20200414, 20200430-20200506
  * `hrr`: 20200406-20200415, 20200430-20200506
  * `msa`: 20200408-20200414, 20200430-20200506
  * `state`: 20200408-20200416, 20200430-20200506

### `google-survey`
### `ght`
### `quidel`
### `jhu-csse`

#### 3 June 2020

We now include figures on Puerto Rico for all `jhu-csse` signals at the state level.

#### 1 September 2020

NY Boroughs county FIPS (36005, 36047, 36061, 36081, 36085) are now split in proportion to the population of each county, instead of being reported in aggregate in FIPS 36061. 

#### 7 October 2020

The following changes were made to all `jhu-csse` signals related to geocoding
- NY Boroughs county FIPS (36005, 36047, 36061, 36081, 36085) are now [differentiated by JHU](https://github.com/CSSEGISandData/COVID-19/issues/3084),
- “Unassigned” and “Out of State” counts are assigned to a megaFIPS at the county level (XX000 where XX is the state FIPS code) and will now be incorporated into the state totals
- The split of the Kansas City, Missouri into its four subcounties is now done with a more precise population proportion,
- The split of the Dukes and Nantucket, Massachusetts FIPS codes into the two subcounties is now done with a more precise population proportion,
- Some counts are reported in the Utah territories JHU UIDs 84070015-84070020. These are now properly aggregated into the state megaFIPS 49000, which will be aggregated in state level information.

### `indicator-combination`

#### 3 June 2020

Standard errors are now included in the `nmf_day_doc_fbc_fbs_ght` signal for all geo levels and dates, representing the estimated uncertainty in this signal. This uncertainty comes because the signal is a combination of the other signals which are based on survey estimates or other estimates with margins of error.

* `nmf_day_doc_fbc_fbs_ght`
  * all geo levels
    * all dates

#### 12 October 2020

The 10 October 2020 issue of all `indicator-combination` deaths signals has been removed from the API. These signals are primarily constructed of USAFacts data, whose 10 October 2020 issue was discovered to be corrupt on 11 October and repaired on 12 October. Subsequent issues have adequate coverage of all regions and dates which were included in the 10 October issue, so this change only affects forecasters which intend to pull training data with an `as_of` or `issues` parameter set to 20201010.

### `usa-facts`

#### 12 October 2020

The 10 October 2020 issue of all `usa-facts` deaths signals has been removed from the API. The file for deaths provided by USAFacts on 10 October included cases data instead. The resulting spurious 100x increase in magnitude of COVIDcast `usa-facts` deaths signals was noticed on 11 October and repaired on 12 October. Subsequent issues have adequate coverage of all regions and dates which were included in the 10 October issue, so this change only affects forecasters which intend to pull training data with an `as_of` or `issues` parameter set to 20201010.
