---
title: SafeGraph
parent: Data Sources and Signals
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
datasets.

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## SafeGraph Social Distancing Metrics

* **First issued:** 23 June 2020
* **Number of data revisions since 23 June 2020:** 1
* **Date of last change:** 3 November 2020

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
| `completely_home_prop` | The fraction of mobile devices that did not leave the immediate area of their home (SafeGraph's `completely_home_device_count / device_count`) |
| `full_time_work_prop` | The fraction of mobile devices that spent more than 6 hours at a location other than their home during the daytime (SafeGraph's `full_time_work_behavior_devices / device_count`) |
| `part_time_work_prop` | The fraction of devices that spent between 3 and 6 hours at a location other than their home during the daytime (SafeGraph's `part_time_work_behavior_devices / device_count`) |
| `median_home_dwell_time` | The median time spent at home for all devices at this location for this time period, in minutes |
| `completely_home_prop_7dav` | Offers a 7-day trailing window average of the `completely_home_prop`. |
| `full_time_work_prop_7dav` | Offers a 7-day trailing window average of the`full_time_work_prop`. |
| `part_time_work_prop_7dav` | Offers a 7-day trailing window average of the`part_time_work_prop`.|
| `median_home_dwell_time_7dav` | Offers a 7-day trailing window average of the `median_home_dwell_time`.|

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


## SafeGraph Weekly Patterns

* **First issued:** 30 November 2020
* **Number of data revisions since 23 June 2020:** 0
* **Date of last change:** never

Data source based on [Weekly
Patterns](https://docs.safegraph.com/docs/weekly-patterns) dataset. SafeGraph
provides this data for different points of interest
([POIs](https://docs.safegraph.com/v4.0/docs#section-core-places)) considering
individual census block groups, using differential privacy to protect individual
people's data privacy.

Delphi gathers the number of daily visits to POIs of certain types(bars,
restaurants, etc.)  from SafeGraph's Weekly Patterns data at the 5-digit ZipCode
level, then aggregates and reports these features to the county, MSA, HRR, and
state levels. The aggregated data is freely available through the COVIDcast API.

For precise definitions of the quantities below, consult the [SafeGraph Weekly 
Patterns documentation](https://docs.safegraph.com/docs/weekly-patterns).

| Signal | Description |
| --- | --- |
| `bars_visit_num` | The number of daily visits made by those with SafeGraph's apps to bar-related POIs in a certain region |
| `bars_visit_prop` | The number of daily visits made by those with SafeGraph's apps to bar-related POIs in a certain region, per 100,000 population |
| `restaurants_visit_num` | The number of daily visits made by those with SafeGraph's apps to restaurant-related POIs in a certain region |
| `restaurants_visit_prop` | The number of daily visits made by those with SafeGraph's apps to restaurant-related POIs in a certain region, per 100,000 population |

SafeGraph delivers the number of daily visits to U.S. POIs, the details of which
are described in the [Places
Manual](https://readme.safegraph.com/docs/places-manual#section-placekey)
dataset.  Delphi aggregates the number of visits to certain types of places,
such as bars (places with [NAICS code =
722410](https://www.census.gov/cgi-bin/sssd/naics/naicsrch?input=722410&search=2017+NAICS+Search&search=2017))
and restaurants (places with [NAICS code =
722511](https://www.census.gov/cgi-bin/sssd/naics/naicsrch)). For example,
Adagio Teas is coded as a bar because it serves alcohol, while Napkin Burger is
considered to be a full-service restaurant.  More information on NAICS codes is
available from the [US Census Bureau: North American Industry Classification
System](https://www.census.gov/eos/www/naics/index.html).

### Lag

SafeGraph provides newly updated data for the previous week every Wednesday,
meaning estimates for a specific day are only available 3-9 days later. It may
take up to an additional day for SafeGraph's data to be ingested into the
COVIDcast API.

### Limitations

This data source is based on mobile devices that are members of SafeGraph panels, which is not necessarily the same thing as measuring the general public. This means that counts are subject to bias if some regions have a greater density of SafeGraph panel members as a percentage of the population. These counts do not represent absolute counts, and only count visits by members of the panel in that region.

The number of POIs coded as bars is much smaller than the number of POIs coded as restaurants. 
SafeGraph's Weekly Patterns data consistently lacks data on bar visits for Alaska, Delaware, Maine, North Dakota, New Hampshire, South Dakota, Vermont, West Virginia, and Wyoming. 
For certain dates, bar visits data is also missing for District of Columbia, Idaho and Washington. Restaurant visits data is available for all of the states, as well as the District of Columbia and Puerto Rico.
