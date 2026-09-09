---
title: NHSN Hospitalizations
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 2
---

# NHSN Respiratory Hospitalizations
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nhsn` |
| **Data Source** | [National Healthcare Safety Network (NHSN)](https://www.cdc.gov/nhsn/index.html) via [HealthData.gov](https://healthdata.gov/) |
| **Geographic Levels** | `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2020-08-08 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V4 [`nhsn`](../covidcast-signals/nhsn.md) source, itself the continuation of the earlier [`hhs`](../covidcast-signals/hhs.md) hospitalization source. The admission counts are unchanged. V5 adds census-level aggregation and bed capacity signals, and folds the preliminary dataset into each signal's revision history rather than publishing separate `_prelim` signals. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Healthcare Safety Network (NHSN) collects weekly respiratory admission and bed capacity metrics from acute care hospitals across the United States. Delphi ingests the weekly Hospital Respiratory Data release published by the CDC on HealthData.gov, covering COVID-19, influenza, and RSV admissions along with inpatient bed counts.

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_ew` | COVID-19 | Count | Weekly confirmed COVID-19 hospital admissions, as reviewed by the jurisdiction. |
| `confirmed_admissions_flu_ew` | Influenza | Count | Weekly confirmed influenza hospital admissions, as reviewed by the jurisdiction. |
| `confirmed_admissions_rsv_ew` | RSV | Count | Weekly confirmed RSV hospital admissions, as reviewed by the jurisdiction. |
| `hosprep_confirmed_admissions_covid_ew` | COVID-19 | Count | Weekly number of hospitals reporting confirmed COVID-19 hospital admissions. |
| `hosprep_confirmed_admissions_flu_ew` | Influenza | Count | Weekly number of hospitals reporting confirmed influenza hospital admissions. |
| `hosprep_confirmed_admissions_rsv_ew` | RSV | Count | Weekly number of hospitals reporting confirmed RSV hospital admissions. |
| `inpatient_beds_ew` | — | Count | Weekly average number of inpatient beds. |
| `inpatient_beds_occupied_pct_ew` | — | Count | Weekly average number of occupied inpatient beds. |

<!-- TODO: inpatient_beds_occupied_pct_ew maps the NHSN numInptBedsOcc count field, not a percentage. Confirm the _pct_ element in the signal name is intended. -->

---

## Estimation

### Metric Definition

All signals are raw weekly counts from source fields. These correspond to column names in the original upstream CDC NHSN Hospital Respiratory Data release (see the [data dictionary](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data)):
- `confirmed_admissions_*`: weekly count of new patient hospital admissions with confirmed infection (columns `totalconf_<disease>_newadm`).
- `hosprep_confirmed_admissions_*`: weekly count of hospitals reporting confirmed admissions (columns `totalconf_<disease>_newadmhosprep`).
- `inpatient_beds_*`: weekly average bed counts (columns `numinptbeds` and `numinptbedsocc`).

### Temporal Handling

Each value covers a 7-day week (Sunday through Saturday), labelled by its Saturday week-ending date.

The CDC publishes a preliminary weekly file about 4 days after the reference week ends, followed by a finalized file 2 to 3 days later. Both releases share the same signal names and are distinguished by publication date (`report_time`). Default snapshot queries return the latest finalized values, while earlier preliminary releases remain accessible by specifying a past `snapshot_date` or through the `/archive/` endpoint.

### Geographic Handling

The source file carries values for states (`state`), HHS regions (`hhs`), and the nation (`nation`), which Delphi reads directly. Census divisions (`census_division`) and census regions (`census_region`) are a plain sum of the member state values based on the [U.S. Census Bureau regions and divisions](https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf).

Values are ingested directly or summed without imputation, so `fill_method` is always `source`.

---

## Relationship to V4

The V4 `nhsn` source published the same admission counts for state, HHS regions, and nation. What changed in V5:

- Expanded Geographies. V5 adds census divisions and census regions, summed from state values.
- Preliminary Data. The CDC publishes a preliminary weekly file a few days ahead of the finalized file. V4 presented the preliminary file as separate `_prelim` signals. V5 writes both files to the same signal names, so the preliminary numbers appear as an earlier release and the finalized numbers supersede them on the next update. Read a past `snapshot_date`, or the `/archive/` endpoint, to recover the preliminary values.
- New Signals. V5 adds `inpatient_beds_ew` and `inpatient_beds_occupied_pct_ew`, which V4 `nhsn` did not carry.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., `ca` for California, `us` for national). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation, always `source` for this source. |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation, labeled by Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded measurement (hospital admissions, reporting hospital counts, or average bed counts). |


---

## Missingness & Privacy

The source applies no cell suppression or volume masking. All reported counts are published directly.

Unobserved values reflect facility non-reporting. Missing hospital reports are not imputed. In census roll-ups, missing states are omitted from the sum.

---

## Limitations

The network excludes psychiatric, rehabilitation, and religious non-medical facilities. Reporting rules and platforms have changed over time, most notably the 2023 move from HHS Protect to NHSN, so long series cross more than one collection ownership. Values before December 2020 predate the current data quality review and may be anomalous.

---

## Lag & Backfill

The preliminary file is published approximately four days after the reference week ends. The finalized weekly files publish 6 to 7 days after the reference week ends. The CDC continues to revise recent weeks, usually within two months, and revisions tend to be small and upward.

---

## Source and Licensing

This dataset is published by the CDC via HealthData.gov under [Public Domain U.S. Government](https://www.usa.gov/government-works) terms.
