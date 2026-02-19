---
title: Epic Cosmos
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
nav_order: 1
---
# Epic Cosmos
{: .no_toc}

* **Source name:** `pophive`
* **Earliest issue available:** TBD
* **Number of data revisions:** 0
* **Date of last change:** Never
* **Available for:** nation, state, county (see [geography coding docs](../covidcast_geography.md))
* **Time type:** week, month (see [date format docs](../covidcast_times.md))
* **License:** [PopHIVE (Attribution)](https://github.com/PopHIVE/Ingest)

## Overview

[Epic Cosmos](https://cosmos.epic.com/) is a collaborative research platform containing de-identified patient data from over 300 million patients across more than 1,600 hospitals and health systems using Epic electronic health record systems. Data is accessed via SlicerDicer, a self-service analytics tool. The dataset includes emergency department visits, diagnoses, immunizations, laboratory results, and other clinical data.

Due to privacy protections, counts fewer than 10 are suppressed and imputed. Coverage extends across all U.S. states and territories. Note that county-level and city-level stratifications could differ markedly in total sample size due to high levels of missingness of county data in some states.

These signals are available for several age groups and use different methods to handle missing data. The full signal name is formed by taking the base signal name and appending an age group and a fill method suffix. 

For example, `epic_n_all_encounters_weekly_18_49_yo_fa` represents the weekly encounter count for the 18-49 age group using the "fill average" method.

**Age groups:** `less_1_yo`, `1_4_yo`, `5_17_yo`, `18_49_yo`, `50_64_yo`, `more_65_yo`, and `total`.

**Fill methods:**
* `_fa`: Fill average (imputed values based on averages)
* `_fz`: Fill zero (missing values treated as zero)

| Signal | Description |
| --- | --- |
| `epic_n_all_encounters_weekly` | Total number of all patient encounters over the entire week (Sunday-Saturday). |
| `epic_n_covid` | Total number of patient encounters with a COVID-19 diagnosis over the entire week. |
| `epic_n_flu` | Total number of patient encounters with an influenza diagnosis over the entire week. |
| `epic_n_rsv` | Total number of patient encounters with an RSV diagnosis over the entire week. |
| `epic_pct_covid` | Percentage of patient encounters with a COVID-19 diagnosis over the entire week. |
| `epic_pct_flu` | Percentage of patient encounters with an influenza diagnosis over the entire week. |
| `epic_pct_rsv` | Percentage of patient encounters with an RSV diagnosis over the entire week. |


## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Epic Cosmos data is aggregated from electronic health records of participating healthcare systems. The signals are derived from de-identified patient data, including visits, diagnoses, and laboratory results. Percentages are calculated as the ratio of encounters with a specific diagnosis or result to the total number of relevant encounters.

## Missingness

Due to privacy protections, counts fewer than 10 are suppressed and imputed. This data is subject to variability based on the participation of health systems and the completeness of their electronic health records. County-level and city-level stratifications could differ markedly in total sample size due to high levels of missingness of county data in some states.

## Limitations

Epic Cosmos represents data from hospitals and health systems using Epic EHR. This may not be representative of the entire population, especially in regions with low Epic adoption. Additionally, data is subject to suppression for small counts to protect patient privacy.

## Source and Licensing

This data source is provided by the [PopHIVE platform](https://github.com/PopHIVE/Ingest) and is based on de-identified data from [Epic Cosmos](https://cosmos.epic.com/).

**Citation and Attribution:** The data can be re-used with appropriate attribution. A suggested citation relating to this data is "Results of research performed with Epic Cosmos were obtained from the PopHIVE platform (https://github.com/PopHIVE/Ingest)."
