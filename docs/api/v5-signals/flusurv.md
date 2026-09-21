---
title: FluSurv-NET Hospitalizations
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 9
---

# FluSurv-NET Hospitalizations
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `flusurv` |
| **Data Source** | [CDC FluSurv-NET](https://www.cdc.gov/fluview/overview/influenza-hospitalization-surveillance.html) via [CDC GRASP API](https://gis.cdc.gov/Flu3/) |
| **Geographic Levels** | `state`, `flusurv_site` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2003-10-04 (2003w40) |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V3 [`flusurv`](../flusurv.md) endpoint. Each demographic and virus-specific rate is published as an individual signal under standard V5 conventions. See [Relationship to V3](#relationship-to-v3).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The Influenza Hospitalization Surveillance Network (FluSurv-NET), administered by the CDC, conducts population-based surveillance for laboratory-confirmed influenza-associated hospitalizations. FluSurv-NET covers select counties in Emerging Infections Program (EIP) states and additional Influenza Hospitalization Surveillance Project (IHSP) states, representing approximately 9 percent of the U.S. population.

Delphi fetches hospitalization data weekly from the CDC FluSurv-NET portal. The dataset reports hospitalization rates per 100,000 residents overall and stratified by age, race and ethnicity, sex, and influenza type (A and B).

---

## Indicators (Signals)

All signals represent weekly hospitalization rates per 100,000 residents.

### Overall and Virus Type

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `rate_overall` | Influenza | Rate per 100k | Overall weekly influenza hospitalization rate. |
| `rate_flu_a` | Influenza A | Rate per 100k | Weekly hospitalization rate for confirmed Influenza A infections. |
| `rate_flu_b` | Influenza B | Rate per 100k | Weekly hospitalization rate for confirmed Influenza B infections. |

### Age Strata

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `rate_age_0` | Influenza | Rate per 100k | Weekly rate for ages 0–4 years. |
| `rate_age_1` | Influenza | Rate per 100k | Weekly rate for ages 5–17 years. |
| `rate_age_2` | Influenza | Rate per 100k | Weekly rate for ages 18–49 years. |
| `rate_age_3` | Influenza | Rate per 100k | Weekly rate for ages 50–64 years. |
| `rate_age_4` | Influenza | Rate per 100k | Weekly rate for ages 65 years and older. |
| `rate_age_5` | Influenza | Rate per 100k | Weekly rate for ages 65–74 years. |
| `rate_age_6` | Influenza | Rate per 100k | Weekly rate for ages 75–84 years. |
| `rate_age_7` | Influenza | Rate per 100k | Weekly rate for ages 85 years and older. |
| `rate_age_0tlt1` | Influenza | Rate per 100k | Weekly rate for infants under 1 year (<1 yr). |
| `rate_age_1t4` | Influenza | Rate per 100k | Weekly rate for ages 1–4 years. |
| `rate_age_5t11` | Influenza | Rate per 100k | Weekly rate for ages 5–11 years. |
| `rate_age_12t17` | Influenza | Rate per 100k | Weekly rate for ages 12–17 years. |
| `rate_age_18t29` | Influenza | Rate per 100k | Weekly rate for ages 18–29 years. |
| `rate_age_30t39` | Influenza | Rate per 100k | Weekly rate for ages 30–39 years. |
| `rate_age_40t49` | Influenza | Rate per 100k | Weekly rate for ages 40–49 years. |
| `rate_age_gte75` | Influenza | Rate per 100k | Weekly rate for ages 75 years and older. |
| `rate_age_lt18` | Influenza | Rate per 100k | Weekly rate for pediatric populations (<18 years). |
| `rate_age_gte18` | Influenza | Rate per 100k | Weekly rate for adult populations (18 years and older). |

### Race, Ethnicity, and Sex

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `rate_race_white` | Influenza | Rate per 100k | Weekly rate for White individuals. |
| `rate_race_black` | Influenza | Rate per 100k | Weekly rate for Black or African American individuals. |
| `rate_race_hisp` | Influenza | Rate per 100k | Weekly rate for Hispanic or Latino individuals. |
| `rate_race_asian` | Influenza | Rate per 100k | Weekly rate for Asian or Pacific Islander individuals. |
| `rate_race_natamer` | Influenza | Rate per 100k | Weekly rate for American Indian or Alaska Native individuals. |
| `rate_sex_male` | Influenza | Rate per 100k | Weekly rate for male individuals. |
| `rate_sex_female` | Influenza | Rate per 100k | Weekly rate for female individuals. |

---

## Estimation

### Metric Definition

Weekly hospitalization rates per 100,000 population are computed upstream by the CDC for each catchment area $$i$$, surveillance week $$t$$, and demographic stratum $$k$$:

$$
\text{Rate}_{it}^k = 100{,}000 \cdot \frac{Y_{it}^k}{N_{it}^k}
$$

where $$Y_{it}^k$$ is the count of residents hospitalized with laboratory-confirmed influenza, and $$N_{it}^k$$ is the census population estimate for that stratum in the participating catchment counties.

Delphi ingests these rates directly and publishes each category as an individual signal.

### Smoothing

All signals are unsmoothed weekly rate estimates.

### Uncertainty

CDC releases do not report standard errors, confidence intervals, sample sizes, or underlying raw hospitalization counts.

### Temporal Handling

Observations cover 7-day epidemiological weeks defined by the CDC's Morbidity and Mortality Weekly Report (MMWR). An MMWR week runs from Sunday through Saturday, standardizing public health reporting across calendar years.

- `reference_time` is the Saturday week-ending date of the surveillance week.
- `report_time` is the release date when Delphi ingested the weekly CDC snapshot. Revisions update historical rates as hospitals complete retrospective case ascertainment.

### Geographic Handling

Both geographic levels (`state` and `flusurv_site`) are computed upstream by the CDC. Since Delphi ingests these rates directly from the CDC without spatial interpolation, regional aggregation, or imputation, `fill_method` is always set to `source`.

FluSurv-NET monitors hospitalized cases across designated sentinel hospital catchments rather than whole state or national populations.

The `state` level reports rates for participating sentinel states using standard two-letter postal codes. These rates reflect participating county catchments within each state rather than complete statewide populations.

The `flusurv_site` level covers sub-state catchments and multi-state network rollups computed by the CDC:

| Location | Description |
| :--- | :--- |
| `ny_albany` | Albany, NY catchment area |
| `ny_rochester` | Rochester, NY catchment area |
| `network_all` | Entire FluSurv-NET surveillance network |
| `network_eip` | Emerging Infections Program network sites |
| `network_ihsp` | Influenza Hospitalization Surveillance Project sites |

---

## Relationship to V3

This source reproduces the legacy V3 `flusurv` endpoint (`https://api.delphi.cmu.edu/epidata/flusurv/`).

In V3, queries returned wide records containing all demographic rate fields in a single response object. In V5, each stratum is queried as an individual signal conforming to the standard Delphi schema.

| V3 Field | V5 Signal | Notes |
| :--- | :--- | :--- |
| `rate_overall` | `rate_overall` | Exact match |
| `rate_age_0` | `rate_age_0` | Exact match |
| `rate_age_1` | `rate_age_1` | Exact match |
| `rate_age_2` | `rate_age_2` | Exact match |
| `rate_age_3` | `rate_age_3` | Exact match |
| `rate_age_4` | `rate_age_4` | Exact match |
| `rate_age_5` | `rate_age_5` | Exact match |
| `rate_age_6` | `rate_age_6` | Exact match |
| `rate_age_7` | `rate_age_7` | Exact match |
| `rate_age_0tlt1` | `rate_age_0tlt1` | Exact match |
| `rate_age_1t4` | `rate_age_1t4` | Exact match |
| `rate_age_5t11` | `rate_age_5t11` | Exact match |
| `rate_age_12t17` | `rate_age_12t17` | Exact match |
| `rate_age_18t29` | `rate_age_18t29` | Exact match |
| `rate_age_30t39` | `rate_age_30t39` | Exact match |
| `rate_age_40t49` | `rate_age_40t49` | Exact match |
| `rate_age_gte75` | `rate_age_gte75` | Exact match |
| `rate_age_lt18` | `rate_age_lt18` | Exact match |
| `rate_age_gte18` | `rate_age_gte18` | Exact match |
| `rate_race_white` | `rate_race_white` | Exact match |
| `rate_race_black` | `rate_race_black` | Exact match |
| `rate_race_hisp` | `rate_race_hisp` | Exact match |
| `rate_race_asian` | `rate_race_asian` | Exact match |
| `rate_race_natamer` | `rate_race_natamer` | Exact match |
| `rate_sex_male` | `rate_sex_male` | Exact match |
| `rate_sex_female` | `rate_sex_female` | Exact match |
| `rate_flu_a` | `rate_flu_a` | Exact match |
| `rate_flu_b` | `rate_flu_b` | Exact match |

What changed in V5:

- **Signal Standardization.** Demographic rate categories are queried as individual signals using the standard `signal` parameter rather than separate columns in a single record.
- **Geographic Distinction.** Sentinel states are classified as `geo_type = 'state'`, while multi-site networks and sub-state catchments are assigned `geo_type = 'flusurv_site'`.
- **Revision History.** Past releases and revisions are queried using `snapshot_date` or the `/archive/` endpoint instead of the legacy `issues` and `lag` parameters.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the indicator (e.g., `rate_overall`, `rate_age_0`). |
| `report_time` | Primary Key | date | The CDC update date on which Delphi fetched the data (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic category (`state` or `flusurv_site`). |
| `geo_value` | Primary Key | string | Catchment identifier. |
| `fill_method` | Primary Key | string | Treatment of missing data or aggregation. Always `source` because rates are ingested directly without imputation. |
| `reference_time` | Primary Key | date | Saturday week-ending date of the surveillance week (`YYYY-MM-DD`). |
| `value` | Value Column | float | Laboratory-confirmed influenza hospitalization rate per 100,000 population. |

---

## Missingness & Privacy

- No cell suppression or differential privacy masking is applied because data is published upstream exclusively as aggregate population rates.
- Rates are published only for surveillance weeks and strata where active surveillance occurred. Periods outside active surveillance are omitted rather than reported as zero.

---

## Limitations

- FluSurv-NET catchments cover approximately 9 percent of the U.S. population. Rates reflect designated counties in participating states and do not represent entire statewide or nationwide populations.
- Network composition changes over time as states and hospitals join or exit surveillance. For instance, North Carolina joined during the 2023–24 season, and Ohio ceased participation after 2024–25.
- FluSurv-NET tracks patients hospitalized with laboratory-confirmed influenza. Variations in clinical testing practices across facilities and seasons can influence case detection.

---

## Lag & Backfill

- Updated data is published by the CDC on Fridays.
- Data is preliminary and subject to backfill as hospitals complete retrospective case ascertainment and medical record reviews. Historical revisions can be accessed via the `/archive/` endpoint or by querying with `snapshot_date`.

---

## Source and Licensing

FluSurv-NET is a collaborative surveillance network administered by the CDC. Data is in the [public domain](https://www.usa.gov/government-works). When utilizing this dataset, citation of FluSurv-NET is recommended:

> Chaves, S. S., Lynfield, R., Lindegren, M. L., Bresee, J., & Finelli, L. (2015). The US Influenza Hospitalization Surveillance Network. *Emerging Infectious Diseases*, 21(9), 1543–1550.
