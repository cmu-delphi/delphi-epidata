---
title: FluView Public Health Laboratory Surveillance
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 12
---

# FluView Public Health Laboratory Surveillance
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `fluview_resp_lab_ph` |
| **Data Source** | [CDC FluView / Public Health Laboratories](https://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) |
| **Geographic Levels** | `state`, `census_division`, `hhs`, `nation` |
| **Temporal Granularity** | Weekly for `nation`, `hhs`, `census_division` (week ending Saturday). Seasonal for `state` (anchored to week 40) |
| **Reporting Cadence** | Weekly (Fridays) |
| **Temporal Scope Start** | 2015-10-10 (2015w40) |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces and expands the public health laboratory component of legacy V3 [`fluview_clinical`](../fluview_clinical.md). Subtype counts are organized under dedicated signal names, including Avian Influenza A(H5). See [Relationship to V3](#relationship-to-v3).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

Public health laboratories report influenza testing and subtyping results to the CDC through the National Respiratory and Enteric Virus Surveillance System (NREVSS). These laboratories test a subset of positive specimens forwarded from clinical laboratories to identify virus subtypes and lineages.

Delphi ingests this data weekly from the CDC FluView Interactive portal. The dataset tracks circulating strains through specimen counts across nine subtypes and lineages, including A(2009 H1N1), A(H3N2), A(H5), A(H3N2v), B/Victoria, and B/Yamagata.

For diagnostic testing volume and positivity rates from clinical laboratories, see [FluView Clinical Labs](fluview_resp_lab_clinical.md). For outpatient syndromic surveillance, see [FluView ILINet](fluview_ilinet.md).

---

## Indicators (Signals)

All indicators are weekly or seasonal specimen counts.

| Indicator Name | Pathogen or Lineage | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `total_specimens` | Influenza | Count | Total specimens tested by participating public health laboratories. |
| `positive_a_h1n1_2009` | Influenza A(H1N1)pdm09 | Count | Number of specimens positive for pandemic Influenza A(2009 H1N1). |
| `positive_a_h3` | Influenza A(H3N2) | Count | Number of specimens positive for Influenza A(H3N2). |
| `positive_a_h5` | Influenza A(H5) | Count | Number of specimens positive for Influenza A(H5) (Avian Influenza). |
| `positive_a_no_subtype` | Influenza A | Count | Number of Influenza A specimens for which subtyping was not performed. |
| `positive_a_h3n2v` | Influenza A(H3N2v) | Count | Number of specimens positive for variant Influenza A(H3N2v). |
| `positive_b` | Influenza B | Count | Number of Influenza B specimens for which lineage determination was not performed. |
| `positive_b_vic` | Influenza B (Victoria) | Count | Number of specimens positive for Influenza B (Victoria lineage). |
| `positive_b_yam` | Influenza B (Yamagata) | Count | Number of specimens positive for Influenza B (Yamagata lineage). |

---

## Estimation

### Metric Definition

All signals are direct counts of subtyped respiratory specimens without rates:

- For national, HHS, and census division levels (`nation`, `hhs`, `census_division`), counts represent discrete weekly specimen volumes.
- For the state level (`state`), counts represent cumulative seasonal totals starting from MMWR week 40.

### Smoothing

All signals are unsmoothed discrete specimen counts.

### Uncertainty

Uncertainty intervals and standard errors are not published by the CDC for public health laboratory surveillance. The dataset includes `total_specimens` as a direct measure of characterization volume.

### Temporal Handling

Observations cover 7-day epidemiological weeks defined by the CDC's Morbidity and Mortality Weekly Report (MMWR). An MMWR week runs from Sunday through Saturday, standardizing public health reporting across calendar years.

- `reference_time` is the Saturday week-ending date of the surveillance week (or week 40 for seasonal state data).
- `report_time` is the release date when Delphi ingested the weekly CDC snapshot. Revisions update past weeks as delayed laboratory reports arrive.

### Geographic Handling

All four geographic levels (`nation`, `hhs`, `census_division`, `state`) are computed natively by the CDC and ingested directly without regional aggregation (`fill_method = 'source'`).

At the `state` level, the CDC reports New York as two separate jurisdictions: New York City (`nyc`) and New York State excluding NYC (`ny_minus_nyc`). Because all indicators in this source are additive specimen counts, Delphi reconstructs a combined statewide `ny` record (`fill_method = 'nyc_plus_ny_minus_nyc'`) when both are reported for a given period.

Raw counts are summed directly:

$$
C_{\text{NY}, t} = C_{\text{NYC}, t} + C_{\text{NY-NYC}, t}
$$

---

## Relationship to V3

This source reproduces and expands the public health laboratory component formerly bundled within the legacy V3 `fluview_clinical` endpoint and CDC FluView download scripts.

| V3 Concept | V5 Signal | Notes |
| :--- | :--- | :--- |
| `total_specimens` | `total_specimens` | Public health lab testing volume |
| `a_2009_h1n1` | `positive_a_h1n1_2009` | Renamed to standard prefix |
| `a_h3` | `positive_a_h3` | Renamed to standard prefix |
| *(not available)* | `positive_a_h5` | **New in V5.** Captures Avian Influenza A(H5) |
| `a_subtyping_not_performed` | `positive_a_no_subtype` | Renamed to standard prefix |
| `h3n2v` | `positive_a_h3n2v` | Renamed to standard prefix |
| `b` | `positive_b` | Renamed to standard prefix |
| `b_vic` | `positive_b_vic` | Renamed to standard prefix |
| `b_yam` | `positive_b_yam` | Renamed to standard prefix |

What changed in V5:

- **Avian Influenza A(H5) Ingestion.** The CDC added `A (H5)` to the public health laboratory feed to monitor avian influenza spillovers. V5 captures `positive_a_h5` as a standard indicator.
- **Dedicated Source Separation.** Public health laboratory surveillance is separated from clinical laboratory testing into its own endpoint (`fluview_resp_lab_ph`).
- **Explicit Geographic Temporal Model.** Documents the difference between weekly multi-state levels (`nation`, `hhs`, `census_division`) and seasonal state-level reporting.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the indicator (e.g., `total_specimens`, `positive_a_h3`, `positive_a_h5`). |
| `report_time` | Primary Key | date | The date Delphi ingested the CDC weekly file (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state`, `census_division`, `hhs`, `nation`). |
| `geo_value` | Primary Key | string | Location code. |
| `fill_method` | Primary Key | string | `source` for directly ingested rows. `nyc_plus_ny_minus_nyc` for reconstructed statewide NY. |
| `reference_time` | Primary Key | date | Saturday week-ending date of the surveillance week (`YYYY-MM-DD`). |
| `value` | Value Column | float | Laboratory specimen count. |

---

## Missingness & Privacy

- This source is a voluntary reporting network. If public health laboratories perform no testing within a jurisdiction during a period, that observation is omitted from the dataset rather than recorded as zero.
- No cell suppression or volume masking is applied.

---

## Limitations

- Public health laboratories do not test a representative sample of respiratory infections. Specimens are selectively forwarded from clinical laboratories based on severity, unusual presentations, or outbreak investigations. Specimen counts track relative strain prevalence and genetic diversity rather than community incidence.
- State counts represent cumulative seasonal totals, while national, HHS, and census division counts represent weekly volumes.
- Due to the global extinction of the Influenza B/Yamagata lineage, `positive_b_yam` counts are expected to remain near zero in modern seasons.

---

## Lag & Backfill

- Initial weekly data is published by the CDC on Fridays, six days after the surveillance week ends.
- Subtyping and genomic sequencing take longer to process than clinical tests. Backfill occurs as laboratories finish sequencing and submit delayed reports. Revisions can be accessed via the `/archive/` endpoint or by querying with `snapshot_date`.

---

## Source and Licensing

Public health laboratory surveillance data is coordinated by the CDC National Center for Immunization and Respiratory Diseases (NCIRD) via NREVSS. The data is in the [public domain](https://www.usa.gov/government-works).
