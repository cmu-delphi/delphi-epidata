---
title: Youtube Survey
parent: Inactive Signals
grand_parent: COVIDcast Main Endpoint
---

# Youtube Survey
{: .no_toc}

* **Source name:** `youtube-survey`
* **Earliest issue available:** April, 04, 2020
* **Number of data revisions since May 19, 2020:** 0
* **Date of last change:** Never
* **Available for:** state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY-NC](../covidcast_licensing.md#creative-commons-attribution-noncommercial)

## Overview

The Youtube-survey is a voluntary COVID-like illness 4-question survey that was part of a research study led by the Delphi group at Carnegie Mellon University. The survey consisted of the following introduction and questions:

This voluntary survey is part of a research study led by the Delphi group at Carnegie Mellon University. Even if you are healthy, your responses may contribute to a better public health understanding of where the coronavirus pandemic is moving, to improve our local and national responses. The data captured does not include any personally identifiable information about you and your answers to all questions will remain confidential. Published results will be in aggregate and will not identify individual participants or their responses. This study is not conducted by YouTube and no individual responses will be shared back to YouTube. There are no foreseeable risks in participating and no compensation is offered. If you have any questions, contact: delphi-admin-survey-yt@lists.andrew.cmu.edu.

Qualifying Questions
You must be 18 years or older to take this survey. Are you 18 years or older?
What is the ZIP Code of the city or town where you slept last night? [We mean the place where you are currently staying. This may be different from your usual residence.]
What is your current ZIP code?

List of Symptoms
Fever (100°F or higher)
Sore throat
Cough
Shortness of breath
Difficulty breathing

Survey Question 1
"How many additional people in your local community that you know personally are sick (fever, along with at least one other symptom from the above list)?

Survey Question 2
"How many people in your household (including yourself) are sick (fever, along with at least one other symptom from the above list)?"

Survey Question 3
"How many people in your household (including yourself) are experiencing at least one symptom from above?"

Survey Question 4
"In the past 24 hours, have you or anyone in your household experienced any of the following:"

| Signal | Description |
| --- | --- |
| `smoothed_outpatient_covid` | Estimated percentage of outpatient doctor visits with confirmed COVID-19, based on Change Healthcare claims data that has been de-identified in accordance with HIPAA privacy regulations, smoothed in time using a Gaussian linear smoother <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_adj_outpatient_covid` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_outpatient_cli` | Estimated percentage of outpatient doctor visits primarily about COVID-related symptoms, based on Change Healthcare claims data that has been de-identified in accordance with HIPAA privacy regulations, smoothed in time using a Gaussian linear smoother <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_adj_outpatient_cli` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_outpatient_flu` | Estimated percentage of outpatient doctor visits with confirmed influenza, based on Change Healthcare claims data that has been de-identified in accordance with HIPAA privacy regulations, smoothed in time using a Gaussian linear smoother <br/> **Earliest issue available:** 2021-12-06 <br/> **Earliest date available:** 2020-02-01 |
| `smoothed_adj_outpatient_flu` | Same, but with systematic day-of-week effects removed; see [details below](#day-of-week-adjustment) <br/> **Earliest issue available:** 2021-12-06 <br/> **Earliest date available:** 2020-02-01 |

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

### Day-of-Week Adjustment



### Backwards Padding



### Smoothing



## Lag and Backfill



## Limitations

When interpreting the signals above, it is important to keep in mind several
limitations of this survey data.

* **Survey population.** People are eligible to participate in the survey if
  they are age 18 or older, they are currently located in the USA, and they are
  an active user of Youtube. The survey data does not report on children under
  age 18, and the Youtube adult user population may differ from the United
  States population generally in important ways. We use our [survey
  weighting](#survey-weighting-and-estimation) to adjust the estimates to match
  age and gender demographics by state, but this process doesn't adjust for
  other demographic biases we may not be aware of.
* **Non-response bias.** The survey is voluntary, and people who accept the
  invitation when it is presented to them on Youtube may be different from
  those who do not. The [survey weights provided by
  Youtube](#survey-weighting-and-estimation) attempt to model the probability
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
* **Repeat invitations.** Individual respondents can be invited by Youtube to
  take the survey several times. Usually Youtube only re-invites a respondent
  after one month. Hence estimates of values on a single day are calculated
  using independent survey responses from unique respondents (or, at least,
  unique Youtube accounts), whereas estimates from different months may involve
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