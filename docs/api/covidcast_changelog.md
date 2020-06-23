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

### `indicator-combination`

#### 3 June 2020

Standard errors are now included in the `nmf_day_doc_fbc_fbs_ght` signal for all geo levels and dates, representing the estimated uncertainty in this signal. This uncertainty comes because the signal is a combination of the other signals which are based on survey estimates or other estimates with margins of error.

* `nmf_day_doc_fbc_fbs_ght`
  * all geo levels
    * all dates
