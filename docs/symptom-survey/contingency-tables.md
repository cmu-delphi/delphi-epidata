---
title: Contingency Tables
parent: COVID Symptom Survey
nav_order: 4
---

# Contingency Tables
{: .no_toc}

This documentation describes the fine-resolution contingency tables produced by
grouping [COVID Symptom Survey](./index.md) individual responses by various
demographic features:

* [Weekly files](https://www.cmu.edu/delphi-web/surveys/weekly/)
* [Monthly files](https://www.cmu.edu/delphi-web/surveys/monthly/)

These contingency tables provide demographic breakdowns of COVID-related topics such as
vaccine uptake and acceptance. They are more detailed than the
[coarse aggregates reported in the COVIDcast Epidata API](../api/covidcast-signals/fb-survey.md),
which are grouped only by geographic region. [Individual response data](survey-files.md)
for the survey is available, but only to academic or nonprofit researchers who
sign a Data Use Agreement, whereas these contingency tables are available to the
general public.

Please see our survey [credits](index.md#credits) and [citation information](index.md#citing-the-survey)
for information on how to cite this data if you use it in a publication.

Important updates for data users, including corrections to data or updates on
data processing delays, are posted as `OUTAGES.txt` in the directory where the
data is hosted.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Available Data Files

We provide two types of data files, weekly and monthly. Users who need the most
up-to-date data or are interested in timeseries should use the weekly files,
while those who want to study groups with smaller sample sizes should use the
monthly files. Because monthly aggregates include more responses, they have
lower missingness when grouping by several features at a time.

## Dates

The included files provide estimates for various metrics of interest over a
period of either a full epiweek (or [MMWR
week](https://wwwn.cdc.gov/nndss/document/MMWR_week_overview.pdf), a
standardized numbering of weeks throughout the year) or a full calendar month.

Note: CSVs for the month of January 2021 only use data from January 6-31 due to
a [definitional change in a major vaccine item on January 6](./coding.md#new-items-2).
Indicators based on [item V9 use data starting January 12](./coding.md#new-items-2).
CSVs for the week starting January 6, 2021, only use data from January 6-9 due to the
same definitional change.

## Aggregation

The aggregates are filtered to only include estimates for a particular group if
that group includes 100 or more responses. Especially in the weekly aggregates,
many of the state-level groups have been filtered out due to low sample size. In
such cases, the state marginal files, which group by a single demographic of
interest at a time, will likely provide more coverage.

## File Format

### Naming

Each CSV is named as follows:

    {date}_{region}_{vars}.csv

Dates are of the form `YYYYmmdd`. `date` refers to the first day of the time
period survey responses were aggregated over, in the Pacific time zone (UTC -
7). Unless noted otherwise, the time period is always a complete month or
epiweek. `region` is the geographic level responses were aggregated over. At the
moment, only nation-wide and state groupings are available. `vars` is a list all
other grouping variables used in the aggregation, ordered alphabetically.

### Columns

Within a CSV, the first few columns are the grouping variables, ordered
alphabetically. Each aggregate reports four columns (unrounded):

* `val_<indicator name>`: the main value of interest, e.g., percent, average, or
  count, estimated using the [survey weights](weights.md) to better match state
  demographics
* `se_<indicator name>`: the standard error of `val_<indicator name>`
* `sample_size_<indicator name>`: the number of survey responses used to
  calculate `val_<indicator name>`
* `represented_<indicator name>`: the number of people in the population that
  `val_<indicator name>` represents over all days in the given time period. This
  is the sum of [survey weights](./weights.md) for all survey responses
  used.

All aggregates using the same set of grouping variables appear in a single CSV.
Grouping variables use prefixes to indicate the format of the column and the
originating question.

* `b_` indicates a binary variable, coded as a boolean (True/False or 1/0).
  The originating item may be a yes/no question, or the variable may be
  a binary interpretation of a multiple choice or multi-select item.
* `mc_` indicates a multiple choice question, where the respondent is able to
  select no more than one response. For example, age in D2.
* `ms_` indicates a multi-select question, where the respondent is able to
  select more than one response if desired. For example, pre-existing medical
  conditions in C1.


## Indicators

The files contain [weighted estimates](../api/covidcast-signals/fb-survey.md#survey-weighting) of the percent of
respondents who fulfill one or several criteria. Estimates are broken out by
state, age, gender, race, ethnicity, occupation, and health conditions.

Indicators beginning "hesitant_" (not listed) are variants of other described indicators calculated among respondents who say they would "probably not" or "definitely not" choose to get vaccinated, if offered today (item V3). Indicators beginning "defno_" (not listed) are variants of other described indicators calculated among respondents who say they would "definitely not" choose to get vaccinated, if offered today.

We plan to expand this list of indicators based on research needs; if you have a
public health or research need for a particular variable not listed here, please
contact us at <delphi-survey-info@lists.andrew.cmu.edu>.


### Symptoms

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_cli` | Estimated percentage of people with COVID-like illness, using the same [definition as in the API](../api/covidcast-signals/fb-survey.md#estimating-percent-ili-and-cli). <br/> **Earliest date available:** 2021-01-01 | A1 and A2 |
| `pct_ili` | Estimated percentage of people with influenza-like illness, using the same [definition as in the API](../api/covidcast-signals/fb-survey.md#estimating-percent-ili-and-cli). <br/> **Earliest date available:** 2021-01-01 | A1 and A2 |
| `pct_hh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, including their household, using the same [definition as in the API](../api/covidcast-signals/fb-survey.m#estimating-community-cli). <br/> **Earliest date available:** 2021-01-01 | A1, A2, and A4 |
| `pct_anosmia` | Estimated percentage of people experiencing loss of smell or taste in the last 24 hours. <br/> **Earliest date available:** 2021-01-01 | A2 |

### Behavior

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_direct_contact` | Estimated percentage of people who in the past 24 hours had a non-physical interaction (like conversing) for more than 5 minutes at a distance of 6 feet or less or a physical interaction (like hand-shaking, hugging, or kissing) with anyone outside their household. <br/> **Earliest date available:** 2021-01-01 | C10 |
| `pct_wearing_mask_7d` | Estimated percentage of people who wore a mask for most or all of the time while in public in the past 7 days; those not in public in the past 7 days are not counted. <br/> **Earliest date available:** 2021-02-08 | C14a |
| `pct_wearing_mask_5d` | *Discontinued as of Wave 8, Feb 8, 2021* Estimated percentage of people who wore a mask for most or all of the time while in public in the past 5 days; those not in public in the past 5 days are not counted. <br/> **Earliest date available:** 2021-01-01 | C14 |

### Vaccine Uptake and Acceptance

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccinated` | Estimated percentage of respondents who have already received a COVID vaccine. <br/> **Earliest date available:** 2021-01-01 | V1 |
| `pct_received_2_vaccine_doses` | Estimated percentage of respondents who have received two doses of a COVID-19 vaccine, among respondents who have received either one or two doses of a COVID-19 vaccine. <br/> **Earliest date available:** 2021-01-01 | V2 |
| `pct_vaccinated_or_accept` | Estimated percentage of respondents who *either* have already received a COVID vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today. <br/> **Earliest date available:** 2021-01-01 | V1 and V3 |
| `pct_accept_vaccine` | Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_hesitant_vaccine` | Estimated percentage of respondents who would definitely not or probably not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_defyes` | Estimated percentage of respondents who would definitely choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_probyes` | Estimated percentage of respondents who would probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_probno` | Estimated percentage of respondents who would probably not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_defno` | Estimated percentage of respondents who would definitely not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_informed_access` | Estimated percentage of respondents who are very or moderately informed about how to get a COVID-19 vaccination. <br/> **Earliest date available:** 2021-02-08 | V13 |
| `pct_appointment_have` | Estimated percentage of respondents who have an appointment to get a COVID-19 vaccine, among respondents who answered "Yes, definitely" or "Yes, probably" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-03-02 | V11 |
| `pct_appointment_tried` | Estimated percentage of respondents who have tried to make an appointment to get a COVID-19 vaccine, among respondents who answered "Yes, definitely" or "Yes, probably" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-03-02 | V12 |

### Outreach and Image

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccine_likely_friends` (formerly `pct_trust_fam`)| Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by friends and family, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_who` (formerly `pct_trust_who`) | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by the World Health Organization, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_govt_health` (formerly `pct_trust_govt`) | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by government health officials, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_politicians` (formerly `pct_trust_politicians`) | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by politicians, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_doctors` | Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by doctors and other health professionals they go to for medical care, among respondents who have not yet been vaccinated. This item was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-08 | V4 |
| `pct_vaccine_likely_local_health` (formerly `pct_trust_healthcare`) | *Discontinued as of Wave 8, Feb 8, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by local health workers, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |

### Reasons for Hesitancy

The set of "barrier" items correspond to the set of ["hesitancy_reasons" items
in the API](../api/covidcast-signals/fb-survey.md#reasons-for-hesitancy).

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_worried_vaccine_sideeffects` (formerly `pct_concerned_sideeffects`) | Estimated percentage of respondents who are very or moderately concerned that they would "experience a side effect from a COVID-19 vaccination." **Note:** Until March 2, 2021, all respondents answered this question, including those who had already received one or more doses of a COVID-19 vaccine; beginning on that date, only respondents who said they have not received a COVID vaccine are asked this question. <br/> **Earliest date available:** 2021-01-01 | V9 |
| `pct_barrier_sideeffects` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about side effects, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_allergic` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about having an allergic reaction, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_ineffective` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't know if a COVID-19 vaccine will work, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_dontneed` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't believe they need a COVID-19 vaccine, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_dislike_vaccines` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they dislike vaccines, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_not_recommended` | Estimated percentage of respondents who say they are hesitant to get vaccinated because their doctor did not recommend it, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_wait_safety` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they want to wait to see if the COVID-19 vaccines are safe, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_low_priority` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they think other people need it more than they do, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_cost` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about the cost, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_distrust_vaccines` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't trust COVID-19 vaccines, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_distrust_govt` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't trust the government, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_health_condition` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they have a health condition that may impact the safety of a COVID-19 vaccine, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_pregnant` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are pregnant or breastfeeding, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_religious` | Estimated percentage of respondents who say they are hesitant to get vaccinated because it is against their religious beliefs, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_other` | Estimated percentage of respondents who say they are hesitant to get vaccinated for another reason, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |

### Reasons for Believing Vaccine is Unnecessary

Respondents who indicate that "I don't believe I need a COVID-19 vaccine" (in
items V5a, V5b, V5c, or V5d) are asked a follow-up item asking why they don't
believe they need the vaccine. These signals summarize the reasons selected.
Respondents who do not select any reason (including "Other") are treated as
missing.

This item was shown to respondents starting in Wave 8.

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_dontneed_reason_had_covid` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they already had the illness, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_dont_spend_time` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't spend time with high-risk people, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_not_high_risk` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they are not in a high-risk group, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_precautions` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they will use other precautions, such as a mask, instead, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_not_serious` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't believe COVID-19 is a serious illness, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_not_beneficial` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't think vaccines are beneficial, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_other` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine for another reason, among respondents who answered "No, probably not" or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |


