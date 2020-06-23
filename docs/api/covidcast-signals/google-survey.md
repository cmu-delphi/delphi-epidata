---
title: Google Symptom Surveys
parent: Inactive Signals
grand_parent: COVIDcast API
---

# Google Symptom Surveys

* **Source name:** `google-survey`
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never

Data source based on Google-run symptom surveys, through publisher websites,
their Opinions Reward app, and similar applications. Respondents can opt to skip
the survey and complete a different one if they prefer not to answer. The survey
is just one question long, and asks "Do you know someone in your community who
is sick (fever, along with cough, or shortness of breath, or difficulty
breathing) right now?" Using this survey data, we estimate the percentage of
people in a given location, on a given day, that *know somebody who has a
COVID-like illness*. Note that this is tracking a different quantity than the
surveys through Facebook, and (unsurprisingly) the estimates here tend to be
much larger.

The survey sampled from all counties with greater than 100,000 population, along
with a separate random sample from each state. This means that the megacounties
(discussed in the [COVIDcast API documentation](covidcast.md)) are always the
counties with populations smaller than 100,000, and megacounty estimates are
created by combining the state-level survey with the observed county surveys.

These surveys were run daily until May 15, 2020. After that date, new national
data will not be collected regularly, although the surveys may be deployed in
specific geographical areas as needed to support forecasting efforts.

| Signal | Description |
| --- | --- |
| `raw_cli` | Estimated percentage of people who know someone in their community with COVID-like illness |
| `smoothed_cli` | Estimated percentage of people who know someone in their community with COVID-like illness, smoothed in time |
