---
title: FluView Clinical Laboratory Surveillance
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 11
---

# FluView Clinical Laboratory Surveillance
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `fluview_resp_lab_clinical` |
| **Data Source** | [CDC FluView / Clinical Laboratories](https://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) |
| **Geographic Levels** | `state`, `census_division`, `hhs`, `nation` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly (Fridays) |
| **Temporal Scope Start** | 2015-10-10 (2015w40) |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V3 [`fluview_clinical`](../fluview_clinical.md) endpoint. Signal names follow standard V5 conventions, statewide New York is pooled from NYC and non-NYC components, and public health lab data is now separated into [`fluview_resp_lab_ph`](fluview_resp_lab_ph.md). See [Relationship to V3](#relationship-to-v3).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

Clinical laboratories in hospitals, commercial reference labs, and clinics report weekly respiratory test results to the CDC through the National Respiratory and Enteric Virus Surveillance System (NREVSS).

Delphi ingests this data weekly from the CDC FluView Interactive portal. The dataset reports laboratory-confirmed influenza test volume, positive results for Influenza A and B, and test positivity rates.

For outpatient syndromic surveillance, see [FluView ILINet](fluview_ilinet.md). For subtyping and lineage data, see [FluView Public Health Labs](fluview_resp_lab_ph.md).

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `total_specimens` | Influenza | Count | Weekly count of respiratory specimens tested for influenza by participating clinical laboratories. |
| `positive_a` | Influenza A | Count | Weekly count of specimens testing positive for Influenza A. |
| `positive_b` | Influenza B | Count | Weekly count of specimens testing positive for Influenza B. |
| `pct_positive` | Influenza | Percentage | Percentage of tested specimens positive for any influenza virus ($100 \cdot \frac{\text{positive\_a} + \text{positive\_b}}{\text{total\_specimens}}$). |
| `pct_positive_a` | Influenza A | Percentage | Percentage of tested specimens positive for Influenza A. |
| `pct_positive_b` | Influenza B | Percentage | Percentage of tested specimens positive for Influenza B. |

---

## Estimation

### Metric Definition

- Overall positivity (`pct_positive`) is the percentage of tested specimens positive for any influenza virus, dividing combined positive detections (`positive_a` plus `positive_b`) by `total_specimens` and multiplying by 100.
- Specific positivity (`pct_positive_a`, `pct_positive_b`) is the percentage of tested specimens positive for Influenza A or B, dividing `positive_a` or `positive_b` by `total_specimens` and multiplying by 100.
- Counts (`total_specimens`, `positive_a`, `positive_b`) pass through directly from the CDC as raw weekly test volumes and positive detections.

### Smoothing

All signals are unsmoothed discrete 7-day weekly totals or ratios.

### Uncertainty

Uncertainty intervals and standard errors are not published by the CDC for clinical laboratory surveillance. The dataset includes `total_specimens` as a direct measure of reporting volume.

### Temporal Handling

Observations cover 7-day epidemiological weeks defined by the CDC's Morbidity and Mortality Weekly Report (MMWR). An MMWR week runs from Sunday through Saturday, standardizing public health reporting across calendar years.

- `reference_time` is the Saturday week-ending date of the surveillance week.
- `report_time` is the release date when Delphi ingested the weekly CDC snapshot. Revisions update past weeks as delayed laboratory reports arrive.

### Geographic Handling

All four geographic levels (`nation`, `hhs`, `census_division`, `state`) are computed natively by the CDC and ingested directly without regional aggregation (`fill_method = 'source'`).

At the `state` level, the CDC reports New York as two separate jurisdictions: New York City (`nyc`) and New York State excluding NYC (`ny_minus_nyc`). When both are reported for a given week, Delphi reconstructs a combined statewide `ny` record (`fill_method = 'nyc_plus_ny_minus_nyc'`).

Raw counts are summed directly:

$$
C_{\text{NY}, t} = C_{\text{NYC}, t} + C_{\text{NY-NYC}, t}
$$

where $$C$$ represents each specimen count (`total_specimens`, `positive_a`, `positive_b`).

Positivity percentages are recomputed as pooled ratios using the summed counts:

$$
\text{pct\_positive}_{\text{NY}, t} = 100 \cdot \frac{\text{positive\_a}_{\text{NY}, t} + \text{positive\_b}_{\text{NY}, t}}{\text{total\_specimens}_{\text{NY}, t}}
$$

Type-specific positivity percentages (`pct_positive_a`, `pct_positive_b`) are recomputed analogously using their respective summed counts.

---

## Relationship to V3

This source reproduces the legacy V3 `fluview_clinical` endpoint (`https://api.delphi.cmu.edu/epidata/fluview_clinical/`).

| V3 Field | V5 Signal | Notes |
| :--- | :--- | :--- |
| `total_specimens` | `total_specimens` | Exact match |
| `total_a` | `positive_a` | Renamed to standard `positive_*` prefix (Influenza A positive count) |
| `total_b` | `positive_b` | Renamed to standard `positive_*` prefix (Influenza B positive count) |
| `percent_positive` | `pct_positive` | Renamed from `percent_` to standard `pct_` prefix |
| `percent_a` | `pct_positive_a` | Renamed from `percent_` to standard `pct_` prefix |
| `percent_b` | `pct_positive_b` | Renamed from `percent_` to standard `pct_` prefix |

What changed in V5:

- **Standardized Signal Naming.** Positive counts use the `positive_*` prefix (formerly `total_a`, `total_b`), and positivity percentages use the `pct_*` prefix (formerly `percent_*`).
- **Dedicated Source Separation.** Clinical laboratory surveillance is separated from public health laboratory testing into its own endpoint (`fluview_resp_lab_clinical`).

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the indicator (`total_specimens`, `positive_a`, `positive_b`, `pct_positive`, `pct_positive_a`, `pct_positive_b`). |
| `report_time` | Primary Key | date | The date Delphi ingested the CDC weekly file (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state`, `census_division`, `hhs`, `nation`). |
| `geo_value` | Primary Key | string | Location code. |
| `fill_method` | Primary Key | string | `source` for directly ingested rows. `nyc_plus_ny_minus_nyc` for reconstructed statewide NY. |
| `reference_time` | Primary Key | date | Saturday week-ending date of the surveillance week (`YYYY-MM-DD`). |
| `value` | Value Column | float | Test positivity percentage or specimen count. |

---

## Missingness & Privacy

- This source is a voluntary reporting network. If no laboratories report within a jurisdiction during a week, that observation is omitted from the dataset rather than recorded as zero.
- No cell suppression or volume masking is applied to clinical laboratory testing data.

---

## Limitations

- Testing practices vary over time and across facilities. Changes in clinician testing thresholds, adoption of multiplex PCR panels, and institutional guidelines can affect test positivity rates.
- Laboratory participation varies across states. Coverage depends on the number and market share of enrolled laboratories in each jurisdiction.
- Clinical laboratories differentiate between Influenza A and B, but do not perform genetic subtyping. For subtyping, consult [`fluview_resp_lab_ph`](fluview_resp_lab_ph.md).

---

## Lag & Backfill

- Initial weekly data is published by the CDC on Fridays, six days after the surveillance week ends.
- Backfill is common during the first two to four weeks as participating laboratories submit delayed reports. Revisions can be accessed via the `/archive/` endpoint or by querying with `snapshot_date`.

---

## Source and Licensing

Clinical laboratory surveillance data is collected by the CDC National Center for Immunization and Respiratory Diseases (NCIRD) via NREVSS. The data is in the [public domain](https://www.usa.gov/government-works).
