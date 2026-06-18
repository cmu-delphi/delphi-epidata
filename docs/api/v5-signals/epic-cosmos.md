---
title: PopHive Claims
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 3
---

# PopHive Claims Aggregations (Epic Cosmos)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `pophive` |
| **Data Source** | [Epic Cosmos](https://cosmos.epic.com/) via [PopHIVE](https://github.com/PopHIVE/Ingest) |
| **Geographic Levels** | HHS Regions (`hhs`), nation, state |
| **Temporal Granularity** | Weekly (epiweeks; dates are Saturdays, the last day of the week) |
| **Reporting Cadence** | Irregular (biweekly to monthly updates; see [Overview](#overview)) |
| **Date of last data revision:** | Never (see [data revision docs](#changelog)) |
| **Temporal Scope Start** | <span class="source-metadata-field" data-source="pophive" data-field="reference_time_range.first">2018-01-07 (loading...)</span> |
| **Latest Data Available** | <span class="source-metadata-field" data-source="pophive" data-field="reference_time_range.latest">loading...</span> |
| **First Report Time** | <span class="source-metadata-field" data-source="pophive" data-field="report_time_range.first">loading...</span> |
| **Latest Report Time** | <span class="source-metadata-field" data-source="pophive" data-field="report_time_range.latest">loading...</span> |
| **License** | [PopHIVE Attribution](https://github.com/PopHIVE/Ingest) / [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en)|

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **2025-09-23**. Data ingestion starts (earliest report date in the dataset).

</details>

## Overview
{: .no_toc}

[Epic Cosmos](https://cosmos.epic.com/) is a collaborative research platform containing de-identified patient data from over 300 million patients across more than 1,600 hospitals and health systems using Epic electronic health record systems. Data is accessed via SlicerDicer, a self-service analytics tool. The dataset includes emergency department visits, diagnoses, immunizations, laboratory results, and other clinical data.

Note that while data updates are expected to be biweekly, the actual reporting cadence is irregular. Historically, the interval between releases has ranged from weekly to monthly, with occasional lags exceeding four weeks.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Available Signals

| Signal | Description |
| :--- | :--- |
| `all_n_encounters_ed` | Total number of all patient emergency department encounters over the reference week. |
| `covid_n_ed` | Total number of patient emergency department encounters with a COVID-19 diagnosis over the reference week. |
| `covid_pct_ed` | Percentage of patient emergency department encounters with a COVID-19 diagnosis over the reference week. |
| `flu_n_ed` | Total number of patient emergency department encounters with an influenza diagnosis over the reference week. |
| `flu_pct_ed` | Percentage of patient emergency department encounters with an influenza diagnosis over the reference week. |
| `rsv_n_ed` | Total number of patient emergency department encounters with an RSV diagnosis over the reference week. |
| `rsv_pct_ed` | Percentage of patient emergency department encounters with an RSV diagnosis over the reference week. |

---

## Estimation

Epic Cosmos data is aggregated from electronic health records of participating healthcare systems. Percentages are calculated as the ratio of encounters with a specific diagnosis or result to the total number of relevant encounters.

---

## Temporal Representation

Dates in this dataset represent epiweeks, where the reported dates (`time_value`) correspond to Saturdays (the last day of each week).

---

## Available Additional Columns

Each row in this dataset includes two extra columns: `age_group` and `fill_method`. You can use these to filter data by population subgroup and decide how to treat missing values.

### Population Subgroups

Data is stratified into age bands so you can focus on a specific population. The available groups are:

| Value | Description |
| :--- | :--- |
| `all` | All ages combined |
| `0-1` | Infants under 1 year |
| `1-5` | Children aged 1–4 |
| `5-18` | Children and adolescents aged 5–17 |
| `18-50` | Adults aged 18–49 |
| `50-65` | Adults aged 50–64 |
| `65+` | Adults 65 and older |

To filter by age group, pass the column as an extra key in your query (e.g. `extra_keys=age_group:18-50`).

### Imputation Methods

The `fill_method` column indicates how missing values were filled:

| Value | Behavior |
| :--- | :--- |
| `source` | Returns the raw reported value. |
| `ave` | Fills missing values using the average of neighboring values during aggregation. |
| `zero` | Treats missing values as zero during aggregation. |

If you do not specify a `fill_method`, the API returns all available rows across all methods.


---

## Missingness

Due to privacy protections, count values fewer than 10 are suppressed and imputed. This data is subject to variability based on the participation of health systems and the completeness of their electronic health records. 

---

## Limitations

Epic Cosmos represents data from hospitals and health systems using Epic EHR. This may not be representative of the entire U.S. population, especially in regions with lower Epic market adoption.

---

## Source and Licensing

This data source is provided by the [PopHIVE platform](https://github.com/PopHIVE/Ingest) and is based on de-identified data from [Epic Cosmos](https://cosmos.epic.com/).

The data can be re-used with appropriate attribution. A suggested citation relating to this data is:
> Results of research performed with Epic Cosmos were obtained from the PopHIVE platform (https://github.com/PopHIVE/Ingest).
