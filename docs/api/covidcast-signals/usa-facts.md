---
title: USAFacts Cases and Deaths
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# USAFacts Cases and Deaths
{: .no_toc}

* **Source name:** `usa-facts`
* **Number of data revisions since 19 May 2020:** 2
* **Date of last change:** [3 November 2020](../covidcast_changelog.md#usa-facts)
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](#source-and-licensing)

This data source of confirmed COVID-19 cases and deaths is based on reports made
available by [USAFacts](https://usafacts.org/).

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumulative_num` | Cumulative number of confirmed COVID-19 cases |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumulative_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population |
| `confirmed_incidence_num` | `confirmed_7dav_incidence_num` | Number of new confirmed COVID-19 cases, daily |
| `confirmed_incidence_prop` | `confirmed_7dav_incidence_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily |
| `deaths_cumulative_num` | `deaths_7dav_cumulative_num` | Cumulative number of confirmed deaths due to COVID-19 |
| `deaths_cumulative_prop` | `deaths_7dav_cumulative_prop` | Cumulative number of confirmed due to COVID-19, per 100,000 population |
| `deaths_incidence_num` | `deaths_7dav_incidence_num` | Number of new confirmed deaths due to COVID-19, daily |
| `deaths_incidence_prop` | `deaths_7dav_incidence_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily |

These signals are taken directly from the USAFacts [COVID-19 Map by County and
State](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/)
without changes. The 7-day average signals are computed by Delphi by calculating
moving averages of the preceding 7 days, so e.g. the signal for June 7 is the
average of the underlying data for June 1 through 7, inclusive.

This data is similar in intent to our [JHU Cases and Deaths](jhu-csse.md)
source, but as USAFacts collects and aggregates its data in slightly different
ways, the data is not identical. Users should evaluate which source better fits
their needs. Users should evaluate which source better fits their needs, or use
the [combination signal of both USAFacts and JHU data](indicator-combination.md).

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Limitations

USAFacts reports cumulative cases and deaths, so our incidence signals are
calculated by subtracting each day's cumulative count from the previous day.
Since cumulative figures are sometimes corrected or amended by health
authorities, this can sometimes result in negative incidence. Health authorities
can also change reporting standards in ways that dramatically increase the
number of cumulative deaths, resulting in an apparent spike in incidence. This
should be interpreted purely as an artifact of data reporting and correction.

There is no information provided for Puerto Rico in USAFacts's data. There are
unallocated cases/deaths reported for different states, and New York City.
Due to differences in state reporting standards, certain counties are not
reported in the USAFacts data or are reported combined with other counties;
these exceptions are explained below.

## Geographical Exceptions

### New York City

New York City comprises five boroughs, each of which is a county:

|Borough Name       |County Name        |FIPS Code      |
|-------------------|-------------------|---------------|
|Manhattan          |New York County    |36061          |
|The Bronx          |Bronx County       |36005          |
|Brooklyn           |Kings County       |36047          |
|Queens             |Queens County      |36081          |
|Staten Island      |Richmond County    |36085          |

USAFacts reports cases and deaths for each of these counties, but *also* reports
New York City counts not allocated to a specific county. We split unallocated
cases and deaths evenly among the five counties, which results in non-integer
counts.

All NYC counts are mapped to the MSA with CBSA ID 35620, which encompasses all
five boroughs. All NYC counts are mapped to HRR 303, which intersects all five
boroughs (297 also intersects the Bronx, 301 also intersects Brooklyn and
Queens, but absent additional information, we leave all counts in 303).

### Mismatched FIPS Codes

There are two FIPS codes that were changed in 2015 (see the [Census Bureau
documentation](https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.html)),
leading to mismatch between us and USAFacts. We report the data using the FIPS
code used by USAFacts, again to promote consistency and avoid confusion by
external users of the dataset. For the mapping to MSA, HRR, these two counties
are included properly.

|County Name        |State          |"Our" FIPS         |USAFacts FIPS  |
|-------------------|---------------|-------------------|---------------|
|Oglala Lakota      |South Dakota   |46113              |46102          |
|Kusilvak           |Alaska         |02270              |02158 & 02270  |

Besides, Wade Hampton Census Area and Kusilvak Census Area are reported by
USAFacts with FIPS 02270 and 02158 respectively, though there is always 0
cases/deaths reported for Wade Hampton Census Area (02270). [According to the US
Census Bureau](https://www.census.gov/quickfacts/kusilvakcensusareaalaska), Wade
Hampton Census Area has changed name and code from Wade Hampton Census Area,
Alaska (02270) to Kusilvak Census Area, Alaska (02158) effective July 1, 2015.

### Grand Princess Cruise Ship

Data from the [*Grand Princess* cruise
ship](https://en.wikipedia.org/wiki/COVID-19_pandemic_on_Grand_Princess) is
reported by USAFacts as its own distinct geographical area, with FIPS code 6000.
We do not report these cases and deaths in the API.

### Non-Integral Counts

Because the MSA and HRR counts are computed by combining multiple counties,
weighted by their overlap with the MSA or HRR, the count data at those
geographical levels may not be integers.

### Counties Not in our Canonical Dataset

Due to technical limitations in how our system relates ZIP codes, county FIPS
codes, and MSAs or HRRs, a small number of county FIPS codes can't be directly
mapped to MSAs and HRRs. These counties appear correctly in the API, but when
they are aggregated into MSAs and HRRs, our code must first disburse their
counts to other counties that share ZIP codes. This may change the reported MSA
and HRR results slightly.

The full list of affected FIPS codes, and the FIPS codes they are disbursed to,
is

```
SECONDARY_FIPS = [   # generated by notebooks/create-mappings.ipynb
	('51620', ['51093', '51175']),
	('51685', ['51153']),
	('28039', ['28059', '28041', '28131', '28045', '28059', '28109',
                    '28047']),
	('51690', ['51089', '51067']),
	('51595', ['51081', '51025', '51175', '51183']),
	('51600', ['51059', '51059', '51059']),
	('51580', ['51005']),
	('51678', ['51163']),
    ]
```

## Source and Licensing

This data set is republished from the [USAFacts known cases and deaths
datasets](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/),
under the terms of the [Creative Commons Attribution 4.0 International (CC BY
4.0) license](https://creativecommons.org/licenses/by/4.0/).
