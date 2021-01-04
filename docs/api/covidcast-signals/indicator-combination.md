---
title: Indicator Combination
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Indicator Combination
{: .no_toc}

* **Source name:** `indicator-combination`

This source provides signals which are combinations of the other sources,
calculated or composed by Delphi. It is not a primary data source.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Statistical Combination Signals

* **First issued:** 19 May 2020
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#indicator-combination)
* **Available for:** county, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

These signals combine Delphi's indicators---*not* including cases and deaths,
but including other signals expected to be related to the underlying rate of
coronavirus infection---to produce a single indicator. The goal is to provide a
single map of the COVID-19 activity at each geographic level each day that
summarizes other indicators so that users can study its fluctuations over space
and time and not be overwhelmed by having to necessarily monitor many individual
sensors.

* `nmf_day_doc_fbc_fbs_ght`: This signal uses a rank-1 approximation, from a
  nonnegative matrix factorization approach, to identify an underlying signal
  that best reconstructs the Doctor Visits (`smoothed_adj_cli`), Facebook
  Symptoms surveys (`smoothed_cli`), Facebook Symptoms in Community surveys
  (`smoothed_hh_cmnty_cli`), and Search Trends (`smoothed_search`) indicators.
  It does not include official reports (cases and deaths from the `jhu-csse`
  source). Higher values of the combined signal correspond to higher values of
  the other indicators, but the scale (units) of the combination is arbitrary.
  Note that the Search Trends source is not available at the county level, so
  county values of this signal do not use it.
* `nmf_day_doc_fbs_ght`: This signal is calculated in the same way as
  `nmf_day_doc_fbc_fbs_ght`, but does *not* include the Symptoms in Community
  survey signal, which was not available at the time this signal was introduced.
  It also uses `smoothed_cli` from the `doctor-visits` source instead of
  `smoothed_adj_cli`. This signal is deprecated and is no longer updated as of
  May 28, 2020.

### Estimation

Let $$x_{rs}(t)$$ denote the value of sensor $$s$$ on day $$t$$ in region $$r$$
(*not* necessarily mean centered). We aim to construct a single scalar latent
variable each day for every region $$r$$, denoted by $$z_{r}(t)$$, that can
simultaneously reconstruct all other reported sensors. We call this scalar
summary the *combined* indicator signal. Below we describe the method used to
compute the combined signal. For notational brevity, we fix a time $$t$$ and
drop the corresponding index.


#### Optimization Objective

At each time $$t$$ (which in our case has resolution of a day), given a set
$$\mathcal{S}$$ of sensors (with total $$S$$ sensors) and a set $$\mathcal{R}$$
of regions (with total $$R$$ regions), we aim to find a combined indicator that
best reconstructs all sensor observations after being passed through a learned
sensor-specific transformation $$g_{s}(\cdot)$$. That is, for each time $$t$$, we
minimize the sum of squared reconstruction error:

$$
\sum_{s \in \mathcal{S}} \sum_{r \in \mathcal{R}} (x_{rs} - g_{s}(z_{r}))^2,
$$

over combined indicator values $$z = z_{1:R}$$ and candidate transformations $$g
= g_{1:S}$$. To solve the optimization problem, we constrain $$z$$ and $$g$$ in
specific ways as explained next.

#### Optimization Constraints

We constrain the sensor-specific transformation $$g_{s}$$ to be a linear
function such that $$g_{s}(x) = a_{s} x$$. Then, the transformations $$g$$ are simply
various rescalings $$a = a_{1:S}$$, and the objective can be more succinctly
written as

$$
\min_{z \in\mathbb{R}^{R}, a\in\mathbb{R}^S} \|X - z a^\top\|_F^2.
$$

where $$X$$ is the $$R \times S$$ matrix of sensor values $$x_{rs}$$ (each row
corresponds to a region and each column to a sensor value). Additionally, to
make the parameters identifiable, we constrain the norm of $$a$$.

If $$u_1, v_1, \sigma_1$$ represent the first left singular vector, right singular
vector, and singular value of $$X$$, then the well-known solution to
this objective is given by $$z = \sigma_1 u_1$$ and $$a = v_1$$, which is
similar to the principal component analysis (PCA). However, in contrast to PCA,
we *do not remove the mean signal* from each column of $$X$$. To the extent
that the mean signals are important for reconstruction, they are reflected in
$$z$$.

Furthermore, since all sensors should be increasing in the combined indicator
value, we further constrain the entries of $$a$$ to be nonnegative. Similarly,
since all sensors are nonnegative, we also constrain the entries of $$z$$ to be
nonnegative. This effectively turns the optimization problem into a non-negative
matrix factorization problem as follows:

$$
\min_{z \in\mathbb{R}^{R}: z \ge 0, a\in\mathbb{R}^S : a \ge 0} \|X - z a^\top\|_F^2.
$$

### Data Preprocessing

#### Scaling of Data

Since different sensor values are on different scales, we perform global column
scaling. Before approximating the matrix $$X$$, we scale each column by the root
mean square observed entry of that sensor over all of time (so that the same
scaling is applied each day).

Note that one might consider local column scaling before approximating the
matrix $$X$$, where we scale each column by its root mean square observed entry
each so that each sensor has (observed) second moment equal to 1 (each day). But
this suffers from the issue that the locally scaled time series for a given
sensor and region can look quite different from the unscaled time series. In
particular, increasing trends can be replaced with decreasing trends and, as a
result, the derived combined indicator may look quite distinct from any unscaled
sensor. This can be avoided with global column scaling.

#### Lags and Sporadic Missingness

The matrix $$X$$ is not necessarily complete and we may have entries missing.
Several forms of missingness arise in our data. On certain days, all
observations of a given sensor are missing due to release lag. For example,
Doctor Visits is released several days late. Also, for any given region and
sensor, a sensor may be available on some days but not others due to sample size
cutoffs. Additionally, on any given day, different sensors are observed in
different regions.

To ensure that our combined indicator value has comparable scaling over time and
is free from erratic jumps that are just due to missingness, we use the
following imputation strategies:
* *lag imputation*, where if a sensor is missing for all regions on a given day,
  we copy all observations from the last day on which any observation was
  available for that sensor;
* *recent imputation*, where if a sensor value if missing on a given day is
  missing but at least one of past $$T$$ values is observed, we impute it with
  the most recent value. We limit $$T$$ to be 7 days.

#### Persistent Missingness

Even with the above imputation strategies, we still have issues that some
sensors are never available in a given region. The result is that combined
indicator values for that region that may be on a completely different scale
from values in other regions with additional observed sensors. This can only be
overcome by regularizing or pooling information across space. Note that a very
similar problem occurs when a sensor is unavailable for a very long period of
time (so long that recent imputation is inadvisable and avoided by setting $$T =
7$$ days).

We deal with this problem by *geographic imputation*, where we impute values from
regions that share a higher level of aggregation (e.g., the median observed score
in an MSA or state), or by imputing values from megacounties (since the counties
in question are missing and hence should be reflected in the rest of state
estimate). The order in which we look to perform geographic imputations is
observed values from megacounties, followed by median
observed values in the geographic hierarchy (county, MSA, state, or country).
We chose this imputation sequence among different options by evaluating 
their effectiveness to mimic the actual observed sensor values in validation experiments.

### Standard Errors

We compute standard errors for the combined indicator using the bootstrap.
The input data sources are resampled individually, and the combined indicator
is recomputed for the resampled input.  Then, the standard error is given by
taking the standard deviation of the resampled combined indicators.  We take
$$B=100$$ bootstrap replicates and use the jackknife to verify that
for this number of replicates, estimated variance is small relative to the
variance of variances.

The resampling method for each input source is as follows:

* *Doctor Visits:* We inject a single additional observation with value 0.5 into
  the calculation of the proportion, and then resample from the binomial
  distribution, using the "Jeffreysized" proportion and sample size $$n+1$$.
* *Symptom Survey:* We first inject a single additional observation with value
  0.35 into the calculation of the proportion $$p$$. Then, we sample an average of
  $$n+1$$ independent $$\text{Binomial}(p, m)/m$$ variables, where we choose $$m$$
  so the household variance $$p(1-p)/m = n\text{SE}^2$$, which is equivalent to
  sampling $$\text{Binomial}(p, mn) / mn$$. The prior proportion of 0.35 was
  chosen to match the resampling distribution with the original distribution.
* *Facebook Community Survey:* We resample from the binomial distribution, with
  the reported proportion and sample size.
* *Google Health Trends:* Because we do not have access to the sampling
  distribution, we do not resample this signal.


## Compositional Signals: Confirmed Cases and Deaths

* **First issued:** 7 July 2020
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [12 October 2020](../covidcast_changelog.md#indicator-combination)
* **Available for:** county, msa, hrr, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))

These signals combine the cases and deaths data from JHU and USA Facts. This is
a straight composition: the signals below use the [JHU signal data](jhu-csse.md)
for Puerto Rico, and the [USA Facts signal data](usa-facts.md) everywhere else.
Consult each signal's documentation for information about geographic reporting,
backfill, and other limitations.

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
