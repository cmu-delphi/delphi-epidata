---
title: NSSP ED Visits
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
nav_order: 1
---
# National Syndromic Surveillance Program Emergency Department Visits
{: .no_toc}

* **Source name:** `nssp`
* **Earliest issue available:** April 17, 2024
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state, hhs, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

## Overview

[The National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) is an effort to track epidemiologically relevant conditions.
This dataset in particular tracks emergency department (ED) visits arising from a subset of influenza-like illnesses, specifically influenza, COVID-19, and respiratory syncytial virus (RSV).
It is derived from the CDC's [Respiratory Virus Response NSSP Emergency Department Visit Trajectories dataset](https://data.cdc.gov/Public-Health-Surveillance/2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/rdmq-nq56/about_data), which started reporting data in late 2022.
As of May 2024, NSSP received data from 78% of US EDs.

| Signal                          | Description                                                                                                                          |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `pct_ed_visits_covid`              | Percent of ED visits that had a discharge diagnosis code of COVID-19 <br/> **Earliest date available:** 2022-10-01                      |
| `pct_ed_visits_influenza`          | Percent of ED visits that had a discharge diagnosis code of influenza  <br/> **Earliest date available:** 2022-10-01                 |
| `pct_ed_visits_rsv`                | Percent of ED visits that had a discharge diagnosis code of rsv  <br/> **Earliest date available:** 2022-10-01                       |
| `pct_ed_visits_combined`           | Percent of ED visits that had a discharge diagnosis code of COVID-19, influenza, or rsv   <br/> **Earliest date available:** 2022-10-01 |
| `smoothed_pct_ed_visits_covid`     | 3 week moving average of `pct_ed_visits_covid`  <br/> **Earliest date available:** 2022-10-01                                           |
| `smoothed_pct_ed_visits_influenza` | 3 week moving average of `pct_ed_visits_influenza`   <br/> **Earliest date available:** 2022-10-01                                      |
| `smoothed_pct_ed_visits_rsv`       | 3 week moving average of `pct_ed_visits_rsv`   <br/> **Earliest date available:** 2022-10-01                                            |
| `smoothed_pct_ed_visits_combined`  | 3 week moving average of `pct_ed_visits_combined`   <br/> **Earliest date available:** 2022-10-01                                       |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

The percent visits signals are calculated as a fraction of visits at facilities reporting to NSSP, rather than all facilities in the area.
`county`, `state` and `nation` level data is reported as-is from NSSP, without modification, while `hhs`, `hrr` and `msa` are estimated by Delphi.

### Geographic weighting
As the original data is a percentage and raw case counts are not available, `hrr`,`msa`, and `hhs` values are computed from county-level data using a weighted mean. Each county is assigned a weight equal to its population in the last census (2020). Unreported counties are implicitly treated as having a weight of 0 or a value equal to the group mean.

This weighting approach assumes that the number of ED visits is proportional to the overall population of a county, i.e. the per-capita ED visit rate is the same for all counties, which may not be the case (for example, denser counties may have easier access to EDs and thus higher rates of ED visits per capita).

State reporting process is separate from the county reporting process. As such, state-level data is **not** simply an average of the county-level data, but may contain facilities omitted at the regional level. For example, state-level values are available for California, even though no California county data is reported; see the [missingness section below](#missingness) for a list of such states.

### Smoothing

Smoothed signals are calculated using a simple 3 week moving average of the relevant weekly signals. Note that since the unsmoothed `pct_ed_visits_*` signals report weekly data, each smoothed signal value is computed from 3 points rather than 21, as would be used if the unsmoothed data were reported daily.


## Missingness

As of May 2024, NSSP received data from 78% of US EDs.

[The NSSP site participation map](https://www.cdc.gov/nssp/media/images/2024/04/Participation-with-date.png) shows counties containing at least one reporting ED between January 2023 and April 2024.
California, Colorado, Missouri, Oklahoma, and Virginia have the most noticeable gaps in coverage, with many counties in those states having either no eligible EDs or having no recently reported data in NSSP. However, most states have some counties that do not contain any reporting EDs.

NSSP does not report county-level data for all counties with reporting EDs; some reporting EDs are only included in state-level values.

The following states report no data through NSSP at the county level: CA, WA, AK, AZ, AL, CO, SD, ND, MO, AR, FL, OH, NH, CT, NJ.

South Dakota, Missouri, and territories report no data through NSSP at the state level.


## Lag and Backfill

The weekly signal is reported on Friday mornings, adding data from the prior week.
For example, on Friday, 2024-04-19, the source added new data from the week ending 2024-04-13.

This data source has frequent backfill, primarily arising from newly included EDs. When a new facility joins the reporting network, its historical data is added to the dataset, resulting in changes to historical values for every geographic level that ED is part of (county through nation). Because of this, the broadest geographic levels are more likely to be revised.

In previous revisions, we have noted changes to values dating back about 2 years.
The following states have no county-level data at all: AK, AL, AR, AZ, CA, FL, MO, ND, NH, NJ, OH, SD, WA.
Counties with `NA` values are as originally reported in the dataset from which this source is derived; this is not a complete list of counties, and reflects missing data as collected by the NSSP.


## Limitations

There is substantial missingness at the county level. This tends to impact more rural and lower population locations. See the [missingness section](#missingness) for more information.

Not all counties contain reporting EDs, including in states where NSSP reports state-level data.
A minority of these (as of June 2024) are counties without EDs, while others are only covered by the ~22% of EDs that don't yet report to the NSSP.
