---
title: PopHive Claims
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
---

# PopHive Claims (Epic Cosmos)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `pophive` |
| **Data Source** | [Epic Cosmos](https://cosmos.epic.com/) via [PopHIVE](https://github.com/PopHIVE/Ingest) |
| **Geographic Levels** | `nation`, `state`, `hhs` |
| **Temporal Granularity** | Weekly, week ending Saturday |
| **Reporting Cadence** | Irregular (biweekly to monthly updates) |
| **Temporal Scope Start** | 2018-01-07 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | `age_group` |
| **License** | [PopHIVE Attribution](https://github.com/PopHIVE/Ingest) / [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

[Epic Cosmos](https://cosmos.epic.com/) is a collaborative research platform containing de-identified patient data from over 300 million patients across more than 1,600 hospitals and health systems using Epic electronic health record systems. Data is accessed via SlicerDicer, a self-service analytics tool. The dataset includes emergency department encounters, diagnoses, immunizations, laboratory results, and other clinical data.

Delphi ingests aggregated emergency department encounter data curated by the [PopHIVE platform](https://github.com/PopHIVE/Ingest).

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `all_n_encounters_ed` | All Conditions | Count | Total emergency department encounters over the reference week. |
| `covid_n_ed` | COVID-19 | Count | Emergency department encounters with a COVID-19 diagnosis. |
| `covid_pct_ed` | COVID-19 | Percentage | Percentage of emergency department encounters with a COVID-19 diagnosis. |
| `flu_n_ed` | Influenza | Count | Emergency department encounters with an influenza diagnosis. |
| `flu_pct_ed` | Influenza | Percentage | Percentage of emergency department encounters with an influenza diagnosis. |
| `rsv_n_ed` | RSV | Count | Emergency department encounters with an RSV diagnosis. |
| `rsv_pct_ed` | RSV | Percentage | Percentage of emergency department encounters with an RSV diagnosis. |

---

## Estimation

### Metric Definition

Count signals report the total number of emergency department encounters observed during the reference week.

Percentage signals report the share of those encounters diagnosed with the specified condition for the same location, age group, and week.

### Temporal Handling

Dates in this dataset represent surveillance epiweeks, where each reference date (`reference_time`) corresponds to a Saturday week-ending date.

Upstream updates are expected biweekly, but the release schedule is irregular. Intervals between releases have ranged from weekly to monthly, with occasional publication delays exceeding four weeks.

### Geographic Handling

PopHIVE natively reports national (`nation`) and state (`state`) data directly. These levels use the `source` fill method. Upstream national values are computed by PopHIVE from unsuppressed encounter records.

Delphi calculates HHS regional values (`hhs`) by aggregating state-level data using population weights. When computing HHS regional values, the `fill_method` column distinguishes the imputation method applied to missing or suppressed state values:

- `source`: Direct upstream reporting without imputation (available at `nation` and `state` levels).
- `zero` (or `fill_zero`): Treats missing or suppressed state values as zero during aggregation.
- `ave` (or `fill_ave`): Fills missing or suppressed state values with the population-weighted average of reporting states in the HHS region before aggregating.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | Signal identifier. |
| `report_time` | Primary Key | date | Publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`nation`, `state`, `hhs`). |
| `geo_value` | Primary Key | string | Geographic entity code. |
| `fill_method` | Primary Key | string | Imputation method (`source`, `zero`, `ave`). |
| `age_group` | Primary Key (Extra Key) | string | Age group category. |
| `reference_time` | Primary Key | date | Reference week ending Saturday (`YYYY-MM-DD`). |
| `value` | Value Column | float | Measured encounter count or percentage. |

### Extra keys

The `age_group` column stratifies data into population age categories:

| Value | Description |
| :--- | :--- |
| `all` | All ages combined |
| `<1` | Infants under 1 year |
| `1-4` | Children aged 1 to 4 years |
| `5-17` | Children and adolescents aged 5 to 17 years |
| `18-49` | Adults aged 18 to 49 years |
| `50-64` | Adults aged 50 to 64 years |
| `65+` | Adults 65 years and older |

An unfiltered query returns rows across all age groups. Queries can filter to a specific group using the `extra_keys` parameter (for example, `extra_keys=age_group:18-49`).

---

## Missingness & Privacy

Counts under 10 are suppressed upstream by PopHIVE for patient privacy and replaced with a count of 5. These suppressed cells appear as 5 in the count signals. Percentage signals derived from these counts reflect this imputed value.

Unobserved weeks or locations without reporting health systems are absent from the dataset rather than listed as null.

---

## Limitations

Epic Cosmos reflects data only from healthcare systems that use Epic electronic health records and participate in Cosmos. Data coverage varies geographically according to Epic market adoption. Regions with lower Epic adoption may not be representative of the broader population.

---

## Lag & Backfill

PopHIVE releases data updates on an irregular cadence, typically every two to four weeks. Each release publishes a full revision of historical data, which updates prior reference dates.

---

## Source and Licensing

This data source is provided by the [PopHIVE platform](https://github.com/PopHIVE/Ingest) and is based on de-identified data from [Epic Cosmos](https://cosmos.epic.com/).

The data can be re-used with appropriate attribution under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en). A suggested citation relating to this data is:

> Results of research performed with Epic Cosmos were obtained from the PopHIVE platform (https://github.com/PopHIVE/Ingest).
