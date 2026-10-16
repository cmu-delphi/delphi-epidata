---
title: NREVSS Respiratory Viruses
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 13
---

# National Respiratory and Enteric Virus Surveillance System (NREVSS)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nrevss` |
| **Data Source** | [CDC National Respiratory and Enteric Virus Surveillance System (NREVSS)](https://data.cdc.gov/Laboratory-Surveillance/Percent-positivity-of-respiratory-viruses-by-nucle/rgnm-fkqb/about_data) |
| **Geographic Levels** | `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Weekly, week ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2019-07-06 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain U.S. Government](https://www.usa.gov/government-works) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

This source measures laboratory testing volumes and percent positivity for non-influenza respiratory diseases reported weekly by clinical and public health laboratories across the United States.

Data is collected by the [National Respiratory and Enteric Virus Surveillance System (NREVSS)](https://www.cdc.gov/nrevss/php/dashboard/index.html), a laboratory-based surveillance network coordinated by the CDC National Center for Immunization and Respiratory Diseases (NCIRD). The network includes more than 450 laboratories across all 50 states, the District of Columbia, Puerto Rico, and the U.S. Virgin Islands.
Participation is voluntary.

Data in this source is reported for seven respiratory virus groups:

- Adenovirus (`adv`)
- Human Coronavirus (`hcov`)
- Human Metapneumovirus (`hmpv`)
- Human Parainfluenza Virus (`hpiv`)
- Enterovirus / Rhinovirus (`evrv`)
- Respiratory Syncytial Virus (`rsv`)
- SARS-CoV-2 (`covid`)

While NREVSS also collects influenza laboratory tests, influenza data is not published in this Socrata dataset. Influenza laboratory surveillance from NREVSS is reported through CDC FluView and documented separately in Delphi's [`fluview_resp_lab_clinical`](fluview_resp_lab_clinical.md) and [`fluview_resp_lab_ph`](fluview_resp_lab_ph.md) endpoints.

Signals report combined pathogen totals. For human parainfluenza and seasonal coronavirus, Delphi publishes the CDC's combined totals (`hpiv` and `hcov`) rather than individual subtypes.

---

## Indicators (Signals)

Indicators in this source combine a pathogen prefix with a metric suffix in the format `<pathogen>_<metric>`.
Only RSV and SARS-CoV-2 are available for state-level (and derived) metrics, `tests_3wav`, `positive_tests_5wav`, `pct_positive_3wav`, `pct_positive_est`.
All other pathogen-metric combinations exist.

### Pathogen Prefixes

| Prefix | Pathogen | Geographic Availability | Notes |
| :--- | :--- | :--- | :--- |
| `adv` | Adenovirus | `hhs`, `nation` | - |
| `hcov` | Human coronavirus | `hhs`, `nation` | Combined seasonal coronavirus types (229E, HKU1, NL63, OC43) |
| `hmpv` | Human metapneumovirus | `hhs`, `nation` | - |
| `hpiv` | Human parainfluenza virus | `hhs`, `nation` | Combined human parainfluenza types (PIV 1–4) |
| `evrv` | Enterovirus / Rhinovirus | `hhs`, `nation` | Combined single diagnostic target for enteroviruses and rhinoviruses |
| `rsv` | Respiratory syncytial virus | `state`, `hhs`, `census_division`, `census_region`, `nation` | - |
| `covid` | SARS-CoV-2 | `state`, `hhs`, `census_division`, `census_region`, `nation` | - |

### Metric Suffixes

| Metric Suffix | Metric Type | Geographic Levels | Description |
| :--- | :--- | :--- | :--- |
| `tests` | Count | `hhs`, `nation` | Weekly count of total NAAT tests performed. Reported directly by CDC. |
| `positive_tests` | Count | `hhs`, `nation` | Weekly count of positive NAAT test detections. Reported directly by CDC. |
| `pct_positive` | Percentage | `hhs`, `nation` | Weekly percent test positivity ($$100 \cdot \frac{\text{positive\_tests}}{\text{tests}}$$). Reported directly by CDC. |
| `tests_3wav` | Count (smoothed) | `state`, `census_division`, `census_region` | 3-week centered moving average of total NAAT tests. Reported by CDC for `state`. Aggregated by Delphi to census regions and divisions. |
| `positive_tests_5wav` | Count (smoothed) | `state`, `census_division`, `census_region` | 5-week trailing moving average of positive NAAT detections. Reported by CDC for `state`. Aggregated by Delphi to census regions and divisions. |
| `pct_positive_3wav` | Percentage (smoothed) | `state`, `census_division`, `census_region` | 3-week centered moving average of percent test positivity. Reported by CDC for `state`. Aggregated by Delphi to census regions and divisions. |
| `pct_positive_est` | Percentage (estimate) | `state`, `census_division`, `census_region` | Estimated weekly percent test positivity derived by Delphi via deconvolution under smoothing assumptions. |

---

## Estimation

### Metric Definition

- **Percent positivity** (`pct_positive`) is the percentage of performed NAAT tests with positive detections ($$100 \cdot \frac{\text{positive\_tests}}{\text{tests}}$$).
- **Weekly counts** (`tests`, `positive_tests`) pass through directly from CDC as raw weekly test volumes and detections.

#### State Moving Averages (CDC)

At the state level, CDC publishes data only for RSV and SARS-CoV-2. CDC does not publish raw weekly counts or unwindowed weekly percentages. Instead, CDC reports:

- `tests_3wav` and `pct_positive_3wav`: 3-week centered moving averages of total tests and percent positivity (covering weeks $$t-1$$, $$t$$, and $$t+1$$). For the latest reported surveillance week, CDC computes a 2-week average of the current and prior week ($$t-1$$ and $$t$$) because the subsequent week has not yet occurred.
- `positive_tests_5wav`: 5-week trailing moving average of positive detections (covering weeks $$t-4$$ through $$t$$).

#### Weekly State Estimates

Because CDC reports state-level data only as moving averages, Delphi derives single-week estimates (`pct_positive_est`). For each contiguous run of reported weeks, Delphi solves a linear system under smoothing boundary assumptions to estimate the underlying weekly values.

To fully constrain the system and make it solvable, we make several assumptions.
For a contiguous run of reported weeks that includes the most-recently reported value, we assume that the first two values in the run are equal.
For a run of reported weeks that doesn't include the most recent value, we assume that the last three values are equal.

State series cover a rolling 105-week window, so the date where the leading assumption is used moves forward one week per release rather than staying fixed.

We also estimate unsmoothed weekly tests at the state level for internal use (geoaggregation via summing numerator and denominator counts).
To expand the period of time we can solve the system over, we impute missing values using a log-linear imputation strategy between available values.

Estimated values are bounded to valid ranges ($$\ge 0$$ for counts, $$[0, 100]$$ for percentages) and rounded to two decimal places to match source precision.

### Smoothing

- Moving averages at the state level (`tests_3wav`, `pct_positive_3wav`, `positive_tests_5wav`) are computed by CDC.
- Delphi computes a 3-week trailing moving average of positive test detections (`positive_tests_3wav`) for `hhs` and `nation` levels, averaging over the current and prior two weeks ($$t-2, t-1, t$$) with at least one reported week required in the window.

### Temporal Handling

Non-smoothed observations cover 7-day epidemiological weeks defined by the CDC Morbidity and Mortality Weekly Report (MMWR), running Sunday through Saturday.

- `reference_time` (`YYYY-MM-DD`) is the Saturday week-ending date of the surveillance week.
- `report_time` is the snapshot date when Delphi processed the data, in UTC.
- Data availability begins 2019-07-06 (MMWR week 2019w27).
- The CDC source updates provisional records for up to 2 years after initial publication. Delphi re-ingests and updates the entire 2-year revision window on every weekly pipeline run. Revisions are largest during the first 1 to 2 weeks following initial release as laboratory backlogs clear (>90% complete after 2 weeks), with smaller revisions occurring over subsequent months.

### Geographic Handling

Data arrives at three native geographic levels: `state`, `hhs`, and `nation`.

All native geographic levels are ingested directly without spatial imputation.

Delphi constructs two derived geographic levels from state-level values using geographic crosswalks: `census_division` and `census_region`.

For Census regions and divisions:

- Count-like averages and estimates (`tests_3wav`, `positive_tests_5wav`, `tests_est`) are aggregated by summing state values. Delphi produces these aggregates under two fill methods:
  - `fill_zero` treats unobserved states as 0.
  - `fill_ave` imputes unobserved states based on reporting states weighted by population.
- `pct_positive_est` is recomputed from the summed state estimate counts.
- `pct_positive_3wav` is recomputed as a population-weighted average of state 3-week centered moving average percentages. It is published only with `fill_ave` processing.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator (e.g. `covid_pct_positive`, `rsv_pct_positive_est`). |
| `report_time` | Primary Key | date | The date Delphi ingested the CDC weekly snapshot (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | string | Location code (e.g. `us`, `1`-`10`, 2-letter state postal code, census code). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation (`source`, `fill_zero`, or `fill_ave`). |
| `reference_time` | Primary Key | date | Saturday week-ending date of the surveillance week (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded measurement (count, percentage, moving average, or statistical estimate). |

---

## Missingness & Privacy

CDC suppresses positive test counts (numerators) between 1 and 4 to protect patient confidentiality. Denominators (total tests) are suppressed by association regardless of sample volume to prevent back-calculation of numerators.

In Delphi's normalized tables, censored values (missing or uncollected) are coerced to `NULL`.

Pathogens other than RSV and SARS-CoV-2 are unobserved at the state level. States that do not meet CDC laboratory participation criteria are omitted by CDC. Unobserved observations are omitted from Delphi's output tables.

---

## Limitations

NREVSS is a voluntary network of more than 450 clinical and public health laboratories. The number and composition of participating laboratories change over time, across seasons, and across states.

Data reflects clinical laboratory testing conducted primarily among symptomatic individuals seeking healthcare. Results are not representative of population-level infection prevalence or asymptomatic transmission.

NREVSS reports aggregate laboratory counts without patient demographic characteristics (age, sex, race, ethnicity) or clinical outcomes (hospitalization, death).

State-level surveillance is restricted to RSV and SARS-CoV-2. Adenovirus, HCoV, HMPV, HPIV, and EV/RV are only available at HHS regional and national levels.

---

## Lag & Backfill

Data is updated weekly by CDC, typically with a reporting lag of 1 to 2 weeks following the close of the surveillance week.

Data is provisional and subject to ongoing updates for up to 2 years. Testing data for the most recent 1 to 2 weeks is incomplete (>90% complete by week 2), while smaller revisions continue as delayed laboratory reports are processed. Delphi re-ingests and updates the full 2-year window.

Comparing values reported in consecutive reports in June 2026, we see O(1) revisions to counts going back at least 6 months.
We see O(10) revisions to counts going back 3 months, although percent positivity is fairly stable after a week.

---

## Source and Licensing

Data is coordinated by the CDC National Center for Immunization and Respiratory Diseases (NCIRD) via the National Respiratory and Enteric Virus Surveillance System (NREVSS).

The primary data feed is the CDC Socrata dataset [Percent positivity of respiratory viruses by nucleic acid amplification test (NAAT), NREVSS](https://data.cdc.gov/Laboratory-Surveillance/Percent-positivity-of-respiratory-viruses-by-nucle/rgnm-fkqb/about_data) (Dataset ID `rgnm-fkqb`). Interactive visualizations are available on the [CDC NREVSS Dashboard](https://www.cdc.gov/nrevss/php/dashboard/index.html).

This dataset is in the [public domain](https://www.usa.gov/government-works) as a work of the United States Government under 17 U.S.C. § 105.
