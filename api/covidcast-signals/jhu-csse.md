---
title: JHU Cases and Deaths
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# JHU Cases and Deaths
{: .no_toc}

* **Source name:** `jhu-csse`
* **Earliest issue available:** May 7, 2020
* **Number of data revisions since May 19, 2020:** 1
* **Date of last change:** [October 7, 2020](../covidcast_changelog.md#jhu-csse)
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](#source-and-licensing)

## Overview

This data source of confirmed COVID-19 cases and deaths is based on reports made
available by the Center for Systems Science and Engineering at Johns Hopkins
University.

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumulative_num` | Cumulative number of confirmed COVID-19 cases <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumulative_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `confirmed_incidence_num` | `confirmed_7dav_incidence_num` | Number of new confirmed COVID-19 cases, daily <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `confirmed_incidence_prop` | `confirmed_7dav_incidence_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `deaths_cumulative_num` | `deaths_7dav_cumulative_num` | Cumulative number of confirmed deaths due to COVID-19 <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `deaths_cumulative_prop` | `deaths_7dav_cumulative_prop` | Cumulative number of confirmed due to COVID-19, per 100,000 population <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `deaths_incidence_num` | `deaths_7dav_incidence_num` | Number of new confirmed deaths due to COVID-19, daily <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |
| `deaths_incidence_prop` | `deaths_7dav_incidence_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily <br/> **Earliest date available:** 2020-01-22 & 2020-02-20 |

These signals are taken directly from the JHU CSSE [COVID-19 GitHub
repository](https://github.com/CSSEGISandData/COVID-19) without changes. The
7-day average signals are computed by Delphi by calculating moving averages of
the preceding 7 days, so e.g. the signal for June 7 is the average of the
underlying data for June 1 through 7, inclusive.

This data is similar in intent to our [USAFacts Cases and Deaths](usa-facts.md)
source, but as USAFacts collects and aggregates its data in slightly different
ways, the data is not identical. Users should evaluate which source better fits
their needs, or use the [combination signal of both USAFacts and JHU data](indicator-combination.md).

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Limitations

JHU's data reports cumulative cases and deaths, so our incidence signals are
calculated by subtracting each day's cumulative count from the previous day.
Since cumulative figures are sometimes corrected or amended by health
authorities, this can sometimes result in negative incidence. Health authorities
can also change reporting standards in ways that dramatically increase the
number of cumulative deaths, resulting in an apparent spike in incidence. This
should be interpreted purely as an artifact of data reporting and correction.

## Geographical Exceptions

Due to differences in state reporting standards, certain counties are not
reported in the JHU data or are reported combined with other counties.

### Rhode Island

As of June 2020, the JHU data [does not report any cases or deaths](https://github.com/CSSEGISandData/COVID-19/issues/3165) for individual counties in Rhode Island. These cases and deaths are reported unassigned to any individual county, and are attributed to the megaFIPS 44000 as well as contributing to the state-level estimates.

### Puerto Rico

JHU does not report Puerto Rico deaths at the municipal level, but instead reports the numbers for the whole Commonwealth in the "Unassigned" category. We map this JHU UID to megaFIPS 72000 and use this information when reporting deaths at the state level.

### Utah

JHU reports some counts for Utah in special geocodes. These geocodes correspond to clusters of counties overseen by the same health department.

|County Name        |JHU UID Code   |
|-------------------|---------------|
|Bear River         |84070015       |
|Central Utah       |84070016       |
|Southeast Utah     |84070017       |
|Southwest Utah     |84070018       |
|TriCounty          |84070019       |
|Weber-Morgan       |84070020       |

These are mapped to the megaFIPS 49000 and accounted for in the state totals.

### Kansas City, Missouri

Kansas City intersects the following four counties, which themselves report confirmed case and deaths data:

|County Name        |FIPS Code      |
|-------------------|---------------|
|Jackson County     |29095          |
|Platte County      |29165          |
|Cass County        |29037          |
|Clay County        |29047          |

**We distribute count totals to each of these counties in proportion to the population.**  JHU reports all of these in the UID 84070003, which does not correspond to a Census Bureau FIPS.

### Dukes and Nantucket Counties, Massachusetts

**The counties of Dukes and Nantucket report their figures together; We distribute count totals to each of these counties in proportion to the population.**  JHU reports all of these in the UID 84070002, which does not correspond to a Census Bureau FIPS. Here are the FIPS codes for the individual counties:

|County Name        |FIPS Code      |
|-------------------|---------------|
|Dukes County       |25007          |
|Nantucket County   |25019          |

### Mismatched FIPS Codes

Finally, there are two FIPS codes that were changed in 2015 (see the [Census
Bureau
documentation](https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.html)),
leading to mismatch between us and JHU. We report the data using the FIPS code
used by JHU, again to promote consistency and avoid confusion by external users
of the dataset. For the mapping to MSA and HRR, these two counties are included
properly.

|County Name        |State          |"Our" FIPS         |JHU FIPS       |
|-------------------|---------------|-------------------|---------------|
|Oglala Lakota      |South Dakota   |46113              |46102          |
|Kusilvak           |Alaska         |02270              |02158          |

## Source and Licensing

This data set is republished from the COVID-19 Data Repository by the Center for
Systems Science and Engineering (CSSE) at Johns Hopkins University, under the
terms of the [Creative Commons Attribution 4.0 International (CC BY 4.0)
license](https://creativecommons.org/licenses/by/4.0/). If you use this data,
you are requested to attribute the data as follows:

> COVID-19 Data Repository by the Center for Systems Science and Engineering
> (CSSE) at Johns Hopkins University.
> <https://github.com/CSSEGISandData/COVID-19>
