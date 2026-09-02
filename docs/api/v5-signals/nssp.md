---
title: NSSP ED Visits
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 1
---

# NSSP Emergency Department Visits (V5)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nssp` |
| **Data Source** | [National Syndromic Surveillance Program (NSSP)](https://www.cdc.gov/nssp/php/about/index.html) via [CDC Socrata](https://data.cdc.gov/Public-Health-Surveillance/NSSP-Emergency-Department-Visit-Trajectories-by-S/rdmq-nq56) |
| **Geographic Levels** | `nation`, `state`, `hhs`, `census_division`, `census_region`, `hrr`, `msa`, `county`, `hsa_nci` |
| **Temporal Granularity** | Weekly, week ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2022-10-01 |
| **Date of Last Revision** | Revised on backfill (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> **Reproduces V4.** This source reproduces the legacy V4 COVIDcast [`nssp`](../covidcast-signals/nssp.md) source with the same signal definitions. V5 adds finer geographies, exposes the aggregation choice through `fill_method`, adds an acute respiratory illness signal, and serves revision history through the [`/archive/` and `/snapshot/`](../v5_api_queries.md) endpoints. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Syndromic Surveillance Program tracks the share of emergency department (ED) visits associated with respiratory illness across participating facilities in the United States. The CDC publishes weekly percentages for COVID-19, influenza, RSV, a combined category, and broader acute respiratory illness (ARI). Delphi ingests the CDC Socrata release, with the [CDC forecast-hub GitHub mirror](https://github.com/CDCgov/covid19-forecast-hub/tree/main/auxiliary-data/nssp-raw-data) as a fallback when Socrata is unavailable.

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
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

### Geographic Aggregation

The CDC reports values natively for the nation (`nation`), counties (`county`), and NCI-modified Health Service Areas (`hsa_nci`), which Delphi reads directly. State values come from a separate CDC reporting path and are served as published, so a state value is not the mean of its counties.

Delphi derives the remaining levels as a population-weighted mean of the native values. State, HHS, census region, and census division are built from state records. HRR and MSA are built from county records. For a target geography $$g$$ made of sub-units $$c$$ with 2020 census population $$w_c$$ and reported percentage $$p_c$$,

$$
\hat{p}_g = \frac{\sum_{c \in g} w_c\, p_c}{\sum_{c \in g} w_c}.
$$

Because the source gives percentages rather than counts, a sub-unit that did not report has to be handled explicitly, and the choice is exposed as `fill_method`. With `fill_zero`, a missing sub-unit contributes $$p_c = 0$$ but still counts in the denominator. With `fill_ave`, a missing sub-unit is dropped from both sums, so $$\hat{p}_g$$ is the weighted mean over reporting sub-units only. Native values carry `fill_method = source`.

This weighting assumes ED visits scale with resident population, which need not hold. Denser areas tend to have more and larger EDs and easier access, so per-capita visit rates can differ between urban and rural counties.

### Temporal Handling

Each value covers one epiweek, labelled by its Saturday week-ending date.

### Smoothing

The `smoothed_` signals are a trailing 3-week mean, computed and published by the CDC and passed through unchanged. Each smoothed value therefore averages 3 weekly points, not 21 daily points.

### Uncertainty

This source publishes no standard errors, sample sizes, or confidence intervals.

---

## Relationship to V4

The V4 `nssp` source used the same CDC dataset and the same signal definitions, so the values are directly comparable. What changed in V5:

Geographies. V4 served nation, HHS regions, and state. V5 adds county, `hsa_nci`, HRR, MSA, census region, and census division.

Imputation is now a choice. V4 baked a single treatment of missing sub-units into each published value. V5 computes both and lets the caller pick with `fill_method` (`source`, `fill_zero`, `fill_ave`).

Signals. V5 adds `pct_ed_visits_ari`. The COVID-19, influenza, RSV, and combined pairs are unchanged.

Revisions. V5 exposes the full revision history through `/archive/` and point-in-time reads through `/snapshot/`.

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic level. |
| `geo_value` | Primary Key | Geographic code (e.g. `tx` for Texas, `06001` for Alameda County). |
| `fill_method` | Primary Key | Aggregation treatment of missing sub-units (`source`, `fill_zero`, `fill_ave`). |
| `time_value` | Primary Key | Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | Percentage of ED visits, 0 to 100. |

### Fill methods

| Value | Meaning |
| :--- | :--- |
| `source` | Native CDC value for nation, county, and HSA, and the state pass-through. |
| `fill_zero` | Derived geography with missing sub-units counted as zero. |
| `fill_ave` | Derived geography averaged over reporting sub-units only. |

### Example Query

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=nssp&signal=pct_ed_visits_covid&geo_type=state&fill_method=fill_ave
```

---

## Missingness & Privacy

The CDC suppresses values for facilities and counties with low visit volumes. Suppressed values are read as missing and then handled by the selected `fill_method` during aggregation. Wyoming reports a literal zero that the CDC uses as a missing marker, so those points are converted to missing during ingestion. County coverage is uneven and weaker in rural and low-population areas, and several states report no county-level data at all.

---

## Limitations

Percentages are computed over visits at facilities that report to NSSP, not all EDs in an area, and coverage has grown over time. Discharge diagnoses reflect clinical coding at discharge and are not confirmed by laboratory testing. Not every ED patient is tested for these conditions, so percentages can be biased downward. Low-volume counties occasionally report extreme values such as 50 or 100 percent by chance.

---

## Lag & Backfill

The weekly file is released on Friday mornings and adds the prior week. Historical weeks revise as facilities join the reporting network and their back data is added, which moves every geography that facility belongs to. Broader geographies revise more often for this reason, and revisions reaching back about two years have been seen.
