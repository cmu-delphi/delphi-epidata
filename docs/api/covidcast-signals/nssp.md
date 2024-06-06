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
* **Available for:** county, hrr, msa, state, nation (see [geography coding docs](../covidcast_geography.md))
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
As the original data is a percentage and raw case counts are not available, `hrr` and `msa` values are computed from county-level data using a weighted mean. Each county is assigned a weight equal to its population in the last census (2020). Unreported counties are implicitly treated as having a weight of 0 or a value equal to the group mean.

This weighting approach assumes that the number of ED visits is proportional to the overall population of a county, i.e. the per-capita ED visit rate is the same for all counties, which may not be the case (for example, denser counties may have easier access to EDs and thus higher rates of ED visits per capita).

State reporting process is separate from the county reporting process. As such, state-level data is **not** simply an average of the county-level data, but may contain facilities omitted at the regional level. For example, state-level values are available for California, even though no California county data is reported.

### Smoothing

Smoothed signals are calculated using a simple 3 week moving average of the relevant weekly signals. Note that since the unsmoothed `pct_visits_*` signals report weekly data, each smoothed signal value is computed from 3 points rather than 21, as would be used if the unsmoothed data were reported daily.


## Limitations

There is substantial missingness at the county level. This tends to impact more rural and lower population locations. See the [missingness section below](#missingness) for more information.

NSSP notes that not every patient entering an ED is tested for the conditions of interest, so the data may undercount total cases and as a result percent visits may be biased downward.

Our [geographic weighting approach](#geographic-weighting) assumes that the number of ED visits is proportional to the overall population of a county. However, in reality, there are various factors that could affect the accuracy of this assumption.

For example, we might expect denser, more urban counties to have 1) more and larger EDs and 2) easier access to EDs. The first factor may mean that residents of rural counties are more likely to go to EDs in urban counties. The second factor may increase the total number of ED visits that someone living in an urban county will make, that is, the average urban resident may make more ED visits than the average rural resident over a given period of time.

As a result, total ED visits per capita in rural counties may be lower than total ED visits per capita in urban counties. Since our weighting approach uses population as the weights, rural counties would tend to be overrepresented in estimated values.

Some low population counties occasionally report outliers, e.g. 33.33%, 50%, 100% of ER visits being covid-related. As of May 2024, an analysis shows around 10 unusually high values across the full history of all signals, so they are rare. We expect that these high rates are by chance, due to a small total number of ED visits in a given week.

Not all counties contain reporting EDs, including in states where NSSP reports state-level data.


## Missingness

As of May 2024, NSSP received data from 78% of US EDs.

[The NSSP site participation map](https://www.cdc.gov/nssp/media/images/2024/04/Participation-with-date.png) shows counties containing at least one reporting ED between January 2023 and April 2024.
California, Colorado, Missouri, Oklahoma, and Virginia have the most noticeable gaps in coverage, with many component counties having either no eligible EDs or having no recently reported data in NSSP. However, most states have some counties that are absent.

NSSP does not report county-level data for all counties with reporting EDs; some reporting EDs are only included in state-level values.

The following states report no data through NSSP at the county level: CA, WA, AK, AZ, AL, CO, SD, ND, MO, AR, FL, OH, NH, CT, NJ.

South Dakota, Missouri, and territories report no data through NSSP at the state level.


## Lag and Backfill

The weekly signal is reported on Friday mornings, adding data from the prior week.
For example, on Friday, 2024-04-19, the source added new data from the week ending 2024-04-13.

This data source has frequent backfill, primarily arising from newly included EDs. When a new facility joins the reporting network, its historical data is added to the dataset, resulting in changes to historical values for every geographic level that ED is part of (county through nation). Because of this, the broadest geographic levels are more likely to be revised.

In previous revisions, we have noted changes to values dating back about 2 years.


## Source and Licensing

This source is derived from the CDC's [Respiratory Virus Response NSSP Emergency Department Visit Trajectories dataset](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/rdmq-nq56/about_data).
There is another version of the dataset that includes [state data only](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/7mra-9cq9/about_data).

This data was originally published by the National Center for Health Statistics, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).
