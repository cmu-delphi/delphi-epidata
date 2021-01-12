---
title: Doctor Visits
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Doctor Visits
{: .no_toc}

* **Source name:** `doctor-visits`
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** 9 November 2020
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)


## Overview

This data source is based on information about outpatient visits, provided to us
by health system partners. Using this outpatient data, we estimate the
percentage of COVID-related doctor's visits in a given location, on a given day.

| Signal | Description |
| --- | --- |
| `smoothed_cli` | Estimated percentage of outpatient doctor visits primarily about COVID-related symptoms, based on data from health system partners, smoothed in time using a Gaussian linear smoother |
| `smoothed_adj_cli` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

### COVID-Like Illness

For a fixed location $$i$$ and time $$t$$, let $$Y_{it}^{\text{Covid-like}}$$,
$$Y_{it}^{\text{Flu-like}}$$, $$Y_{it}^{\text{Mixed}}$$, $$Y_{it}^{\text{Flu}}$$
denote the correspondingly named ICD-filtered counts and let $$N_{it}$$ be the
total count of visits (the *Denominator*). Our estimate of the CLI percentage is
given by

$$
\hat p_{it} = 100 \cdot  \frac{Y_{it}^{\text{Covid-like}} +
	\left((Y_{it}^{\text{Flu-like}} + Y_{it}^{\text{Mixed}}) -
	Y_{it}^{\text{Flu}}\right)}{N_{it}}
$$

The estimated standard error is:

$$
\widehat{\text{se}}(\hat{p}_{it}) =  100 \sqrt{\frac{\frac{\hat{p}_{it}}{100}(1-\frac{\hat{p}_{it}}{100})}{N_{it}}}.
$$

Note the quantity above is not going to be correct for multiple reasons: smoothing/day of
week adjustments/etc.

### Day-of-Week Adjustment

The fraction of visits due to CLI is dependent on the day of the week. On
weekends, doctors see a higher percentage of acute conditions, so the percentage
of CLI is higher. Each day of the week has a different behavior, and if we do
not adjust for this effect, we will not be able to meaningfully compare the
doctor visits signal across different days of the week. We use a Poisson
regression model to produce a signal adjusted for this effect.

We assume that this weekday effect is multiplicative. For example, if the
underlying rate of CLI on each Monday was the same as the previous Sunday, then
the ratio between the doctor visit signals on Sunday and Monday would be a
constant. Formally, we assume that

$$
\begin{aligned}
\mathbb{E}[Y_{it}] &= \mu_t\\
\log \mu_t &= \alpha_{\text{wd}(t)} + \phi_t,
\end{aligned}
$$

where $$Y_{it}$$ is the observed doctor visits percentage of CLI at time $$t$$,
$$\text{wd}(t) \in \{0, \dots, 6\}$$ is the day-of-week of time $$t$$,
$$\alpha_{\text{wd}(t)}$$ is the corresponding weekday correction, and
$$\phi_t$$ is the corrected doctor visits percentage of CLI at time $$t$$.

For simplicity, we assume that the weekday parameters do not change over time or
location. To fit the $$\alpha$$ parameters, we minimize the following convex
objective function:

$$
f(\alpha, \phi | \mu) = -\log \ell (\alpha,\phi|\mu) + \lambda ||\Delta^3 \phi||_1
$$

where $$\ell$$ is the Poisson likelihood and $$\Delta^3 \phi$$ is the third
differences of $$\phi$$. For identifiability, we constrain the sum of $$\alpha$$
to be zero by setting Sunday's fixed effect to be the negative sum of the other
weekdays. The penalty term encourages the $$\phi$$ curve to be smooth and
produces meaningful $$\alpha$$ values.

Once we have estimated values for $$\alpha$$ for each type of count $$k$$ in
{*COVID-like*, *Flu-like*, *Mixed*, *Flu*}, we obtain the adjusted count

$$\dot{Y}_{it}^k = Y_{it}^k / \alpha_{wd(t)}.$$

We then use these adjusted counts to estimate the CLI percentage as described
above.

### Backwards Padding

To help with the reporting delay, we perform the following simple
correction on each location. At each time $$t$$, we consider the total visit
count. If the value is less than a minimum sample threshold, we go back to the
previous time $$t-1$$, and add this visit count to the previous total, again
checking to see if the threshold has been met. If not, we continue to move
backwards in time until we meet the threshold, and take the estimate at time
$$t$$ to be the average over the smallest window that meets the threshold. We
enforce a hard stop to consider only the past 7 days, if we have not yet met the
threshold during that time bin, no estimate will be produced. If, for instance,
at time $$t$$, the minimum sample threshold is already met, then the estimate
only contains data from time $$t$$. This is a dynamic-length moving average,
working backwards through time. The threshold is set at 500 observations.

### Smoothing

To help with variability, we also employ a local linear regression filter with a
Gaussian kernel. The bandwidth is fixed to approximately cover a rolling 7 day
window, with the highest weight placed on the right edge of the window (the most
recent timepoint). Given this smoothing step, the standard error estimate shown
above is not exactly correct, as the calculation is done post-smoothing.

## Lag and Backfill

Note that because doctor's visits may be reported to the health system partners
several days after they occur, these signals are typically available with
several days of lag. This means that estimates for a specific day are only
available several days later. 

The amount of lag in reporting can vary, and not all visits are reported with
the same lag. After we first report estimates for a specific date, further data
may arrive about outpatients visits on that date. When this occurs, we issue new
estimates for those dates that include the most recent data reports. This means
that a reported estimate for, June 10th, may first be available in the API on
June 14th and subsequently revised on June 16th.

As insurance claims are available at a significant and variable latency, the
signal experiences heavy backfill with data delayed for a couple of weeks.  We
expect estimates available for the most recent 5-7 days to change substantially
in later data revisions (having a median delta of 10% or more). Estimates for
dates more than 50 days in the past are expected to remain fairly static (having
a median delta of 1% or less), as most major revisions have already occurred.

See our [blog post](https://delphi.cmu.edu/blog/2020/11/05/a-syndromic-covid-19-indicator-based-on-insurance-claims-of-outpatient-visits/#backfill) for more information on backfill.

## Limitations

This data source is based on outpatient visit data provided to us by health
system partners. The partners can report on a portion of United States
outpatient doctor's visits, but not all of them, and so this source only
represents those visits known to them. Their coverage may vary across the United
States.

Standard errors are not available for this data source.

Due to changes in medical-seeking behavior on holidays, this data source has
upward spikes in the fraction of doctor's visits that are COVID-related around
major holidays (e.g. Memorial Day, July 4, Labor Day, etc.). These spikes are
not necessarily indicative of a true increase of COVID-like illness in a
location.

Note that due to local differences in health record-keeping practices, estimates
are not always comparable across locations. We are currently working on
adjustments to correct this spatial bias.

## Qualifying Conditions

We receive data on the following five categories of counts:

- Denominator: Daily count of all unique outpatient visits.
- COVID-like: Daily count of all unique outpatient visits with primary ICD-10 code
	of any of: {U071, U072, B9729, J1281, Z03818, B342, J1289}.
- Flu-like: Daily count of all unique outpatient visits with primary ICD-10 code
	of any of: {J22, B349}. The occurrence of these codes in an area is
	correlated with that area's historical influenza activity, but are
	diagnostic codes not specific to influenza and can appear in COVID-19 cases.
- Mixed: Daily count of all unique outpatient visits with primary ICD-10 code of
	any of: {Z20828, J129}. The occurance of these codes in an area is
	correlated to a blend of that area's COVID-19 confirmed case counts and
	influenza behavior, and are not diagnostic codes specific to either disease.
- Flu: Daily count of all unique outpatient visits with primary ICD-10 code of
	any of: {J09\*, J10\*, J11\*}. The asterisk `*` indicates inclusion of all
	subcodes. This set of codes are assigned to influenza viruses.

If a patient has multiple visits on the same date (and hence multiple primary
ICD-10 codes), then we will only count one of and in descending order: *Flu*,
*COVID-like*, *Flu-like*, *Mixed*. This ordering tries to account for the most
definitive confirmation, e.g. the codes assigned to *Flu* are only used for
confirmed influenza cases, which are unrelated to the COVID-19 coronavirus.
