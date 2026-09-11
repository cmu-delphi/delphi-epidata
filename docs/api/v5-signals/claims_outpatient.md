---
title: Outpatient Claims
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 6
---

# Outpatient Claims
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `claims_outpatient` |
| **Data Source** | De-identified medical billing claims from Delphi health system partners |
| **Geographic Levels** | `county`, `hrr`, `msa`, `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Daily, by date of service |
| **Reporting Cadence** | Daily |
| **Temporal Scope Start** | 2019-10-01; the other-ARI signal begins 2022-08-01 |
| **Temporal Scope End** | Ongoing |
| **[Extra Key Columns](../v5_api_queries.md#key-types-and-column-roles)** | None |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

> This source reproduces the legacy V4 [`doctor-visits`](../covidcast-signals/doctor-visits.md) source. It keeps the same claims feed but replaces the COVID-like illness model and its adjustments with a plain 7-day windowed ratio, splits the metric into per-pathogen signals, and serves revision history through the [`/archive/`](../v5_api_queries.md) and [`/snapshot/`](../v5_api_queries.md) endpoints. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

This source measures the share of outpatient office visits and clinical encounters that carry a respiratory illness diagnosis. It is built from de-identified medical billing claims contributed by Delphi health system partners and covers COVID-19, influenza, and other acute respiratory illness (ARI).

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `claims_outpatient_ov_pct_claims_covid` | COVID-19 | Percentage, 7-day window | Share of outpatient visit claims with a COVID-19 diagnosis. |
| `claims_outpatient_ov_pct_claims_flu` | Influenza | Percentage, 7-day window | Share of outpatient visit claims with a confirmed influenza diagnosis. |
| `claims_outpatient_ov_pct_ari_other` | Other ARI | Percentage, 7-day window | Share of outpatient visit claims with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. History for this signal begins 2022-08-01. |

---

## Estimation

### Metric Definition

For location $$i$$ and service date $$t$$, let $$W_t = \{t-6, \dots, t\}$$ be the trailing 7-day window, $$N_{is}$$ total visit claims on day $$s$$, and $$Y_{is}^k$$ claims carrying diagnosis group $$k$$. The published percentage is

$$
\hat{p}_{it}^k = 100 \cdot \frac{\sum_{s \in W_t} Y_{is}^k}{\sum_{s \in W_t} N_{is}},
$$

computed only when at least 5 days contribute and $$\sum_{s \in W_t} N_{is} \ge 100$$.

### Qualifying Conditions

The raw claims feed categorizes unique daily outpatient visits into five mutually exclusive count categories based on primary ICD-10 diagnosis codes. When a patient encounter carries multiple qualifying diagnosis codes on the same date, priority is assigned in descending order of diagnostic specificity: **Flu**, **COVID-like**, **Flu-like**, then **Mixed**.

| Category | Primary ICD-10 Codes | Description |
| :--- | :--- | :--- |
| **Denominator** | All | Total count of all unique outpatient visits. |
| **Flu** | `J09*`, `J10*`, `J11*` | Confirmed influenza diagnoses (`*` includes all subcodes). |
| **COVID-like** | `U07.1`, `U07.2`, `B97.29`, `J12.81`, `Z03.818`, `B34.2`, `J12.89` | Confirmed or suspected COVID-19 diagnoses. |
| **Flu-like** | `J22`, `B34.9` | Unspecified acute lower-respiratory infections and unspecified viral infections. Correlated with respiratory illness but not specific to influenza. Tracked COVID-19 early in the pandemic before specific codes were widely adopted. |
| **Mixed** | `Z20.828`, `J12.9` | Suspected exposure to other viral communicable diseases and viral pneumonia, unspecified. |

#### Signal Composition

These raw categories map to the three published V5 indicators as follows:

- COVID-19 (`pct_claims_covid`)
  - Before 2021-06-01. Sums `COVID-like` and `Flu-like` counts over the denominator. The `Flu-like` (unspecified lower-respiratory) category tracked COVID-19 closely during the early pandemic while specific codes were not yet in widespread use.
  - From 2021-06-01 onward. Uses `COVID-like` counts only over the denominator.
- Influenza (`pct_claims_flu`). Uses the confirmed `Flu` count over the denominator across the entire series.
- Other ARI (`pct_ari_other`). Published from 2022-08-01 onward. Combines the `Mixed` and `Flu-like` counts over the denominator, capturing acute respiratory illness encounters not attributed to COVID-19 or confirmed influenza.

### Smoothing

For each geography, a 7-day trailing sum is taken of every diagnosis count and the total claim count. The window must contain at least 5 of 7 days to produce a value.

### Temporal Handling

Dates refer to the clinical date of service. Claims dated to the first calendar day of any month are dropped, because submission batching inflates that day. Service dates before 2019-10-01, and service dates in the future, are also dropped.

### Geographic Handling

Claims arrive at two native geographic levels: county (`county`) and Hospital Referral Region (`hrr`). HRR values are served as reported.

All other geographic levels (`msa`, `state`, `hhs`, `census_division`, `census_region`, `nation`) are built by directly summing raw daily county counts (numerators and denominators are aggregated separately). Aggregation is performed on raw daily counts before computing 7-day sums, without imputation, so `fill_method` is always `source`.

---

## Relationship to V4

The V4 `doctor-visits` source used the same outpatient claims and published a single COVID-like illness (CLI) percentage, through `smoothed_cli` and its day-of-week-adjusted twin `smoothed_adj_cli`.

| V4 Signal | V5 Signal | Notes |
| :--- | :--- | :--- |
| `smoothed_cli` | `claims_outpatient_ov_pct_claims_covid` | Replaced blended CLI estimator with 7-day trailing ratio for COVID-19 |
| `smoothed_adj_cli` | *(not available)* | Day-of-week adjustment discontinued |
| *(not available)* | `claims_outpatient_ov_pct_claims_flu` | New in V5 |
| *(not available)* | `claims_outpatient_ov_pct_ari_other` | New in V5 |

What changed in V5:

- **Expanded Geographies.** V4 served state, county, HRR, and MSA. V5 adds nation, HHS regions, census divisions, and census regions.
- **Broader Signal Set.** V5 publishes COVID-19, influenza, and other-ARI percentages separately rather than one blended CLI signal.
- **Revised Estimator.** V4 estimated CLI as an excess over expected respiratory illness, roughly $$Y^{\text{covid-like}} + \big(Y^{\text{flu-like}} + Y^{\text{mixed}} - Y^{\text{flu}}\big)$$ over the denominator, then applied backwards padding to a 500-visit threshold, a Poisson day-of-week adjustment, and a Gaussian linear smoother. V5 uses the 7-day trailing ratio from [Metric Definition](#metric-definition), with no subtraction of influenza and no day-of-week or smoothing model.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (e.g., `county`, `state`, `nation`) |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., `fl` for Florida, `06001` for Alameda County). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation, always `source` for this source. |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation (`YYYY-MM-DD`, date of service). |
| `value` | Value Column | float | The recorded percentage of visit claims over the trailing 7-day window. |

---

## Missingness & Privacy

To protect patient privacy, observations with fewer than 100 total claims across the trailing 7-day window are suppressed and omitted from publication. Windows with fewer than 5 days of data are withheld due to data sparsity and are likewise omitted.

Unobserved dates or geographies without reporting claims produce no records. Both suppressed and unobserved values are omitted entirely from query responses.

---

## Limitations

This source only captures visits from healthcare providers that partner with Delphi, which does not cover all outpatient facilities in the United States. Coverage density varies across states and counties.

The data reflects insured patients who seek outpatient care. Uninsured populations and individuals who do not access formal medical care are not represented.

Uncertainty measures for this source are not published.

Care-seeking behavior changes noticeably around major holidays such as Memorial Day, July 4, Labor Day, Thanksgiving, and Christmas. During these periods, total outpatient visits drop while urgent visits remain steady. This produces artificial upward spikes in the percentage of respiratory visits that do not reflect true changes in community disease transmission.

Differences in local coding habits, billing practices, and provider participation mean that absolute levels are not always comparable across different regions. Trends within a single location over time are generally more reliable than spatial comparisons.

---

## Lag & Backfill

Doctor visits are reported with several days of lag, so estimates for a given date of service typically become available 3 to 7 days later.

Insurance claims experience substantial backfill over several weeks as providers and payers submit and adjust claims on varying schedules. Delphi runs daily updates across historical dates to incorporate late-arriving records.

Estimates for the most recent 5 to 7 days change significantly across subsequent revisions, often showing median shifts of 10 percent or more. Data points older than 50 days are generally stable, with subsequent median revisions under 1 percent. Delphi documented the empirical behavior of this backfill process in a [blog post on outpatient claims backfill](https://delphi.cmu.edu/blog/2020/11/05/a-syndromic-covid-19-indicator-based-on-insurance-claims-of-outpatient-visits/#backfill).

---

## Source and Licensing

De-identified medical billing claims contributed by Delphi health system partners. This dataset is made available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
