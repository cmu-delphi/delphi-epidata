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
| **Temporal Granularity** | Daily, by date of service |
| **Reporting Cadence** | Daily |
| **Temporal Scope Start** | 2019-10-01 |
| **Date of Last Revision** | Rolling lookback window (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | None |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

> **Reproduces V4.** This source reproduces the legacy V4 COVIDcast [`hospital-admissions`](../covidcast-signals/hospital-admissions.md) source. It keeps the same claims feed and the claims-only definition of a respiratory admission, but replaces the day-of-week and backfill adjustments with a plain 7-day windowed ratio, adds influenza and other-ARI signals, and serves revision history through the [`/archive/` and `/snapshot/`](../v5_api_queries.md) endpoints. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

This source measures the share of inpatient hospital admission claims that carry a respiratory illness diagnosis. It is built from de-identified medical billing claims contributed by Delphi's health system partners and covers COVID-19, influenza, and other acute respiratory illness (ARI). The data is distributed under CC BY 4.0.

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `claims_inpatient_adm_pct_claims_covid` | COVID-19 | Percentage, 7-day window | Share of inpatient admission claims with a COVID-19 diagnosis. |
| `claims_inpatient_adm_pct_claims_flu` | Influenza | Percentage, 7-day window | Share of inpatient admission claims with a confirmed influenza diagnosis. |
| `claims_inpatient_adm_pct_ari_other` | Other ARI | Percentage, 7-day window | Share of inpatient admission claims with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. Published from 2022-08-01. |

---

## Estimation

### Geographic Aggregation

Claims arrive keyed to county (`county`) and Hospital Referral Region (`hrr`). During normalization, counts are summed across patient age groups, and the free-text HRR name is dropped because the same HRR is occasionally labelled with two different names in the raw feed.

County counts are then crosswalked into the remaining levels (`msa`, `state`, `hhs`, `census_division`, `census_region`, `nation`) as a population-weighted sum, using the 2020 county population crosswalk. HRR values are served as reported. All aggregation happens on the raw counts, before the 7-day sum.

### Temporal Handling

Observations are keyed by the clinical date of service. Claims dated to the first calendar day of any month are dropped, because submission batching inflates that day. Service dates before 2019-10-01, and service dates in the future, are also dropped.

### Smoothing

For each geography, a 7-day trailing sum is taken of every diagnosis count and of the total claim count. The window must contain at least 5 of 7 days, otherwise no value is produced for that day.

### Metric Definition

For a location $$i$$ and service date $$t$$, let $$W_t = \{t-6, \dots, t\}$$ be the trailing 7-day window, $$N_{is}$$ the total admission claims on day $$s$$, and $$Y^{k}_{is}$$ the claims carrying diagnosis group $$k$$. The published percentage is

$$
\hat{p}^{\,k}_{it} = 100 \cdot \frac{\sum_{s \in W_t} Y^{k}_{is}}{\sum_{s \in W_t} N_{is}},
$$

computed only when at least 5 days contribute and $$\sum_{s \in W_t} N_{is} \ge 100$$. This is a ratio of summed counts, equivalently a denominator-weighted average of the daily rates, the same form used for laboratory test positivity.

The diagnosis groups are ICD-filtered counts from the raw feed:

- COVID-19 (`pct_claims_covid`): the COVID-like count. Before 2021-06-01 it also includes the unspecified lower-respiratory count, which tracked COVID-19 closely while specific codes were not yet in wide use. From 2021-06-01 on, only the COVID-like count is used.
- Influenza (`pct_claims_flu`): the confirmed-influenza count.
- Other ARI (`pct_ari_other`): the mixed and unspecified lower-respiratory counts combined, from 2022-08-01.

### Uncertainty

This source publishes no standard errors, sample sizes, or confidence intervals.

---

## Relationship to V4

The V4 `hospital-admissions` source used the same health system claims and published a single COVID-19 percentage, through `smoothed_covid19_from_claims` and its day-of-week-adjusted twin `smoothed_adj_covid19_from_claims`. Three things changed in V5.

The estimator is now a plain windowed ratio. V4 applied a Jeffreys-style $$\frac{Y + 0.5}{N + 1}$$ correction, a backwards-padding step that widened the averaging window until a 500-visit threshold was met, a Poisson day-of-week adjustment, and a Gaussian linear smoother. V5 replaces all of it with the 7-day trailing sum above.

The signal set is broader. V5 adds influenza and other-ARI percentages next to COVID-19, and drops the combined electronic-record-and-claims variant that V4 froze in 2020.

Coverage and revisions are wider and explicit. V4 served nation, state, county, HRR, and MSA. V5 adds HHS regions, census divisions, and census regions, reprocesses a trailing lookback window on every run, and exposes the full revision history through `/archive/`.

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic level (`nation`, `state`, `hhs`, `census_division`, `census_region`, `msa`, `hrr`, `county`). |
| `geo_value` | Primary Key | Geographic code (e.g. `pa` for Pennsylvania, `42003` for Allegheny County). |
| `fill_method` | Primary Key | Aggregation path. A single value for this source (see below). |
| `time_value` | Primary Key | Date of service (`YYYY-MM-DD`). |
| `value` | Value Column | Percentage of claims, 0 to 100. |

### Fill methods

Every row is produced through the one population-weighted crosswalk path described under [Geographic Aggregation](#geographic-aggregation). There are no zero-fill or average-fill variants, so `fill_method` does not select among alternatives for this source.

### Example Query

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=claims_inpatient&signal=claims_inpatient_adm_pct_claims_covid&geo_type=state
```

---

## Missingness & Privacy

For stability and privacy, any geography and date whose 7-day summed denominator is below 100 claims is dropped and does not appear in the output.

---

## Limitations

Claims cover the insured patients of participating providers and do not represent uninsured people. Provider and payer submission schedules vary, so counts for the most recent days are incomplete and revise upward. Local differences in coding practice mean levels are not always comparable across locations.

---

## Lag & Backfill

Claims typically arrive 3 to 7 days after the date of service. Delphi runs daily and reprocesses a rolling lookback window, so late-arriving and corrected claims are folded into earlier dates.
