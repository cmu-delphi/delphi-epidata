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
different datasets to eligible researchers. We currently surface signals from one such
dataset.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## SafeGraph Social Distancing Metrics (Inactive)

These signals were updated until April 19th, 2021, when Safegraph ceased updating the dataset.
Documentation for these signals is still available on the [inactive Safegraph page](safegraph-inactive.md).

## SafeGraph Weekly Patterns

* **Earliest issue available:** November 30, 2020
* **Number of data revisions since June 23, 2020:** 0
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
| `bars_visit_num` | The number of daily visits made by those with SafeGraph's apps to bar-related POIs in a certain region <br/> **Earliest date available:** 01/01/2019 |
| `bars_visit_prop` | The number of daily visits made by those with SafeGraph's apps to bar-related POIs in a certain region, per 100,000 population <br/> **Earliest date available:** 01/01/2019 |
| `restaurants_visit_num` | The number of daily visits made by those with SafeGraph's apps to restaurant-related POIs in a certain region <br/> **Earliest date available:** 01/01/2019 |
| `restaurants_visit_prop` | The number of daily visits made by those with SafeGraph's apps to restaurant-related POIs in a certain region, per 100,000 population <br/> **Earliest date available:** 01/01/2019 |

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

The number of POIs coded as bars is much smaller than the number of POIs coded as restaurants.
SafeGraph's Weekly Patterns data consistently lacks data on bar visits for Alaska, Delaware, Maine, North Dakota, New Hampshire, South Dakota, Vermont, West Virginia, and Wyoming.
For certain dates, bar visits data is also missing for District of Columbia, Idaho and Washington. Restaurant visits data is available for all of the states, as well as the District of Columbia and Puerto Rico.

### Lag

SafeGraph provides newly updated data for the previous week every Wednesday,
meaning estimates for a specific day are only available 3-9 days later. It may
take up to an additional day for SafeGraph's data to be ingested into the
COVIDcast API.

## Limitations

SafeGraph's Social Distancing Metrics and Weekly Patterns are based on mobile devices that are members of SafeGraph panels, which is not necessarily the same thing as measuring the general public. These counts do not represent absolute counts, and only count visits by members of the panel in that region. This can result in several biases:

* **Geographic bias.** If some regions have a greater density of SafeGraph panel members as a percentage of the population than other regions, comparisons of metrics between regions may be biased. Regions with more SafeGraph panel members will appear to have more visits counted, even if the rate of visits in the general population is the same.
* **Demographic bias.** SafeGraph panels may not be representative of the local population as a whole. For example, [some research suggests](https://arxiv.org/abs/2011.07194) that "older and non-white voters are less likely to be captured by mobility data", so this data will not accurately reflect behavior in those populations. Since population demographics vary across the United States, this can also contribute to geographic biases.
