---
title: Contingency Tables
parent: COVID Symptom Survey
nav_order: 4
---

# Contingency Tables
{: .no_toc}

This documentation describes the fine-resolution contingency tables produced by
grouping [COVID Symptom Survey](./index.md) individual responses by various
demographic features.

Please also take a look at the [individual response data](./survey-files.md),
and the geographic aggregate data available [through the COVIDcast
API](../api/covidcast-signals/fb-survey.md) to find the data product that best
suits your needs.

Important updates for data users, including corrections to data or updates on
data processing delays, are posted as `OUTAGES.txt` in the directory
where the data is hosted.

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

### Weekly Files

Once a week, we write CSV files with names following this pattern:

  {date}_{region}_{vars}.csv

Dates in of the form `YYYYmmdd`. `date` refers to the first day of the epiweek survey responses were aggregated over, in the Pacific time zone (UTC - 7). Unless noted otherwise, this is always a complete week. `region` is the geographic level responses were aggregated over. At the moment, only nation-wide and state groupings are available.

### Monthly Files

Once a month, we write CSV files that aggregate responses over the last complete month. Format and naming schemes are identical to the weekly case.
