---
title: SafeGraph
parent: Inactive Signals
grand_parent: COVIDcast Epidata API
---

# SafeGraph
{: .no_toc}
* **Source name:** `safegraph`
* **Available for:** county, MSA, HRR, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

This data source uses data reported by [SafeGraph](https://www.safegraph.com/)
using anonymized location data from mobile phones. SafeGraph provides several
different datasets to eligible researchers. We surface signals from two such
datasets. This dataset is no longer updated after April 19th, 2021.

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## SafeGraph Social Distancing Metrics

* **Earliest issue available:** June 20, 2020
* **Number of data revisions since June 23, 2020:** 1
* **Date of last change:** November 3, 2020

Data source based on [social distancing
metrics](https://docs.safegraph.com/docs/social-distancing-metrics).  SafeGraph
provides this data for individual census block groups, using differential
privacy to protect individual people's data privacy.

Delphi creates features of the SafeGraph data at the census block group level,
then aggregates these features to the county and state levels. The aggregated
data is freely available through the COVIDcast API.

For precise definitions of the quantities below, consult the [SafeGraph social
distancing metric
documentation](https://docs.safegraph.com/docs/social-distancing-metrics).

| Signal | Description |
| --- | --- |
| `completely_home_prop` | The fraction of mobile devices that did not leave the immediate area of their home (SafeGraph's `completely_home_device_count / device_count`) <br/> **Earliest date available:** 01/01/2019 |
| `full_time_work_prop` | The fraction of mobile devices that spent more than 6 hours at a location other than their home during the daytime (SafeGraph's `full_time_work_behavior_devices / device_count`) <br/> **Earliest date available:** 01/01/2019 |
| `part_time_work_prop` | The fraction of devices that spent between 3 and 6 hours at a location other than their home during the daytime (SafeGraph's `part_time_work_behavior_devices / device_count`) <br/> **Earliest date available:** 01/01/2019 |
| `median_home_dwell_time` | The median time spent at home for all devices at this location for this time period, in minutes <br/> **Earliest date available:** 01/01/2019 |
| `completely_home_prop_7dav` | Offers a 7-day trailing window average of the `completely_home_prop`. <br/> **Earliest date available:** 01/01/2019 |
| `full_time_work_prop_7dav` | Offers a 7-day trailing window average of the`full_time_work_prop`. <br/> **Earliest date available:** 01/01/2019 |
| `part_time_work_prop_7dav` | Offers a 7-day trailing window average of the`part_time_work_prop`. <br/> **Earliest date available:** 01/01/2019 |
| `median_home_dwell_time_7dav` | Offers a 7-day trailing window average of the `median_home_dwell_time`. <br/> **Earliest date available:** 01/01/2019 |

After computing each metric on the census block group (CBG) level, we aggregate
to the county-level by taking the mean over CBGs in a county to obtain the value
and taking `sd / sqrt(n)` for the standard error, where `sd` is the standard
deviation over the metric values and `n` is the number of CBGs in the county. In
doing so, we make the simplifying assumption that each CBG contributes an iid
observation to the county-level distribution. `n` also serves as the sample
size. The same method is used for aggregation to states.

SafeGraph's signals measure mobility each day, which causes strong day-of-week
effects: weekends have substantially different values than weekdays. Users
interested in long-term trends, rather than mobility on one specific day, may
prefer the `7dav` signals since averaging over the preceding 7 days removes
these day-of-week effects.

### Lag

SafeGraph provides this data with a three-day lag, meaning estimates for a
specific day are only available three days later. It may take up to an
additional day for SafeGraph's data to be ingested into the COVIDcast API.

