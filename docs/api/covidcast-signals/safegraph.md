---
title: SafeGraph Mobility
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# SafeGraph
{: .no_toc}
* **Source name:** `safegraph`

This data source uses data reported by [SafeGraph](https://www.safegraph.com/)
using anonymized location data from mobile phones. SafeGraph provides several different datasets to eligible researchers. We surface signals from two such datasets.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## SafeGraph Social Distancing Metrics

* **First issued:** 23 June 2020
* **Number of data revisions since 23 June 2020:** 0
* **Date of last change:** never
* **Available for:** county, state (see [geography coding docs](../covidcast_geography.md))

Data source based on [social
distancing metrics](https://docs.safegraph.com/docs/social-distancing-metrics). 
SafeGraph provides this data for
individual census block groups, using differential privacy to protect individual people's data privacy.

Delphi creates features of the SafeGraph data at the census block group level,
then aggregates these features to the county and state levels. The aggregated
data is freely available through the COVIDcast API.

For precise definitions of the quantities below, consult the [SafeGraph social
distancing metric
documentation](https://docs.safegraph.com/docs/social-distancing-metrics).

| Signal | Description |
| --- | --- |
| `completely_home_prop` | The fraction of mobile devices that did not leave the immediate area of their home (SafeGraph's `completely_home_device_count / device_count`) |
| `full_time_work_prop` | The fraction of mobile devices that spent more than 6 hours at a location other than their home during the daytime (SafeGraph's `full_time_work_behavior_devices / device_count`) |
| `part_time_work_prop` | The fraction of devices that spent between 3 and 6 hours at a location other than their home during the daytime (SafeGraph's `part_time_work_behavior_devices / device_count`) |
| `median_home_dwell_time` | The median time spent at home for all devices at this location for this time period, in minutes |

After computing each metric on the census block group (CBG) level, we aggregate
to the county-level by taking the mean over CBGs in a county to obtain the value
and taking `sd / sqrt(n)` for the standard error, where `sd` is the standard
deviation over the metric values and `n` is the number of CBGs in the county. In
doing so, we make the simplifying assumption that each CBG contributes an iid
observation to the county-level distribution. `n` also serves as the sample
size. The same method is used for aggregation to states.

### Lag

SafeGraph provides this data with a three-day lag, meaning estimates for a
specific day are only available three days later. It may take up to an
additional day for SafeGraph's data to be ingested into the COVIDcast API.


## SafeGraph Weekly Patterns


* **Number of data revisions since 23 June 2020:** 0
* **Date of last change:** never
* **Available for:** county, MSA, HRR, state (see [geography coding docs](../covidcast_geography.md))

Data source based on
[Weekly Patterns](https://docs.safegraph.com/docs/weekly-patterns) dataset. SafeGraph provides this data for
different points of interest ([POIs](https://docs.safegraph.com/v4.0/docs#section-core-places)) considering individual census block groups, using differential privacy to protect individual people's data privacy.

Delphi gathers the number of daily visits to POIs of certain types(bars, restaurants, etc.) 
from SafeGraph' Weekly Patterns data at the 5-digit ZipCode level, then aggregates and reports these features to the county, MSA, HRR, and state levels. The aggregated data is freely available through the COVIDcast API.

For precise definitions of the quantities below, consult the [SafeGraph Weekly 
Patterns documentation](https://docs.safegraph.com/docs/weekly-patterns).

| Signal | Description |
| --- | --- |
| `bars_visit_num` | The number of daily visits to bar-related POIs in a certain region |
| `bars_visit_prop` | The number of daily visits to bar-related POIs in a certain region, per 100,000 population |
| `restaurants_visit_num` | The number of daily visits to restaurant-related POIs in a certain region |
| `restaurants_visit_prop` | The number of daily visits to restaurant-related POIs in a certain region, per 100,000 population |

SafeGraph delivers the number of daily visits to U.S. POIs, the details of which are described in 
the [Places Manual](https://readme.safegraph.com/docs/places-manual#section-placekey) dataset. 
Delphi aggregates the number of visits to certain types of places, such as 
bars (places with NAICS code = 722410) and restaurants (places with NAICS code = 722511). For example, Adagio Teas belongs to the first group while Napkin Burger is considered to be a restaurant.

### Lag

SafeGraph provides newly updated data for the previous week every Wednesday, 
meaning estimates for a specific day are only available 3-9 days later. It may take up to an
additional day for SafeGraph's data to be ingested into the COVIDcast API.
