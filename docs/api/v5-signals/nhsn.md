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
| **Temporal Granularity** | Weekly, week ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2020-08-08 |
| **Date of Last Revision** | Revised on backfill (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> **Reproduces V4.** This source reproduces the legacy V4 COVIDcast [`nhsn`](../covidcast-signals/nhsn.md) source, itself the continuation of the earlier [`hhs`](../covidcast-signals/hhs.md) hospitalization source. The admission counts are unchanged. V5 adds census-level aggregation and bed capacity signals, and folds the preliminary dataset into each signal's revision history rather than publishing separate `_prelim` signals. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Healthcare Safety Network collects weekly respiratory admission and bed capacity metrics from acute care hospitals across the United States. Delphi ingests the weekly Hospital Respiratory Data release published by the CDC on HealthData.gov, covering COVID-19, influenza, and RSV admissions along with inpatient bed counts.

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_ew` | COVID-19 | Count | Weekly confirmed COVID-19 hospital admissions, as reviewed by the jurisdiction. |
| `confirmed_admissions_flu_ew` | Influenza | Count | Weekly confirmed influenza hospital admissions, as reviewed by the jurisdiction. |
| `confirmed_admissions_rsv_ew` | RSV | Count | Weekly confirmed RSV hospital admissions, as reviewed by the jurisdiction. |
| `hosprep_confirmed_admissions_covid_ew` | COVID-19 | Count | Weekly confirmed COVID-19 hospital admissions, as reported directly by hospitals ahead of jurisdiction review. |
| `hosprep_confirmed_admissions_flu_ew` | Influenza | Count | Weekly confirmed influenza hospital admissions, as reported directly by hospitals ahead of jurisdiction review. |
| `hosprep_confirmed_admissions_rsv_ew` | RSV | Count | Weekly confirmed RSV hospital admissions, as reported directly by hospitals ahead of jurisdiction review. |
| `inpatient_beds_ew` | — | Count | Weekly average number of inpatient beds. |
| `inpatient_beds_occupied_pct_ew` | — | Count | Weekly average number of occupied inpatient beds. |

<!-- TODO: inpatient_beds_occupied_pct_ew maps the NHSN numInptBedsOcc count field, not a percentage. Confirm the _pct_ element in the signal name is intended. -->
<!-- TODO: confirm hosprep_ semantics against the NHSN HRD data dictionary (totalconf<pathogen>newadmhosprep). -->

---

## Estimation

### Geographic Aggregation

The source file carries values for states (`state`), the nation (`nation`), and HHS regions (`hhs`), which Delphi reads directly. Census divisions (`census_division`) and census regions (`census_region`) are a plain sum of the member state values,

$$
V_g = \sum_{s \in g} V_s.
$$

### Temporal Handling

Each value covers one ISO week and is labelled by its Saturday week-ending date.

### Metric Definition

All signals are counts taken straight from the source fields, with no rate conversion, smoothing, or modelling. The `confirmed_admissions_*` signals carry the jurisdiction-reviewed field (`totalconf<pathogen>newadm`). The `hosprep_confirmed_admissions_*` signals carry the hospital-reported field (`totalconf<pathogen>newadmhosprep`) for the same week, before that review. The bed signals carry the weekly average bed counts.

### Uncertainty

This source publishes no standard errors, sample sizes, or confidence intervals.

---

## Relationship to V4

The V4 `nhsn` source published the same admission counts for nation, HHS regions, and state. What changed in V5:

Geographies. V5 adds census divisions and census regions, summed from state values.

Preliminary data. The CDC publishes a preliminary weekly file a few days ahead of the finalized file. V4 exposed the preliminary file as separate `_prelim` signals. V5 writes both files to the same signal names, so the preliminary numbers appear as an earlier release and the finalized numbers supersede them on the next update. Read a past `snapshot_date`, or the `/archive/` endpoint, to recover the preliminary values.

Bed capacity. V5 adds `inpatient_beds_ew` and `inpatient_beds_occupied_pct_ew`, which V4 `nhsn` did not carry.

The `hosprep_` prefix means the same thing in both APIs: figures as first reported by hospitals, before the jurisdiction review that produces the `confirmed_admissions_*` figures.

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic level (`state`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | Geographic code (e.g. `ca` for California, `us` for national). |
| `fill_method` | Primary Key | Aggregation path, always `source` for this source. |
| `time_value` | Primary Key | Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | Count. |

### Example Query

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=nhsn&signal=confirmed_admissions_covid_ew&geo_type=state
```

---

## Missingness & Privacy

Hospital reporting has moved between mandatory and voluntary periods, so participation varies by state and week. Weeks a hospital did not report are left missing and are not imputed. RSV admissions from the voluntary period before November 2024 are badly undercounted. Census aggregates are summed from whatever states are present, so a missing state lowers the aggregate rather than blocking it.

---

## Limitations

The network excludes psychiatric, rehabilitation, and religious non-medical facilities. Reporting rules and platforms have changed over time, most notably the 2023 move from HHS Protect to NHSN, so long series cross more than one collection regime. Values before December 2020 predate the current data quality review and may be anomalous.

---

## Lag & Backfill

Finalized weekly files publish 6 to 7 days after the reference week ends, and the preliminary file lands about 4 days after. The CDC continues to revise recent weeks, usually within two months, and revisions tend to be small and upward.
