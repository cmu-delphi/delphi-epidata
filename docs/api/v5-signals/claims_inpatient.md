---
title: Inpatient Claims
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 7
---

# Inpatient Claims (V5)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `claims_inpatient` |
| **Data Source** | De-identified medical billing claims from Delphi health system partners |
| **Geographic Levels** | `nation`, `state`, `hhs`, `census_division`, `census_region`, `msa`, `hrr`, `county` |
| **Temporal Granularity** | Daily (first of each month excluded; see [Temporal Handling](#temporal-handling)) |
| **Reporting Cadence** | Daily |
| **Temporal Scope Start** | 2019-10-01 |
| **Date of Last Revision** | Rolling lookback window (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | `fill_method` |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The inpatient claims dataset measures the percentage of inpatient hospital admission claims associated with respiratory illness diagnoses. Derived from de-identified medical billing claims provided by Delphi health system partners, this dataset tracks admissions for COVID-19, Influenza, and other acute respiratory illnesses (ARI).

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `claims_inpatient_adm_pct_claims_covid` | COVID-19 | Percentage (7-day sum) | 7-day smoothed percentage of inpatient admission claims with a COVID-19 diagnosis. |
| `claims_inpatient_adm_pct_claims_flu` | Influenza | Percentage (7-day sum) | 7-day smoothed percentage of inpatient admission claims with an Influenza diagnosis. |
| `claims_inpatient_adm_pct_ari_other` | Other ARI | Percentage (7-day sum) | 7-day smoothed percentage of inpatient admission claims with acute respiratory illness diagnoses not attributed to COVID-19 or Influenza. |

---

## Estimation

### Geographic Aggregation

Source claims are reported natively at the county (`county`) and Hospital Referral Region (`hrr`) levels. Counts are summed across patient age groups during initial normalization.

Delphi aggregates raw county counts into Metropolitan Statistical Areas (`msa`), states (`state`), HHS regions (`hhs`), census divisions (`census_division`), census regions (`census_region`), and the nation (`nation`) using county population crosswalk weights before smoothing.

### Temporal Handling

Observations are keyed by the clinical date of service (`time_value`).

Due to recurring billing submission spikes, the first day of every calendar month is excluded. In addition, observations before October 1, 2019, and future service dates are omitted.

### Smoothing

A 7-day trailing sum is calculated for each numerator and the total claim denominator across all geographic levels. A minimum of 5 days within the 7-day window is required to compute the sum.

### Metric Calculations

Percentages are calculated as the ratio of disease-specific admission claims to total inpatient admission claims multiplied by 100:

- **COVID-19 (`pct_claims_covid`)**: Before June 1, 2021, the numerator combines COVID-like and unspecified respiratory diagnosis codes. Starting June 1, 2021, the numerator uses specific COVID-19 codes.
- **Influenza (`pct_claims_flu`)**: The numerator uses confirmed influenza diagnosis codes.
- **Other ARI (`pct_ari_other`)**: Published starting August 1, 2022, combining mixed and unspecified acute respiratory illness codes.

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic granularity level (`nation`, `state`, `hhs`, `census_division`, `census_region`, `msa`, `hrr`, `county`). |
| `geo_value` | Primary Key | Geographic entity code (e.g. `pa` for Pennsylvania, `42003` for Allegheny County). |
| `fill_method` | Primary Key (Extra Key) | Aggregation method (`source`). |
| `time_value` | Primary Key | Date of service (`YYYY-MM-DD`). |
| `value` | Value Column | Percentage of claims (0–100). |

### Extra Keys

The `fill_method` column identifies the record origin:

| Value | Description |
| :--- | :--- |
| `source` | Native county and HRR records or direct population-weighted crosswalk aggregations. |

### Example Query

```text
signal=claims_inpatient_adm_pct_claims_covid&geo_type=state&geo_values=ny&time_values=2024-01-15
```

---

## Missingness & Privacy

A volume threshold is enforced for stability and privacy. Any geographic area on a date where the 7-day smoothed total denominator is fewer than 100 claims is censored and removed from publication.

---

## Limitations

Medical claims represent insured patient populations covered by participating data providers and do not represent uninsured populations. Because claims submission schedules vary by provider and payer, counts for recent days are subject to reporting delays.

---

## Lag & Backfill

Claims data typically exhibits a reporting latency of 3 to 7 days. Delphi processes daily updates with a rolling lookback window to incorporate late-arriving and revised claims.

---

## Source & Licensing

Data is derived from de-identified medical claims provided by Delphi health system partners and is distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **2024-11-01**. Initial release on Delphi V5 API.

</details>
