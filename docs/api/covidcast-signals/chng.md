---
title: Change Healthcare
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Change Healthcare
{: .no_toc}

* **Source name:** `chng`
* **Earliest issue available:** November 4, 2020
* **Number of data revisions since May 19, 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY-NC](../covidcast_licensing.md#creative-commons-attribution-noncommercial)

## Overview

This data source is based on Change Healthcare claims data that has been
de-identified in accordance with HIPAA privacy regulations. Change Healthcare is
a healthcare technology company that aggregates data from many healthcare providers.

The signals under this source are made available under a CC BY-NC license, which
differs from the typical COVIDcast license. You may not use this data for
commercial purposes.

| Signal | Description |
| --- | --- |
| `smoothed_outpatient_covid` | Estimated percentage of outpatient doctor visits with confirmed COVID-19, based on Change Healthcare claims data that has been de-identified in accordance with HIPAA privacy regulations, smoothed in time using a Gaussian linear smoother <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_adj_outpatient_covid` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_outpatient_cli` | Estimated percentage of outpatient doctor visits primarily about COVID-related symptoms, based on Change Healthcare claims data that has been de-identified in accordance with HIPAA privacy regulations, smoothed in time using a Gaussian linear smoother <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_adj_outpatient_cli` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) <br/> **Earliest date available:** 2020-02-01 |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

### COVID Illness

The following estimation method is used for the `*_outpatient_covid` signals.

For a fixed location $$i$$ and time $$t$$, let $$Y_{it}$$
denote the Covid counts and let $$N_{it}$$ be the
total count of visits (the *Denominator*). Our estimate of the COVID-19
percentage is given by

$$
\hat p_{it} = 100 \cdot  \frac{Y_{it}}{N_{it}}
$$

### COVID-Like Illness

The following estimation method is used for the `*_outpatient_cli` signals.

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

### Day-of-Week Adjustment

The fraction of visits due to COVID-19 is dependent on the day of the week. On
weekends, doctors see a higher percentage of acute conditions, so the percentage
of COVID-19 is higher. Each day of the week has a different behavior, and if we do
not adjust for this effect, we will not be able to meaningfully compare the
doctor visits signal across different days of the week. We use a Poisson
regression model to produce a signal adjusted for this effect.

We assume that this weekday effect is multiplicative. For example, if the
underlying rate of COVID-19 on each Monday was the same as the previous Sunday, then
the ratio between the doctor visit signals on Sunday and Monday would be a
constant. Formally, we assume that

$$
\begin{aligned}
\mathbb{E}[Y_{it}] &= \mu_t\\
\log \mu_t &= \alpha_{\text{wd}(t)} + \phi_t,
\end{aligned}
$$

where $$Y_{it}$$ is the observed doctor visits percentage of COVID-19 at time $$t$$,
$$\text{wd}(t) \in \{0, \dots, 6\}$$ is the day-of-week of time $$t$$,
$$\alpha_{\text{wd}(t)}$$ is the corresponding weekday correction, and
$$\phi_t$$ is the corrected doctor visits percentage of COVID-19 at time $$t$$.

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

Once we have estimated values for $$\alpha$$ for the Covid counts, we obtain the
adjusted count

$$\dot{Y}_{it} = Y_{it} / \alpha_{wd(t)}.$$

We then use these adjusted counts to estimate the COVID-19 percentage as described
above.

For the CLI indicator, we apply the same method to the numerator $$Y_{it} =
Y_{it}^{\text{Covid-like}} + \left((Y_{it}^{\text{Flu-like}} +
Y_{it}^{\text{Mixed}}) - Y_{it}^{\text{Flu}}\right).$$

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
working backwards through time. The threshold is set at 100 observations.

### Smoothing

To help with variability, we also employ a local linear regression filter with a
Gaussian kernel. The bandwidth is fixed to approximately cover a rolling 7 day
window, with the highest weight placed on the right edge of the window (the most
recent timepoint).

## Lag and Backfill

Note that because doctor's visits may be reported to Change Healthcare
several days after they occur, these signals are typically available with
several days of lag. This means that estimates for a specific day are only
available several days later.

The amount of lag in reporting can vary, and not all visits are reported with
the same lag. After we first report estimates for a specific date, further data
may arrive about outpatient visits on that date. When this occurs, we issue new
estimates for those dates to backfill any missing data. This means that a
reported estimate for, say, June 10th may first be available in the API on June
14th and subsequently revised on June 16th.

As doctor’s visits data are available at a significant and variable latency, the
signal experiences heavy backfill with data delayed for a couple of weeks.  We
expect estimates available for the most recent 4-6 days to change substantially
in later data revisions (having a median delta of 10% or more). Estimates for
dates more than 45 days in the past are expected to remain fairly static (having
a median delta of 1% or less), as most major revisions have already occurred.

We are currently working on adjustments to correct for this.

## Limitations

This data source is based on data provided to us by Change Healthcare. Change
Healthcare reports on a portion of United States healthcare encounters, but not
all of them, and so this source only represents those encounters known to
them. Their coverage may vary across the United States, but they report on about
45% of all doctor's visits nationally.

Standard errors are not available for this data source.

Due to changes in medical-seeking behavior on holidays, this data source has
upward spikes in the fraction of doctor's visits that are COVID-related around
major holidays (e.g. Memorial Day, July 4, Labor Day, etc.). These spikes are
not necessarily indicative of a true increase of COVID-19 in a location.

Note that due to local differences in health record-keeping practices, estimates
are not always comparable across locations. We are currently working on
adjustments to correct this spatial bias.

## Qualifying Conditions

We receive data on the following six categories of counts:

- Denominator: Daily count of all unique outpatient visits.
- Covid: Daily count of all unique visits with primary ICD-10 code in any of:
{U07.1, B97.21, or B97.29}.
- COVID-like: Daily count of all unique outpatient visits with primary ICD-10 code
	of any of: {U07.1, U07.2, B97.29, J12.81, Z03.818, B34.2, J12.89}.
- Flu-like: Daily count of all unique outpatient visits with primary ICD-10 code
	of any of: {J22, B34.9}. The occurrence of these codes in an area is
	correlated with that area's historical influenza activity, but are
	diagnostic codes not specific to influenza and can appear in COVID-19 cases.
- Mixed: Daily count of all unique outpatient visits with primary ICD-10 code of
	any of: {Z20.828, J12.9}. The occurance of these codes in an area is
	correlated to a blend of that area's COVID-19 confirmed case counts and
	influenza behavior, and are not diagnostic codes specific to either disease.
- Flu: Daily count of all unique outpatient visits with primary ICD-10 code of
	any of: {J09\*, J10\*, J11\*}. The asterisk `*` indicates inclusion of all
	subcodes. This set of codes are assigned to influenza viruses.

For the COVID signal, we consider only the *Denominator* and *Covid* counts.

For the CLI signal, if a patient has multiple visits on the same date (and hence
multiple primary ICD-10 codes), then we will only count one of and in descending
order: *Flu*, *COVID-like*, *Flu-like*, *Mixed*. This ordering tries to account for
the most definitive confirmation, e.g. the codes assigned to *Flu* are only used
for confirmed influenza cases, which are unrelated to the COVID-19 coronavirus.
