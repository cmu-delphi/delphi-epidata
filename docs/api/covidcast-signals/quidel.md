---
title: Quidel
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---

# Quidel
{: .no_toc}

* **Source name:** `quidel`

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Accessibility: Delphi-internal only

## COVID-19 Tests

* **Earliest issue available:** July 29, 2020 
* **Number of data revisions since May 19, 2020:** 1
* **Date of last change:** October 22, 2020
* **Available for:** county, hrr, msa, state, HHS, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

Data source based on COVID-19 Antigen tests, provided to us by Quidel, Inc. When
a patient (whether at a doctor’s office, clinic, or hospital) has COVID-like
symptoms, doctors may order an antigen test. An antigen test can detect parts of
the virus that are present during an active infection. This is in contrast with
antibody tests, which detect parts of the immune system that react to the virus,
but which persist long after the infection has passed. Quidel began providing us
with test data starting May 9, 2020, and data volume increased to statistically
meaningful levels starting May 26, 2020.

| Signal | Description |
| --- | --- |
| `covid_ag_raw_pct_positive` | Percentage of antigen tests that were positive for COVID-19 (all ages), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_raw_pct_positive_age_0_4` | Percentage of antigen tests that were positive for COVID-19 (ages 0-4), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_raw_pct_positive_age_5_17` | Percentage of antigen tests that were positive for COVID-19 (ages 5-17), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_raw_pct_positive_age_18_49` | Percentage of antigen tests that were positive for COVID-19 (ages 18-49), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_raw_pct_positive_age_50_64` | Percentage of antigen tests that were positive for COVID-19 (ages 50-64), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_raw_pct_positive_age_65plus` | Percentage of antigen tests that were positive for COVID-19 (ages 65+), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_raw_pct_positive_age_0_17` | Percentage of antigen tests that were positive for COVID-19 (ages 0-17), with no smoothing applied. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive` | Percentage of antigen tests that were positive for COVID-19 (all ages), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive_age_0_4` | Percentage of antigen tests that were positive for COVID-19 (ages 0-4), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive_age_5_17` | Percentage of antigen tests that were positive for COVID-19 (ages 5-17), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive_age_18_49` | Percentage of antigen tests that were positive for COVID-19 (ages 18-49), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive_age_50_64` | Percentage of antigen tests that were positive for COVID-19 (ages 50-64), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive_age_65plus` | Percentage of antigen tests that were positive for COVID-19 (ages 65+), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |
| `covid_ag_smoothed_pct_positive_age_0_17` | Percentage of antigen tests that were positive for COVID-19 (ages 0-17), smoothed by pooling together the last 7 days of tests. <br/> **Earliest date available:** 2020-05-26 |

### Estimation

The source data from which we derive our estimates contains a number of features
for every test, including localization at 5-digit Zip Code level, a TestDate and
StorageDate, patient age, and unique identifiers for the device on which the
test was performed, the individual test, and the result. Multiple tests are
stored on each device.

Let $$n$$ be the number of total COVID tests taken over a given time period and a
given location (the test result can be negative, positive, or invalid). Let $$x$$ be the
number of tests taken with positive results in this location over the given time
period. We are interested in estimating the percentage of positive tests which
is defined as:

$$
p = \frac{100 x}{n}
$$

We estimate p across 6 temporal-spatial aggregation schemes:
- daily, at the county level;
- daily, at the MSA (metropolitan statistical area) level;
- daily, at the HRR (hospital referral region) level;
- daily, at the state level;
- daily, at the HHS level;
- daily, at the US national level.

#### Standard Error

We assume the estimates for each time point follow a binomial distribution. The
estimated standard error then is:

$$
\text{se} = 100 \sqrt{ \frac{\frac{p}{100}(1- \frac{p}{100})}{N} } 
$$

#### Smoothing

We add two kinds of smoothing to the smoothed signals:

##### Temporal Smoothing
Smoothed estimates are formed by pooling data over time. That is, daily, for
each location, we first pool all data available in that location over the last 7
days, and we then recompute everything described in the two subsections above. 

Pooling in this way makes estimates available in more geographic areas, as many areas 
report very few tests per day, but have enough data to report when 7 days are considered.

##### Geographical Smoothing

**County, MSA and HRR levels**: In a given County, MSA or HRR, suppose $$N$$ COVID tests 
are taken in a certain time period, $$X$$ is the number of tests taken with positive
results. 


For smoothed signals, after taking the temporal pooling,
- if $$N \geq 50$$, we still use:
$$
p = \frac{100 X}{N}
$$
- if $$25 \leq N < 50$$, we lend $$50 - N$$ fake samples from its parent state to shrink the
estimate to the state's mean, which means:
$$
p = 100 \left( \frac{N}{50} \frac{X}{N} + \frac{50 - N}{50}  \frac{X_s}{N_s} \right) 
$$
where $$N_s, X_s$$ are the number of COVID tests and the number of COVID tests
taken with positive results taken in its parent state in the same time period.
A parent state is defined as the state with the largest proportion of the population 
in this county/MSA/HRR.

Counties with sample sizes smaller than 50 are merged into megacounties for 
the raw signals; counties with sample sizes smaller than 25 are merged into megacounties for
the smoothed signals.

**State level, HHS level, National level**: locations with fewer than 50 tests are discarded. For the remaining locations,
$$
p = \frac{100 X}{N}
$$

### Lag and Backfill

Because testing centers may report their data to Quidel several days after they
occur, these signals are typically available with 5-6 days of lag. This
means that estimates for a specific day first become available 5-6 days
later.

The amount of lag in reporting can vary, and not all tests are reported with the
same lag. After we first report estimates for a specific date, further data may
arrive about tests that occurred on that date, sometimes six weeks later or
more. When this happens, we issue new estimates for those dates. This means that
a reported estimate for, say, June 10th may first be available in the API on
June 14th and subsequently revised on June 16th.

### Limitations

This data source is based on data provided to us by a lab testing company. They can report on a portion of United States COVID-19 Antigen tests, but not all of them, and so this source only represents those tests known to them. Their coverage may vary across the United States. The coverage of the signals for some age groups (e.g. age 0-4 and age 65+) are extremely limited at HRR and MSA level, and can even be limited at state level on weekends. 

### Missingness

When fewer than 50 tests are reported in a state/a HHS region/US on a specific day, no data is
reported for that area on that day; an API query for all reported states on that
day will not include it.

When fewer than 50 tests are reported in a county, HRR or MSA on a specific day, and
not enough samples can be filled in from the parent state for smoothed signals specifically, 
no data is reported for that area on that day; an API query for all reported geographic areas on
that day will not include it.

## Flu Tests (inactive)
These signals were updated until May 19, 2020. Documentation is still available on the [inactive Quidel page](quidel-inactive.md).