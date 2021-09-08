---
title: Contingency Tables
parent: COVID-19 Trends and Impact Survey
nav_order: 4
---

# Contingency Tables
{: .no_toc}

This documentation describes the fine-resolution contingency tables produced by
grouping [COVID-19 Trends and Impact Survey (CTIS)](./index.md) individual responses by various
self-reported demographic features.

* [Weekly files](https://www.cmu.edu/delphi-web/surveys/weekly-rollup/)
* [Monthly files](https://www.cmu.edu/delphi-web/surveys/monthly-rollup/)

These contingency tables provide granular breakdowns of COVID-related topics such as
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

## Available Data

We currently provide data files at several levels of geographic and temporal
aggregation. The reason for this is that each file is filtered to only include
estimates for a particular group if that group includes 100 or more responses.
Providing several levels of granularity allows us to provide coverage for a
variety of use cases. For example, users who need the most up-to-date data or
are interested in time series analysis should use the weekly files, while
those who want to study groups with smaller sample sizes should use the
monthly files. Because monthly aggregates include more responses, they have
lower missingness when grouping by several features at a time.

* [Weekly files](https://www.cmu.edu/delphi-web/surveys/weekly-rollup/)
* [Monthly files](https://www.cmu.edu/delphi-web/surveys/monthly-rollup/)

Files contain all time periods for a given period type-aggregation
type combination.

Individual CSVs containing a single [week](https://www.cmu.edu/delphi-web/surveys/weekly/) or [month](https://www.cmu.edu/delphi-web/surveys/monthly/) for a given aggregation type are also available.

### Dates

The included files provide estimates for various metrics of interest over a
period of either a full epiweek (or [MMWR
week](https://wwwn.cdc.gov/nndss/document/MMWR_week_overview.pdf), a
standardized numbering of weeks throughout the year) or a full calendar month.

Note: If a survey item was introduced in the middle of an aggregation period,
derived indicators will be included in aggregations for that period but will
only use a partial week or month of data.

CSVs for the month of January 2021 only use data from January 6-31 due to a
[definitional change in a major vaccine item on January 6](./coding.md#new-items-2).

### Regions

At the moment, only nation-wide and state groupings are available.

Facebook only invites users to take the survey if they appear, based on
attributes in their Facebook profiles, to reside in the 50 states or
Washington, DC. Puerto Rico is sampled separately as part of the
[international version of the survey](https://covidmap.umd.edu/). If Facebook
believes a user qualifies for the survey, but the user then replies that they
live in Puerto Rico or another US territory, we do not include their response
in the aggregations.

### Privacy

The aggregates are filtered to only include estimates for a particular group
if that group includes 100 or more responses. Especially in the weekly
aggregates, many of the state-level groups have been filtered out due to low
sample size. In such cases, files that group by a single demographic of
interest will likely provide more coverage.

## File Format

### Naming

"Rollup" files containing all time periods for a given period type-aggregation
type combination have names of the form:

    {period_type}_{geo_type}_{aggregation_type}.csv.gz

CSVs for individual time periods have names of the form:

    {period_start}_{period_end}_{period_type}_{geo_type}_{aggregation_type}.csv

Dates are in `yyyyMMdd` format. `period_start` refers to the first day of
the time period survey responses were aggregated over, in the Pacific time
zone (UTC - 7). Unless noted otherwise, the time period is always a complete
month (`period_type` = `monthly`) or epiweek (`period_type` = `weekly`).
`geo_type` is the geographic level responses were aggregated over. `aggregation_type`
is a concatenated list of other grouping variables used, ordered
alphabetically. Values for variables used in file naming align with those
within files as specified in the column section below.

### Columns

Within a CSV, the first few columns store metadata of the aggregation:

| Column | Description |
| --- | --- |
| `survey_geo` | Survey geography ("US") |
| `period_start` | Date of first day of time period used in aggregation |
| `period_end` | Date of last day of time period used in aggregation |
| `period_val` | Month or week number |
| `geo_type` | Geography type ("state", "nation") |
| `aggregation_type` | Concatenated list of grouping variables, ordered alphabetically |
| `country` | Country name ("United States") |
| `ISO_3` | Three-letter ISO country code ("USA") |
| `GID_0` | GADM level 0 ID |
| `state` | State name; "Overall" if aggregation not grouped at the state level |
| `GID_1` | GADM level 1 ID |
| `state_fips` | State FIPS code; `NA` if aggregation not grouped at the state level |
| `county` | County name; "Overall" if aggregation not grouped at the county level |
| `county_fips` | County FIPS code; `NA` if aggregation not grouped at the county level |
| `issue_date` | Date on which estimates were generated |

These are followed by the grouping variables used in the aggregation, ordered
alphabetically, and the indicators. Each indicator reports four columns
(unrounded):

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

### Missing Values

Grouping variables (including region) will be missing (`NA`) to represent
respondents who provided one or more responses to survey items used for
indicators (e.g., vaccine uptake) but who  did not provide a response to the
survey item used for the particular grouping variable. For example, if
grouping by gender, we would report the groups: male, female, other, and `NA`,
respondents who did not provide a response to the gender question.

For a given respondent group (25-34 year old healthcare workers in Nebraska,
e.g.) sample size can vary by indicator because of the survey display logic.
For example, all respondents are asked if they have received a COVID-19
vaccination (item V1), but only those who say they *have* are asked how many
doses they have received (item V2). This means that the sample size for V2 is
smaller than that for V1. Because indicators are [censored](#privacy)
individually, it is possible that V1-derived indicators will be reported for a
given group while V2-derived indicators are not. In this case, the V2-derived
indicator columns will be marked as missing (`NA`) for that group.

## Indicators

The files contain [weighted estimates](../api/covidcast-signals/fb-survey.md#survey-weighting)
of the percent of respondents who fulfill one or several criteria. Estimates are
broken out by state, age, gender, race, ethnicity, occupation, and health
conditions.

Indicators beginning "hesitant_" (not listed) are variants of other described
indicators calculated among respondents who say they would "probably not" or
"definitely not" choose to get vaccinated, if offered today (item V3/V3a).
**Note:** Until Wave 11 (May 19, 2021), this item was asked of everyone who
indicated that they had not received a COVID-19 vaccine; after that date, this
item was only asked of people who indicated that they had not received a
COVID-19 vaccine and did not have an appointment to do so.

Indicators beginning "defno_" (not listed) are variants of other described
indicators calculated among respondents who say they would "definitely not"
choose to get vaccinated, if offered today.

We plan to expand this list of indicators based on research needs; if you have
a public health or research need for a particular variable not listed here,
please contact us at <delphi-survey-info@lists.andrew.cmu.edu>.


### Symptoms

#### ILI and CLI

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_cli` | Estimated percentage of people with COVID-like illness, using the same [definition as in the API](../api/covidcast-signals/fb-survey.md#estimating-percent-ili-and-cli). <br/> **Earliest date available:** 2021-01-01 | A1 and A2 |
| `pct_ili` | Estimated percentage of people with influenza-like illness, using the same [definition as in the API](../api/covidcast-signals/fb-survey.md#estimating-percent-ili-and-cli). <br/> **Earliest date available:** 2021-01-01 | A1 and A2 |
| `pct_hh_cmnty_cli` | Estimated percentage of people reporting illness in their local community, including their household, using the same [definition as in the API](../api/covidcast-signals/fb-survey.m#estimating-community-cli). <br/> **Earliest date available:** 2021-01-01 | A1, A2, and A4 |

#### Individual Symptoms

These indicators are accompanied by variants with the suffix `_unusual` reporting the estimated percentage of respondents experiencing a given symptom as new or unusual, out of all respondents reporting that symptom in the last 24 hours.

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_anosmia` | Estimated percentage of respondents experiencing loss of smell or taste in the last 24 hours. <br/> **Earliest date available:** 2021-01-06 | B2 |
| `pct_symp_fever` | Estimated percentage of people experiencing a fever in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_cough` | Estimated percentage of people experiencing a cough in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_shortness_breath` | Estimated percentage of people experiencing shortness of breath in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_diff_breathing` | Estimated percentage of people experiencing difficulty breathing in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_fatigue` | Estimated percentage of people experiencing fatigue in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_stuffy_nose` | Estimated percentage of people experiencing a stuffy or runny nose in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_aches` | Estimated percentage of people experiencing muscle or joint aches in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_sore_throat` | Estimated percentage of people experiencing a sore throat in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_chest_pain` | Estimated percentage of people experiencing chest pain or pressure in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_nausea` | Estimated percentage of people experiencing nausea or vomiting in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_diarrhea` | Estimated percentage of people experiencing diarrhea in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_other` | Estimated percentage of people experiencing other symptoms in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_none` | Estimated percentage of people experiencing none of the listed symptoms in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_chills` | Estimated percentage of people experiencing chills in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_headache` | Estimated percentage of people experiencing a headache in the last 24 hours. <br/> **Earliest date available:** 2021-08-16 | B2 |
| `pct_symp_nasal_congestion` | *Discontinued as of Wave 11, May 19, 2021*  Estimated percentage of people experiencing nasal congestion in the last 24 hours. | B2 |
| `pct_symp_eye_pain` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people experiencing eye pain in the last 24 hours. | B2 |
| `pct_symp_sleep_changes` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people experiencing changes in sleep in the last 24 hours. | B2 |
| `pct_symp_runny_nose` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people experiencing a runny nose in the last 24 hours. | B2 |


### Behaviors

#### Mask Use

| Indicator | Description | Survey Item |
| --- | --- | --- | --- |
| `pct_others_masked_public` | Estimated percentage of respondents who say that most or all *other* people wear masks, when they are in public. <br/> **Earliest date available:** 2021-08-16 | H2 |
| `pct_wearing_mask_7d` | Estimated percentage of people who wore a mask for most or all of the time while in public in the past 7 days; those not in public in the past 7 days are not counted. <br/> **Earliest date available:** 2021-02-08 | C14a |
| `pct_mask_public_transit_1d` | Estimated percentage of respondents who reported using a mask while using public transit, of all respondents who used public transit in the past 24 hours <br/> **Earliest date available:** 2020-08-16 | C13 or C13b, and C13a or C13c |
| `pct_mask_work_outside_home_indoors_1d` | Estimated percentage of respondents who reported using a mask while working or going to school indoors and outside their home, of all resondents who worked or went to school outside their home in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b and C13c |
| `pct_mask_shop_indoors_1d` | Estimated percentage of respondents who reported using a mask while going to an "indoor market, grocery store, or pharmacy", of all respondents who did this activity in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b and C13c |
| `pct_mask_restaurant_indoors_1d` | Estimated percentage of respondents who reported using a mask while going to an indoor "bar, restaurant, or cafe", of all respondents who did this activity in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b and C13c |
| `pct_mask_spent_time_indoors_1d` | Estimated percentage of respondents who reported using a mask while spending time "indoors with someone who isn't currently staying with you", of all respondents who did this activity in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b and C13c |
| `pct_mask_large_event_indoors_1d` | Estimated percentage of respondents who reported using a mask while attending "an indoor event with more than 10 people", of all respondents who did this activity in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b and C13a |
| `pct_mask_shop_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who went to a "market, grocery store, or pharmacy", of all respondents who did this activity in the past 24 hours. | C13 and C13a |
| `pct_mask_restaurant_1d` | *Discontinued as of Wave reported using a mask while 10, Mar 2, 2021* Estimated percentage of respondents who went to a "bar, restaurant, or cafe", of all respondents who did this activity in the past 24 hours. | C13 and C13a |
| `pct_mask_large_event_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who "attended an event with more than 10 people", of all respondents who did this activity in the past 24 hours. | C13 and C13a |
| `pct_mask_work_outside_home_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who worked or went to school outside their home, of all respondents who did this activity in the past 24 hours. | C13 and C13a |
| `pct_mask_spent_time_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who "spent time with someone who isn't currently staying with you", of all respondents who did this activity in the past 24 hours. | C13 and C13a |
| `pct_wearing_mask_5d` | *Discontinued as of Wave 8, Feb 8, 2021* Estimated percentage of people who wore a mask for most or all of the time while in public in the past 5 days; those not in public in the past 5 days are not counted. <br/> **Earliest date available:** 2021-01-01 | C14 |
| `pct_direct_contact` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people who in the past 24 hours had a non-physical interaction (like conversing) for more than 5 minutes at a distance of 6 feet or less or a physical interaction (like hand-shaking, hugging, or kissing) with anyone outside their household. <br/> **Earliest date available:** 2021-01-01 | C10 |

#### Social Distancing and Travel

| Indicator | Description | Survey Item |
| --- | --- | --- | --- |
| `pct_others_distanced_public` | Estimated percentage of respondents who reported that all or most people they enountered in public in the past 7 days maintained a distance of at least 6 feet. Respondents who said that they have not been in public for the past 7 days are excluded. <br/> **Earliest date available:** 2021-08-16 | H1 |
| `pct_public_transit_1d` | Estimated percentage of respondents who "used public transit" in the past 24 hours <br/> **Earliest date available:** 2020-08-16 | C13 or C13b |
| `pct_work_outside_home_indoors_1d` | Estimated percentage of respondents who worked or went to school indoors and outside their home in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b |
| `pct_shop_indoors_1d` | Estimated percentage of respondents who went to an "indoor market, grocery store, or pharmacy" in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b |
| `pct_restaurant_indoors_1d` | Estimated percentage of respondents who went to an indoor "bar, restaurant, or cafe" in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b |
| `pct_spent_time_indoors_1d` | Estimated percentage of respondents who "spent time indoors with someone who isn't currently staying with you" in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b |
| `pct_large_event_indoors_1d` | Estimated percentage of respondents who "attended an indoor event with more than 10 people" in the past 24 hours <br/> **Earliest date available:** 2021-08-06 | C13b |
| `pct_travel_outside_state_7d` | Estimated percentage of respondents who report traveling outside their state in the past 7 days. This item was asked of respondents starting in Wave 10. <br/> **Earliest date available:** 2021-08-06 | C13b |
| `pct_travel_outside_state_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who report traveling outside their state in the past 5 days. | C6 |
| `pct_shop_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who went to a "market, grocery store, or pharmacy" in the past 24 hours. | C13 |
| `pct_restaurant_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who went to a "bar, restaurant, or cafe" in the past 24 hours. | C13 |
| `pct_spent_time_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who "spent time with someone who isn't currently staying with you" in the past 24 hours. | C13 |
| `pct_large_event_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who "attended an event with more than 10 people" in the past 24 hours. | C13 |
| `pct_work_outside_home_1d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who worked or went to school outside their home in the past 24 hours. | C13 |


### Testing

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_tested_14d` | Estimated percentage of people who were tested for COVID-19 in the past 14 days, regardless of their test result <br/> **Earliest date available:** 2021-08-16 | B8, B10 |
| `pct_tested_positive_14d` | Estimated test positivity rate (percent) among people tested for COVID-19 in the past 14 days <br/> **Earliest date available:** 2021-08-16 | B10a or B10c |
| `pct_had_covid_ever` | Estimated percentage of people who report having ever had COVID-19. <br/> **Earliest date available:** 2021-08-16 | B13 |
| `pct_wanted_test_14d` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people who *wanted* to be tested for COVID-19 in the past 14 days, out of people who were *not* tested in that time. | B12 |
| `pct_ever_tested` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people who have ever been tested for COVID-19. | B8 |

#### Testing Reasons

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_test_reason_sick` | Estimated percentage of people who were tested because they felt sick, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_contact` | Estimated percentage of people who were tested because they were in contact with someone who was sick, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_medical` | Estimated percentage of people who were tested because they were receiving medical care, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_required` | Estimated percentage of people who were tested because their work or school required it, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_visit` | Estimated percentage of people who were tested so that they could visit family and friends, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_travel` | Estimated percentage of people who were tested because it was required for travel, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_none` | Estimated percentage of people who reported that none of the listed reasons described why they were tested, out of all respondents tested in the last 14 days. <br/> **Earliest date available:** 2021-08-16 | B10b |
| `pct_test_reason_large_event` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people who were tested because they attended a large outdoor event or gathering, out of all respondents tested in the last 14 days. | B10b |
| `pct_test_reason_crowd` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of people who were tested because they were in a crowded indoor environment, out of all respondents tested in the last 14 days. | B10b |


### Vaccines

#### Vaccine Uptake and Acceptance

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccinated` | Estimated percentage of respondents who have already received a COVID vaccine. <br/> **Earliest date available:** 2021-01-01 | V1 |
| `pct_received_2_vaccine_doses` | Estimated percentage of respondents who have received two doses of a COVID-19 vaccine, among respondents who have received either one or two doses of a COVID-19 vaccine. <br/> **Earliest date available:** 2021-01-01 | V2 |
| `pct_vaccinated_appointment_or_accept` | Estimated percentage of respondents who *either* have already received a COVID vaccine *or* have an appointment to get a COVID vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today. <br/> **Earliest date available:** 2021-05-19 | V1, V11a, V3a |
| `pct_appointment_or_accept_vaccine` | Estimated percentage of respondents who *either* have an appointment to get a COVID-19 vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-05-19 | V11a, V3a |
| `pct_accept_vaccine_no_appointment` | Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated and do not have an appointment to do so. <br/> **Earliest date available:** 2021-05-19 | V3a |
| `pct_covid_vaccinated_friends` | Estimated percentage of respondents who report that most of their friends and family have received a COVID-19 vaccine. <br/> **Earliest date available:** 2021-08-16 | H3 |
| `pct_vaccinate_children` | Estimated percentage of respondents with children who report that they will definitely or probably get the vaccine for their children. <br/> **Earliest date available:** 2021-08-16 | E4 |
| `pct_hesitant_vaccine` | Estimated percentage of respondents who would definitely not or probably not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. **Note:** Until Wave 11 (May 19, 2021), this item was asked of everyone who indicated that they had not received a COVID-19 vaccine; after that date, this item was only asked of people who indicated that they had not received a COVID-19 vaccine and did not have an appointment to do so.  <br/> **Earliest date available:** 2021-01-01 | V3 or V3a |
| `pct_accept_vaccine_no_appointment_defyes` | Estimated percentage of respondents who would definitely choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated and do not have an appointment to do so. <br/> **Earliest date available:** 2021-05-19 | V3a |
| `pct_accept_vaccine_no_appointment_probyes` | Estimated percentage of respondents who would probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated and do not have an appointment to do so. <br/> **Earliest date available:** 2021-05-19 | V3a |
| `pct_accept_vaccine_no_appointment_probno` | Estimated percentage of respondents who would probably not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated and do not have an appointment to do so. <br/> **Earliest date available:** 2021-05-19 | V3a |
| `pct_accept_vaccine_no_appointment_defno` | Estimated percentage of respondents who would definitely not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated and do not have an appointment to do so. <br/> **Earliest date available:** 2021-05-19 | V3a |
| `pct_vaccinated_or_accept` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who *either* have already received a COVID-19 vaccine *or* would definitely or probably choose to get vaccinated, if a vaccine were offered to them today. <br/> **Earliest date available:** 2021-01-01 | V1, V3 |
| `pct_accept_vaccine` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would definitely or probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_defyes` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would definitely choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_probyes` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would probably choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_probno` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would probably not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_accept_vaccine_defno` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would definitely not choose to get vaccinated, if a vaccine were offered to them today, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V3 |
| `pct_informed_access` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who are very or moderately informed about how to get a COVID-19 vaccination. <br/> **Earliest date available:** 2021-02-08 | V13 |
| `pct_appointment_not_vaccinated` | Estimated percentage of respondents who have an appointment to get a COVID-19 vaccine, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-05-19 | V11a |
| `pct_appointment_have` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who have an appointment to get a COVID-19 vaccine, among respondents who answered "Yes, definitely" or "Yes, probably" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-03-02 | V11 |
| `pct_vaccine_tried` | Estimated percentage of respondents who have tried to get a COVID-19 vaccine, among respondents who answered "Yes, definitely" or "Yes, probably" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-05-19 | V12a |
| `pct_appointment_tried` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who have tried to make an appointment to get a COVID-19 vaccine, among respondents who answered "Yes, definitely" or "Yes, probably" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-03-02 | V12 |

#### Vaccine Timing

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccine_timing_weeks` | Estimated percentage of respondents who say they will try to get the vaccine within a week or two, out of respondents who have not yet been vaccinated, do not have an appointment to do so, *and* are unsure if they would choose to get vaccinated (answering that they would either "yes, probably" or "no, probably not" get vaccinated if offered today). <br/> **Earliest date available:** 2021-08-16 | V16 |
| `pct_vaccine_timing_onemonth` | Estimated percentage of respondents who say they will try to get the vaccine within a month, out of respondents who have not yet been vaccinated, do not have an appointment to do so, *and* are unsure if they would choose to get vaccinated (answering that they would either "yes, probably" or "no, probably not" get vaccinated if offered today). <br/> **Earliest date available:** 2021-08-16 | V16 |
| `pct_vaccine_timing_threemonths` | Estimated percentage of respondents who say they will try to get the vaccine within three months, out of respondents who have not yet been vaccinated, do not have an appointment to do so, *and* are unsure if they would choose to get vaccinated (answering that they would either "yes, probably" or "no, probably not" get vaccinated if offered today). <br/> **Earliest date available:** 2021-08-16 | V16 |
| `pct_vaccine_timing_sixmonths` | Estimated percentage of respondents who say they will try to get the vaccine within six months, out of respondents who have not yet been vaccinated, do not have an appointment to do so, *and* are unsure if they would choose to get vaccinated (answering that they would either "yes, probably" or "no, probably not" get vaccinated if offered today). <br/> **Earliest date available:** 2021-08-16 | V16 |
| `pct_vaccine_timing_morethansix` | Estimated percentage of respondents who say they will try to get the vaccine in more than six months, out of respondents who have not yet been vaccinated, do not have an appointment to do so, *and* are unsure if they would choose to get vaccinated (answering that they would either "yes, probably" or "no, probably not" get vaccinated if offered today). <br/> **Earliest date available:** 2021-08-16 | V16 |
| `pct_vaccine_timing_dontknow` | Estimated percentage of respondents who don't know when they will try to get the vaccine, out of respondents who have not yet been vaccinated, do not have an appointment to do so, *and* are unsure if they would choose to get vaccinated (answering that they would either "yes, probably" or "no, probably not" get vaccinated if offered today). <br/> **Earliest date available:** 2021-08-16 | V16 |

#### Outreach and Image

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccine_likely_friends` (formerly `pct_trust_fam`)| *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by friends and family, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_who` (formerly `pct_trust_who`) | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by the World Health Organization, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_govt_health` (formerly `pct_trust_govt`) | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by government health officials, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_politicians` (formerly `pct_trust_politicians`) | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by politicians, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |
| `pct_vaccine_likely_doctors` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by doctors and other health professionals they go to for medical care, among respondents who have not yet been vaccinated. This item was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-08 | V4 |
| `pct_vaccine_likely_local_health` (formerly `pct_trust_healthcare`) | *Discontinued as of Wave 8, Feb 8, 2021* Estimated percentage of respondents who would be more likely to get a COVID-19 vaccine if it were recommended to them by local health workers, among respondents who have not yet been vaccinated. <br/> **Earliest date available:** 2021-01-01 | V4 |

#### Reasons for Vaccine Hesitancy

The set of "barrier" items correspond to the set of ["hesitancy_reasons" items in the API](../api/covidcast-signals/fb-survey.md#reasons-for-hesitancy).

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_worried_vaccine_sideeffects` (formerly `pct_concerned_sideeffects`) | Estimated percentage of respondents who are very or moderately concerned that they would "experience a side effect from a COVID-19 vaccination." **Note:** Until March 2, 2021, all respondents answered this question, including those who had already received one or more doses of a COVID-19 vaccine; beginning on that date, only respondents who said they have not received a COVID vaccine are asked this question. <br/> **Earliest date available:** 2021-01-01 | V9 |
| `pct_barrier_sideeffects` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about side effects, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_allergic` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about having an allergic reaction, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_ineffective` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't know if a COVID-19 vaccine will work, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_dontneed` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't believe they need a COVID-19 vaccine, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_dislike_vaccines` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they dislike vaccines, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_wait_safety` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they want to wait to see if the COVID-19 vaccines are safe, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_low_priority` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they think other people need it more than they do, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_cost` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they are worried about the cost, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. This series of items was shown to respondents starting in Wave 8. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_distrust_govt` | Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't trust the government, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_religious` | Estimated percentage of respondents who say they are hesitant to get vaccinated because it is against their religious beliefs, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_other` | Estimated percentage of respondents who say they are hesitant to get vaccinated for another reason, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_not_recommended` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because their doctor did not recommend it, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_distrust_vaccines` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they don't trust COVID-19 vaccines, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_health_condition` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they have a health condition that may impact the safety of a COVID-19 vaccine, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |
| `pct_barrier_pregnant` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who say they are hesitant to get vaccinated because they are currently, or are planning to be, pregnant or breastfeeding, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered. <br/> **Earliest date available:** 2021-02-08 | V5abc |

#### Reasons for Believing Vaccine is Unnecessary

Respondents who indicate that "I don't believe I need a COVID-19 vaccine" (in
items V5a, V5b, V5c, or, prior to Wave 11, V5d) are asked a follow-up item
asking why they don't believe they need the vaccine. These signals summarize
the reasons selected. Respondents who do not select any reason (including
"Other") are treated as missing.

This item was shown to respondents starting in Wave 8.

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_dontneed_reason_had_covid` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they already had the illness, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_dont_spend_time` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't spend time with high-risk people, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_not_high_risk` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they are not in a high-risk group, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_precautions` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they will use other precautions, such as a mask, instead, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_not_serious` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't believe COVID-19 is a serious illness, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_not_beneficial` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine because they don't think vaccines are beneficial, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |
| `pct_dontneed_reason_other` | Estimated percentage of respondents who say they don't need to get a COVID-19 vaccine for another reason, among respondents who answered "Yes, probably", "No, probably not", or "No, definitely not" when asked if they would get vaccinated if offered and provided at least one reason for why they believe a COVID-19 vaccine is unnecessary. <br/> **Earliest date available:** 2021-02-08 | V6 and V5bc |

#### Barriers to Accessing Vaccination

Vaccine barrier items are reported in three ways: among those who have already been vaccinated or have tried to get vaccinated, among only those who have already been vaccinated (accompanied by the suffix `_has`), and among only those who have tried to get vaccinated (accompanied by the suffix `_tried`). For example, the combined metric `pct_vaccine_barrier_eligible` has `pct_vaccine_barrier_eligible_has` and `pct_vaccine_barrier_eligible_tried` variants that report the component groups separately.

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_vaccine_barrier_eligible` | Estimated percentage of respondents who report eligibility requirements as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_no_appointments` | Estimated percentage of respondents who report lack of vaccine or vaccine appointments as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_appointment_time` | Estimated percentage of respondents who report available appointment times as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_technical_difficulties` | Estimated percentage of respondents who report technical difficulties with the website or phone line as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_document` | Estimated percentage of respondents who report inability to provide required documents as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_technology_access` | Estimated percentage of respondents who report limited access to internet or phone as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_travel` | Estimated percentage of respondents who report difficulty traveling to vaccination sites as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_language` | Estimated percentage of respondents who report information not being available in their native language as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_childcare` | Estimated percentage of respondents who report lack of childcare as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_time` | Estimated percentage of respondents who report difficulty getting time away from work or school as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_type` | Estimated percentage of respondents who report available vaccine type as a barrier to getting the vaccine, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |
| `pct_vaccine_barrier_none` | Estimated percentage of respondents who report experiencing none of the listed barriers to gettint the vaccing, among those who have already been vaccinated or have tried to get vaccinated. <br/> **Earliest date available:** 2021-08-16 | V15a and V15b |

### Mental Health Indicators

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_finance` | Estimated percentage of respondents who report being very or somewhat worried about their "household's finances for the next month" <br/> **Earliest date available:** 2021-08-16 | C15 |
| `pct_anxious_7d` | Estimated percentage of respondents who reported feeling "nervous, anxious, or on edge" for most or all of the past 7 days. This item was shown to respondents starting in Wave 10. <br/> **Earliest date available:** 2021-08-16 | C8a or C18a |
| `pct_depressed_7d` | Estimated percentage of respondents who reported feeling depressed for most or all of the past 7 days. This item was shown to respondents starting in Wave 10. <br/> **Earliest date available:** 2021-08-16 | C8a or C18b |
| `pct_worried_catch_covid` | Estimated percentage of respondents worrying either a great deal or a moderate amount about catching COVID-19. <br/> **Earliest date available:** 2021-08-16 | G1 |
| `pct_felt_isolated_7d` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who reported feeling "isolated from others" for most or all of the past 7 days. This item was shown to respondents starting in Wave 10. | C8a |
| `pct_anxious_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who reported feeling "nervous, anxious, or on edge" for most or all of the past 5 days | C8 |
| `pct_depressed_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who reported feeling depressed for most or all of the past 5 days | C8 |
| `pct_felt_isolated_5d` | *Discontinued as of Wave 10, Mar 2, 2021* Estimated percentage of respondents who reported feeling "isolated from others" for most or all of the past 5 days | C8 |
| `pct_worried_become_ill` | *Discontinued as of Wave 11, May 19, 2021* Estimated percentage of respondents who reported feeling very or somewhat worried that "you or someone in your immediate family might become seriously ill from COVID-19" | C9 |


### Beliefs

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_belief_masking_effective` | Estimated percentage of respondents who believe that wearing a face mask is either very or moderately effective for preventing the spread of COVID-19. <br/> **Earliest date available:** 2021-08-16 | G3 |
| `pct_belief_distancing_effective` | Estimated percentage of respondents who believe that social distancing is either very or moderately effective for preventing the spread of COVID-19. <br/> **Earliest date available:** 2021-08-16 | G2 |
| `pct_belief_vaccinated_mask_unnecessary` | Estimated percentage of people who believe that the statement "Getting the COVID-19 vaccine means that you can stop wearing a mask around people outside your household" is definitely or probably true. <br/> **Earliest date available:** 2021-08-16 | I1 |
| `pct_belief_children_immune` | Estimated pPercentage of people who believe that the statement "Children cannot get COVID-19" is definitely or probably true. <br/> **Earliest date available:** 2021-08-16 | I2 |
| `pct_belief_created_small_group` | Estimated percentage of people who believe that the statement "COVID-19 was deliberately created by a small group of people who secretly manipulate world events" is definitely or probably true. <br/> **Earliest date available:** 2021-08-16 | I3 |
| `pct_belief_govt_exploitation` | Estimated percentage of people who indicate that the statement "The COVID-19 pandemic is being exploited by the government to control people" is definitely or probably true. <br/> **Earliest date available:** 2021-08-16 | I4 |


### Medical Care Experiences Indicators

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_delayed_care_cost` | Estimated percentage of respondents who have ever delayed or not sought medical care in the past year because of cost. <br/> **Earliest date available:** 2021-08-16 | K1 |
| `pct_race_treated_fairly_healthcare` | Estimated percentage of respondents who somewhat or strongly agree that people of their race are treated fairly in a healthcare setting. <br/> **Earliest date available:** 2021-08-16 | K2 |


### News and Information Indicators

#### Sources of News

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_received_news_local_health` | Estimated percentage of respondents who received news about COVID-19 from local health workers, clinics, and community organizations in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_experts` | Estimated percentage of respondents who received news about COVID-19 from scientists and other health experts in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_cdc` | Estimated percentage of respondents who received news about COVID-19 from the CDC in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_govt_health` | Estimated percentage of respondents who received news about COVID-19 from government health authorities or officials in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_politicians` | Estimated percentage of respondents who received news about COVID-19 from politicians in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_journalists` | Estimated percentage of respondents who received news about COVID-19 from journalists in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_friends` | Estimated percentage of respondents who received news about COVID-19 from friends and family in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_religious` | Estimated percentage of respondents who received news about COVID-19 from religious leaders in the past 7 days. <br/> **Earliest date available:** 2021-08-16 | I5 |
| `pct_received_news_none` | Estimated percentage of respondents who in the past 7 days received news about COVID-19 from none of the listed sources. <br/> **Earliest date available:** 2021-08-16 | I5 |

#### Trusted Sources of Information

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_trust_covid_info_doctors` | Estimated percentage of respondents who trust doctors and other health professionals they go to for medical care to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_experts` | Estimated percentage of respondents who trust scientists and other health experts to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_cdc` | Estimated percentage of respondents who trust the Centers for Disease Control (CDC) to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_govt_health` | Estimated percentage of respondents who trust government health officials to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_politicians` | Estimated percentage of respondents who trust politicians to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_journalists` | Estimated percentage of respondents who trust journalists to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_friends` | Estimated percentage of respondents who trust friends and family to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |
| `pct_trust_covid_info_religious` | Estimated percentage of respondents who trust religious leaders to provide accurate news and information about COVID-19. <br/> **Earliest date available:** 2021-08-16 | I6 |

#### Desired Information

| Indicator | Description | Survey Item |
| --- | --- | --- |
| `pct_want_info_covid_treatment` | Estimated percentage of people who want more information about the treatment of COVID-19. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_vaccine_access` | Estimated percentage of people who want more information about how to get a COVID-19 vaccine. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_vaccine_types` | Estimated percentage of people who want more information about different types of COVID-19 vaccines. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_covid_variants` | Estimated percentage of people who want more information about COVID-19 variants and mutations. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_children_education` | Estimated percentage of people who want more information about how to support their children's education. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_mental_health` | Estimated percentage of people who want more information about how to maintain their mental health. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_relationships` | Estimated percentage of people who want more information about how to maintain their social relationships despite physical distancing. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_employment` | Estimated percentage of people who want more information about employment and other economic and financial issues. <br/> **Earliest date available:** 2021-08-16 | I7 |
| `pct_want_info_none` | Estimated percentage of people who want more information about none of the listed topics. <br/> **Earliest date available:** 2021-08-16 | I7 |
