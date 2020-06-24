---
title: Symptom Surveys
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Symptom Surveys
{: .no_toc}

* **Source name:** `fb-survey`
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#fb-survey)
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source is based on symptom surveys run by Carnegie Mellon. Facebook
directs a random sample of its users to these surveys, which are voluntary.
Individual survey responses are held by CMU and are sharable with other health
researchers under a data use agreement. No individual survey responses are
shared back to Facebook. Of primary interest in these surveys are the symptoms
defining a COVID-like illness (fever, along with cough, or shortness of breath,
or difficulty breathing) or influenza-like illness (fever, along with cough or
sore throat). Using this survey data, we estimate the percentage of people who
have a COVID-like illness, or influenza-like illness, in a given location, on a
given day.

| Signal | Description |
| --- | --- |
| `raw_cli` | Estimated percentage of people with COVID-like illness, with no smoothing or survey weighting |
| `raw_ili` | Estimated percentage of people with influenza-like illness, with no smoothing or survey weighting |
| `raw_wcli` | Estimated percentage of people with COVID-like illness; adjusted using survey weights |
| `raw_wili` | Estimated percentage of people with influenza-like illness; adjusted using survey weights |
| `raw_hh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, including their household, with no smoothing or survey weighting |
| `raw_nohh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, not including their household, with no smoothing or survey weighting |

Note that for `raw_hh_cmnty_cli` and `raw_nohh_cmnty_cli`, the illnesses
included are broader: a respondent is included if they know someone in their
household (for `raw_hh_cmnty_cli`) or community with fever, along with sore
throat, cough, shortness of breath, or difficulty breathing. This does not
attempt to distinguish between COVID-like and influenza-like illness.

Along with the `raw_` signals, there are additional signals with names beginning
with `smoothed_`. These estimate the same quantities as the above signals, but
are smoothed in time to reduce day-to-day sampling noise; importantly (due to
the way in which our smoothing works, which is based on pooling data across
successive days), these smoothed signals are generally available at many more
counties (and MSAs) than the raw signals.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Survey Questions

The survey starts with the following 5 questions:

1. In the past 24 hours, have you or anyone in your household had any of the
   following (yes/no for each):
   - (a) Fever (100 °F or higher)
   - (b) Sore throat
   - (c) Cough
   - (d) Shortness of breath
   - (e) Difficulty breathing
2. How many people in your household (including yourself) are sick (fever, along
   with at least one other symptom from the above list)?
3. How many people are there in your household in total (including yourself)?
4. What is your current ZIP code?
5. How many additional people in your local community that you know personally
   are sick (fever, along with at least one other symptom from the above list)?


Beyond these 5 questions, there are also many other questions that follow in the
survey, which go into more detail on symptoms and demographics. These are
primarily of interest to other researchers, but could still be useful for our
purposes. The full survey can be found TODO.

As of mid-June 2020, the median number of Facebook survey responses per day, is
about 72,000.


## ILI and CLI Indicators

Influenza-like illness or ILI is a standard indicator, and is defined by the CDC
as: fever along with sore throat or cough. From the list of symptoms from Q1 on
our survey, this means a and (b or c).

COVID-like illness or CLI is not a standard indicator. Through our discussions
with the CDC, we chose to define it as: fever along with cough or shortness of
breath or difficulty breathing.

### Defining Household ILI and CLI

For a single survey, we are interested in the quantities:

- $$X =$$ the number of people in the household with ILI;
- $$Y =$$ the number of people in the household with CLI;
- $$N =$$ the number of people in the household.

Note that $$N$$ comes directly from the answer to Q3, but neither $$X$$ nor
$$Y$$ can be computed directly (because Q2 does not give an answer to the
precise symptomatic profile of all individuals in the household, it only asks
how many individuals have fever and at least one other symptom from the list).

We hence estimate $$X$$ and $$Y$$ with the following simple strategy. Consider
ILI, without a loss of generality (we apply the same strategy to CLI). Let $$Z$$
be the answer to Q2.

- If the answer to Q1 does not meet the ILI definition, then we report $$X=0$$.
- If the answer to Q1 does meet the ILI definition, then we report $$X = Z$$.

This can only "over count" (result in too large estimates of) the true $$X$$ and
$$Y$$. For example, this happens when some members of the household experience
ILI that does not also qualify as CLI, while others experience CLI that does not
also qualify as ILI. In this case, for both $$X$$ and $$Y$$, our simple strategy
would return the sum of both types of cases. However, given the extreme degree
of overlap between the definitions of ILI and CLI, it is reasonable to believe
that, if symptoms across all household members qualified as both ILI and CLI,
each individual would have both, or neither---with neither being more common.
Therefore we do not consider this "over counting" phenomenon practically
problematic.

### Estimating Percent ILI and CLI

Let $$x$$ and $$y$$ be the number of people with ILI and CLI, respectively, over
a given time period, and in a given location (for example, the time period being
a particular day, and a location being a particular county). Let $$n$$ be the
total number of people in this location. We are interested in estimating the
true ILI and CLI percentages, which we denote by $$p$$ and $$q$$, respectively:

$$
p = 100 \cdot \frac{x}{n}
\quad\text{and}\quad
q = 100 \cdot \frac{y}{n}.
$$

We estimate $$p$$ and $$q$$ across 4 temporal-spatial aggregation schemes:

1. daily, at the county level;
2. daily, at the MSA (metropolitan statistical area) level;
3. daily, at the HRR (hospital referral region) level;
4. daily, at the state level.

Note that these spatial aggregations are possible as we have the ZIP code of the
household from Q4 of the survey. Our current rule-of-thumb is to discard any
estimate (whether at a county, MSA, HRR, or state level) that is comprised of
less than 100 survey responses. When our geographical mapping data indicates
that a ZIP code is part of multiple geographical units in a single aggregation,
we assign weights to each of these units and proceed as described below, but
with uniform participation weights ($$w^{\text{part}}_i=1$$ for all $$i$$).

In a given temporal-spatial unit (for example, daily-county), let $$X_i$$ and
$$Y_i$$ denote number of ILI and CLI cases in the household, respectively
(computed according to the simple strategy described above), and let $$N_i$$
denote the total number of people in the household, in survey $$i$$, out of
$$m$$ surveys we collected. Then our estimates of $$p$$ and $$q$$ (see Appendix
below for motivating details) are:

$$
\hat{p} = 100 \cdot \frac{1}{m}\sum_{i=1}^m \frac{X_i}{N_i}
\quad\text{and}\quad
\hat{q} = 100 \cdot \frac{1}{m}\sum_{i=1}^m \frac{Y_i}{N_i}.
$$

Their estimated standard errors are:

$$
\begin{aligned}
\widehat{\mathrm{se}}(\hat{p}) &= 100 \cdot \frac{1}{m+1}\sqrt{
  \left(\frac{1}{2} - \hat{p}\right)^2 +
  \sum_{i=1}^m \left(\frac{X_i}{N_i} - \hat{p}\right)^2
} \\
\widehat{\mathrm{se}}(\hat{q}) &= 100 \cdot \frac{1}{m+1}\sqrt{
  \left(\frac{1}{2} - \hat{q}\right)^2 +
  \sum_{i=1}^m \left(\frac{Y_i}{N_i} - \hat{q}\right)^2
},
\end{aligned}
$$

the standard deviations of the estimators after adding a single
pseudo-observation at 1/2 (treating $$m$$ as fixed). The use of the
pseudo-observation prevents standard error estimates of zero, and in simulations
improves the quality of the standard error estimates.

The pseudo-observation is not used in $$\hat{p}$$ and $$\hat{q}$$ themselves, to
avoid potentially large amounts of estimation bias, as $$p$$ and $$q$$ are
expected to be small.

### Estimating "Community CLI"

Over a given time period, and in a given location, let $$u$$ be the number of
people who know someone in their community with CLI, and let $$v$$ be the number
of people who know someone in their community, outside of their household, with
CLI. With $$n$$ denoting the number of people total in this location, we are
interested in the percentages:

$$
a = 100 \cdot \frac{u}{n}
\quad\text{and}\quad
b = 100 \cdot \frac{y}{n}.
$$

We will estimate $$a$$ and $$b$$ across the same 4 temporal-spatial aggregation
schemes as before.

For a single survey, let:

- $$U = 1$$ if and only if a positive number is reported for Q2 or Q5;
- $$V = 1$$ if and only if a positive number is reported for Q2.

In a given temporal-spatial unit (for example, daily-county), let $$U_i$$ and
$$V_i$$ denote these quantities for survey $$i$$, and $$m$$ denote the number of
surveys total.  Then to estimate $$a$$ and $$b$$, we simply use:

$$
\hat{a} = 100 \cdot \frac{1}{m} \sum_{i=1}^m U_i
\quad\text{and}\quad
\hat{b} = 100 \cdot \frac{1}{m} \sum_{i=1}^m V_i.
$$

Their estimated standard errors are:

$$
\begin{aligned}
\widehat{\mathrm{se}}(\hat{a}) &= 100 \cdot \sqrt{\frac{\hat{a}(1-\hat{a})}{m}} \\
\widehat{\mathrm{se}}(\hat{b}) &= 100 \cdot \sqrt{\frac{\hat{b}(1-\hat{b})}{m}},
\end{aligned}
$$

which are the plug-in estimates of the standard errors of the binomial
proportions (treating $$m$$ as fixed).

Note that $$\sum_{i=1}^m U_i$$ is the number of survey respondents who know
someone in their community with *either ILI or CLI*, and not CLI alone; and
similarly for $$V$$. Hence $$\hat{a}$$ and $$\hat{b}$$ will generally
overestimate $$a$$ and $$b$$. However, given the extremely high overlap between
the definitions of ILI and CLI, we do not consider this to be practically very
problematic.

## Survey Weighting

Notice that the estimates defined in last two subsections actually reflect the
percentage of inviduals with ILI and CLI, and individuals who know someone with
CLI, with respect to the population of US Facebook users. (To be precise, the
estimates above actually reflect the percentage inviduals with ILI and CLI, with
respect to the population of US Facebook users *and* their households members).
In reality, our estimates are even further skewed by the propensity of people in
the population of US Facebook users to take our survey in the first place.

When Facebook sends a user to our survey, it generates a random ID number and
sends this to us as well. Once the user completes the survey, we pass this ID
number back to Facebook to confirm completion, and in return receive a
weight---call it $$w_i$$ for user $$i$$. (To be clear, the random ID number that
is generated is completely meaningless for any other purpose than receiving said
weight, and does not allow us to access any information about the user's
Facebook profile, or anything else whatsoever.)

We can use these weights to adjust our estimates of the true ILI and CLI
proportions so that they are representative of the US population---adjusting
both for the differences between the US population and US Facebook users
(according to a state-by-age-gender stratification of the US population from the
2018 Census March Supplement), and for the propensity of a Facebook user to
take our survey in the first  place.

In more detail, we receive a participation
weight

$$
w^{\text{part}}_i = \frac{c^{\text{part}}}{\pi^{\text{part}}_i},
$$

where $$\pi_i$$ is an estimated probability (produced by Facebook) that an
individual with the same state-by-age-gender profile as user $$i$$ would be a
Facebook user and take our CMU survey, scaled by some unknown constant $$c>0$$.
The adjustment we make follows a standard inverse probability weighting strategy
(this being a special case of importance sampling).

### Adjusting Household ILI and CLI

As before, for a given temporal-spatial unit (for example, daily-county), let
$$X_i$$ and $$Y_i$$ denote number of ILI and CLI cases in household $$i$$,
respectively (computed according to the simple strategy above), and let $$N_i$$
denote the total number of people in the household, out of the $$m$$ "relevant"
surveys we collected. A survey is considered relevant if it was started during
the time interval of interest and the respondent's ZIP code overlaps the spatial
unit of interest. Each of these surveys is assigned two weights: the
participation weight $$w^{\text{part}}_i$$, and a geographical-division weight
$$w^{\text{geodiv}}_i$$ describing how much a participant's ZIP code "belongs"
in the spatial unit of interest. (For example, a ZIP code may overlap with
multiple counties, so the weight describes what proportion of the ZIP code's
population is in each county.)

Let $$w^{\text{init}}_i=w^{\text{part}}_i w^{\text{geodiv}}_i=c/\pi_i$$ denote
the initial weight assigned to this survey, where $$c>0$$ is chosen so that
$$\sum_{i=1}^m w_i=1$$.

First, the initial weights are adjusted to reduce sensitivity to any individual
survey by "mixing" them with a uniform weighting across all relevant surveys.

Specifically, we select

$$
w_i=a\cdot\frac1m + (1-a)\cdot w^{\text{init}}_i
$$

using the smallest value of $$a\in[0.05,1]$$ such that $$w_i\le 0.01$$ for all
$$i$$; if such a selection is impossible, then we have insufficient survey
responses (less than 100), and do not produce an estimate for the given
temporal-spatial unit.

Then our adjusted estimates of $$p$$ and $$q$$ are:

$$
\begin{aligned}
\hat{p}_w &= 100 \cdot \sum_{i=1}^m w_i \frac{X_i}{N_i} \\
\hat{q}_w &= 100 \cdot \sum_{i=1}^m w_i \frac{Y_i}{N_i},
\end{aligned}
$$

with estimated standard errors:

$$
\begin{aligned}
\widehat{\mathrm{se}}(\hat{p}_w) &= 100 \cdot \sqrt{
  \Big(\frac{1}{1 + n_e}\Big)^2 \Big(\frac12 - \hat{p}_w\Big)^2 +
  n_e \hat{s}_p^2
}\\
\widehat{\mathrm{se}}(\hat{q}_w) &= 100 \cdot \sqrt{
  \Big(\frac{1}{1 + n_e}\Big)^2 \Big(\frac12 - \hat{q}_w\Big)^2 +
  n_e \hat{s}_q^2
},
\end{aligned}
$$

where

$$
\begin{aligned}
\hat{s}_p^2 &= \sum_{i=1}^m w_i^2 \Big(\frac{X_i}{N_i} - \hat{p}_w\Big)^2 \\
\hat{s}_q^2 &= \sum_{i=1}^m w_i^2 \Big(\frac{Y_i}{N_i} - \hat{q}_w\Big)^2 \\
n_e &= \frac1{\sum_{i=1}^m w_i^2},
\end{aligned}
$$

the delta method estimates of variance associated with self-normalized
importance sampling estimators above, after combining with a pseudo-observation
of 1/2 with weight assigned to appear like a single effective observation
according to importance sampling diagnostics.

The sample size reported is calculated by rounding down $$\sum_{i=1}^{m}
w^{\text{geodiv}}_i$$ before adding the pseudo-observations. When ZIP codes do
not overlap multiple spatial units of interest, these weights are all one, and
this expression simplifies to $$m$$. When estimates are available for all
spatial units of a given type over some time period, the sum of the associated
sample sizes under this definition is consistent with the number of surveys used
to prepare the estimate. (This notion of sample size is distinct from
"effective" sample sizes based on variance of the importance sampling estimators
which were used above.)

### Adjusting Community CLI

As before, in a given temporal-spatial unit (for example, daily-county), let
$$U_i$$ and $$V_i$$ denote the indicators that the survey respondent knows someone
in their community with CLI, including and not including their household,
respectively, for survey $$i$$, out of $$m$$ surveys collected.   Also let $$w_i$$ be
the self-normalized weight that accompanies survey $$i$$, as above. Then our
adjusted estimates of $$a$$ and $$b$$ are:

$$
\begin{aligned}
\hat{a}_w &= 100 \cdot \sum_{i=1}^m w_i U_i \\
\hat{b}_w &= 100 \cdot \sum_{i=1}^m w_i V_i.
\end{aligned}
$$

with estimated standard errors:

$$
\begin{aligned}
\widehat{\mathrm{se}}(\hat{a}_w) &= 100 \cdot \sqrt{\sum_{i=1}^m
w_i^2 (U_i - \hat{a}_w)^2} \\
\widehat{\mathrm{se}}(\hat{b}_w) &= 100 \cdot \sqrt{\sum_{i=1}^m
w_i^2 (V_i - \hat{b}_w)^2},
\end{aligned}
$$

the delta method estimates of variance associated with self-normalized
importance sampling estimators.
