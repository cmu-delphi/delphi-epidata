---
title: Change Healthcare
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Change Healthcare
{: .no_toc}

* **Source name:** `changehc`
* **First issued:** November 4, 2020
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source is based on information about outpatient visits, provided to
us by Change Healthcare. Change Healthcare is a healthcare technology company
that provides us with information about outpatient visits, which they aggregate
from many healthcare providers. Using this outpatient data, we estimate the
percentage of COVID-related doctor's visits in a given location, on a given day.

| Signal | Description |
| --- | --- |
| `smoothed_covid` | Estimated percentage of outpatient doctor visits with confirmed COVID-19, based on data from Change Healthcare, smoothed in time using a Gaussian linear smoother |
| `smoothed_adj_covid` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Lag and Backfill

Note that because doctor's visits may be reported to Change Healthcare
several days after they occur, these signals are typically available with
several days of lag. This means that estimates for a specific day are only
available several days later.

The amount of lag in reporting can vary, and not all visits are reported with
the same lag. After we first report estimates for a specific date, further data
may arrive about outpatient visits on that date. When this occurs, we issue new
estimates for those dates. This means that a reported estimate for, say, June
10th may first be available in the API on June 14th and subsequently revised on
June 16th.

## Limitations

This data source is based on outpatient visit data provided to us by Change
Healthcare. Change Healthcare reports on a portion of United States
outpatient doctor's visits, but not all of them, and so this source only
represents those visits known to them. Their coverage may vary across the United
States, but they report on about 45% of all doctor's visits nationally.

Standard errors are not available for this data source.

Due to changes in medical-seeking behavior on holidays, this data source has
upward spikes in the fraction of doctor's visits that are COVID-related around
major holidays (e.g. Memorial Day, July 4, Labor Day, etc.). These spikes are
not necessarily indicative of a true increase of COVID-like illness in a
location.

## Qualifying Conditions

We receive data on the following two categories of counts:

- Denominator: Daily count of all unique outpatient visits.
- Covid: Daily count of all unique visits with primary ICD-10 code in any of:
{U071, U072, B9721, or B9729}.

## Estimation

### COVID-Like Illness

For a fixed location $i$ and time $t$, let $Y_{it}$
denote the Covid counts and let $N_{it}$ be the
total count of visits (the *Denominator*). Our estimate of the CLI percentage is
given by

$$
\hat p_{it} = 100 \cdot  \frac{Y_{it}}{N_{it}}
$$

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

where $Y_{it}$ is the observed doctor visits percentage of CLI at time $t$,
$\text{wd}(t) \in \{0, \dots, 6\}$ is the day-of-week of time $t$,
$\alpha_{\text{wd}(t)}$ is the corresponding weekday correction, and
$\phi_t$ is the corrected doctor visits percentage of CLI at time $t$.

For simplicity, we assume that the weekday parameters do not change over time or
location. To fit the $\alpha$ parameters, we minimize the following convex
objective function:

$$
f(\alpha, \phi | \mu) = -\log \ell (\alpha,\phi|\mu) + \lambda ||\Delta^3 \phi||_1
$$

where $\ell$ is the Poisson likelihood and $\Delta^3 \phi$ is the third
differences of $\phi$. For identifiability, we constrain the sum of $\alpha$
to be zero by setting Sunday's fixed effect to be the negative sum of the other
weekdays. The penalty term encourages the $\phi$ curve to be smooth and
produces meaningful $\alpha$ values.

Once we have estimated values for $\alpha$ for the Covid counts, we obtain the
adjusted count

$$\dot{Y}_{it} = Y_{it} / \alpha_{wd(t)}.$$

We then use these adjusted counts to estimate the CLI percentage as described
above.

### Backwards Padding

To help with the reporting delay, we perform the following simple
correction on each location. At each time $t$, we consider the total visit
count. If the value is less than a minimum sample threshold, we go back to the
previous time $t-1$, and add this visit count to the previous total, again
checking to see if the threshold has been met. If not, we continue to move
backwards in time until we meet the threshold, and take the estimate at time
$t$ to be the average over the smallest window that meets the threshold. We
enforce a hard stop to consider only the past 7 days, if we have not yet met the
threshold during that time bin, no estimate will be produced. If, for instance,
at time $t$, the minimum sample threshold is already met, then the estimate
only contains data from time $t$. This is a dynamic-length moving average,
working backwards through time. The threshold is set at 100 observations.

### Smoothing

To help with variability, we also employ a local linear regression filter with a
Gaussian kernel. The bandwidth is fixed to approximately cover a rolling 7 day
window, with the highest weight placed on the right edge of the window (the most
recent timepoint).
