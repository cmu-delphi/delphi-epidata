---
title: <i>inactive</i> COVID Act Now
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
nav_order: 2
---

# COVID Act Now (CAN)
{: .no_toc}

* **Source name:** `covid-act-now`
* **Earliest issue available:** 2021-03-25
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state, hhs, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY-NC](../covidcast_licensing.md#creative-commons-attribution-noncommercial)

The [COVID Act Now (CAN)](https://covidactnow.org/) data source provides COVID-19 testing statistics, such as positivity rates and total tests performed.
The county-level positivity rates and test totals are pulled directly from CAN using [their API](https://covidactnow.org/data-api).
While CAN provides this data potentially from multiple sources, we only use data that CAN sources from the
[CDC's COVID-19 Integrated County View](https://covid.cdc.gov/covid-data-tracker/#county-view).

Delphi's mirror of the CAN data was deactivated in December 2021 (last issue 2021-12-10) in favor of the [DSEW CPR data](./dsew-cpr.md), which reports the same information under the `covid_naat_pct_positive_7dav` signal.


| Signal                         | Description                                                    |
|--------------------------------|----------------------------------------------------------------|
| `pcr_specimen_positivity_rate` | Proportion of PCR specimens tested that have a positive result |
| `pcr_specimen_total_tests`     | Total number of PCR specimens tested                           |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

We receive county-level positivity rate and total tests from CAN, originating from the CDC.
These quantiles are based on the counts of PCR specimens tested.
They are also already smoothed with a 7-day-average.

For a fixed location $$i$$ and time $$t$$, let $$Y_{it}$$ denote the number of PCR specimens 
tested that have a positive result. Let $$N_{it}$$ denote the total number of PCR specimens tested.
Let $$p_{it}$$ be the PCR-specimen positivity rate as a binomial proportion.

At the county-level, $$p_{it}$$ and $$N_{it}$$ are taken directly from CAN / CDC without modification.
For the sake of aggregating to other geographical levels, we estimate each county's $$Y_{it}$$ as

$$
\hat{Y}_{it} =  N_{it} p_{it}
$$

Let $$G$$ be a set of counties with associated population weights $$w_i$$ for each county $$i \in G$$.
At other geographical levels, the total number of tests $$N_{Gt}$$ 
and our estimate of the positivity rate $$\hat{p}_{Gt}$$ is:

$$
\begin{aligned}
    N_{Gt} &= \sum_{i \in G} w_i N_{it} \\
    \hat{p}_{Gt} &= \frac{ \sum_{i \in G} w_i \hat{Y}_{it} }{ N_{Gt} }
\end{aligned}
$$

Note that in order to more closely mirror the CAN data source, no pseudo-observations
(such as we would typically apply for a Jeffreys prior)
are used in the estimation of these proportions. Instead of using the Jeffreys prior to
more accurately estimate the standard error when the value is zero, we suppress all
entries with zero sample size (total tests performed) and leave those with 0 positive results as-is.

### Standard Error

The estimated standard errors are estimated by:

$$
\begin{aligned}
    \hat{se}(p_{it}) &= \sqrt{\frac{p_{it} (1 - p_{it})}{N_{it}}} \\
    \hat{se}(\hat{p}_{Gt}) &= \sqrt{\frac{\hat{p}_{Gt} (1 - \hat{p}_{Gt})}{N_{Gt}}}
\end{aligned}
$$

### Smoothing

No additional smoothing is done to avoid double-smoothing, since the CAN data
is already smoothed with a 7-day-average.

## Limitations

Estimates for geographical levels beyond counties may be inaccurate because our aggregations
are performed on smoothed values instead of the raw values.
Ideally we would aggregate raw values
then smooth, but the raw values are not accessible in this case.

The reported test positivity rate should not be interpreted as the population positivity rate as
the testing performed are typically not randomly sampled, especially for early data 
with lower testing volumes.

A few counties, most notably in California, are also not covered by this data source.

Entries with zero total tests performed are suppressed, even if it was actually the case that
no tests were performed for the day.

## Lag and Backfill

The lag for these signals varies depending on the reporting patterns of individual counties.
Most counties have their latest data report with a lag of 2 days, while others can take 9 days 
or more, as is the case with California counties.

Revisions are sometimes made to the data. For example, backlogged test results can get assigned to past dates.
The majority of recent test positivity rates do not change substantially with backfill (having a median delta of close to 0).
However, the majority of recent total tests performed is expected to increase in later data revisions (having a median increase of 7%).
Values more than 5 days in the past are expected to remain fairly static (with total tests performed 
having a median increase of 1% of less), as most major revisions have already occurred.

## Source and Licensing

County-level testing data is scraped by [CAN](https://covidactnow.org/) from the
[CDC's COVID-19 Integrated County View](https://covid.cdc.gov/covid-data-tracker/#county-view),
and made available through [CAN's API](https://covidactnow.org/tools).

The data is made available under a [CC BY-NC](../covidcast_licensing.md#creative-commons-attribution-noncommercial) license.
