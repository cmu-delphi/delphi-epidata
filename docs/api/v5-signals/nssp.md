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
| **Geographic Levels** | `nation`, `state`, `hhs`, `census_division`, `census_region`, `hrr`, `msa`, `county`, `hsa_nci` |
| **Temporal Granularity** | Weekly, week ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2022-10-01 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V4 [`nssp`](../covidcast-signals/nssp.md) source with the same signal definitions. V5 adds finer geographies, exposes the aggregation choice through `fill_method`, adds an acute respiratory illness signal, and serves revision history through the [`/archive/` and `/snapshot/`](../v5_api_queries.md) endpoints. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Syndromic Surveillance Program tracks the share of emergency department (ED) visits associated with respiratory illness across participating facilities in the United States. The CDC publishes weekly percentages for COVID-19, influenza, RSV, a combined category, and broader acute respiratory illness (ARI). Delphi ingests the CDC Socrata release, with the [CDC forecast-hub GitHub mirror](https://github.com/CDCgov/covid19-forecast-hub/tree/main/auxiliary-data/nssp-raw-data) as a fallback when Socrata is unavailable.

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

The `smoothed_` signals are a trailing 3-week mean computed by the CDC and passed through unchanged.

### Temporal Handling

Each value covers one epiweek, labelled by its Saturday week-ending date.

### Geographic Handling

The CDC reports values natively for the nation (`nation`), counties (`county`), and NCI-modified Health Service Areas (`hsa_nci`), which Delphi reads directly. State values come from a separate CDC reporting path and are served as published.

Delphi derives the remaining levels as a population-weighted mean of native values. State records aggregate into HHS regions, census regions, and census divisions. County records aggregate into HRRs and MSAs. For target geography $$g$$ composed of sub-units $$c$$ with 2020 US Census population $$w_c$$ and reported percentage $$p_c$$,

$$
\hat{p}_g = \frac{\sum_{c \in g} w_c\, p_c}{\sum_{c \in g} w_c}.
$$

Because values are percentages rather than counts, missing sub-units are handled explicitly through `fill_method`:
- `fill_zero`: missing sub-units contribute $$p_c = 0$$ while retaining their population weight in the denominator.
- `fill_ave`: missing sub-units are excluded from both numerator and denominator.
- `source`: native reported values.

---

## Relationship to V4

The V4 `nssp` source used the same CDC dataset and the same signal definitions, so the values are directly comparable. What changed in V5:

- V4 served nation, HHS regions, and state. V5 adds county, `hsa_nci`, HRR, MSA, census region, and census division.
- V4 baked a single treatment of missing sub-units into each published value. V5 computes both and lets the caller pick with `fill_method` (`source`, `fill_zero`, `fill_ave`).
- V5 adds `pct_ed_visits_ari`. The COVID-19, influenza, RSV, and combined pairs are unchanged.
- V5 exposes the full revision history through `/archive/` and point-in-time reads through `/snapshot/`.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`nation`, `state`, `hhs`, `census_division`, `census_region`, `hrr`, `msa`, `county`, `hsa_nci`). |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., `tx` for Texas, `06001` for Alameda County). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation (`source`, `fill_zero`, or `fill_ave`). |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation, labeled by Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded measurement. |

### Fill methods

| Value | Meaning |
| :--- | :--- |
| `source` | Native CDC value for nation, county, and HSA, and the state pass-through. |
| `fill_zero` | Derived geography with missing sub-units counted as zero. |
| `fill_ave` | Derived geography averaged over reporting sub-units only. |

---

## Missingness & Privacy

The CDC suppresses facility and county values with low visit volumes to protect patient privacy. Suppressed values are treated as missing.

Unobserved values also occur from facility non-reporting, uneven rural participation, states that do not report county-level data, and literal zeros reported by Wyoming (converted to missing during ingestion).

Missing sub-units during spatial roll-ups are handled according to the selected `fill_method`, as described under [Geographic Handling](#geographic-handling).

---

## Limitations

Percentages reflect visits at facilities reporting to NSSP rather than all facilities in a region. Diagnoses reflect clinical coding at discharge without mandatory laboratory confirmation. In addition, population-weighted spatial aggregation assumes ED visits scale proportionally with resident population.

---

## Lag & Backfill

The weekly file publishes Friday mornings for the preceding epiweek. Historical weeks revise as facilities join the network and submit backlogged data, which can affect series for up to two years.

---

## Source and Licensing

This dataset originates from the CDC [National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) and is published under [Public Domain U.S. Government](https://www.usa.gov/government-works) terms.
