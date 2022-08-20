---
title: COVID-19 Trends and Impact Survey
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---

# COVID-19 Trends and Impact Survey
{: .no_toc}

* **Source name:** `fb-survey`
* **Earliest issue available:** April 29, 2020
* **Number of data revisions since May 19, 2020:** 1
* **Date of last change:** [June 3, 2020](../covidcast_changelog.md#fb-survey)
* **Available for:** county, hrr, msa, state, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY](../covidcast_licensing.md#creative-commons-attribution)

## Overview

This data source is based on the [COVID-19 Trends and Impact Survey (CTIS)](../../symptom-survey/)
run by the Delphi group at Carnegie Mellon.
Facebook directs a random sample of its users to these surveys, which are
voluntary. Users age 18 or older are eligible to complete the surveys, and
their survey responses are held by CMU and are sharable with other health
researchers under a data use agreement. No individual survey responses are
shared back to Facebook. See our [surveys
page](https://delphi.cmu.edu/covid19/ctis/) for more detail about how the
surveys work and how they are used outside the COVIDcast API.

As of November 2021, the average number of Facebook survey responses we
receive each day is about 40,000, and the total number of survey responses we
have received is over 25 million.

We produce several sets of signals based on the survey data, listed and
described in the sections below:

1. [Influenza-like and COVID-like illness indicators](#ili-and-cli-indicators),
   based on reported symptoms
2. [Behavior indicators](#behavior-indicators), including mask-wearing,
   traveling, in-person schooling, and other activities outside the home
3. [Testing indicators](#testing-indicators) based on respondent reporting of
   their COVID test results
4. [Vaccination indicators](#vaccination-indicators), based on respondent
   reporting of COVID vaccinations, whether they would accept a vaccine, and
   reasons for any hesitancy to accept a vaccine
5. [Mental health indicators](#mental-health-indicators), based on self-reports
   of anxiety, depression, isolation, and worry about COVID
6. [Belief, experience, and information
   indicators](#belief-experience-and-information-indicators), about the
   respondent's beliefs about COVID-19, their experiences of health care, their
   sources of information about COVID-19, and their degree of trust in different
   sources

Many of these signals can also be browsed on our [survey
dashboard](https://delphi.cmu.edu/covidcast/survey-results/) at any selected
location.

Additionally, contingency tables containing demographic breakdowns of survey
data are [available for download](../../symptom-survey/contingency-tables.md).
Researchers can [request access](../../symptom-survey/data-access.md)
to (fully de-identified) individual survey responses for research purposes.

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

## ILI and CLI Indicators

We define COVID-like illness (fever, along with cough, or shortness of breath,
or difficulty breathing) or influenza-like illness (fever, along with cough or
sore throat) for use in forecasting and modeling. Using this survey data, we
estimate the percentage of people (age 18 or older) who have a COVID-like
illness, or influenza-like illness, in a given location, on a given day.

Signals beginning `raw_w` or `smoothed_w` are [adjusted using survey weights to
be demographically representative](#survey-weighting-and-estimation) as
described below. Weighted signals have 1-2 days of lag, so if low latency is
paramount, unweighted signals are also available. These begin `smoothed_` or
`raw_`, such as `raw_cli` instead of `raw_wcli`.

| Signals | Description |
| --- | --- |
| `raw_wcli` and `smoothed_wcli` | Estimated percentage of people with COVID-like illness <br/> **Earliest date available:** 2020-04-06 |
| `raw_wili` and `smoothed_wili` | Estimated percentage of people with influenza-like illness <br/> **Earliest date available:** 2020-04-06 |
| `raw_whh_cmnty_cli` and `smoothed_whh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, as [described below](#estimating-community-cli), including their household <br/> **Earliest date available:** 2020-04-15 |
| `raw_wnohh_cmnty_cli` and `smoothed_wnohh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, as [described below](#estimating-community-cli), not including their household <br/> **Earliest date available:** 2020-04-15 |

Note that for `raw_whh_cmnty_cli` and `raw_wnohh_cmnty_cli`, the illnesses
included are broader: a respondent is included if they know someone in their
household (for `raw_whh_cmnty_cli`) or community with fever, along with sore
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

**Smoothing.** The signals beginning with `smoothed` estimate the same quantities as their
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

In a given aggregation unit (for example, daily-county), let $$X_i$$ and $$Y_i$$
denote number of ILI and CLI cases in the household, respectively (computed
according to the simple strategy [described
above](#defining-household-ili-and-cli)), and let $$N_i$$ denote the total
number of people in the household, in survey $$i$$, out of $$m$$ surveys we
collected. Then our unweighted estimates of $$p$$ and $$q$$ are:

$$
\hat{p} = 100 \cdot \frac{1}{m}\sum_{i=1}^m \frac{X_i}{N_i}
\quad\text{and}\quad
\hat{q} = 100 \cdot \frac{1}{m}\sum_{i=1}^m \frac{Y_i}{N_i}.
$$

[See below](#adjusting-household-ili-and-cli) for details on weighting and
standard errors for these estimates.

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

For a single survey, let:

- $$U = 1$$ if and only if a positive number is reported for Q2 or Q5;
- $$V = 1$$ if and only if a positive number is reported for Q2.

Let $$U_i$$ and $$V_i$$ denote these quantities for survey $$i$$, and $$m$$
denote the number of surveys total. We report the percentage of surveys where
$$U_i = 1$$ as in the `hh_cmnty_cli` signals and the percentage where $$V_i =
1$$ in the `nohh_cmnty_cli` signals. The exact estimators are [described
below](#adjusting-other-percentage-estimators).

Note that $$\sum_{i=1}^m U_i$$ is the number of survey respondents who know
someone in their community with *either ILI or CLI*, and not CLI alone; and
similarly for $$V$$. Hence $$\hat{a}$$ and $$\hat{b}$$ will generally
overestimate $$a$$ and $$b$$. However, given the extremely high overlap between
the definitions of ILI and CLI, we do not consider this to be practically very
problematic.


### Smoothing

The smoothed versions of all `fb-survey` signals (with `smoothed` prefix) are
calculated using seven day pooling. For example, the estimate reported for June
7 in a specific geographical area (such as county or MSA) is formed by
collecting all surveys completed between June 1 and 7 (inclusive) and using that
data in the estimation procedures described above.


## Behavior Indicators

Signals beginning `smoothed_w` are [adjusted using survey weights to be
demographically representative](#survey-weighting-and-estimation) as described
below. Weighted signals have 1-2 days of lag, so if low latency is paramount,
unweighted signals are also available. These begin `smoothed_`, such as
`smoothed_wearing_mask` instead of `smoothed_wwearing_mask`.

### Mask Use

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- | --- |
| `smoothed_wwearing_mask_7d` | Estimated percentage of people who wore a mask for most or all of the time while in public in the past 7 days; those not in public in the past 7 days are not counted. <br/> **Earliest date available:** 2021-02-08 | C14a | Wave 8, Feb 8, 2021 |
| `smoothed_wwearing_mask` | *Discontinued as of Wave 8, Feb 8, 2021* Estimated percentage of people who wore a mask for most or all of the time while in public in the past 5 days; those not in public in the past 5 days are not counted. <br/> **Earliest date available:** 2020-09-08 | C14 | Wave 4, Sept 8, 2020 |
| `smoothed_wothers_masked_public` | Estimated percentage of respondents who say that most or all *other* people wear masks, when they are in public. <br/> **Earliest date available:** 2021-05-19 | H2 | Wave 11, May 19, 2021 |
| `smoothed_wothers_masked` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say that most or all *other* people wear masks, when they are in public and social distancing is not possible. <br/> **Earliest date available:** 2020-11-24 | C16 | Wave 5, Nov 24, 2020 |

### Social Distancing and Travel

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- | --- |
| `smoothed_wothers_distanced_public` | Estimated percentage of respondents who reported that all or most people they enountered in public in the past 7 days maintained a distance of at least 6 feet. Respondents who said that they have not been in public for the past 7 days are excluded. <br/> **Earliest date available:** 2021-06-04 | H1 | Wave 11, May 19, 2021 |
| `smoothed_wpublic_transit_1d` | Estimated percentage of respondents who "used public transit" in the past 24 hours <br/> **Earliest date available:** 2020-09-08 | C13 or C13b | Wave 4, Sept 8, 2020 |
| `smoothed_wtravel_outside_state_7d` | Estimated percentage of respondents who report traveling outside their state in the past 7 days. This item was asked of respondents starting in Wave 10. <br/> **Earliest date available:** 2021-03-02 | C6a | Wave 10 |
| `smoothed_wwork_outside_home_indoors_1d` | Estimated percentage of respondents who worked or went to school indoors and outside their home in the past 24 hours <br/> **Earliest date available:** 2021-03-02 | C13b | Wave 10, Mar 2, 2021 |
| `smoothed_wshop_indoors_1d` | Estimated percentage of respondents who went to an "indoor market, grocery store, or pharmacy" in the past 24 hours <br/> **Earliest date available:** 2021-03-02 | C13b | Wave 10, Mar 2, 2021 |
| `smoothed_wrestaurant_indoors_1d` | Estimated percentage of respondents who went to an indoor "bar, restaurant, or cafe" in the past 24 hours <br/> **Earliest date available:** 2021-03-02 | C13b | Wave 10, Mar 2, 2021 |
| `smoothed_wspent_time_indoors_1d` | Estimated percentage of respondents who "spent time indoors with someone who isn't currently staying with you" in the past 24 hours <br/> **Earliest date available:** 2021-03-02 | C13b | Wave 10, Mar 2, 2021 |
| `smoothed_wlarge_event_indoors_1d` | Estimated percentage of respondents who "attended an indoor event with more than 10 people" in the past 24 hours <br/> **Earliest date available:** 2021-03-02 | C13b | Wave 10, Mar 2, 2021 |
| `smoothed_wtravel_outside_state_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who report traveling outside their state in the past 5 days <br/> **Earliest date available:** 2020-04-06 | C6 | Wave 1 |
| `smoothed_wwork_outside_home_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who worked or went to school outside their home in the past 24 hours <br/> **Earliest date available:** 2020-09-08 | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_wshop_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who went to a "market, grocery store, or pharmacy" in the past 24 hours <br/> **Earliest date available:** 2020-09-08 | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_wrestaurant_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who went to a "bar, restaurant, or cafe" in the past 24 hours <br/> **Earliest date available:** 2020-09-08 | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_wspent_time_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who "spent time with someone who isn't currently staying with you" in the past 24 hours <br/> **Earliest date available:** 2020-09-08 | C13 | Wave 4, Sept 8, 2020 |
| `smoothed_wlarge_event_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who "attended an event with more than 10 people" in the past 24 hours <br/> **Earliest date available:** 2020-09-08 | C13 | Wave 4, Sept 8, 2020 |

### Schooling Indicators

#### Schooling Type

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_winperson_school_fulltime_oldest` | Estimated percentage of people whose oldest child attends in-person school on a full-time basis, among people with any children younger than 18 reporting that their oldest child is currently in school, but not homeschooled. <br/> **Earliest date available:** 2021-12-19 | P5 |
| `smoothed_winperson_school_parttime_oldest` | Estimated percentage of people whose oldest child attends in-person school on a part-time basis, among people with any children younger than 18 reporting that their oldest child is currently in school, but not homeschooled. <br/> **Earliest date available:** 2021-12-19 | P5 |
| `smoothed_wremote_school_fulltime_oldest` | Estimated percentage of people whose oldest child attends remote school on a full-time basis, among people with any children younger than 18 reporting that their oldest child is currently in school, but not homeschooled. <br/> **Earliest date available:** 2022-03-23 | P5 |
| `smoothed_winperson_school_fulltime` | *Discontinued as of Wave 12, Dec 19, 2021* Estimated percentage of people who had any children attending in-person school on a full-time basis, among people reporting any pre-K-grade 12 children in their household. <br/> **Earliest date available:** 2020-11-24 | E2 |
| `smoothed_winperson_school_parttime` | *Discontinued as of Wave 12, Dec 19, 2021* Estimated percentage of people who had any children attending in-person school on a part-time basis, among people reporting any pre-K-grade 12 children in their household. <br/> **Earliest date available:** 2020-11-24 | E2 |

#### School Safety Measures

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wschool_safety_measures_mask_students` | Estimated percentage of people whose oldest child's school mandates mask-wearing for students, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_mask_teachers` | Estimated percentage of people whose oldest child's school mandates mask-wearing for teachers, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_restricted_entry` | Estimated percentage of people whose oldest child's school restricts entry into school, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_separators` | Estimated percentage of people whose oldest child's school uses separators or desk shields in classrooms, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_extracurricular` | Estimated percentage of people whose oldest child's school has no school-based extracurricular activities, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_symptom_screen` | Estimated percentage of people whose oldest child's school has daily symptom screening, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_ventilation` | Estimated percentage of people whose oldest child's school improved ventilation, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_testing_staff` | Estimated percentage of people whose oldest child's school regularly tests teachers and staff, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_testing_students` | Estimated percentage of people whose oldest child's school regularly tests students, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_vaccine_staff` | Estimated percentage of people whose oldest child's school has a vaccine requirement for teachers and staff, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_vaccine_students` | Estimated percentage of people whose oldest child's school has a vaccine requirement for eligible students, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_cafeteria` | Estimated percentage of people whose oldest child's school had modified cafeteria usage, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |
| `smoothed_wschool_safety_measures_dont_know` | Estimated percentage of people who don't know what safety measure their oldest child's school has taken, among people with any children younger than 18 whose oldest child attends in-person school on a full-time or part-time basis. <br/> **Earliest date available:** 2022-03-23 | P6 |

## Testing Indicators

Signals beginning `smoothed_w` are [adjusted using survey weights to be
demographically representative](#survey-weighting-and-estimation) as described
below. Weighted signals have 1-2 days of lag, so if low latency is paramount,
unweighted signals are also available. These begin `smoothed_`, such as
`smoothed_tested_14d` instead of `smoothed_wtested_14d`.

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wtested_14d` | Estimated percentage of people who were tested for COVID-19 in the past 14 days, regardless of their test result <br/> **Earliest date available:** 2020-09-08 | B8, B10 |
| `smoothed_wtested_positive_14d` | Estimated test positivity rate (percent) among people tested for COVID-19 in the past 14 days <br/> **Earliest date available:** 2020-09-08 | B10a or B10c |
| `smoothed_wscreening_tested_positive_14d` | Estimated test positivity rate (percent) among people tested for COVID-19 in the past 14 days who were being screened with no symptoms or known exposure. **Note:** Until Wave 11 (May 19, 2021), this included people who said they were tested while receiving other medical care, because their employer or school required it, after attending a large outdoor gathering, or prior to visiting friends or family. After that date, this includes people who said they were tested while receiving other medical care, because their employer or school required it, prior to visiting friends or family, or prior to domestic or international travel. <br/> **Earliest date available:** 2021-03-20 | B10a or B10c, B10b |
| `smoothed_whad_covid_ever` | Estimated percentage of people who report having ever had COVID-19. <br/> **Earliest date available:** 2021-05-20 | B13 |
| `smoothed_wwanted_test_14d` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people who *wanted* to be tested for COVID-19 in the past 14 days, out of people who were *not* tested in that time <br/> **Earliest date available:** 2020-09-08 | B12 |

These indicators are based on questions in Wave 4 of the survey, introduced on
September 8, 2020.


## Vaccination Indicators

Signals beginning `smoothed_w` are [adjusted using survey weights to be
demographically representative](#survey-weighting-and-estimation) as described
below. Weighted signals have 1-2 days of lag, so if low latency is paramount,
unweighted signals are also available. These begin `smoothed_`, such as
`smoothed_covid_vaccinated` instead of `smoothed_wcovid_vaccinated`.

### Vaccine Uptake and Acceptance

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wcovid_vaccinated_appointment_or_accept` | Estimated percentage of respondents who *either* have already received a COVID vaccine *or* have an appointment to get a COVID vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today. <br/> **Earliest date available:** 2021-05-19 | V1, V11a, V3a |
| `smoothed_wcovid_vaccinated_or_accept` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who *either* have already received a COVID vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today. <br/> **Earliest date available:** 2021-01-06 | V1 and V3 |
| `smoothed_wappointment_or_accept_covid_vaccine` | Estimated percentage of respondents who *either* have an appointment to get a COVID-19 vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-05-19 | V11a, V3a |
| `smoothed_waccept_covid_vaccine_no_appointment` | Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated and do not have an appointment to do so. <br/> **Earliest date available:** 2021-05-19 | V3a |
| `smoothed_waccept_covid_vaccine` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a COVID-19 vaccine were offered to them today. **Note:** Until January 6, 2021, all respondents answered this question; beginning on that date, only respondents who said they have not received a COVID vaccine are asked this question. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `smoothed_wcovid_vaccinated` | Estimated percentage of respondents who have already received a vaccine for COVID-19. **Note:** The Centers for Disease Control compiles data on vaccine administration across the United States. This signal may differ from CDC data because of survey biases and should not be treated as authoritative. However, the survey signal is not subject to the lags and reporting problems in official vaccination data. <br/> **Earliest date available:** 2021-01-06 | V1 |
| `smoothed_wappointment_not_vaccinated` | Estimated percentage of respondents who have an appointment to get a COVID-19 vaccine, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-05-19 | V11a |
| `smoothed_wcovid_vaccinated_friends` | Estimated percentage of respondents who report that most of their friends and family have received a COVID-19 vaccine. <br/> **Earliest date available:** 2021-05-20 | H3 |
| `smoothed_wtry_vaccinate_1m` | Estimated percentage of respondents who report that they will try to get the COVID-19 vaccine within a week to a month, among unvaccinated respondents who do not have a vaccination appointment and who are uncertain about getting vaccinated (i.e. did not say they definitely would get vaccinated, nor that they definitely would not). <br/> **Earliest date available:** 2021-06-10 | V16 |
| `smoothed_wflu_vaccinated_2021` | Estimated percentage of respondents who have received a season flu vaccine since July 1, 2021, among all respondents. <br/> **Earliest date available:** 2022-03-04 | C17b |

### Vaccine Uptake and Acceptance for Children

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wvaccinate_child_oldest` | Estimated percentage of people who would "definitely" or "probably" get their oldest child vaccinated against COVID-19 when eligible or already have, among people with any children younger than 18. <br/> **Earliest date available:** 2021-12-19 | P3 |
| `smoothed_wchild_vaccine_already` | Estimated percentage of people whose oldest child is already vaccinated against COVID-19, among people with any children younger than 18. <br/> **Earliest date available:** 2022-03-23 | P3 |
| `smoothed_wchild_vaccine_yes_def` | Estimated percentage of people who would "definitely" get their oldest child vaccinated against COVID-19 when eligible, among people with any children younger than 18. <br/> **Earliest date available:** 2022-03-23 | P3 |
| `smoothed_wchild_vaccine_yes_prob` | Estimated percentage of people who would "probably" get their oldest child vaccinated against COVID-19 when eligible, among people with any children younger than 18. <br/> **Earliest date available:** 2022-03-23 | P3 |
| `smoothed_wchild_vaccine_no_prob` | Estimated percentage of people who would "probably not" get their oldest child vaccinated against COVID-19 when eligible, among people with any children younger than 18. <br/> **Earliest date available:** 2022-03-23 | P3 |
| `smoothed_wchild_vaccine_no_def` | Estimated percentage of people who would "definitely not" get their oldest child vaccinated against COVID-19 when eligible, among people with any children younger than 18. <br/> **Earliest date available:** 2022-03-23 | P3 |
| `smoothed_wvaccinate_children` | *Discontinued as of Wave 12, Dec 19, 2021* Estimated percentage of respondents with children who report that they will definitely or probably get the vaccine for their children. <br/> **Earliest date available:** 2021-06-04 | E4 |

### Vaccine Doses

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_winitial_dose_one_of_one` | Estimated percentage of respondents who initially received one dose of a one-dose COVID-19 vaccine, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2d |
| `smoothed_winitial_dose_one_of_two` | Estimated percentage of respondents who initially received one dose of a two-dose COVID-19 vaccine, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2d |
| `smoothed_winitial_dose_two_of_two` | Estimated percentage of respondents who initially received two doses of a two-dose COVID-19 vaccine, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2d |
| `smoothed_wvaccinated_one_booster` | Estimated percentage of respondents who have received one booster dose of a COVID-19 vaccine, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2b |
| `smoothed_wvaccinated_two_or_more_boosters` | Estimated percentage of respondents who have received two or more booster doses of a COVID-19 vaccine, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2b |
| `smoothed_wvaccinated_no_booster` | Estimated percentage of respondents who have not received any COVID-19 vaccine booster doses, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2b |
| `smoothed_wvaccinated_at_least_one_booster` | Estimated percentage of respondents who have received one or more dose of a COVID-19 vaccine, among respondents who have received any COVID-19 vaccine. <br/> **Earliest date available:** 2022-03-04 | V2b |
| `smoothed_wvaccinated_booster_accept` | Estimated percentage of respondents who either "definitely" or "probably" plan to get a booster shot of the COVID-19 vaccine, among respondents who have received any COVID-19 vaccine and who indicated that they have not yet received any COVID-19 boosters. <br/> **Earliest date available:** 2022-03-04 | V2c |
| `smoothed_wvaccinated_booster_hesitant` | Estimated percentage of respondents who either "definitely" don't or "probably" don't plan to get a booster shot of the COVID-19 vaccine, among respondents who have received any COVID-19 vaccine and who indicated that they have not yet received any COVID-19 boosters. <br/> **Earliest date available:** 2022-03-04 | V2c |
| `smoothed_wvaccinated_booster_defyes` | Estimated percentage of respondents who "definitely" plan to get a booster shot of the COVID-19 vaccine, among respondents who have received any COVID-19 vaccine and who indicated that they have not yet received any COVID-19 boosters. <br/> **Earliest date available:** 2022-03-04 | V2c |
| `smoothed_wvaccinated_booster_probyes` | Estimated percentage of respondents who "probably" plan to get a booster shot of the COVID-19 vaccine, among respondents who have received any COVID-19 vaccine and who indicated that they have not yet received any COVID-19 boosters. <br/> **Earliest date available:** 2022-03-04 | V2c |
| `smoothed_wvaccinated_booster_probno` | Estimated percentage of respondents who "probably" don't plan to get a booster shot of the COVID-19 vaccine, among respondents who have received any COVID-19 vaccine and who indicated that they have not yet received any COVID-19 boosters. <br/> **Earliest date available:** 2022-03-04 | V2c |
| `smoothed_wvaccinated_booster_defno` | Estimated percentage of respondents who "definitely" don't plan to get a booster shot of the COVID-19 vaccine, among respondents who have received any COVID-19 vaccine and who indicated that they have not yet received any COVID-19 boosters. <br/> **Earliest date available:** 2022-03-04 | V2c |
| `smoothed_wreceived_2_vaccine_doses` | *Discontinued mid-Wave 11, Nov 8, 2021* Estimated percentage of respondents who have received two doses of a COVID-19 vaccine, among respondents who have received either one or two doses of a COVID-19 vaccine. This item was shown to respondents starting in Wave 7. <br/> **Earliest date available:** 2021-02-06 | V2 |

### Barriers to Accessing Vaccination

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wvaccine_barrier_eligible_tried` | Estimated percentage of respondents who report eligibility requirements as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_no_appointments_tried` | Estimated percentage of respondents who report lack of vaccine or vaccine appointments as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_appointment_time_tried` | Estimated percentage of respondents who report available appointment times as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_technical_difficulties_tried` | Estimated percentage of respondents who report technical difficulties with the website or phone line as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_document_tried` | Estimated percentage of respondents who report inability to provide required documents as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_technology_access_tried` | Estimated percentage of respondents who report limited access to internet or phone as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_travel_tried` | Estimated percentage of respondents who report difficulty traveling to vaccination sites as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_language_tried` | Estimated percentage of respondents who report information not being available in their native language as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_childcare_tried` | Estimated percentage of respondents who report lack of childcare as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_time_tried` | Estimated percentage of respondents who report difficulty getting time away from work or school as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_type_tried` | Estimated percentage of respondents who report available vaccine type as a barrier to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_none_tried` | Estimated percentage of respondents who report experiencing none of the listed barriers to getting the vaccine, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15b |
| `smoothed_wvaccine_barrier_other_tried` | Estimated percentage of respondents who report experiencing some unlisted issue, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-12-19 | V15b |
| `smoothed_wvaccine_barrier_appointment_location_tried` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents for whom the available appointment locations didn't work, among those who have tried to get vaccinated. <br/> **Earliest date available:** 2021-12-19 | V15b |
| `smoothed_wvaccine_barrier_eligible` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report eligibility requirements as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_no_appointments` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report lack of vaccine or vaccine appointments as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_appointment_time` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report available appointment times as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_technical_difficulties` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report technical difficulties with the website or phone line as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_document` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report inability to provide required documents as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_technology_access` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report limited access to internet or phone as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_travel` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report difficulty traveling to vaccination sites as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_language` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report information not being available in their native language as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_childcare` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report lack of childcare as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_time` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report difficulty getting time away from work or school as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_type` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report available vaccine type as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_none` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report experiencing none of the listed barriers to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-06-04 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_other` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report experiencing some unlisted issue, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-12-19 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_appointment_location` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents for whom the available appointment locations didn't work, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-12-19 | V15a and V15b, or V15c and V15b |
| `smoothed_wvaccine_barrier_eligible_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report eligibility requirements as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_no_appointments_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report lack of vaccine or vaccine appointments as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_appointment_time_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report available appointment times as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_technical_difficulties_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report technical difficulties with the website or phone line as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_document_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report inability to provide required documents as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_technology_access_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report limited access to internet or phone as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_travel_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report difficulty traveling to vaccination sites as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_language_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report information not being available in their native language as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_childcare_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report lack of childcare as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_time_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report difficulty getting time away from work or school as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_type_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report available vaccine type as a barrier to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_none_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report experiencing none of the listed barriers to getting the vaccine, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_other_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents who report experiencing some unlisted issue, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |
| `smoothed_wvaccine_barrier_appointment_location_has` | *Discontinued as of Wave 13, Jan 30, 2022* Estimated percentage of respondents for whom the available appointment locations didn't work, among those who have already been vaccinated. <br/> **Earliest date available:** 2021-07-30 | V15a or V15c |

### Reasons for Vaccine Hesitancy

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wworried_vaccine_side_effects` | Estimated percentage of respondents who are very or moderately concerned that they would "experience a side effect from a COVID-19 vaccination." **Note:** Until March 2, 2021, all respondents answered this question, including those who had already received one or more doses of a COVID-19 vaccine; beginning on that date, only respondents who said they have not received a COVID vaccine are asked this question. <br/> **Earliest date available:** 2021-01-12 | V9 |
| `smoothed_whesitancy_reason_sideeffects` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about side effects, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_allergic` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about having an allergic reaction, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_ineffective` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't know if a COVID-19 vaccine will work, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_unnecessary` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't believe they need a COVID-19 vaccine, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_dislike_vaccines_generally` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they dislike vaccines generally, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-12-19 | V5abc |
| `smoothed_whesitancy_reason_dislike_vaccines` | *Discontinued as of Wave 12, Dec 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they dislike vaccines, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_not_recommended` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because their doctor did not recommend it, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_wait_safety` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they want to wait to see if the COVID-19 vaccines are safe, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_low_priority` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they think other people need it more than they do, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_cost` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about the cost, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_distrust_vaccines` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't trust COVID-19 vaccines, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_distrust_gov` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't trust the government, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_health_condition` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they have a health condition that may impact the safety of a COVID-19 vaccine, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_pregnant` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they are pregnant or breastfeeding, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_religious` | Estimated percentage of respondents who say they are hesitant to get vaccinated because it is against their religious beliefs, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |
| `smoothed_whesitancy_reason_other` | Estimated percentage of respondents who say they are hesitant to get vaccinated for another reason, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered (item V3). This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-26 | V5abc |

### Reasons for Believing Vaccine is Unnecessary

Respondents who indicate that "I don't believe I need a COVID-19 vaccine" (in
items V5a, V5b, V5c, or, prior to Wave 11, V5d) are asked a follow-up item
asking why they don't believe they need the vaccine. These signals summarize
the reasons selected. Respondents who do not select any reason (including
"Other") are treated as missing.

**Note**: Item V5d was removed in Wave 11, thus these indicators no longer
include respondents who indicate in V5d that "I don't believe I need a
COVID-19 vaccine". Item V5d was shown to those who received one dose of a
COVID-19 vaccine, but are not planning to get all recommended doses.

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wdontneed_reason_had_covid` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they already had the illness, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |
| `smoothed_wdontneed_reason_dont_spend_time` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't spend time with high-risk people, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |
| `smoothed_wdontneed_reason_not_high_risk` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they are not in a high-risk group, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |
| `smoothed_wdontneed_reason_precautions` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they will use other precautions, such as a mask, instead, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |
| `smoothed_wdontneed_reason_not_serious` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't believe COVID-19 is a serious illness, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |
| `smoothed_wdontneed_reason_not_beneficial` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't think vaccines are beneficial, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |
| `smoothed_wdontneed_reason_other` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine for another reason, among respondents who provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-03-12 | V6 |

### Outreach and Image

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wvaccine_likely_friends` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by friends and family, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-20 | V4 |
| `smoothed_wvaccine_likely_local_health` | *Discontinued as of Wave 8, Feb 8, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by local health workers, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-20 | V4 |
| `smoothed_wvaccine_likely_who` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by the World Health Organization, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-20 | V4 |
| `smoothed_wvaccine_likely_govt_health` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by government health officials, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-20 | V4 |
| `smoothed_wvaccine_likely_politicians` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by politicians, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-20 | V4 |
| `smoothed_wvaccine_likely_doctors` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by doctors and other health professionals they go to for medical care, among respondents who have not yet been vaccinated. This item was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-08 | V4 |

The "vaccine_likely_*" indicators are based on questions added in Wave 6 of
the survey, introduced on December 19, 2020; however, Delphi only enabled item
V1 beginning January 6, 2021.


## Mental Health Indicators

Signals beginning `smoothed_w` are [adjusted using survey weights to be
demographically representative](#survey-weighting-and-estimation) as described
below. Weighted signals have 1-2 days of lag, so if low latency is paramount,
unweighted signals are also available. These begin `smoothed_`, such as
`smoothed_anxious_5d` instead of `smoothed_wanxious_5d`.

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wworried_finances` | Estimated percentage of respondents who report being very or somewhat worried about their "household's finances for the next month" <br/> **Earliest date available:** 2020-09-08 | C15 |
| `smoothed_wanxious_7d` | Estimated percentage of respondents who reported feeling "nervous, anxious, or on edge" for most or all of the past 7 days. This item was shown to respondents starting in Wave 10. <br/> **Earliest date available:** 2021-03-02 | C8a or C18a |
| `smoothed_wdepressed_7d` | Estimated percentage of respondents who reported feeling depressed for most or all of the past 7 days. This item was shown to respondents starting in Wave 10. <br/> **Earliest date available:** 2021-03-02 | C8a or C18b |
| `smoothed_wworried_catch_covid` | Estimated percentage of respondents worrying either a great deal or a moderate amount about catching COVID-19. <br/> **Earliest date available:** 2021-05-20 | G1 |
| `smoothed_wfelt_isolated_7d` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who reported feeling "isolated from others" for most or all of the past 7 days. This item was shown to respondents starting in Wave 10. <br/> **Earliest date available:** 2021-03-02 | C8a |
| `smoothed_wanxious_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who reported feeling "nervous, anxious, or on edge" for most or all of the past 5 days <br/> **Earliest date available:** 2020-09-08 | C8 |
| `smoothed_wdepressed_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who reported feeling depressed for most or all of the past 5 days <br/> **Earliest date available:** 2020-09-08 | C8 |
| `smoothed_wfelt_isolated_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who reported feeling "isolated from others" for most or all of the past 5 days <br/> **Earliest date available:** 2020-09-08 | C8 |
| `smoothed_wworried_become_ill` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who reported feeling very or somewhat worried that "you or someone in your immediate family might become seriously ill from COVID-19" <br/> **Earliest date available:** 2020-09-08 | C9 |

Some of these questions were present in the earliest waves of the survey, but
only in Wave 4 did respondents consent to our use of aggregate data to
study other impacts of COVID, such as mental health. Hence, these aggregates only
include respondents to Wave 4 and later waves, beginning September 8, 2020.


## Belief, Experience, and Information Indicators

Signals beginning `smoothed_w` are [adjusted using survey weights to be
demographically representative](#survey-weighting-and-estimation) as described
below. Weighted signals have 1-2 days of lag, so if low latency is paramount,
unweighted signals are also available. These begin `smoothed_`, such as
`smoothed_belief_children_immune` instead of `smoothed_wbelief_children_immune`.

### Beliefs About COVID-19

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- |
| `smoothed_wbelief_masking_effective` | Estimated percentage of respondents who believe that wearing a face mask is either very or moderately effective for preventing the spread of COVID-19. <br/> **Earliest date available:** 2021-06-04 | G3 | Wave 11, May 19, 2021 |
| `smoothed_wbelief_distancing_effective` | Estimated percentage of respondents who believe that social distancing is either very or moderately effective for preventing the spread of COVID-19. <br/> **Earliest date available:** 2021-05-20 | G2 | Wave 11, May 19, 2021 |
| `smoothed_wbelief_vaccinated_mask_unnecessary` | Estimated percentage of people who believe that the statement "Getting the COVID-19 vaccine means that you can stop wearing a mask around people outside your household" is definitely or probably true. <br/> **Earliest date available:** 2021-05-20 | I1 | Wave 11, May 19, 2021 |
| `smoothed_wbelief_children_immune` | Estimated pPercentage of people who believe that the statement "Children cannot get COVID-19" is definitely or probably true. <br/> **Earliest date available:** 2021-05-20 | I2 | Wave 11, May 19, 2021 |
| `smoothed_wbelief_created_small_group` | Estimated percentage of people who believe that the statement "COVID-19 was deliberately created by a small group of people who secretly manipulate world events" is definitely or probably true. <br/> **Earliest date available:** 2021-05-20 | I3 | Wave 11, May 19, 2021 |
| `smoothed_wbelief_govt_exploitation` | Estimated percentage of people who indicate that the statement "The COVID-19 pandemic is being exploited by the government to control people" is definitely or probably true. <br/> **Earliest date available:** 2021-05-20 | I4 | Wave 11, May 19, 2021 |


### Medical Care Experiences

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- |
| `smoothed_wdelayed_care_cost` | Estimated percentage of respondents who have ever delayed or not sought medical care in the past year because of cost. <br/> **Earliest date available:** 2021-05-20 | K1 | Wave 11, May 19, 2021 |
| `smoothed_wrace_treated_fairly_healthcare` | Estimated percentage of respondents who somewhat or strongly agree that people of their race are treated fairly in a healthcare setting. <br/> **Earliest date available:** 2021-05-20 | K2 | Wave 11, May 19, 2021 |


### Sources of News

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- |
| `smoothed_wreceived_news_local_health` | Estimated percentage of respondents who received news about COVID-19 from local health workers, clinics, and community organizations in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_experts` | Estimated percentage of respondents who received news about COVID-19 from scientists and other health experts in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_cdc` | Estimated percentage of respondents who received news about COVID-19 from the CDC in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_govt_health` | Estimated percentage of respondents who received news about COVID-19 from government health authorities or officials in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_politicians` | Estimated percentage of respondents who received news about COVID-19 from politicians in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_journalists` | Estimated percentage of respondents who received news about COVID-19 from journalists in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_friends` | Estimated percentage of respondents who received news about COVID-19 from friends and family in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_religious` | Estimated percentage of respondents who received news about COVID-19 from religious leaders in the past 7 days. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |
| `smoothed_wreceived_news_none` | Estimated percentage of respondents who in the past 7 days received news about COVID-19 from none of the listed sources. <br/> **Earliest date available:** 2021-05-20 | I5 | Wave 11, May 19, 2021 |

### Trusted Sources of Information

| Signal | Description | Survey Item |
| --- | --- | --- |
| `smoothed_wtrust_covid_info_doctors` | Estimated percentage of respondents who trust doctors and other health professionals they go to for medical care to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_experts` | Estimated percentage of respondents who trust scientists and other health experts to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_cdc` | Estimated percentage of respondents who trust the Centers for Disease Control (CDC) to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_govt_health` | Estimated percentage of respondents who trust government health officials to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_politicians` | Estimated percentage of respondents who trust politicians to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_journalists` | Estimated percentage of respondents who trust journalists to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_friends` | Estimated percentage of respondents who trust friends and family to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |
| `smoothed_wtrust_covid_info_religious` | Estimated percentage of respondents who trust religious leaders to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-05-19 | I6 |

### Desired Information

| Signal | Description | Survey Item | Introduced |
| --- | --- | --- |
| `smoothed_wwant_info_covid_treatment` | Estimated percentage of people who want more information about the treatment of COVID-19. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_vaccine_access` | Estimated percentage of people who want more information about how to get a COVID-19 vaccine. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_vaccine_types` | Estimated percentage of people who want more information about different types of COVID-19 vaccines. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_covid_variants` | Estimated percentage of people who want more information about COVID-19 variants and mutations. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_children_education` | Estimated percentage of people who want more information about how to support their children's education. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_mental_health` | Estimated percentage of people who want more information about how to maintain their mental health. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_relationships` | Estimated percentage of people who want more information about how to maintain their social relationships despite physical distancing. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_employment` | Estimated percentage of people who want more information about employment and other economic and financial issues. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |
| `smoothed_wwant_info_none` | Estimated percentage of people who want more information about none of the listed topics. <br/> **Earliest date available:** 2021-05-20 | I7 | Wave 11, May 19, 2021 |


## Limitations

When interpreting the signals above, it is important to keep in mind several
limitations of this survey data.

* **Survey population.** People are eligible to participate in the survey if
  they are age 18 or older, they are currently located in the USA, and they are
  an active user of Facebook. The survey data does not report on children under
  age 18, and the Facebook adult user population may differ from the United
  States population generally in important ways. We use our [survey
  weighting](#survey-weighting-and-estimation) to adjust the estimates to match
  age and gender demographics by state, but this process doesn't adjust for
  other demographic biases we may not be aware of.
* **Non-response bias.** The survey is voluntary, and people who accept the
  invitation when it is presented to them on Facebook may be different from
  those who do not. The [survey weights provided by
  Facebook](#survey-weighting-and-estimation) attempt to model the probability
  of response for each user and hence adjust for this, but it is difficult to
  tell if these weights account for all possible non-response bias.
* **Social desirability.** Previous survey research has shown that people's
  responses to surveys are often biased by what responses they believe are
  socially desirable or acceptable. For example, if it there is widespread
  pressure to wear masks, respondents who do *not* wear masks may feel pressured
  to answer that they *do*. This survey is anonymous and online, meaning we
  expect the social desirability effect to be smaller, but it may still be
  present.
* **False responses.** As with anything on the Internet, a small percentage of
  users give deliberately incorrect responses. We discard a small number of
  responses that are obviously false, but do **not** perform extensive
  filtering. However, the large size of the study, and our procedure for
  ensuring that each respondent can only be counted once when they are invited
  to take the survey, prevents individual respondents from having a large effect
  on results.
* **Repeat invitations.** Individual respondents can be invited by Facebook to
  take the survey several times. Usually Facebook only re-invites a respondent
  after one month. Hence estimates of values on a single day are calculated
  using independent survey responses from unique respondents (or, at least,
  unique Facebook accounts), whereas estimates from different months may involve
  the same respondents.

Whenever possible, you should compare this data to other independent sources. We
believe that while these biases may affect point estimates -- that is, they may
bias estimates on a specific day up or down -- the biases should not change
strongly over time. This means that *changes* in signals, such as increases or
decreases, are likely to represent true changes in the underlying population,
even if point estimates are biased.

### Privacy Restrictions

To protect respondent privacy, we discard any estimate (whether at a county,
MSA, HRR, or state level) that is based on fewer than 100 survey responses. For
signals reported using a 7-day average (those beginning with `smoothed_`), this
means a geographic area must have at least 100 responses in 7 days to be
reported.

This affects some items more than others. For instance, items about vaccine
hesitancy reasons are only asked of respondents who are unvaccinated and
hesitant, not to all survey respondents. It also affects some geographic areas
more than others, particularly rural areas with low population densities. When
doing analysis of county-level data, one should be aware that missing counties
are typically more rural and less populous than those present in the data, which
may introduce bias into the analysis.

### Declining Response Rate

We have noted a steady decrease in the number of daily survey responses,
beginning no later than January 2021. As the number of survey responses
declines, some indicators will become unavailable once they no longer meet the
privacy limit for sample size. This affects some signals, such as those based on
a subset of responses, more than others, with finer geographic resolutions
becoming unavailable first.

### Target Region

Facebook only invites users to take the survey if they appear, based on
attributes in their Facebook profiles, to reside in the 50 states or
Washington, DC. Puerto Rico is sampled separately as part of the
[international version of the survey](https://covidmap.umd.edu/). If Facebook
believes a user qualifies for the survey, but the user then replies that they
live in Puerto Rico or another US territory, we do not include their response
in the aggregations.


## Survey Weighting and Estimation

When Facebook sends a user to our survey, it generates a random ID number and
sends this to us as well. Once the user completes the survey, we pass this ID
number back to Facebook to confirm completion, and in return receive a weight.
(The random ID number is completely meaningless for any other purpose than
receiving this weight, and does not allow us to access any information about the
user's Facebook profile. Nor does it provide Facebook any information about the
survey responses.)

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
Facebook user and take our survey. The adjustment we make follows a standard
inverse probability weighting strategy.

Detailed documentation on how Facebook calculates these weights is available in
our [survey weight documentation](../../symptom-survey/weights.md).

For unweighted survey signals, we set $$w^\text{part}_i = 1$$ for all
respondents.

### Geographic Weighting and Mixing

Besides the participation weight $$w^\text{part}_i$$, each survey response
receives a geographical-division weight $$w^{\text{geodiv}}_i$$ describing how
much a participant's ZIP code "belongs" in the spatial unit of interest. For
example, a ZIP code may overlap with multiple counties, so the weight describes
what proportion of the ZIP code's population is in each county.

Each survey's weight is hence $$w^{\text{init}}_i = w^{\text{part}}_i
w^{\text{geodiv}}_i$$. When a ZIP code spans multiple counties or states, a
single survey may have different weights when used to calculate different
geographic aggregates.

### Adjusting Household ILI and CLI

For a given aggregation unit (for example, daily-county), let $$X_i$$ and
$$Y_i$$ denote the numbers of ILI and CLI cases in household $$i$$, respectively
(computed according to the simple strategy above), and let $$N_i$$ denote the
total number of people in the household. Let $$i = 1, \dots, m$$ denote the
surveys started during the time period of interest and reported in a ZIP code
intersecting the spatial unit of interest.

First, we adjust the initial weights $$w^\text{init}$$ to reduce sensitivity to
any individual survey by "mixing" them with a uniform weighting across all
relevant surveys. This prevents specific survey respondents with high survey
weights having disproportionate influence on the weighted estimates.

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
\widehat{\mathrm{se}}(\hat{p}_w) &= 100 \cdot \frac{1}{1 + n_e} \sqrt{
  \left(\frac12 - \frac{\hat{p}_w}{100}\right)^2 +
  n_e^2 \hat{s}_p^2
}\\
\widehat{\mathrm{se}}(\hat{q}_w) &= 100 \cdot \frac{1}{1 + n_e} \sqrt{
  \left(\frac12 - \frac{\hat{q}_w}{100}\right)^2 +
  n_e^2 \hat{s}_q^2
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
of 1/2 with weight $$1/n_e$$, assigned to appear like a single effective
observation. The use of the pseudo-observation prevents standard error estimates
of zero, and in simulations improves the quality of the standard error
estimates. See the [Appendix](#appendix) for further motivation for these
estimators.

<div style="background-color:#FCC; padding: 10px 30px;"><strong>Note:</strong>
Currently the standard errors are calculated as though all survey weights are
equal, that is \(w^\text{part}_i = 1\) for all respondents. The result is that
reported standard errors are artificially narrow for weighted estimates. This
will be corrected in a future update to the API.
</div>

The pseudo-observation is not used in $$\hat{p}$$ and $$\hat{q}$$ themselves, to
avoid potentially large amounts of estimation bias, as $$p$$ and $$q$$ are
expected to be small.

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

In a given aggregation unit (for example, daily-county), let $$U_i$$ denote the
indicator that the survey respondent knows someone in their community with CLI,
including their household, for survey $$i$$, out of $$m$$ surveys collected.
Also let $$w_i$$ be the weight that accompanies survey $$i$$, normalized to sum
to 1 as above. Then our initial weighted estimate of the population proportion
$$a$$ is:

$$
\hat{a}_{w, \text{init}} = 100 \cdot \sum_{i=1}^m w_i U_i
$$

To prevent observations and standard errors from being zero, we add a
pseudo-observation of 1/2 with weight $$1/n_e$$. (This psuedo-observation can be
thought of as equivalent to using a Bayesian estimate of the proportion, with a
Jeffreys prior.) The estimate is hence:

$$
\hat{a}_w = 100 \cdot \frac{n_e \frac{\hat{a}_{w, \text{init}}}{100} + \frac12}{1 + n_e},
$$

with estimated standard error:

$$
\widehat{\mathrm{se}}(\hat{a}_w) = 100 \cdot \sqrt{\frac{\frac{\hat{a}_w}{100}(1-\frac{\hat{a}_w}{100})}{1 + n_e}}
$$

which is the plug-in estimate of the standard error of the binomial proportion.


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
