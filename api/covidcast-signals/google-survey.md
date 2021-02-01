---
title: Google Symptom Surveys
parent: Inactive Signals
grand_parent: COVIDcast Epidata API
---

# Google Symptom Surveys
{: .no_toc}

* **Source name:** `google-survey`
* **Earliest issue available:** April 29, 2020
* **Number of data revisions since May 19, 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

## Overview

Data source based on Google-run symptom surveys, through publisher websites,
their Opinions Reward app, and similar applications. Respondents can opt to skip
the survey and complete a different one if they prefer not to answer. The survey
is just one question long, and asks "Do you know someone in your community who
is sick (fever, along with cough, or shortness of breath, or difficulty
breathing) right now?" Using this survey data, we estimate the percentage of
people in a given location, on a given day, that *know somebody who has a
COVID-like illness*. This estimates a similar quantity to the `*_cmnty_cli`
signals from the [Symptom Surveys](fb-survey.md) (`fb-survey`) source, but using
a different survey population and recruitment method.

The survey sampled from all counties with greater than 100,000 population, along
with a separate random sample from each state. This means that the megacounties
(discussed in the [COVIDcast API documentation](../covidcast.md)) are always the
counties with populations smaller than 100,000, and megacounty estimates are
created by combining the state-level survey with the observed county surveys.

These surveys were run daily until May 15, 2020. After that date, new national
data will not be collected regularly, although the surveys may be deployed in
specific geographical areas as needed to support forecasting efforts.

| Signal | Description |
| --- | --- |
| `raw_cli` | Estimated percentage of people who know someone in their community with COVID-like illness <br/> **Earliest date available:** 2020-04-11 |
| `smoothed_cli` | Estimated percentage of people who know someone in their community with COVID-like illness, smoothed in time [as described below](#smoothing) <br/> **Earliest date available:** 2020-04-11 |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Let $$Y$$ be the number of people who know someone in their community with
COVID-like illness or CLI, over a given time period and in a given location, and
let $$N$$ be the number of people in this location who do *not* know someone in
their community with CLI. We are interested in the proportion

$$
p = \frac{Y}{Y+N}.
$$

Since the Google Surveys system provides estimated counties for each respondent,
we are able to report $$p$$ for counties, MSAs, HRRs, and states. Our current
rule-of-thumb is to discard any estimate (whether at a county, MSA, HRR, or
state level) that is composed of fewer than 100 survey responses.

At the county level, MSA, and HRR levels, our estimation procedure is fairly
simple, and is outlined below. Estimation for mega-counties and states is more
complex, and deferred to the next subsection.

### County Level

Recall that we run surveys separately (in a stratified manner) in each county.
In a given county, if $$Y$$ denotes the number of respondents who know someone
in their community with CLI, $$N$$ denotes the total number who do not, and $$n
= Y + N$$ the number of "yes" and "no" responses combined, then to estimate
$$p$$ in the county, we simply use:

$$
\hat{p} = \frac{Y}{n}.
$$

Its estimated standard error is:

$$
\widehat{\text{se}}(\hat{p}) = \sqrt{\frac{\hat{p}(1-\hat{p})}{n}},
$$

which is the plug-in estimate of the standard error of the estimator, treating
$$n$$ as fixed.

### MSA and HRR Levels

Suppose a given MSA or HRR contains $$m$$ counties. In county $$i$$, let $$Y_i$$ denote the
number of "yes" responses, $$N_i$$ denote the number of "no" responses, and
$$n_i = Y_i + N_i$$ the total number of yes and no responses. Let $$\hat p_i =
Y_i/n_i$$ be the estimate for each county. Also, let $$k_i$$ denote the
population of county $$i$$, and let $$k = \sum_{i=1}^m k_i$$ denote the total
population of all surveyed counties within the MSA or HRR.

Our estimator is then

$$
\hat{p} = \sum_{i=1}^m \frac{k_i}{k} \hat{p}_i,
$$

the standard stratified sampling estimate of $$p$$. Its estimated standard error
is

$$
\hat{p} = \sqrt{\sum_{i=1}^m \Big(\frac{k_i}{k}\Big)^2
  \frac{\hat{p}_i(1-\hat{p}_i)}{n_i}},
$$

again the plug-in estimate of standard error of the estimator.

### State and Mega-County Estimates

State estimates are somewhat complicated by the multi-resolution nature of
sampling within a state: recall that we run surveys directly in each state, but
also in directly in all of its counties with more than 100,000 population. In
order to combine state and county level surveys into a state-level community
%CLI estimate, we use a Bayesian approach.

For *every* county $$i$$ in the state, irrespective of whether the county was
surveyed, let $$(Y_{c,i},N_{c,i})$$ represent the number of observed yes and no
responses, and define $$n_{c,i} = Y_{c,i} + N_{c,i}$$. Let $$m_{c,i}$$ be the county
population, and let $$p_{c,i}^*$$ represent the true fraction of individuals in
county $$i$$ who would have responded yes (assuming all individuals would have
responded yes or no and ignoring that "unsure" is a valid option). Note that for a
county not surveyed, we have $$Y_{c,i} = N_{c,i} = n_{c,i} = 0$$.

For the state survey, let $$(Y_s,N_s)$$ be the number of observed yes and no
responses, and define $$n_{s} = Y_{s} + N_{s}$$. Let $$m_{s}$$ be the state
population, and let

$$
p_{s}^* = \sum_{i} m_{c,i} p_{c,i}^*/m_s
$$

represent the true fraction of individuals in the state who would have responded
yes (assuming all individuals would have responded yes or no and ignoring that
unsure is a valid option).

Suppose that we assume the county probabilities $$p_{c,i}^*$$ are drawn
independently from a common $$\operatorname{Beta}(a,b)$$ prior.

Maximum a posteriori (MAP) estimates $$\hat{p}_{c,i}$$ of $$p_{c,i}^*$$
can be obtained for all counties $$i$$ by maximizing

$$
\begin{aligned}
    &Y_s \log(p_s) + N_s \log(1-p_s) +
    \sum_{i} \tilde{Y}_{c,i} \log (p_{c,i}) + \tilde{N}_{c,i} \log(1 - p_{c,i}) \\
    &=
    Y_s \log\left(\sum_{i} m_{c,i} p_{c,i}/m_s\right) + N_s \log\left(1-\sum_{i}
    m_{c,i} p_{c,i}/m_s\right) \\
    &+
    \sum_{i} \tilde{Y}_{c,i} \log (p_{c,i}) + \tilde{N}_{c,i} \log(1 - p_{c,i})
\end{aligned}
$$

over $$p_{c,i}$$ subject to

$$
\begin{aligned}
    0 &\leq p_{c,i} & \forall i &: \tilde{Y}_{c,i} = 0 \text{ and} \\
    p_{c,i} &\leq 1 & \forall i &: \tilde{N}_{c,i} = 0,
\end{aligned}
$$

where

$$
(\tilde{Y}_{c,i},\tilde{N}_{c,i},\tilde{n}_{c,i})=(Y_{c,i}+a-1, N_{c,i}+b-1, \tilde{Y}_{c,i}+\tilde{N}_{c,i})
$$

are pseudo-counts induced by the prior.
Then the MAP estimate for the state probability is given by

$$
\hat{p}_s = \sum_{i} m_{c,i} \hat{p}_{c,i}/m_s.
$$

For the megacounty, we can lump all unsurveyed counties together into a single
"other" county with associated population $$m_o = \sum_{\text{unsurveyed } i}
m_{c,i}$$ and estimated proportion given by

$$
\hat{p}_o = \sum_{\text{unsurveyed } i} m_{c,i} \hat{p}_{c,i}/m_o.
$$

Notably, the maximization problem is concave and coincides with maximum
likelihood estimation when $$a = b = 1$$.

#### Empirical Bayes and Prior Choice

Selecting $$a, b > 1$$ ensures that all pseudo-counts are non-zero and prevents
degenerate estimates of the form $$p_{c,i} \in \{0,1\}$$ by shrinking each
county estimate, even the unsurveyed ones, toward some relevant prior value.

We currently set the prior hyperparameters so that the prior mode
$$\frac{a-1}{(a-1)+(b-1)}$$ matches the pooled mean of surveyed county
proportions and each county receives $$\tilde{n}$$ additional pseudocounts from
the prior:

$$
\begin{aligned}
a &= 1 + \tilde{n}\hat{\mu}\\
b &= 1 + \tilde{n}(1-\hat{\mu}), \text{ for}\\
\hat{\mu} &= \frac{\sum_{\text{surveyed } i} Y_{c,i}}{\sum_{\text{surveyed } i} n_{c,i}}.
\end{aligned}
$$

The number of pseudocounts $$\tilde n$$ is currently set to 5, although it may
be possible to choose a value that varies to minimize mean squared error.

#### Modification for when State Survey is Missing

When state survey results are missing due to problems in the sampling process,
the MAP estimate of the megacounties can be obtained by directly taking the
prior mode:

$$
\hat p_o = \frac{a-1}{(b-1)+(a-1)} = \hat \mu = \sum_{\text{surveyed } i}
Y_{c,i} / \sum_{\text{surveyed } i} n_{c,i}
$$

and the state MAP estimate is the weighted average of the individual
county-level estimates, reproduced here:

$$
\hat{p}_s = \frac{m_o \hat p_o + \sum_{\text{surveyed } i} m_{c,i} \hat
p_{c,i}}{m_s} = \frac{\sum_{\text{surveyed } i} m_{c,i} \hat p_{c,i}}{m_s-m_o}.
$$

Since this estimator is clearly biased, the variance is not representative of
the amount of uncertainty in the estimate. Our alternative to reporting variance
is to report the MSE of the MAP estimate:

$$
\text{MSE}(\hat p_s) =
\left(\sum_{\text{surveyed } i} \frac{\hat{p}_{c,i}
\left(1-\hat{p}_{c,i}\right)}{n_i}\left(\frac{m_i}{m}\right)^2\right) +
\left(\sum_{\text{unsurveyed } i} \frac{m_i}{m} \cdot (\hat{p}_{c,i} - p_{c,i})
\right)^2,
$$

using the pseudocount $$n_i = Y_{c,i} + N_{c,i} + \tilde n$$. Writing the latter
bias term using the megacounty, an upper bound for this term is (using $$m =
\sum_i m_i$$):

$$
\left(\frac{m_o}{m}\right)^2(\hat{p}_o - p_o)^2 \le \left(\frac{m_o}{m}\right)^2
\max\left((1-\hat{p}_o)^2, \hat{p}_o^2\right)
$$

The MSE assumes that the the survey county data is random and that the prior
parameters are fixed and not random, so the unsurveyed counties only contribute
bias while the surveyed counties are unbiased for their respective county
probabilities and contribute variance.

### Smoothing

Additionally, as with the Facebook surveys, we consider estimates formed by
pooling data over time.  That is, daily, for each location, we first pool all
data available in that location over the last 5 days, and compute the estimates
given above using all five days of data.

In contrast to the Facebook surveys, this pooling does not significantly change
the availability of estimates, because of our stratified sampling procedure
(essentially always) delivers sufficient data at the county level---at least 100
survey responses---to warrant their own estimates. However, the pooling
procedure still does help by serving as a smoother.
