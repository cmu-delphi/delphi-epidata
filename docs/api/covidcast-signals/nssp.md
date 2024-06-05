---
title: NSSP emergency department visits
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---
# National Syndromic Surveillance Program (NSSP) Emerency Department (ED) visits
{: .no_toc}

* **Source name:** `nssp`
* **Earliest issue available:** (TODO ask Minh)
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

## Overview

[The National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) is an effort to track epidemiologically relevant conditions.
This dataset in particular tracks emergency department (ED) visits arising from a subset of influenza-like illnesses, specifically influenza, COVID-19, and RSV.
It is derived from the CDC's [Respiratory Virus Response NSSP Emergency Department Visit Trajectories dataset](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/rdmq-nq56/about_data), which started reporting data in late 2022.
As of May 2024, NSSP received data from 78% of US EDs.

| Signal                          | Description                                                             |
|---------------------------------|-------------------------------------------------------------------------|
| `pct_visits_covid`              | Percent of ED visits that had a discharge diagnosis code of covid              |
| `pct_visits_influenza`          | Percent of ED visits that had a discharge diagnosis code of influenza          |
| `pct_visits_rsv`                | Percent of ED visits that had a discharge diagnosis code of rsv                |
| `pct_visits_combined`           | Percent of ED visits that had a discharge diagnosis code of covid, influenza, or rsv |
| `smoothed_pct_visits_covid`     | 3 week moving average of `pct_visits_covid`                        |
| `smoothed_pct_visits_influenza` | 3 week moving average of `pct_visits_influenza`                    |
| `smoothed_pct_visits_rsv`       | 3 week moving average of `pct_visits_rsv`                          |
| `smoothed_pct_visits_combined`  | 3 week moving average of `pct_visits_combined`                     |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

The percent visits signals are calculated as a fraction of visits at facilities reporting to NSSP, rather than all facilities in the area.
County and state level data is reported as-is from NSSP, without modification, while `hrr` and `msa` are estimated by Delphi.

### Geographic weighting
As the original data is a percentage and raw case counts are not available, `hrr` and `msa` values are computed from county-level data using a weighted mean. Each county is assigned a weight equal to its population in the last census (2020).
This assumes that the number of ED visits is proportional to the overall population of a county, i.e. the per-capita ED visit rate is the same for all counties, which may not be the case (for example, denser counties may have easier access to EDs and thus higher rates of ED visits per capita).

State-level data is reported separately, and is **not** simply an average of the county-level data, but may contain facilities omitted at the regional level (for example, if small facilities are excluded for privacy reasons).[^1] 

### Smoothing

Smoothed signals are calculated using a simple 3 week moving average of the relevant weekly signals. Note that since the unsmoothed `pct_visits_*` signals report weekly data, each smoothed signal value is computed from 3 points rather than 21, as would be used if the unsmoothed data were reported daily.

## Limitations

As of May 2024, NSSP received data from 78% of US EDs.
The most noticeable gaps in [geographic coverage](https://www.cdc.gov/nssp/media/images/2024/04/Participation-with-date.png) are in California, Colorado, Missouri, Oklahoma, and Virginia, though most states have some counties that are absent.

NSSP notes that not every patient entering an ED is tested for the conditions of interest, so the data may undercount total cases and as a result underreport percent visits.

Our [geographic weighting approach](#geographic-weighting) assumes that the number of ED visits is proportional to the overall population of a county. However, in reality we expect denser, more urban counties to have 1) more and larger EDs and 2) easier access to EDs. The first factor may mean that residents of rural counties are more likely to go to EDs in urban counties. The second factor may increase the total number of ED visits that someone living in an urban county will make, that is, the average urban resident may make more ED visits than the average rural resident.

As a result, total ED visits per capita in rural counties may be lower than total ED visits per capita in urban counties. Since our weighting approach uses population as the weighting factor, rural counties would tend to be overrepresented in estimated values.


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