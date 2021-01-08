---
title: Quidel
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Quidel
{: .no_toc}

* **Source name:** `quidel`

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## COVID-19 Tests

* **First issued:** 27 July 2020 
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** 22 October 2020
* **Available for:** hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
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

| Signal | Description | First Available |
| --- | --- | --- |
| `covid_ag_raw_pct_positive` | Percentage of antigen tests that were positive for COVID-19, with no smoothing applied. | 00-00-0000 |
| `covid_ag_smoothed_pct_positive` | Percentage of antigen tests that were positive for COVID-19, smoothed by pooling together the last 7 days of tests. | 00-00-0000 |

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

We estimate p across 3 temporal-spatial aggregation schemes:
- daily, at the MSA (metropolitan statistical area) level;
- daily, at the HRR (hospital referral region) level;
- daily, at the state level.

**MSA and HRR levels**: In a given MSA or HRR, suppose $$N$$ COVID tests are taken
in a certain time period, $$X$$ is the number of tests taken with positive
results. If $$N \geq 50$$, we simply use:

$$
p = \frac{100 X}{N}
$$

If $$N < 50$$, we lend $$50 - N$$ fake samples from its home state to shrink the
estimate to the state's mean, which means:

$$
p = 100 \left( \frac{N}{50} \frac{X}{N} + \frac{50 - N}{50}  \frac{X_s}{N_s} \right) 
$$

where $$N_s, X_s$$ are the number of COVID tests and the number of COVID tests
taken with positive results taken in its home state in the same time period.

**State level**: the states with fewer than 50 tests are discarded. For the
rest of the states with sufficient samples,

$$
p = \frac{100 X}{N}
$$

#### Standard Error

We assume the estimates for each time point follow a binomial distribution. The
estimated standard error then is:

$$
\text{se} = 100 \sqrt{ \frac{\frac{p}{100}(1- \frac{p}{100})}{N} } 
$$

#### Smoothing

Smoothed estimates are formed by pooling data over time. That is, daily, for
each location, we first pool all data available in that location over the last 7
days, and we then recompute everything described in the last two
subsections. Pooling in this way makes estimates available in more geographic
areas, as many areas report very few tests per day, but have enough data to
report when 7 days are considered.

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

This data source is based on data provided to us by a lab testing company. They can report on a portion of United States COVID-19 Antigen tests, but not all of them, and so this source only represents those tests known to them. Their coverage may vary across the United States.

### Missingness

When fewer than 50 tests are reported in a state on a specific day, no data is
reported for that area on that day; an API query for all reported states on that
day will not include it.

When fewer than 50 tests are reported in an HRR or MSA on a specific day, and
not enough samples can be filled in from the parent state, no data is reported
for that area on that day; an API query for all reported geographic areas on
that day will not include it.

## Flu Tests

* **First issued:** 20 April 2020
* **Last issued:** 19 May 2020
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))

Data source based on flu lab tests, provided to us by Quidel, Inc. When a
patient (whether at a doctor’s office, clinic, or hospital) has COVID-like
symptoms, doctors may perform a flu test to rule out seasonal flu (influenza),
because these two diseases have similar symptoms. Using this lab test data, we
estimate the total number of flu tests per medical device (a measure of testing
frequency), and the percentage of flu tests that are *negative* (since ruling
out flu leaves open another cause---possibly covid---for the patient's
symptoms), in a given location, on a given day.

The number of flu tests conducted in individual counties can be quite small, so
we do not report these signals at the county level.

The flu test data is no longer updated as of May 19, 2020, as the number of flu
tests conducted during the summer (outside of the normal flu season) is quite
small. The data may be updated again when the Winter 2020 flu season begins.

| Signal | Description |
| --- | --- |
| `raw_pct_negative` | The percentage of flu tests that are negative, suggesting the patient's illness has another cause, possibly COVID-19 |
| `smoothed_pct_negative` | Same as above, but smoothed in time |
| `raw_tests_per_device` | The number of flu tests conducted by each testing device; measures volume of testing |
| `smoothed_tests_per_device` | Same as above, but smoothed in time |
