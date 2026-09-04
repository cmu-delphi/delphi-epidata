---
title: Outpatient Claims
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 6
---

# Outpatient Claims (V5)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `claims_outpatient` |
| **Data Source** | De-identified medical billing claims from Delphi health system partners |
| **Geographic Levels** | `nation`, `state`, `hhs`, `census_division`, `census_region`, `msa`, `hrr`, `county` |
| **Temporal Granularity** | Daily, by date of service |
| **Reporting Cadence** | Daily |
| **Temporal Scope Start** | 2019-10-01 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

> This source reproduces the legacy V4 [`doctor-visits`](../covidcast-signals/doctor-visits.md) source. It keeps the same claims feed but replaces the COVID-like illness model and its adjustments with a plain 7-day windowed ratio, splits the metric into per-pathogen signals, and serves revision history through the [`/archive/` and `/snapshot/`](../v5_api_queries.md) endpoints. See [Relationship to V4](#relationship-to-v4).
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
| `claims_outpatient_ov_pct_ari_other` | Other ARI | Percentage, 7-day window | Share of outpatient visit claims with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. Published from 2022-08-01. |

---

## Estimation

### Geographic Aggregation

Claims arrive at two native geographic levels: county (`county`) and Hospital Referral Region (`hrr`). HRR values are served as reported. All other geographic levels (`msa`, `state`, `hhs`, `census_division`, `census_region`, `nation`) are aggregated from county counts using a 2020 US Census population-weighted crosswalk. Aggregation is performed on raw daily counts before computing 7-day sums.

### Temporal Handling

Dates refer to the clinical date of service. Claims dated to the first calendar day of any month are dropped, because submission batching inflates that day. Service dates before 2019-10-01, and service dates in the future, are also dropped.

### Smoothing

For each geography, a 7-day trailing sum is taken of every diagnosis count and the total claim count. The window must contain at least 5 of 7 days to produce a value.

### Metric Definition

For location $$i$$ and service date $$t$$, let $$W_t = \{t-6, \dots, t\}$$ be the trailing 7-day window, $$N_{is}$$ total visit claims on day $$s$$, and $$Y_{is}^k$$ claims carrying diagnosis group $$k$$. The published percentage is

$$
\hat{p}_{it}^k = 100 \cdot \frac{\sum_{s \in W_t} Y_{is}^k}{\sum_{s \in W_t} N_{is}},
$$

computed only when at least 5 days contribute and $$\sum_{s \in W_t} N_{is} \ge 100$$.

The diagnosis groups are ICD-filtered counts from the raw feed:

- COVID-19 (`pct_claims_covid`): the COVID-like count. Before 2021-06-01 it also includes the unspecified lower-respiratory count, which tracked COVID-19 closely while specific codes were not yet in wide use. From 2021-06-01 on, only the COVID-like count is used.
- Influenza (`pct_claims_flu`): the confirmed-influenza count.
- Other ARI (`pct_ari_other`): the mixed and unspecified lower-respiratory counts combined, from 2022-08-01.

---

## Relationship to V4

The V4 `doctor-visits` source used the same outpatient claims and published a single COVID-like illness (CLI) percentage, through `smoothed_cli` and its day-of-week-adjusted twin `smoothed_adj_cli`.

The estimator is now a plain windowed ratio. V4 estimated CLI as an excess over expected respiratory illness, roughly $$Y^{\text{covid-like}} + \big(Y^{\text{flu-like}} + Y^{\text{mixed}} - Y^{\text{flu}}\big)$$ over the denominator, then applied backwards padding to a 500-visit threshold, a Poisson day-of-week adjustment, and a Gaussian linear smoother. V5 uses the 7-day trailing ratio above, with no subtraction of influenza and no day-of-week or smoothing model.

The signal set is broader. V5 publishes COVID-19, influenza, and other-ARI percentages separately rather than one blended CLI signal.

Geographic coverage is broader. V4 served state, county, HRR, and MSA. V5 adds nation, HHS regions, census divisions, and census regions.

---

## Schema

### Columns

| Column | Key Type | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | Signal identifier. |
| `report_time` | Primary Key | date | Publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`nation`, `state`, `hhs`, `census_division`, `census_region`, `msa`, `hrr`, `county`). |
| `geo_value` | Primary Key | string | Geographic code (e.g. `fl` for Florida, `06001` for Alameda County). |
| `fill_method` | Primary Key | string | Aggregation path, always `source` for this source. |
| `reference_time` | Primary Key | date | Date of service (`YYYY-MM-DD`). |
| `value` | Value Column | float | Percentage of claims, 0 to 100. |

### Fill methods

This source uses a single aggregation path described under [Geographic Aggregation](#geographic-aggregation). The `fill_method` column is always `source`.

### Example Query

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=claims_outpatient&signal=claims_outpatient_ov_pct_claims_covid&geo_type=state
```

---

## Missingness & Privacy

Locations and dates with fewer than 100 total claims over the 7-day window are suppressed for privacy and omitted from publication.

Unobserved dates or geographies without reporting claims produce no records

---

## Limitations

Claims cover the insured patients of participating providers and do not represent uninsured people. Provider and payer submission schedules vary, so counts for the most recent days are incomplete and revise upward. Visit-seeking behaviour rises around major holidays, which can push the COVID-19 share up without a real change in illness. Local differences in coding practice mean levels are not always comparable across locations.

---

## Lag & Backfill

Claims typically arrive 3 to 7 days after the date of service. Delphi runs daily updates across a rolling lookback window to incorporate late-arriving and revised claims.
