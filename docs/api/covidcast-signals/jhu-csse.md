---
title: JHU Cases and Deaths
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# JHU Cases and Deaths
{: .no_toc}

* **Source name:** `jhu-csse`
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#jhu-csse)
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source of confirmed COVID-19 cases and deaths is based on reports made
available by the Center for Systems Science and Engineering at Johns Hopkins
University.

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumul_num` | Cumulative number of confirmed COVID-19 cases |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumul_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population |
| `confirmed_incidence_num` | `confirmed_7dav_incid_num` | Number of new confirmed COVID-19 cases, daily |
| `confirmed_incidence_prop` | `confirmed_7dav_incid_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily |
| `deaths_cumulative_num` | `deaths_7dav_cumul_num` | Cumulative number of confirmed deaths due to COVID-19 |
| `deaths_cumulative_prop` | `deaths_7dav_cumul_prop` | Cumulative number of confirmed due to COVID-19, per 100,000 population |
| `deaths_incidence_num` | `deaths_7dav_incid_num` | Number of new confirmed deaths due to COVID-19, daily |
| `deaths_incidence_prop` | `deaths_7dav_incid_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily |

These signals are taken directly from the JHU CSSE [COVID-19 GitHub
repository](https://github.com/CSSEGISandData/COVID-19) without changes. The
7-day average signals are computed by Delphi by calculating moving averages of
the preceding 7 days, so e.g. the signal for June 7 is the average of the
underlying data for June 1 through 7, inclusive.

This data is similar in intent to our [USAFacts Cases and Deaths](usa-facts.md)
source, but as USAFacts collects and aggregates its data in slightly different
ways, the data is not identical. Users should evaluate which source better fits
their needs.

## Table of contents
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

At the County (FIPS) level, we report the data _exactly_ as JHU reports their
data, to prevent confusing public consumers of the data. JHU FIPS reporting
matches that used in the other signals, except for the following exceptions.

### New York City

New York City comprises five boroughs, each of which is a county:

|Borough Name       |County Name        |FIPS Code      |
|-------------------|-------------------|---------------|
|Manhattan          |New York County    |36061          |
|The Bronx          |Bronx County       |36005          |
|Brooklyn           |Kings County       |36047          |
|Queens             |Queens County      |36081          |
|Staten Island      |Richmond County    |36085          |

**Data from all five boroughs are reported under New York County, FIPS Code
36061.** The other four boroughs are included in the dataset and show up in our
API, but always report zero cases and deaths.

All NYC counts are mapped to the MSA with CBSA ID 35620, which encompasses all
five boroughs. All NYC counts are mapped to HRR 303, which intersects all five
boroughs (297 also intersects the Bronx and 301 also intersects Brooklyn and
Queens, but absent additional information, we chose to leave all counts in 303).

### Rhode Island

As of June 2020, the JHU data does not report any cases or deaths for individual
counties in Rhode Island. These cases and deaths are reported unassigned to any
individual county, and are hence available in state-level estimates only.

### Kansas City, Missouri

Kansas City intersects the following four counties, which themselves report
confirmed case and deaths data:

|County Name        |FIPS Code      |
|-------------------|---------------|
|Jackson County     |29095          |
|Platte County      |29165          |
|Cass County        |29037          |
|Clay County        |29047          |

**Data from Kansas City is given its own dedicated line, with FIPS
code 70003.**  This is how JHU encodes their data.  However, the data in
the four counties that Kansas City intersects is not necessarily zero.

For the mapping to HRR and MSA, the counts for Kansas City are dispersed to
these four counties in equal proportions.

### Dukes and Nantucket Counties, Massachusetts

**The counties of Dukes and Nantucket report their figures together,
and we (like JHU) list them under FIPS Code 70002.**  Here are the FIPS codes
for the individual counties:

|County Name        |FIPS Code      |
|-------------------|---------------|
|Dukes County       |25007          |
|Nantucket County   |25019          |

For the mapping to HRR and MSA, the counts for Dukes and Nantucket are
dispersed to the two counties in equal proportions.

The data in the individual counties is expected to be zero.

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
