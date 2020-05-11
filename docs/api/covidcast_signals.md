# Delphi's COVID-19 Surveillance Streams Data

Delphi's COVID-19 Surveillance Streams data includes the following data sources.
Data from these sources is expected to be updated daily. You can use the
[`covidcast_meta`](covidcast_meta.md) API endpoint to get summary information
about the ranges of the different attributes for the different data sources
currently in the data.

## Signals

### `fb-survey`

This indicator estimates the percentage of people who have a COVID-like illness
(fever, along with cough, or shortness of breath, or difficulty breathing) or
influenza-like illness (fever, along with cough or sore throat), based on
symptom surveys run by Carnegie Mellon. Facebook directs a random sample of its
users to these surveys, which are voluntary. Individual survey responses are
held by CMU and are shareable with other health researchers under a data use
agreement. No individual survey responses are shared back to Facebook.

| Signal | Description |
| --- | --- |
| `raw_cli` | Estimated fraction of people with COVID-like illness, with no smoothing or survey weighting |
| `raw_ili` | Estimated fraction of people with influenza-like illness, with no smoothing or survey weighting |
| `raw_wcli` | Estimated fraction of people with COVID-like illness; adjusted using survey weights |
| `raw_wili` | Estimated fraction of people with influenza-like illness; adjusted using survey weights |

The survey weights, provided by Facebook, are intended to make the sample
representative of the US population, according to the state, age, and gender of
the US population from the 2018 Census March Supplement.

Along with the `raw_` signals, there are additional signals with names beginning
with `smoothed_`. These estimate the same quantities as the above signals, but
smoothed in time to reduce day-to-day sampling noise.

### `google-survey`

This indicator estimates the percentage of people who know someone in their
community with a COVID-like illness (fever, along with cough, or shortness of
breath, or difficulty breathing). The data is based on Google-run symptom
surveys, through publisher websites, their Opinions Reward app, and similar
applications. Respondents can opt to skip the survey and complete a different
one if they prefer not to answer.

The surveys are just one question long, and ask "Do you know someone in your
community who is sick (fever, along with cough, or shortness of breath, or
difficulty breathing) right now?" Using this survey data, we estimate the
percentage of people in a given location, on a given day, that know somebody who
has a COVID-like illness. Note that this is tracking a different quantity than
the surveys through Facebook, and (unsurprisingly) the estimates here tend to be
much larger.

| Signal | Description |
| --- | --- |
| `raw_cli` | Estimated fraction of people who know someone in their community with COVID-like illness |
| `smoothed_cli` | Estimated fraction of people who know someone in their community with COVID-like illness, smoothed in time |

### `ght`

Data signal based on Google searches, provided to us by Google Health
Trends.  Using this search data, we estimate the volume of COVID-related
searches in a given location, on a given day.  This signal is measured in
arbitrary units (its scale is meaningless); larger numbers represent higher
numbers of COVID-related searches.

| Signal | Description |
| --- | --- |
 | `raw_search` | Google search volume for COVID-related searches, in arbitrary units that are normalized for population |
| `smoothed_search` | Google search volume for COVID-related searches, in arbitrary units that are normalized for population, smoothed in time using a Gaussian linear smoother |

### `doctor-visits`

Data based on outpatient visits, provided to us by healthcare partners. Using
this outpatient data, we estimate the percentage of COVID-related doctor's
visits in a given location, on a given day.

| Signal | Description |
| --- | --- |
| `smoothed_cli` | Estimated fraction of outpatient doctor visits primarily about COVID-related symptoms, based on data from healthcare partners. Smoothed in time using a Gaussian linear smoother |
| `smoothed_adj_cli` | Same, but with systematic day-of-week effects removed |

Day-of-week effects are removed by fitting a model to all data in the United
States; the model includes a fixed effect for each day of the week. Once these
effects are estimated, they are subtracted from each geographic area's time
series. This removes day-to-day variation that arises solely from clinic
schedules, work schedules, and other variation in doctor's visits that arise
solely because of the day of week.

Note that because doctor's visits may be reported to our healthcare partners
several days after they occur, these signals are typically available with
several days of lag. This means that estimates for a specific day are only
available several days later.

### `quidel`

Data signal based on flu lab tests, provided to us by Quidel, Inc. When a
patient (whether at a doctor’s office, clinic, or hospital) has COVID-like
symptoms, doctors may perform a flu test to rule out seasonal flu (influenza),
because these two diseases have similar symptoms. Using this lab test data, we
estimate the total number of flu tests per medical device (a measure of testing
frequency), and the percentage of flu tests that are *negative* (since ruling
out flu leaves open another cause---possibly covid---for the patient's
symptoms), in a given location, on a given day.

| Signal | Description |
| --- | --- |
| `raw_pct_negative` | The fraction of flu tests that are negative, suggesting the patient's illness has another cause, possibly COVID-19 |
| `smoothed_pct_negative` | Same as above, but smoothed over 7 days |
| `raw_tests_per_device` | The number of flu tests conducted by each testing device; measures volume of testing |
| `smoothed_tests_per_device` | Same as above, but smoothed over 7 days |

### `jhu-csse`

| Signal | Description |
| --- | --- |
| `confirmed_cumulative_num` | Cumulative number of confirmed COVID-19 cases |
| `confirmed_incidence_num` | Number of new confirmed COVID-19 cases, daily |
| `confirmed_incidence_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily |
| `deaths_cumulative_num` | Cumulative number of confirmed deaths due to COVID-19 |
| `deaths_incidence_num` | Number of new confirmed deaths due to COVID-19, daily |
| `deaths_incidence_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily |

These signals are collected by the Center for Systems Science and Engineering at
Johns Hopkins University, and our signals are taken directly from [their GitHub
repository](https://github.com/CSSEGISandData/COVID-19) without filtering,
smoothing, or changes.

## COVIDcast Map Signals

The following signals are currently displayed on [the public COVIDcast
map](https://covidcast.cmu.edu/):

| Name | Source | Signal |
| --- | --- | --- |
| Doctor's Visits | `doctor-visits` | `smoothed_adj_cli` |
| Surveys (Facebook) | `fb-survey` | `smoothed_cli` |
| Surveys (Google) | `google-survey` | `smoothed_cli` |
| Search Trends (Google) | `ght` | `smoothed_search` |
| Cases (JHU) | `jhu-csse` | `confirmed_incidence_prop` |
| Deaths (JHU) | `jhu-csse` | `deaths_incidence_prop` |
