---
title: Symptom Surveys
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Symptom Surveys

* **Source name:** `fb-survey`
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#fb-survey)

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

The survey weights, provided by Facebook, are intended to make the sample
representative of the US population, according to the state, age, and gender of
the US population from the 2018 Census March Supplement.

Along with the `raw_` signals, there are additional signals with names beginning
with `smoothed_`. These estimate the same quantities as the above signals, but
are smoothed in time to reduce day-to-day sampling noise; importantly (due to
the way in which our smoothing works, which is based on pooling data across
successive days), these smoothed signals are generally available at many more
counties (and MSAs) than the raw signals.
