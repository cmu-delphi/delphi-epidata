---
title: VA Respiratory
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 5
---

# Veterans Affairs Seasonal Respiratory Surveillance (V5)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `va_respiratory` |
| **Data Source** | [VA Seasonal Disease Review](https://www.accesstocare.va.gov/Healthcare/SeasonalDiseaseReview) |
| **Geographic Levels** | Facility (`va_facility`, cases only), State (`state`), MSA (`msa`, cases only), HHS Region (`hhs`), Census Division (`census_division`), Census Region (`census_region`), National (`nation`) |
| **Temporal Granularity** | Daily (season-to-date cumulative counts from Oct 1 to Sep 30) |
| **Reporting Cadence** | Daily |
| **Temporal Scope Start** | Seasonal reporting (starts October 1st of each surveillance season) |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

## Overview
{: .no_toc}

The Department of Veterans Affairs (VA) automated biosurveillance system tracks seasonal respiratory disease cases and vaccinations across VA medical facilities. Data is reported through the VA Access to Care portal for three key respiratory pathogens: COVID-19, Influenza, and RSV.

Delphi ingests two daily feeds: facility-level cumulative case counts from `SeasonalReviewCases.csv` and state-level cumulative vaccination counts from `SeasonalReviewVaccines.csv`.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Available Signals

Signals are organized by pathogen (`covid`, `flu`, `rsv`) and cover cases as well as vaccination metrics.

### Case Signals

Case metrics reflect cumulative counts and population-adjusted rates among Veterans Health Administration (VHA) enrollees:

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `covid_cases_cumulative` | COVID-19 | Cumulative Count | Season-to-date confirmed cases at VA facilities. |
| `covid_cases_per_100k_7dav` | COVID-19 | Rate (7-day average) | 7-day trailing average of daily incident cases per 100,000 VHA-enrolled veterans. Includes 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |
| `flu_cases_cumulative` | Influenza | Cumulative Count | Season-to-date confirmed cases at VA facilities. |
| `flu_cases_per_100k_7dav` | Influenza | Rate (7-day average) | 7-day trailing average of daily incident cases per 100,000 VHA-enrolled veterans. Includes 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |
| `rsv_cases_cumulative` | RSV | Cumulative Count | Season-to-date confirmed cases at VA facilities. |
| `rsv_cases_per_100k_7dav` | RSV | Rate (7-day average) | 7-day trailing average of daily incident cases per 100,000 VHA-enrolled veterans. Includes 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |

### Vaccination Signals

Vaccination metrics track season cumulative uptake across all pathogens, plus lifetime cumulative uptake for RSV:

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `covid_vaccines_season_cumulative` | COVID-19 | Cumulative Count | Season-to-date doses administered to VHA enrollees. |
| `covid_vaccines_season_cumulative_per_100k` | COVID-19 | Rate | Season-to-date doses per 100,000 VHA enrollees with 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |
| `flu_vaccines_season_cumulative` | Influenza | Cumulative Count | Season-to-date doses administered to VHA enrollees. |
| `flu_vaccines_season_cumulative_per_100k` | Influenza | Rate | Season-to-date doses per 100,000 VHA enrollees with 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |
| `rsv_vaccines_season_cumulative` | RSV | Cumulative Count | Season-to-date doses administered to VHA enrollees. |
| `rsv_vaccines_season_cumulative_per_100k` | RSV | Rate | Season-to-date doses per 100,000 VHA enrollees with 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |
| `rsv_vaccines_lifetime_cumulative` | RSV | Cumulative Count | Total cumulative doses administered since tracking began. |
| `rsv_vaccines_lifetime_cumulative_per_100k` | RSV | Rate | Lifetime cumulative doses per 100,000 VHA enrollees with 90% Wilson confidence intervals (`ci_lower`, `ci_upper`). |

---

## Geographic Aggregation

VA hospitals serve regional catchment areas that often cross state borders:

- **Cases:** Reported at the VA Health Care System (`va_facility`) level. Catchment counts are disaggregated to constituent counties using enrollee population weights from the VHA Enrollees by County dataset. County counts are then re-aggregated up to standard geographic levels (`state`, `msa`, `hhs`, `census_division`, `census_region`, `nation`). Raw county counts are not published directly.
- **Vaccinations:** Reported natively at the state level (`state`). These skip county disaggregation and aggregate upward to `hhs`, `census_division`, `census_region`, and `nation`.

Non-standard geographic codes (`ph` for Philippines and `other`) are excluded during aggregation.

---

## Estimation and Indicator Processing

### Daily Incidence and Smoothing

Daily case incidence is computed as the difference between successive cumulative snapshots. To reduce noise from weekend reporting and administrative lags, Delphi calculates a rolling 7-day trailing average (`_7dav`) of daily incidence before standardizing to a per-100,000 rate.

### Handling Cumulative Snapshot Decreases

Cumulative case counts generally increase over the course of a respiratory season, but reporting issues or database synchronization drops can sometimes cause temporary dips that bounce back the next day. Cumulative indicators are provided exactly as published on the VA website without modification. For the derived daily incidence and smoothed rate indicators, however, the pipeline applies an adjustment. Specifically, it smooths over single-day dips when computing daily differences and folds the change into the subsequent recovery snapshot. Other decreases that do not fit this temporary pattern are left as reported.

When a new surveillance season begins on October 1st, that day's count is recorded directly as that day's incidence rather than compared against the end of the previous season.

### Population Normalization

All rates are normalized per 100,000 VHA-enrolled veterans using official county-level enrollment statistics from the VHA Enrollees by County dataset.

### Uncertainty

Rate signals include uncertainty estimates quantified using the 90% Wilson score interval, published directly in the `ci_lower` and `ci_upper` columns.

<!-- TODO: Include full mathematical formulation for Wilson score interval and rate scaling -->

$$
% TODO: add Wilson score interval formula
$$

---

## Schema Details

The V5 table schema for `va_respiratory` includes:

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Name of the signal. |
| `geo_type` | Primary Key | Geographic resolution (`va_facility`, `state`, `msa`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | Geographic identifier. |
| `fill_method` | Primary Key | Imputation method: `source` for reported facility/state grain, `zero` for zero-filled aggregations. |
| `time_value` | Primary Key | Reference date of observation (`YYYY-MM-DD`). |
| `value` | Value Column | Estimated signal value (count or rate per 100,000 enrollees). |
| `ci_lower` | Value Column | Lower bound of the 90% Wilson confidence interval (rate signals only). |
| `ci_upper` | Value Column | Upper bound of the 90% Wilson confidence interval (rate signals only). |

---

## Missingness and Privacy Suppression

Counts fewer than 11 are suppressed by the VA for privacy and reported as `< 11`. These values are parsed as null during ingestion and approximated as 0 during geographic aggregation.

Higher-level cumulative totals are published only when all underlying locations report for a given date; if any location is entirely absent from that day's source file, the aggregate cumulative count is withheld.

## Limitations

Because the VA portal only maintains active files for recent reference days and lacks a complete historical archive, reconstructing a long-term version history retroactively is challenging. 

Additionally, cases are reported on the date when positive confirmation or diagnostic review occurred rather than when medical care was first sought. This means that successive snapshot deltas do not represent true daily clinical incidence. To provide a more reliable approximation of incidence, the pipeline maintains tracking of revisions across recent historical files, restaging a lookback window of snapshots to repair trailing averages and account for delayed reports.

---

## Source and Licensing

Data originates from the [U.S. Department of Veterans Affairs Access to Care Seasonal Disease Review](https://www.accesstocare.va.gov/Healthcare/SeasonalDiseaseReview).

This public dataset is in the public domain and made available under the [U.S. Government Public Domain](https://www.usa.gov/government-works) terms without API access restrictions.
