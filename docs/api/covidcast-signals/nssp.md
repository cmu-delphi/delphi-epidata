---
title: NSSP
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---
# National Syndromic Surveillance Program (NSSP) Emerency Department (ED) visits
{: .no_toc}

* **Source name:** `nssp`
* **Earliest issue available:** (TODO ask Minh)
* **Number of data revisions since 19 May 2020:** (TODO)
* **Date of last change:** TODO
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

[The National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) is an effort to track epidemiologically relevant conditions.
This dataset in particular tracks emergency department (ED) visits arising from a subset of influenza-like illnesses, specifically flu, COVID-19, and RSV.
It is derived from [this cdc dataset](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/rdmq-nq56/about_data). 
Originating in late 2022, as of May 2024, NSSP received data from 78% of US EDs.

| Signal                          | Description                                                             |
|---------------------------------|-------------------------------------------------------------------------|
| `pct_visits_covid`              | Percent of visits with a discharge diagnosis code of covid              |
| `pct_visits_influenza`          | Percent of visits with a discharge diagnosis code of influenza          |
| `pct_visits_rsv`                | Percent of visits with a discharge diagnosis code of rsv                |
| `pct_visits_combined`           | Percent of visits with a discharge diagnosis code of covid, flu, or rsv |
| `smoothed_pct_visits_covid`     | 3 week moving average of `pct_visits_covid`                        |
| `smoothed_pct_visits_influenza` | 3 week moving average of `pct_visits_influenza`                    |
| `smoothed_pct_visits_rsv`       | 3 week moving average of `pct_visits_rsv`                          |
| `smoothed_pct_visits_combined`  | 3 week moving average of `pct_visits_combined`                     |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

The percent visits is as a fraction of visits at facilities reporting to NSSP, rather than all facilities in the area.
The county and state level are direct data sources, while `hrr` and `msa` are estimated.

### Geographic weighting
As the original data is a percentage, to compute `hrr` and `msa` from county-level, we do a weighted mean, weighting by the county's population in the last census (2020).
This assumes that the number of ED visits is proportional to the overall population of the county, which may not strictly be the case (e.g. denser counties having easier access and thus may have a higher rate of ED visits per capita).

State-level data is reported separately, and is **not** simply an average of the county-level data, but may contain facilities omitted at the regional level (for example, if small facilities are excluded for privacy reasons).[^1] 

### Smoothing

The smoothed values are a simple 3 week average of the corresponding signals (note that since this is weekly data, this is 3 values rather than 21).

## Limitations

As of May 2024, NSSP received data from 78% of US EDs.
The geographic distribution of those sites can be seen [here](https://www.cdc.gov/nssp/media/images/2024/04/Participation-with-date.png); the most noticeable gaps in coverage are in California, Oklahoma, and Colorado, though most states have some counties that are absent.

NSSP notes that not every patient entering an ED is tested for these conditions, so this may represent an undercount of total cases.

## Missingness

Counties which do not have data are listed, but with an `NA` value.

## Lag and Backfill

There is significant backfill in this signal, primarily arising when a new facility joins the network and its data is included in a region.
This has the strongest effects at the highest levels of aggregation.


The weekly signal is reported on Friday mornings.

## Source and Licensing

This source is processed from this [data.cdc.gov site](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/rdmq-nq56/about_data).
There is another version of the state-only data available [here](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/7mra-9cq9/about_data).

This data was originally published by the National Center for Health Statistics, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).

If the signal has specific licensing or sourcing that should be acknowledged,
describe it here. Also, include links to source websites for data that is
scraped or received from another source.

[^1]: (TODO should probably confirm this in some way)
