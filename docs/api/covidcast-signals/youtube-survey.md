---
title: <i>inactive</i> Youtube Survey
parent: Data Sources and Signals
nav_order: 2
grand_parent: Main Endpoint (COVIDcast)
---

[//]: # (code at https://github.com/cmu-delphi/covid-19/tree/deeb4dc1e9a30622b415361ef6b99198e77d2a94/youtube)

# Youtube Survey
{: .no_toc}

* **Source name:** `youtube-survey`
* **Earliest issue available:** May 01, 2020
* **Number of data revisions since May 19, 2020:** 0
* **Date of last change:** Never
* **Available for:** state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [CC BY-NC](../covidcast_licensing.md#creative-commons-attribution-noncommercial)

## Overview

This data source is based on a short survey about COVID-19-like illness
run by the Delphi group at Carnegie Mellon.
[Youtube directed](https://9to5google.com/2020/04/29/google-covid-19-cmu-research-survey/)
a random sample of its users to these surveys, which were
voluntary. Users age 18 or older were eligible to complete the surveys, and
their survey responses are held by CMU. No individual survey responses are
shared back to Youtube.

This survey was a pared-down version of the
[COVID-19 Trends and Impact Survey (CTIS)](../../symptom-survey/),
collecting data only about COVID-19 symptoms. CTIS is much longer-running
and more detailed, also collecting belief and behavior data. CTIS also reports
demographic-corrected versions of some metrics. See our
[surveys page](https://delphi.cmu.edu/covid19/ctis/) for more detail
about how CTIS works.

The two surveys report some of the same metrics. While nominally the same,
note that values from the same dates differ between the two surveys for
[unknown reasons](#limitations).

As of late April 2020, the number of Youtube survey responses we received each
day was 4-7 thousand. This was not enough coverage to report at finer
geographic levels, so this indicator only reports at the state level. The
survey ran from April 21, 2020 to June 17, 2020, collecting about 159
thousand responses in the United States in that time.

We produce [influenza-like and COVID-like illness indicators](#ili-and-cli-indicators)
based on the survey data.

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Survey Text and Questions

The survey contains the following 5 questions:

1. In the past 24 hours, have you or anyone in your household experienced any of the following:
   - (a) Fever (100 °F or higher)
   - (b) Sore throat
   - (c) Cough
   - (d) Shortness of breath
   - (e) Difficulty breathing
2. How many people in your household (including yourself) are sick (fever, along with at least one other symptom from the above list)?
3. How many people are there in your household (including yourself)?
4. What is your current ZIP code?
5. How many additional people in your local community that you know personally are sick (fever, along with at least one other symptom from the above list)?


## ILI and CLI Indicators

We define COVID-like illness (fever, along with cough, or shortness of breath,
or difficulty breathing) or influenza-like illness (fever, along with cough or
sore throat) for use in forecasting and modeling. Using this survey data, we
estimate the percentage of people (age 18 or older) who have a COVID-like
illness, or influenza-like illness, in a given location, on a given day.

| Signals | Description |
| --- | --- |
| `raw_cli` and `smoothed_cli` | Estimated percentage of people with COVID-like illness <br/> **Earliest date available:** 2020-04-21 |
| `raw_ili` and `smoothed_ili` | Estimated percentage of people with influenza-like illness <br/> **Earliest date available:** 2020-04-21 |

Influenza-like illness or ILI is a standard indicator, and is defined by the CDC
as: fever along with sore throat or cough. From the list of symptoms from Q1 on
our survey, this means a and (b or c).

COVID-like illness or CLI is not a standard indicator. Through our discussions
with the CDC, we chose to define it as: fever along with cough or shortness of
breath or difficulty breathing. From the list of symptoms from Q1 on
our survey, this means a and (c or d or e).

Symptoms alone are not sufficient to diagnose influenza or coronavirus
infections, and so these ILI and CLI indicators are *not* expected to be
unbiased estimates of the true rate of influenza or coronavirus infections.
These symptoms can be caused by many other conditions, and many true infections
can be asymptomatic. Instead, we expect these indicators to be useful for
comparison across the United States and across time, to determine where symptoms
appear to be increasing.


## Estimation

### Estimating Percent ILI and CLI

Estimates are calculated using the
[same method as CTIS](./fb-survey#estimating-percent-ili-and-cli).
However, the Youtube survey does not do weighting.

### Smoothing

The smoothed versions of all `youtube-survey` signals (with `smoothed` prefix) are
calculated using seven day pooling. For example, the estimate reported for June
7 in a specific geographical area is formed by
collecting all surveys completed between June 1 and 7 (inclusive) and using that
data in the estimation procedures described above. Because the smoothed signals combine
information across multiple days, they have larger sample sizes and hence are
available for more locations than the raw signals.

## Lag and Backfill

This indicator has a lag of 2 days. Reported values can be revised for one
day (corresponding to a lag of 3 days), due to how we receive survey
responses. However, these tend to be associated with minimal changes in
value.


## Limitations

When interpreting the signals above, it is important to keep in mind several
limitations of this survey data.

* **Survey population.** People are eligible to participate in the survey if
  they are age 18 or older, they are currently located in the USA, and they are
  an active user of Youtube. The survey data does not report on children under
  age 18, and the Youtube adult user population may differ from the United
  States population generally in important ways. We don't adjust for any
  demographic biases.
* **Non-response bias.** The survey is voluntary, and people who accept the
  invitation when it is presented to them on Youtube may be different from
  those who do not.
* **Social desirability.** Previous survey research has shown that people's
  responses to surveys are often biased by what responses they believe are
  socially desirable or acceptable. For example, if it there is widespread
  pressure to wear masks, respondents who do *not* wear masks may feel pressured
  to answer that they *do*. This survey is anonymous and online, meaning we
  expect the social desirability effect to be smaller, but it may still be
  present.

Whenever possible, you should compare this data to other independent sources. We
believe that while these biases may affect point estimates -- that is, they may
bias estimates on a specific day up or down -- the biases should not change
strongly over time. This means that *changes* in signals, such as increases or
decreases, are likely to represent true changes in the underlying population,
even if point estimates are biased.

### Privacy Restrictions

To protect respondent privacy, we discard any estimate that is based on fewer than 100 survey responses. For
signals reported using a 7-day average (those beginning with `smoothed_`), this
means a geographic area must have at least 100 responses in 7 days to be
reported.

This affects some items more than others. It affects some geographic areas
more than others, particularly areas with smaller populations. This affect is
less pronounced with smoothed signals, since responses are pooled across a
longer time period.


## Source and Licensing

This indicator aggregates responses from a Delphi-run survey that is hosted on the Youtube platform.
The data is licensed as [CC BY-NC](../covidcast_licensing.md#creative-commons-attribution-noncommercial).
