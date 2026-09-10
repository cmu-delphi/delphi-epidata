---
title: NSSP ED Visits
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 1
---

# NSSP Emergency Department Visits
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nssp` |
| **Data Source** | [National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) via [CDC Socrata](https://data.cdc.gov/Public-Health-Surveillance/NSSP-Emergency-Department-Visit-Trajectories-by-S/rdmq-nq56) |
| **Geographic Levels** | `county`, `hsa_nci`, `hrr`, `msa`, `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2022-10-01 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V4 [`nssp`](../covidcast-signals/nssp.md) source with the same signal definitions plus an additional acute respiratory illness signal. V5 adds census division and census region levels, exposes the aggregation choice through `fill_method`, and serves revision history through the [`/archive/` and `/snapshot/`](../v5_api_queries.md) endpoints. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Syndromic Surveillance Program (NSSP) tracks the share of emergency department (ED) visits associated with respiratory illness across participating facilities in the United States. The CDC publishes weekly percentages for COVID-19, influenza, Respiratory syncytial virus (RSV), a combined category of the previous three diseases listed, and broader acute respiratory illness (ARI). Delphi ingests the CDC Socrata release, with the [CDC forecast-hub GitHub mirror](https://github.com/CDCgov/covid19-forecast-hub/tree/main/auxiliary-data/nssp-raw-data) as a fallback when Socrata is unavailable.

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `pct_ed_visits_covid` | COVID-19 | Percentage | Share of ED visits with a discharge diagnosis of COVID-19. |
| `pct_ed_visits_influenza` | Influenza | Percentage | Share of ED visits with a discharge diagnosis of influenza. |
| `pct_ed_visits_rsv` | RSV | Percentage | Share of ED visits with a discharge diagnosis of RSV. |
| `pct_ed_visits_combined` | Combined | Percentage | Share of ED visits with a discharge diagnosis of COVID-19, influenza, or RSV. |
| `pct_ed_visits_ari` | ARI | Percentage | Share of ED visits with a discharge diagnosis of acute respiratory illness. |
| `smoothed_pct_ed_visits_covid` | COVID-19 | Percentage, 3-week mean | Trailing 3-week mean of `pct_ed_visits_covid`. |
| `smoothed_pct_ed_visits_influenza` | Influenza | Percentage, 3-week mean | Trailing 3-week mean of `pct_ed_visits_influenza`. |
| `smoothed_pct_ed_visits_rsv` | RSV | Percentage, 3-week mean | Trailing 3-week mean of `pct_ed_visits_rsv`. |
| `smoothed_pct_ed_visits_combined` | Combined | Percentage, 3-week mean | Trailing 3-week mean of `pct_ed_visits_combined`. |

---

## Estimation

### Metric Definition

Each raw signal represents the percentage of total emergency department (ED) visits diagnosed with the specified condition.

### Smoothing

The `smoothed_*` signals are a trailing 3-week mean (the average of the reference week and the two preceding weeks) computed by the CDC and passed through unchanged.

### Temporal Handling

Each value covers a 7-day week (Sunday through Saturday), labelled by its Saturday week-ending date.

### Geographic Handling

The CDC reports values natively for the nation (`nation`), states (`state`), counties (`county`), and [NCI-modified Health Service Areas](https://seer.cancer.gov/seerstat/variables/countyattribs/hsa.html) (`hsa_nci`), which Delphi reads directly. Within the dataset, state values are aggregated by the CDC, and are served as published.

Delphi derives the remaining levels as a population-weighted mean of native values. State records aggregate into Department of Health and Human Services (HHS) regions, census divisions, and census regions. County records aggregate into Hospital Referral Regions (HRRs) and Metropolitan Statistical Areas (MSAs). For target geography $$g$$ composed of sub-units $$c$$ with 2020 US Census population $$w_c$$ and reported percentage $$p_c$$,

$$
\hat{p}_g = \frac{\sum_{c \in g} w_c\, p_c}{\sum_{c \in g} w_c}.
$$

Because values are percentages rather than counts, missing sub-units are handled explicitly through `fill_method`:
- `fill_zero`: missing sub-units contribute $$p_c = 0$$ while retaining their population weight in the denominator.
- `fill_ave`: missing sub-units are excluded from both numerator and denominator.
- `source`: native reported values.

---

## Relationship to V4

The V4 `nssp` source published ED visit percentages for nation, state, county, HSA, HRR, MSA, and HHS regions. What changed in V5:

- **Expanded Geographies.** V5 adds census division and census region levels (aggregated from state records).
- **Aggregation Choice.** V4 published derived aggregations with a single fixed treatment of missing sub-units. V5 computes both methods and lets the caller choose via `fill_method`. See [Geographic Handling](#geographic-handling).
- **New Signal.** V5 adds `pct_ed_visits_ari`. The COVID-19, influenza, RSV, and combined pairs are unchanged.
- **Revision History.** V5 exposes the full revision history through `/archive/` and point-in-time reads through `/snapshot/`.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`county`, `hsa_nci`, `hrr`, `msa`, `state`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., `tx` for Texas, `06001` for Alameda County). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation (`source`, `fill_zero`, or `fill_ave`). |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation, labeled by Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded percentage of ED visits. |

---

## Missingness & Privacy

The CDC suppresses facility and county values with low visit volumes to protect patient privacy. Suppressed values are treated as missing.

Unobserved values also occur from facility non-reporting, uneven rural participation, states that do not report county-level data, and literal zeros reported by Wyoming (converted to missing during ingestion).

Missing sub-units during geographic aggregation are handled according to the selected `fill_method`, as described under [Geographic Handling](#geographic-handling).

---

## Limitations

Percentages reflect visits at facilities reporting to NSSP rather than all facilities in a region. Diagnoses reflect clinical coding at discharge without mandatory laboratory confirmation. In addition, population-weighted spatial aggregation assumes ED visits scale proportionally with resident population.

---

## Lag & Backfill

The weekly file publishes on Friday mornings, covering the week that ended the previous Saturday. Historical weeks continue to revise as facilities join the network and as facilities submit backlogged or corrected reports, which can affect series for up to two years.

---

## Source and Licensing

This dataset originates from the CDC [National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) and is published under [Public Domain U.S. Government](https://www.usa.gov/government-works) terms.
