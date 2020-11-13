---
title: SafeGraph Mobility Patterns
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# SafeGraph Mobility Patterns

* **Source name:** `safegraph_patterns`
* **Number of data revisions since 23 June 2020:** 0
* **Date of last change:** never
* **Available for:** county, MSA, HRR, state (see [geography coding docs](../covidcast_geography.md))

This data source uses data reported by [SafeGraph](https://www.safegraph.com/) 
using anonymized location data from mobile phones. SafeGraph provides
[Weekly Patterns](https://docs.safegraph.com/docs/weekly-patterns) dataset
to eligible researchers who obtain an API key. SafeGraph provides this data for
individual census block groups, using differential privacy to protect the
privacy of individual people in the data.

Delphi gathers the number of daily visits to POIs of certain types(bars, restaurants etc.) 
from SafeGraph Weekly Patterns data at the 5-digit ZipCode level, then aggregates and 
reports these features to the county, MSA, HRR, and state levels. The aggregated data 
is freely available through the COVIDcast API.

For precise definitions of the quantities below, consult the [SafeGraph Weekly 
Patterns documentation](https://docs.safegraph.com/docs/weekly-patterns).

| Signal | Description |
| --- | --- |
| `bars_visit_num` | The number of daily visits to bar-related POIs in a certain region |
| `bars_visit_prop` | The number of daily visits to bar-related POIs in a certain region, per 100,000 population |
| `restaurants_visit_num` | The number of daily visits to restaurant-related POIs in a certain region |
| `restaurants_visit_prop` | The number of daily visits to bar-related POIs in a certain region, per 100,000 population |

SafeGraph delivers the number of daily visits to U.S. POIs, the details of which are described in 
[Places Manual](https://readme.safegraph.com/docs/places-manual#section-placekey) dataset. 
Delphi aggregates the number of visits from specific places to certain types of places, such as 
bars and restaurants. 

## Lag

SafeGraph provides newly updated data for the previous week every Wednesday, 
meaning estimates for a specific day are only available 3-9 days later. It may take up to an
additional day for SafeGraph's data to be ingested into the COVIDcast API.
