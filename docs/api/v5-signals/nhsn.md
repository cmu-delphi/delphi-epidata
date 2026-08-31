---
title: NHSN Hospitalizations
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 2
---

# NHSN Respiratory Hospitalizations (V5)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nhsn` |
| **Data Source** | [National Healthcare Safety Network (NHSN)](https://www.cdc.gov/nhsn/index.html) via [HealthData.gov](https://healthdata.gov/) |
| **Geographic Levels** | `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Weekly (Epiweeks; Saturdays) |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2020-08-08 |
| **Date of Last Revision** | Versioned snapshot (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | `fill_method` |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Healthcare Safety Network (NHSN) surveillance system collects hospital respiratory admissions and capacity metrics from acute care facilities across the United States. Ingestion processes weekly releases published by the CDC on HealthData.gov, covering COVID-19, Influenza, and RSV admissions alongside inpatient bed capacity metrics.

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_ew` | COVID-19 | Count | Weekly confirmed COVID-19 hospital admissions from finalized NHSN reporting. |
| `hosprep_confirmed_admissions_covid_ew` | COVID-19 | Count | Preliminary weekly confirmed COVID-19 hospital admissions reported directly by hospitals ahead of NHSN finalization. |
| `confirmed_admissions_flu_ew` | Influenza | Count | Weekly confirmed influenza hospital admissions from finalized NHSN reporting. |
| `hosprep_confirmed_admissions_flu_ew` | Influenza | Count | Preliminary weekly confirmed influenza hospital admissions reported directly by hospitals ahead of NHSN finalization. |
| `confirmed_admissions_rsv_ew` | RSV | Count | Weekly confirmed RSV hospital admissions from finalized NHSN reporting. |
| `hosprep_confirmed_admissions_rsv_ew` | RSV | Count | Preliminary weekly confirmed RSV hospital admissions reported directly by hospitals ahead of NHSN finalization. |
| `inpatient_beds_ew` | — | Count | Total inpatient hospital beds reported. |
| `inpatient_beds_occupied_pct_ew` | — | Percentage | Percentage of inpatient hospital beds occupied. |

---

## Estimation

### Geographic Aggregation

Source files natively contain totals for states (`state`), the nation (`nation`), and HHS regions (`hhs`). Delphi extracts these levels directly.

Census divisions (`census_division`) and census regions (`census_region`) are calculated by aggregating state-level counts using Delphi's geographic crosswalk.

### Temporal Handling

All weekly metrics align to the Saturday week-ending date (`time_value`).

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic granularity level (`state`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | Geographic entity code (e.g. `ca` for California, `us` for national). |
| `fill_method` | Primary Key (Extra Key) | Imputation indicator (`source`). |
| `time_value` | Primary Key | Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | Count or occupancy percentage. |

### Extra Keys

The `fill_method` column identifies the record origin:

| Value | Behavior |
| :--- | :--- |
| `source` | Native reported data from NHSN files or direct state-level aggregations. |

### Example Query

```text
signal=confirmed_admissions_covid_ew&geo_type=state&geo_values=ca&time_values=2024-01-06
```

---

## Missingness & Privacy

Hospital reporting rates vary by jurisdiction and week. Missing or uncollected data in source tables is represented as null. Delphi does not impute missing hospital counts.

---

## Limitations

Reporting mandates and participation rules have shifted over time, notably during the transition from the HHS TeleTracking system to the NHSN reporting platform. Preliminary hospital-reported signals (`hosprep_`) reflect unverified rapid reports and may differ from finalized NHSN releases.

---

## Lag & Backfill

Finalized weekly files typically publish with a latency of 1 to 2 weeks. CDC frequently updates historical weeks in subsequent snapshots, which Delphi reflects upon ingesting new releases.

---

## Source & Licensing

Data is published by the Centers for Disease Control and Prevention (CDC) National Healthcare Safety Network (NHSN) on HealthData.gov. It is available in the public domain.

---

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **2024-11-01**. Initial release on Delphi V5 API.

</details>
