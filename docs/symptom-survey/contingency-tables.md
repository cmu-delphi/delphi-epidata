---
title: Contingency Tables
parent: COVID-19 Trends and Impact Survey
nav_order: 4
---

# Contingency Tables
{: .no_toc}

This documentation describes the fine-resolution contingency tables produced by
grouping [US COVID-19 Trends and Impact Survey (CTIS)](./index.md) individual responses by various
self-reported demographic features.

* [Weekly files](https://www.cmu.edu/delphi-web/surveys/weekly-rollup/)
* [Monthly files](https://www.cmu.edu/delphi-web/surveys/monthly-rollup/)

These contingency tables provide granular breakdowns of COVID-related topics
such as vaccine uptake and acceptance. Compatible tables are also available for
the [UMD Global CTIS](https://covidmap.umd.edu/) for more than 100 countries and
territories worldwide, through [UMD's
website](https://covidmap.umd.edu/umdcsvs/Contingency_Tables/).

These tables are more detailed than the [coarse aggregates reported in the COVIDcast Epidata API](../api/covidcast-signals/fb-survey.md), which are grouped
only by geographic region. [Individual response data](survey-files.md) for the
survey is available, but only to academic or nonprofit researchers who sign a
Data Use Agreement, whereas these contingency tables are available to the
general public.

Please see our survey [credits](index.md#credits) and [citation information](index.md#citing-the-survey)
for information on how to cite this data if you use it in a publication.

Our [Data and Sampling Errors](problems.md) documentation lists important
updates for data users, including corrections to data or updates on data
processing delays.

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

Unless noted otherwise, the time period is always a complete month
(`period_type` = `monthly`) or epiweek (`period_type` = `weekly`). `geo_type` is
the geographic level responses were aggregated over. `aggregation_type` is a
concatenated list of other grouping variables used, ordered alphabetically.
Values for variables used in file naming align with those within files as
specified in the column section below.

### Columns

Within a CSV, the first few columns store metadata of the aggregation:

| Column | Description |
| --- | --- |
| `survey_geo` | Survey geography ("US") |
| `period_start` | Date (yyyyMMdd) of first day of time period used in aggregation, in the Pacific time zone (UTC - 7) |
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

<div style="background-color:#f5f6fa; padding: 10px 30px;"><strong>Indicator
codebook:</strong> Our <a href="contingency-codebook.csv">contingency table
codebook (CSV)</a> lists all indicators available in the US contingency tables
for download, and specifies the survey questions on which they are based. See
the <a href="coding.html">survey instrument codebook</a> for the full text of
all questions.</div>

The files contain [weighted estimates](../api/covidcast-signals/fb-survey.md#survey-weighting-and-estimation)
of the percent of respondents who fulfill one or several criteria. Estimates are
broken out by state, age, gender, race, ethnicity, occupation, and health
conditions.

We plan to expand the list of indicators based on research needs; if you have a
public health or research need for a particular variable not included in our
current tables please contact us at <delphi-survey-info@lists.andrew.cmu.edu>.
