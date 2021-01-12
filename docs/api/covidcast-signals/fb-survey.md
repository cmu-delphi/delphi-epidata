---
title: Symptom Surveys
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Symptom Surveys
{: .no_toc}

* **Source name:** `fb-survey`
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#fb-survey)
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

## Overview

This data source is based on symptom surveys run by the Delphi group at Carnegie
Mellon. Facebook directs a random sample of its users to these surveys, which
are voluntary. Individual survey responses are held by CMU and are sharable with
other health researchers under a data use agreement. No individual survey
responses are shared back to Facebook. See our [surveys
page](https://covidcast.cmu.edu/surveys.html) for more detail about how the
surveys work and how they are used outside the COVIDcast API.

We produce several sets of signals based on the survey data, listed and
described in the sections below:

1. [Influenza-like and COVID-like illness indicators](#ili-and-cli-indicators),
   based on reported symptoms
2. [Behavior indicators](#behavior-indicators), including mask-wearing,
   traveling, and activities outside the home
3. [Testing indicators](#testing-indicators) based on respondent reporting of
   their COVID test results
4. [Vaccination indicators](#vaccination-indicators), based on respondent
   reporting of COVID vaccinations and whether they would accept a vaccine
4. [Mental health indicators](#mental-health-indicators), based on self-reports
   of anxiety, depression, isolation, and worry about COVID

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Survey Text and Questions

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
   *[Beginning in wave 4, this question asks respondents to break the number
   down into three age categories.]*
4. What is your current ZIP code?
5. How many additional people in your local community that you know personally
   are sick (fever, along with at least one other symptom from the above list)?

Beyond these 5 questions, there are also many other questions that follow in the
survey, which go into more detail on symptoms, contacts, risk factors, and
demographics. These are used for many of our behavior and testing indicators
below. The full text of the survey (including all deployed versions) can be
found on our [questions and coding page](../../symptom-survey/coding.md).
Researchers can [request
access](https://dataforgood.fb.com/docs/covid-19-symptom-survey-request-for-data-access/)
to (fully de-identified) individual survey responses for research purposes.

As of mid-August 2020, the average number of Facebook survey responses we
receive each day is about 74,000, and the total number of survey responses we
have received is over 9 million.

## ILI and CLI Indicators

Of primary interest for the API are the symptoms defining a COVID-like illness
(fever, along with cough, or shortness of breath, or difficulty breathing) or
influenza-like illness (fever, along with cough or sore throat). Using this
survey data, we estimate the percentage of people who have a COVID-like illness,
or influenza-like illness, in a given location, on a given day.

| Signals | Description |
| --- | --- |
| `raw_cli` and `smoothed_cli` | Estimated percentage of people with COVID-like illness based on the [criteria below](#ili-and-cli-indicators), with no survey weighting |
| `raw_ili` and `smoothed_ili` | Estimated percentage of people with influenza-like illness based on the [criteria below](#ili-and-cli-indicators), with no survey weighting |
| `raw_wcli` and `smoothed_wcli` | Estimated percentage of people with COVID-like illness; adjusted using survey weights [as described below](#survey-weighting) |
| `raw_wili` and `smoothed_wili` | Estimated percentage of people with influenza-like illness; adjusted using survey weights [as described below](#survey-weighting) |
| `raw_hh_cmnty_cli` and `smoothed_hh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, as [described below](#estimating-community-cli), including their household, with no survey weighting |
| `raw_nohh_cmnty_cli` and `smoothed_nohh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, as [described below](#estimating-community-cli), not including their household, with no survey weighting |

Note that for `raw_hh_cmnty_cli` and `raw_nohh_cmnty_cli`, the illnesses
included are broader: a respondent is included if they know someone in their
household (for `raw_hh_cmnty_cli`) or community with fever, along with sore
throat, cough, shortness of breath, or difficulty breathing. This does not
attempt to distinguish between COVID-like and influenza-like illness.

Influenza-like illness or ILI is a standard indicator, and is defined by the CDC
as: fever along with sore throat or cough. From the list of symptoms from Q1 on
our survey, this means a and (b or c).

COVID-like illness or CLI is not a standard indicator. Through our discussions
with the CDC, we chose to define it as: fever along with cough or shortness of
breath or difficulty breathing.

Symptoms alone are not sufficient to diagnose influenza or coronavirus
infections, and so these ILI and CLI indicators are *not* expected to be
unbiased estimates of the true rate of influenza or coronavirus infections.
These symptoms can be caused by many other conditions, and many true infections
can be asymptomatic. Instead, we expect these indicators to be useful for
comparison across the United States and across time, to determine where symptoms
appear to be increasing.

**Smoothing.** The signals beginning with `smoothed_` estimate the same quantities as their
`raw` partners, but are smoothed in time to reduce day-to-day sampling noise;
see [details below](#smoothing). Crucially, because the smoothed signals combine
information across multiple days, they have larger sample sizes and hence are
available for more counties and MSAs than the raw signals.

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

We estimate $$p$$ and $$q$$ across 4 aggregation schemes:

1. daily, at the county level;
2. daily, at the MSA (metropolitan statistical area) level;
3. daily, at the HRR (hospital referral region) level;
4. daily, at the state level.

These are possible because we have the ZIP code of the household from Q4 of the
survey. Our current rule-of-thumb is to discard any estimate (whether at a
county, MSA, HRR, or state level) that is based on fewer than 100 survey
responses. When our geographical mapping data indicates that a ZIP code is part
of multiple geographical units in a single aggregation, we assign weights
$$w_i^\text{geodiv}$$ to each of these units (based on the ZIP code's overlap
with each geographical unit) and use these weights as part of the survey
weighting, as [described below](#survey-weighting).

In a given aggregation unit (for example, daily-county), let $$X_i$$ and
$$Y_i$$ denote number of ILI and CLI cases in the household, respectively
(computed according to the simple strategy described above), and let $$N_i$$
denote the total number of people in the household, in survey $$i$$, out of
$$m$$ surveys we collected. Then our estimates of $$p$$ and $$q$$ (see
the [appendix](#appendix) for motivating details) are: 

$$
\hat{p} = 100 \cdot \frac{1}{m}\sum_{i=1}^m \frac{X_i}{N_i}
\quad\text{and}\quad
\hat{q} = 100 \cdot \frac{1}{m}\sum_{i=1}^m \frac{Y_i}{N_i}.
$$

Their estimated standard errors are:

$$
\begin{aligned}
\widehat{\mathrm{se}}(\hat{p}) &= 100 \cdot \frac{1}{m+1}\sqrt{
  \left(\frac{1}{2} - \frac{\hat{p}}{100}\right)^2 +
  \sum_{i=1}^m \left(\frac{X_i}{N_i} - \frac{\hat{p}}{100}\right)^2
} \\
\widehat{\mathrm{se}}(\hat{q}) &= 100 \cdot \frac{1}{m+1}\sqrt{
  \left(\frac{1}{2} - \frac{\hat{q}}{100}\right)^2 +
  \sum_{i=1}^m \left(\frac{Y_i}{N_i} - \frac{\hat{q}}{100}\right)^2
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

We will estimate $$a$$ and $$b$$ across the same 4 aggregation schemes as
before. 

For a single survey, let:

- $$U = 1$$ if and only if a positive number is reported for Q2 or Q5;
- $$V = 1$$ if and only if a positive number is reported for Q2.

In a given aggregation unit (for example, daily-county), let $$U_i$$ and
$$V_i$$ denote these quantities for survey $$i$$, and $$m$$ denote the number of
surveys total.  Then to estimate $$a$$ and $$b$$, we simply use:

$$
\hat{a} = 100 \cdot \frac{1}{m} \sum_{i=1}^m U_i
\quad\text{and}\quad
\hat{b} = 100 \cdot \frac{1}{m} \sum_{i=1}^m V_i.
$$

Hence $$\hat{a}$$ is reported in the `hh_cmnty_cli` signals and $$\hat{b}$$ in
the `nohh_cmnty_cli` signals. Their estimated standard errors are:

$$
\begin{aligned}
\widehat{\mathrm{se}}(\hat{a}) &= 100 \cdot \sqrt{\frac{\frac{\hat{a}}{100}(1-\frac{\hat{a}}{100})}{m}} \\
\widehat{\mathrm{se}}(\hat{b}) &= 100 \cdot \sqrt{\frac{\frac{\hat{b}}{100}(1-\frac{\hat{b}}{100})}{m}},
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


### Smoothing

The smoothed versions of all `fb-survey` signals (with `smoothed_` prefix) are
calculated using seven day pooling. For example, the estimate reported for June
7 in a specific geographical area (such as county or MSA) is formed by
collecting all surveys completed between June 1 and 7 (inclusive) and using that
data in the estimation procedures described above.


## Behavior Indicators

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- | --- |
| `smoothed_wearing_mask` | Estimated percentage of people who wore a mask for most or all of the time while in public in the past 5 days; those not in public in the past 5 days are not counted. | C14 | Wave 4, Sept 8, 2020 |
| `smoothed_others_masked` | Estimated percentage of respondents who say that most or all *other* people wear masks, when they are in public and social distancing is not possible | C16 | Wave 5, Nov 24, 2020 |
| `smoothed_travel_outside_state_5d` | Estimated percentage of respondents who report traveling outside their state in the past 5 days | C6 | Wave 1 |
| `smoothed_work_outside_home_1d` | Estimated percentage of respondents who worked or went to school outside their home in the past 24 hours | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_shop_1d` | Estimated percentage of respondents who went to a "market, grocery store, or pharmacy" in the past 24 hours | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_restaurant_1d` | Estimated percentage of respondents who went to a "bar, restaurant, or cafe" in the past 24 hours | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_spent_time_1d` | Estimated percentage of respondents who "spent time with someone who isn't currently staying with you" in the past 24 hours | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_large_event_1d` | Estimated percentage of respondents who "attended an event with more than 10 people" in the past 24 hours | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_public_transit_1d` | Estimated percentage of respondents who "used public transit" in the past 24 hours | C13 | Wave 4, Sept 8, 2020 |

Weighted versions of these signals, using the [survey weighting described
below](#survey-weighting) to be more representative of state demographics, are
also available. These have names beginning `smoothed_w`, such as
`smoothed_wwearing_mask`.


## Testing Indicators

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_tested_14d` | Estimated percentage of people who were tested for COVID-19 in the past 14 days, regardless of their test result | B8, B10 |
| `smoothed_tested_positive_14d` | Estimated test positivity rate (percent) among people tested for COVID-19 in the past 14 days | B10a |
| `smoothed_wanted_test_14d` | Estimated percentage of people who *wanted* to be tested for COVID-19 in the past 14 days, out of people who were *not* tested in that time | B12 |

These indicators are based on questions in Wave 4 of the survey, introduced on
September 8, 2020.

Weighted versions of these signals, using the [survey weighting described
below](#survey-weighting) to be more representative of state demographics, are
also available. These have names beginning `smoothed_w`, such as
`smoothed_wtested_14d`.


## Vaccination Indicators

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_accept_covid_vaccine` | Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a COVID-19 vaccine were offered to them today. **Note:** Until January 6, 2021, all respondents answered this question; beginning on that date, only respondents who said they have not received a COVID vaccine are asked this question. | V3 |

This indicator is based on questions added in Wave 6 of the survey, introduced
on December 19, 2020. **Note:** As of January 2021, vaccination items on the
survey are being revised in preparation for Wave 7. We may replace the signal
above with a new signal (with a different name) if the underlying survey item
changes significantly.

A weighted version of this signal, using the [survey weighting described
below](#survey-weighting) to be more representative of state demographics, is
also available. It is `smoothed_waccept_covid_vaccine`.


## Mental Health Indicators

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_anxious_5d` | Estimated percentage of respondents who reported feeling "nervous, anxious, or on edge" for most or all of the past 5 days | C8 |
| `smoothed_depressed_5d` | Estimated percentage of respondents who reported feeling depressed for most or all of the past 5 days | C8 |
| `smoothed_felt_isolated_5d` | Estimated percentage of respondents who reported feeling "isolated from others" for most or all of the past 5 days | C8 |
| `smoothed_worried_become_ill` | Estimated percentage of respondents who reported feeling very or somewhat worried that "you or someone in your immediate family might become seriously ill from COVID-19" | C9 |
| `smoothed_worried_finances` | Estimated percentage of respondents who report being very or somewhat worried about their "household's finances for the next month" | C15 |

Some of these questions were present in the earliest waves of the survey, but
only in Wave 4 did respondents consent to our use of aggregate data to
study other impacts of COVID, such as mental health. Hence, these aggregates only
include respondents to Wave 4 and later waves, beginning September 8, 2020.

Weighted versions of these signals, using the [survey weighting described
below](#survey-weighting) to be more representative of state demographics, are
also available. These have names beginning `smoothed_w`, such as
`smoothed_wdepressed_14d`.


## Survey Weighting

Notice that the estimates defined in the previous sections are calculated with
respect to the population of US Facebook users. (To be precise, the ILI and CLI
indicators reflect the population of US Facebook users *and* their household
members). In reality, our estimates are even further skewed by the varying
propensity of people in the population of US Facebook users to take our survey
in the first place.

When Facebook sends a user to our survey, it generates a random ID number and
sends this to us as well. Once the user completes the survey, we pass this ID
number back to Facebook to confirm completion, and in return receive a
weight---call it $$w_i$$ for user $$i$$. (The random ID number is completely
meaningless for any other purpose than receiving this weight, and does not allow
us to access any information about the user's Facebook profile.)

We can use these weights to adjust our estimates so that they are representative
of the US population---adjusting both for the differences between the US
population and US Facebook users (according to a state-by-age-gender
stratification of the US population from the 2018 Census March Supplement) and
for the propensity of a Facebook user to take our survey in the first place.

In more detail, we receive a participation weight

$$
w^{\text{part}}_i \propto \frac{1}{\pi_i},
$$

where $$\pi_i$$ is an estimated probability (produced by Facebook) that an
individual with the same state-by-age-gender profile as user $$i$$ would be a
Facebook user and take our CMU survey. The adjustment we make follows a standard
inverse probability weighting strategy (this being a special case of importance
sampling).

Detailed documentation on how Facebook calculates these weights is available on
our [survey weight documentation page](../../symptom-survey/weights.md).

### Adjusting Household ILI and CLI

As before, for a given aggregation unit (for example, daily-county), let $$X_i$$
and $$Y_i$$ denote the numbers of ILI and CLI cases in household $$i$$,
respectively (computed according to the simple strategy above), and let $$N_i$$ 
denote the total number of people in the household. Let $$i = 1, \dots, m$$
denote the surveys started during the time period of interest and reported in a
ZIP code intersecting the spatial unit of interest.

Each of these surveys is assigned two weights: the participation weight
$$w^{\text{part}}_i$$, and a geographical-division weight
$$w^{\text{geodiv}}_i$$ describing how much a participant's ZIP code "belongs"
in the spatial unit of interest. (For example, a ZIP code may overlap with
multiple counties, so the weight describes what proportion of the ZIP code's
population is in each county.)

Let $$w^{\text{init}}_i=w^{\text{part}}_i w^{\text{geodiv}}_i$$ denote the
initial weight assigned to this survey. First, we adjust these initial weights
to reduce sensitivity to any individual survey by "mixing" them with a uniform
weighting across all relevant surveys. This prevents specific survey respondents 
with high survey weights having disproportionate influence on the weighted
estimates. 

Specifically, we select the smallest value of $$a \in [0.05, 1]$$ such that

$$
w_i = a\cdot\frac1m + (1-a)\cdot w^{\text{init}}_i \leq 0.01
$$

for all $$i$$. If such a selection is impossible, then we have insufficient
survey responses (less than 100), and do not produce an estimate for the given
aggregation unit.

Next, we rescale the weights $$w_i$$ over all $$i$$ so that $$\sum_{i=1}^m 
w_i=1$$. Then our adjusted estimates of $$p$$ and $$q$$ are: 

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
  \left(\frac{1}{1 + n_e}\right)^2 \left(\frac12 - \frac{\hat{p}_w}{100}\right)^2 +
  n_e \hat{s}_p^2
}\\
\widehat{\mathrm{se}}(\hat{q}_w) &= 100 \cdot \sqrt{
  \left(\frac{1}{1 + n_e}\right)^2 \left(\frac12 - \frac{\hat{q}_w}{100}\right)^2 +
  n_e \hat{s}_q^2
},
\end{aligned}
$$

where

$$
\begin{aligned}
\hat{s}_p^2 &= \sum_{i=1}^m w_i^2 \left(\frac{X_i}{N_i} - \frac{\hat{p}_w}{100}\right)^2 \\
\hat{s}_q^2 &= \sum_{i=1}^m w_i^2 \left(\frac{Y_i}{N_i} - \frac{\hat{q}_w}{100}\right)^2 \\
n_e &= \frac1{\sum_{i=1}^m w_i^2},
\end{aligned}
$$

which are the delta method estimates of variance associated with self-normalized
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

### Adjusting Other Percentage Estimators

The household ILI and CLI estimates are complex to weight, as shown in the
previous subsection, because they use an estimator based on the survey
respondent *and their household.* All other estimates reported in the API are
simply based on percentages of respondents, such as the percentage who report
knowing someone in their community who is sick. In this subsection we will
describe how survey weights are used to construct weighted estimates for these
indicators, using community CLI as an example.

As before, in a given aggregation unit (for example, daily-county), let $$U_i$$
and $$V_i$$ denote the indicators that the survey respondent knows someone in
their community with CLI, including and not including their household,
respectively, for survey $$i$$, out of $$m$$ surveys collected. Also let
$$w_i$$ be the self-normalized weight that accompanies survey $$i$$, as
above. Then our adjusted estimates of $$a$$ and $$b$$ are: 

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
w_i^2 \left(U_i - \frac{\hat{a}_w}{100} \right)^2} \\
\widehat{\mathrm{se}}(\hat{b}_w) &= 100 \cdot \sqrt{\sum_{i=1}^m
w_i^2 \left(V_i - \frac{\hat{b}_w}{100} \right)^2},
\end{aligned}
$$

the delta method estimates of variance associated with self-normalized
importance sampling estimators.

## Appendix

Here are some details behind the choice of estimators for [percent ILI and
percent CLI](#ili-and-cli-indicators).

Suppose there are $$h$$ households total in the underlying population, and for 
household $$i$$, denote $$\theta_i=N_i/n$$.  Then note that the quantities of 
interest, $$p$$ and $$q$$, are 

$$
p = \sum_{i=1}^h \frac{X_i}{N_i} \theta_i
\quad\text{and}\quad 
q = \sum_{i=1}^h \frac{Y_i}{N_i} \theta_i.
$$

Let $$S \subseteq \{1,\dots,h\}$$ denote sampled households, with $$m=|S|$$,
and suppose we sampled household $$i$$ with probability $$\theta_i=N_i/n$$
proportional to the household size.  Then unbiased estimates of $$p$$ and $$q$$
are simply

$$
\hat{p} = \frac{1}{m} \sum_{i \in S} \frac{X_i}{N_i}
\quad\text{and}\quad 
\hat{q} = \frac{1}{m} \sum_{i \in S} \frac{Y_i}{N_i},
$$

which are an equivalent way of writing our previously-defined estimates. 

Note that we can again rewrite our quantities of interest as

$$
p = \frac{\mu_x}{\mu_n} 
\quad\text{and}\quad 
q = \frac{\mu_y}{\mu_n},
$$

where $$\mu_x=x/h$$, $$\mu_y=y/h$$, $$\mu_n=n/h$$ denote the expected number
people with ILI per household, expected number of people with CLI per household,
and expected number of people total per household, respectively, and $$h$$
denotes the total number of households in the population.

Suppose that instead of proportional sampling, we sampled households uniformly,
resulting in $$S \subseteq \{1,\dots,h\}$$ denote sampled households, with
$$m=|S|$$. Then the natural estimates of $$p$$ and $$q$$ are instead plug-in
estimates of the numerators and denominators in the above, 

$$
\tilde{p} = \frac{\bar{X}}{\bar{N}}
\quad\text{and}\quad 
\tilde{q} = \frac{\bar{X}}{\bar{N}}
$$

where $$\bar{X}=\sum_{i \in S} X_i/m$$, $$\bar{Y}=\sum_{i \in S} Y_i/m$$, and
$$\bar{N}=\sum_{i \in S} N_i/m$$ denote the sample means of $$\{X_i\}_{i \in
S}$$, $$\{Y_i\}_{i \in S}$$, and $$\{N_i\}_{i \in S}$$, respectively.

Whether we consider $$\hat{p}$$ and $$\hat{q}$$, or $$\tilde{p}$$ and
$$\tilde{q}$$, to be more natural---mean of fractions, or fraction of means,
respectively---depends on the sampling model: if we are sampling households
proportional to household size, then it is $$\hat{p}$$ and $$\hat{q}$$; if we
are sampling households uniformly, then it is $$\tilde{p}$$ and $$\tilde{q}$$.
We settled on the former, based on both conceptual and empirical supporting
evidence:

- Conceptually, though we do not know the details, we have reason to believe
  that Facebook offers an essentially uniform random draw of eligible
  users---those 18 years or older---to take our survey.  In this sense, the
  sampling is done proportional to the number of "Facebook adults" in a
  household: individuals 18 years or older, who have a Facebook account.  Hence
  if we posit that the number of "Facebook adults" scales linearly with the
  household size, which seems to us like a reasonable assumption, then sampling
  would still be proportional to household size.  (Notice that this would 
  remain true no matter how small the linear coefficient is, that is, it would
  even be true if Facebook did not have good coverage over the US.)

- Empirically, we have computed the distribution of household sizes (proportion
  of households of size 1, size 2, size 3, etc.) in the Facebook survey data
  thus far, and compared it to the distribution of household sizes from the
  Census.  These align quite closely, also suggesting that sampling is likely
  done proportional to household size.
