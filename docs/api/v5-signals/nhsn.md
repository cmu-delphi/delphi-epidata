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

The source applies no cell suppression or volume masking. All reported counts are published directly without privacy thresholds.

Unobserved values reflect facility non-reporting and changes in reporting mandates over time:

- Reference dates before December 1, 2020 predate routine data quality review procedures, such as automated exclusion of invalid values and systematic error correction. Data from this early period may contain anomalies.
- Reference dates through April 30, 2024 reflect a federal reporting mandate instituted by the Department of Health and Human Services.
- Reference dates between May 1, 2024 and October 31, 2024 fall into a voluntary reporting interval following the expiration of the original federal mandate. Facility participation dropped significantly during these months, meaning reported admissions undercount total admissions.
- Reference dates beginning November 1, 2024 reflect the current federal reporting mandate established under updated CMS conditions of participation.

Missing hospital reports are not imputed. In census division and region roll-ups, missing states are omitted from the sum.

---

## Limitations

NHSN collects data from acute care hospitals. Psychiatric, rehabilitation, and religious non-medical facilities are excluded.

Hospital counts reflect the NHSN unique hospital identifier rather than the CMS certification number. Only facilities designated as active reporters are included.

Admissions during the voluntary reporting window from May 1, 2024 through October 31, 2024 are incomplete because many hospitals did not submit data.

RSV data collected before November 1, 2024 has low completeness. Only a small fraction of hospitals voluntarily reported RSV admissions prior to the November 2024 mandate, undercounting true admissions by an estimated two orders of magnitude. The CDC [RSV-NET](https://www.cdc.gov/rsv/php/surveillance/rsv-net.html) surveillance network offers a more reliable historical benchmark for RSV admissions during that period.

Administration of this surveillance system moved from HHS Protect to NHSN in late 2023. Comparisons across the transition indicate that COVID-19 and influenza figures are largely consistent between both systems. Notable discrepancies exist for a few states, with Georgia until 2023, Louisiana, Nevada, Puerto Rico in late 2020, and Tennessee reporting lower counts in legacy HHS Protect files than in NHSN.

These indicators reflect direct census counts from reporting hospitals rather than statistical samples. Standard errors and sample sizes do not apply.

---

## Lag & Backfill

The CDC publishes preliminary weekly data on Wednesdays, approximately 4 days after the reference week ends. Finalized weekly files publish on Fridays or Saturdays, 6 to 7 days after the reference week ends. In V5, preliminary data is ingested first and then superseded by finalized data under the same signal name.

The CDC continuously updates data for prior weeks as facilities submit late or corrected reports. Most revisions occur within 2 months of initial release. Older data rarely changes.

Approximately 20 percent of values reported within the preceding 2 months undergo revisions. These adjustments usually occur only once or twice per observation. Revisions generally increase reported counts as late submissions arrive, with a median difference of 2 percent between initial and final values.

Large revisions occur occasionally when a facility submits bulk retrospective corrections. Revision volume also varies geographically. For example, Texas experiences more frequent revisions than most states but with small shifts, typically with a median change below 0.1 percent. Other states, including Idaho, New Hampshire, Hawaii, and North Dakota, have exhibited higher percentage volatility when revised.

---

## Source and Licensing

This dataset is published by the CDC via HealthData.gov under [Public Domain U.S. Government](https://www.usa.gov/government-works) terms.
