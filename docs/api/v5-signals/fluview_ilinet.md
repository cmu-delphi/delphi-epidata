---
title: FluView ILINet Outpatient Illness
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 10
---

# FluView ILINet Outpatient Illness
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `fluview_ilinet` |
| **Data Source** | [U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet)](https://gis.cdc.gov/grasp/fluview/fluportaldashboard.html) via CDC FluView |
| **Geographic Levels** | `state`, `census_division`, `hhs`, `nation` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly (Fridays) |
| **Temporal Scope Start** | 1997-10-04 (1997w40); state-level data begins 2010-10-09 (2010w40) |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | `age_group` |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V3 [`fluview`](../fluview.md) endpoint. Age breakdowns are now queried using the `age_group` column, and signal names follow standard V5 conventions. See [Relationship to V3](#relationship-to-v3).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet), administered by the CDC, monitors outpatient visits for influenza-like illness across the United States. Approximately 3,000 healthcare providers (sentinel outpatient clinics, emergency departments, and family medicine practices) voluntarily report weekly summaries of total patient encounters and the number of patients presenting with symptoms meeting the standard ILI case definition.

The CDC defines influenza-like illness as a fever of 100°F (37.8°C) or higher accompanied by a cough or sore throat, without a known cause other than influenza. Delphi fetches ILINet data weekly from the CDC FluView Interactive portal. This dataset provides unweighted and population-weighted ILI visit percentages, ILI encounter counts by age group, and healthcare provider participation numbers.

For companion laboratory surveillance data, see [FluView Clinical Labs](fluview_resp_lab_clinical.md) and [FluView Public Health Labs](fluview_resp_lab_ph.md).

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `wili` | Influenza-like Illness | Percentage | Population-weighted percentage of outpatient visits with ILI. Available for `nation`, `hhs`, and `census_division`; suppressed at `state`. |
| `ili` | Influenza-like Illness | Percentage | Unweighted percentage of outpatient visits with ILI ($100 \cdot \frac{\text{num\_ili}}{\text{num\_patients}}$). |
| `num_ili` | Influenza-like Illness | Count | Weekly count of outpatient visits presenting with ILI. Stratified by `age_group`. |
| `num_providers` | — | Count | Number of healthcare providers reporting to ILINet during the week. |
| `num_patients` | — | Count | Total outpatient visits across all conditions recorded by reporting providers. |

---

## Estimation

### Metric Definition

Let $$Y_{it}$$ be the count of ILI encounters (`ilitotal`) in location $$i$$ during week $$t$$, and let $$N_{it}$$ be the total patient visits (`total_patients`).

- Unweighted ILI (`ili`) is the percentage of outpatient visits meeting the ILI case definition:

  $$
  \text{ILI}_{it} = 100 \cdot \frac{Y_{it}}{N_{it}}
  $$

- Weighted ILI (`wili`) is a population-weighted average of state-level percentages calculated by the CDC for multi-state regions:

  $$
  \text{wILI}_{rt} = \sum_{s \in r} \left( \text{ILI}_{st} \cdot \frac{P_s}{P_r} \right)
  $$

  where $$P_s$$ is the population of state $$s$$ and $$P_r$$ is the total population of region $$r$$. State-level population weights are not applicable, so the CDC does not compute state-level `wili`. Delphi excludes `wili` at the state level.

- Counts (`num_ili`, `num_patients`, `num_providers`) pass through directly from the CDC. `num_ili` is also available by age stratum.

### Smoothing

All signals are unsmoothed discrete 7-day weekly totals or ratios.

### Uncertainty

Uncertainty intervals and standard errors are not published by the CDC for ILINet data. The dataset includes `num_patients` and `num_providers` as direct measures of reporting volume and network coverage.

### Temporal Handling

Observations cover 7-day epidemiological weeks defined by the CDC's Morbidity and Mortality Weekly Report (MMWR). An MMWR week runs from Sunday through Saturday, standardizing public health reporting across calendar years.

- `reference_time` is the Saturday week-ending date of the surveillance week.
- `report_time` is the release date when Delphi ingested the weekly CDC snapshot. Revisions update past weeks as delayed provider reports arrive.

### Geographic Handling

All four geographic levels (`nation`, `hhs`, `census_division`, `state`) are computed natively by the CDC and ingested directly without regional aggregation (`fill_method = 'source'`).

Under `state`, the CDC publishes standard states, territories, and two separate New York records: New York City (`nyc`) and New York State excluding NYC (`ny_minus_nyc`). Delphi reconstructs a combined statewide `ny` record per week (`fill_method = 'nyc_plus_ny_minus_nyc'`) when both components are present and non-null. Raw counts are summed directly:

$$
Y_{\text{NY}, t} = Y_{\text{NYC}, t} + Y_{\text{NY-NYC}, t}
$$

The unweighted percentage (`ili`) is recomputed as a pooled ratio:

$$
\text{ILI}_{\text{NY}, t} = 100 \cdot \frac{Y_{\text{NYC}, t} + Y_{\text{NY-NYC}, t}}{N_{\text{NYC}, t} + N_{\text{NY-NYC}, t}}
$$

Weighted ILI (`wili`) is omitted at the state level because the CDC only calculates population-weighted averages across multi-state regions. 

---

## Relationship to V3

This source reproduces the legacy V3 `fluview` endpoint (`https://api.delphi.cmu.edu/epidata/fluview/`).

In V3, age-stratified counts were flattened into separate columns (`num_age_0` through `num_age_5`). In V5, age stratification is organized under the `age_group` key column of `num_ili`.

| V3 Field | V5 Signal | Extra Key (`age_group`) | Notes |
| :--- | :--- | :--- | :--- |
| `wili` | `wili` | `all` | State-level `wili` excluded in V5 |
| `ili` | `ili` | `all` | Exact match |
| `num_ili` | `num_ili` | `all` | Exact match for total ILI encounters |
| `num_providers` | `num_providers` | `all` | Exact match |
| `num_patients` | `num_patients` | `all` | Exact match |
| `num_age_0` | `num_ili` | `0-4` | Mapped to `0-4` age stratum |
| `num_age_1` | `num_ili` | `5-24` | Mapped to `5-24` age stratum |
| `num_age_2` | `num_ili` | `25-64` | Historical overlapping age bucket |
| `num_age_3` | `num_ili` | `25-49` | Mapped to `25-49` age stratum |
| `num_age_4` | `num_ili` | `50-64` | Mapped to `50-64` age stratum |
| `num_age_5` | `num_ili` | `65+` | Mapped to `65+` age stratum |

What changed in V5:

- **Age Stratification via Keys.** Rather than maintaining separate column names, all age groups are unified under the `num_ili` indicator and categorized using `extra_keys`.
- **Exclusion of State-Level `wili`.** The legacy V3 pipeline coalesced unweighted `ili` into `wili` when weighted ILI was missing at the state level. V5 eliminates this conflation: `wili` is published only where the CDC computes it (national, HHS, and census divisions).
- **Discontinuation of Pre-2010 Imputation.** The legacy V3 endpoint provided sensor-fusion regression estimates for state-level data prior to 2010w40. V5 serves direct CDC observations without synthetic historical imputation.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the indicator (`wili`, `ili`, `num_ili`, `num_providers`, `num_patients`). |
| `report_time` | Primary Key | date | The date Delphi ingested the CDC weekly file (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state`, `census_division`, `hhs`, `nation`). |
| `geo_value` | Primary Key | string | Location code (e.g., `us`, `1`–`10`, `1`–`9`, `pa`, `ny`, `nyc`, `ny_minus_nyc`). |
| `age_group` | Primary Key | string | Age group category (see Extra Keys below). |
| `fill_method` | Primary Key | string | `source` for directly ingested rows; `nyc_plus_ny_minus_nyc` for reconstructed statewide NY. |
| `reference_time` | Primary Key | date | Saturday week-ending date of the surveillance week (`YYYY-MM-DD`). |
| `value` | Value Column | float | Percentage or patient/provider count. |

### Extra Keys

The `age_group` key applies to `num_ili` and accepts the following values:

- `all`: Total ILI encounters across all ages (matches `num_ili` total).
- `0-4`: Patients aged 0 to 4 years.
- `5-24`: Patients aged 5 to 24 years.
- `25-49`: Patients aged 25 to 49 years.
- `50-64`: Patients aged 50 to 64 years.
- `65+`: Patients aged 65 years and older.
- `25-64`: Coarser historical age band used prior to the 25–49 and 50–64 split.

For all other signals (`wili`, `ili`, `num_providers`, `num_patients`), `age_group` is always set to `all`.

---

## Missingness & Privacy

- Weighted ILI (`wili`) is omitted at the state level because the CDC only calculates population-weighted averages for multi-state regions.
- ILINet is a voluntary reporting network. If no providers report within a jurisdiction during a week, that observation is omitted from the dataset rather than recorded as zero.

---

## Limitations

- ILI measures symptoms (fever with cough or sore throat) rather than laboratory-confirmed influenza. Other circulating respiratory pathogens, including COVID-19 and RSV, contribute to ILI counts.
- Provider participation varies across states and clinical specialties. Jurisdictions with more pediatric practices often report higher baseline ILI rates.
- Shifts in healthcare-seeking behavior, insurance coverage, and telehealth usage can influence visit volumes independently of disease spread.

---

## Lag & Backfill

- Initial weekly data is published by the CDC on Fridays, six days after the surveillance week ends.
- Backfill is common during the first two to four weeks as participating clinics submit delayed reports. Revisions can be accessed via the `/archive/` endpoint or by querying with `snapshot_date`.

---

## Source and Licensing

ILINet data is published by the CDC Outpatient Influenza-like Illness Surveillance Network. The data is in the [public domain](https://www.usa.gov/government-works).
