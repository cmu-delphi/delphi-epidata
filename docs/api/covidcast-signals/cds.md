---
title: Corona Data Scraper
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Corona Data Scraper
{: .no_toc}

* **Source name:** `cds`
* **First issued:** DATE RELEASED TO API
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source of confirmed COVID-19 cases and tests taken due to COVID-19 is based on reports made available by the Corona Data Scraper.

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumulative_num` | Cumulative number of confirmed COVID-19 cases |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumulative_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population |
| `confirmed_incidence_num` | `confirmed_7dav_incidence_num` | Number of new confirmed COVID-19 cases, daily |
| `confirmed_incidence_prop` | `confirmed_7dav_incidence_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily |
| `tested_cumulative_num` | `tested_7dav_cumulative_num` | Cumulative number of tests taken due to COVID-19 |
| `tested_cumulative_prop` | `tested_7dav_cumulative_prop` | Cumulative number of tests taken due to COVID-19, per 100,000 population |
| `tested_incidence_num` | `tested_7dav_incidence_num` | Number of new tests taken due to COVID-19, daily |
| `tested_incidence_prop` | `tested_7dav_incidence_prop` | Number of new tests taken due to COVID-19 per 100,000 population, daily |
| `raw_pct_positive` | `smoothed_pct_positive` | Percentage of tests that were positive for COVID-19 |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

These `confirmed_cases` and `tested` related signals are taken directly from the Corona Data Scraper without changes. The 7-day average signals are computed by Delphi by calculating moving averages of the preceding 7 days, so e.g. the signal for June 7 is the average of the underlying data for June 1 through 7, inclusive.

The `confirmed_cases` related signals are similar in intent to our JHU Cases and Deaths source, but Corona Data Scraper collects its data from multiple source including JHU-CSSE,  New York Times and cross checks them which results in the descrepancies in reported numbers. Users should evaluate which source better fits their needs.

Delphi derives the `pct_positive` signals using `confirmed_incidence_num` as the numerator and `tested_incidence_num` as the denominator. Invalid results such as `inf` and negative ratios (which are due to the quality of the raw data) will not be reported. For `pct_positive` signals, 

Let $$n$$ be the number of total COVID tests taken over a given time period and a given location. Let $$x$$ be the number of confirmed cases in this location over the given time period. We are interested in estimating the percentage:

$$ p = \frac{100 x}{n} $$

In order to ensure it is statistically meaningful, locations with total number of tests fewer tha 50 will not be reported. 

### Standard Error

We assume the estimates for each time point follow a binomial distribution. The estimated standard error then is:

$$ \text{se} = 100 \sqrt{ \frac{\frac{p}{100}(1- \frac{p}{100})}{N} } $$

### Sample Size

The sample sizes are number of tests taken due to COVID-19 for a certain location on that day . 

### Smoothing

Smoothed estimates are formed by pooling data over time. That is, daily, for each location, we pool all data available in that location over the last 7 days

## Limitations

Corona Data Scraper's data reports cumulative cases and tests, so our incidence signals are calculated by subtracting each day's cumulative count from the previous day. Since cumulative figures are sometimes corrected or amended by health authorities, this can sometimes result in negative incidence. Health authorities can also change reporting standards in ways that dramatically increase the number of cumulative deaths, resulting in an apparent spike in incidence. This should be interpreted purely as an artifact of data reporting and correction.

Corona Data Scraper provides data at county level and state level respectively. They only provide the number of tests for approximately 700 counties. County level reports can be missed for some states entirely. However, Cororna Data Scraper has a good coverage at state level. Because of this, we report msa/hrr level data based on county level information. As for state level data, we use county level aggregates for confirmed cases but state level data directly from the raw for tested. Note that, this will also influence the `pct_positive` signals since the denominators are number of tests taken due to COVID-19 instead of population. 

## Geographical Exceptions

At the state and County (FIPS) level, we report the data _exactly_ as CDS reports their
data, to prevent confusing public consumers of the data. 
The visualization and modeling teams should take note of these exceptions.

### Ignored Areas at State Level
Due to the lack of population information, we ignore the four areas listed below although 
we have dat provided from Corona Data Scraper:
|Name        |
|-------------------|
|Guam     |
|United States Virgin Islands           |
|Northern Mariana Islands              |
|Washington, D.C.          |

### Mismatched FIPS Codes

There are two FIPS codes that were changed in 2015, leading to
mismatch between us and CDS.  We report the data using the FIPS code used
by CDS, again to promote consistency and avoid confusion by external users
of the dataset.  For the mapping to MSA, HRR, these two counties are
included properly.

|County Name        |State          |"Our" FIPS         |CDS FIPS       |
|-------------------|---------------|-------------------|---------------|
|Oglala Lakota      |South Dakota   |46113              |46102          |
|Kusilvak           |Alaska         |02270              |02158          |

Documentation for the changes made by the US Census Bureau in 2015:
https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.html

