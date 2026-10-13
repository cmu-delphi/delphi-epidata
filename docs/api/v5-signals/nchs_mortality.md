---
title: NCHS Mortality Data
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 8
---

# NCHS Mortality Data
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nchs_mortality` |
| **Data Source** | [National Center for Health Statistics (NCHS)](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm) via [data.cdc.gov Socrata dataset `r8kw-7aab`](https://data.cdc.gov/National-Center-for-Health-Statistics/Provisional-COVID-19-Death-Counts-by-Week-Ending-D/r8kw-7aab/about_data) |
| **Geographic Levels** | `state`, `nation` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2020-01-18 (2020w02 for nation, 2020w05 for state) |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [NCHS Data Use Agreement](https://www.cdc.gov/nchs/data_access/restrictions.htm) |

> This source reproduces the legacy V4 [`nchs-mortality`](../covidcast-signals/nchs-mortality.md) source. All signal names and metrics are preserved, with the source identifier standardized from `nchs-mortality` to `nchs_mortality`. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Center for Health Statistics (NCHS) maintains the National Vital Statistics System (NVSS), which collects and tabulates death certificate data across all 50 states, the District of Columbia, and U.S. territories. Delphi ingests the provisional weekly death data published on data.cdc.gov, tracking deaths associated with COVID-19, influenza, and pneumonia, as well as total all-cause mortality and comparisons against historical baseline levels.

Unlike surveillance data that tabulates cases or deaths on the date they are announced by public health agencies, NCHS mortality counts are organized by the actual date of death occurrence. Because vital registration and medical certification take time to complete, provisional figures for recent weeks undergo continuous retrospective revision as additional death certificates are processed.

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `deaths_covid_incidence_num` | COVID-19 | Count | Weekly count of deaths involving confirmed or presumed COVID-19. |
| `deaths_covid_incidence_prop` | COVID-19 | Rate per 100k | Weekly rate of deaths involving confirmed or presumed COVID-19, per 100,000 population. |
| `deaths_allcause_incidence_num` | All Causes | Count | Weekly count of deaths from all causes. |
| `deaths_allcause_incidence_prop` | All Causes | Rate per 100k | Weekly rate of deaths from all causes, per 100,000 population. |
| `deaths_flu_incidence_num` | Influenza | Count | Weekly count of deaths involving influenza, including those where pneumonia or COVID-19 is also listed. |
| `deaths_flu_incidence_prop` | Influenza | Rate per 100k | Weekly rate of deaths involving influenza, per 100,000 population. |
| `deaths_pneumonia_notflu_incidence_num` | Pneumonia | Count | Weekly count of deaths involving pneumonia, excluding influenza. |
| `deaths_pneumonia_notflu_incidence_prop` | Pneumonia | Rate per 100k | Weekly rate of deaths involving pneumonia, excluding influenza, per 100,000 population. |
| `deaths_covid_and_pneumonia_notflu_incidence_num` | COVID-19, Pneumonia | Count | Weekly count of deaths involving both COVID-19 and pneumonia, excluding influenza. |
| `deaths_covid_and_pneumonia_notflu_incidence_prop` | COVID-19, Pneumonia | Rate per 100k | Weekly rate of deaths involving both COVID-19 and pneumonia, excluding influenza, per 100,000 population. |
| `deaths_pneumonia_or_flu_or_covid_incidence_num` | COVID-19, Flu, Pneumonia | Count | Weekly count of deaths involving pneumonia, influenza, or COVID-19 (PIC). |
| `deaths_pneumonia_or_flu_or_covid_incidence_prop` | COVID-19, Flu, Pneumonia | Rate per 100k | Weekly rate of deaths involving pneumonia, influenza, or COVID-19 (PIC), per 100,000 population. |
| `deaths_percent_of_expected` | All Causes | Percentage | Weekly all-cause deaths expressed as a percentage of the average death count across the same week in 2017–2019. |

---

## Estimation

### Metric Definition

Delphi ingests provisional weekly death counts from NCHS. Cause-specific counts include any death where the disease is listed on the death certificate, either as the primary cause or as a contributing factor.

For location $$i$$ and week $$t$$:

- Counts (`*_num`) are taken directly from NCHS without adjustment.
- Rates (`*_prop`) divide the weekly count $$Y_{it}$$ by location population $$P_i$$ per 100,000 people:

  $$
  \text{Rate}_{it} = 100{,}000 \cdot \frac{Y_{it}}{P_i}
  $$

- Percent of expected (`deaths_percent_of_expected`) compares weekly all-cause deaths to the 2017–2019 baseline average $$E_{it}$$:

  $$
  \text{Percent}_{it} = 100 \cdot \frac{Y_{it}}{E_{it}}
  $$

### Smoothing

All signals are unsmoothed. Values represent discrete 7-day weekly totals without moving averages.

### Uncertainty

These indicators are based on complete vital registration records rather than sample surveys.

### Temporal Handling

Observations cover 7-day epidemiological weeks defined by the CDC's Morbidity and Mortality Weekly Report (MMWR). An MMWR week runs from Sunday through Saturday, standardizing public health reporting across calendar years.

- `reference_time` is the Saturday week-ending date of the surveillance week when deaths occurred.
- `report_time` is the release date when Delphi ingested the weekly NCHS snapshot. Because mortality data undergoes substantial backfill, each new report date revises counts for earlier weeks.

### Geographic Handling

Data is published at two geographic resolutions:

- Nation (`nation`). National totals are labelled as `us`.
- State (`state`). Standard two-letter postal codes. New York City is reported separately in raw NCHS data, but Delphi aggregates New York City counts into New York State (`ny`) before calculating rates.

Because Delphi ingests counts directly without geographic imputation, `fill_method` is always `source`.

---

## Relationship to V4

This source reproduces the legacy V4 `nchs-mortality` data source. All 13 signal names are retained with identical definitions.

| V4 Signal | V5 Signal | Notes |
| :--- | :--- | :--- |
| `deaths_covid_incidence_num` | `deaths_covid_incidence_num` | Exact match |
| `deaths_covid_incidence_prop` | `deaths_covid_incidence_prop` | Exact match |
| `deaths_allcause_incidence_num` | `deaths_allcause_incidence_num` | Exact match |
| `deaths_allcause_incidence_prop` | `deaths_allcause_incidence_prop` | Exact match |
| `deaths_flu_incidence_num` | `deaths_flu_incidence_num` | Exact match |
| `deaths_flu_incidence_prop` | `deaths_flu_incidence_prop` | Exact match |
| `deaths_pneumonia_notflu_incidence_num` | `deaths_pneumonia_notflu_incidence_num` | Exact match |
| `deaths_pneumonia_notflu_incidence_prop` | `deaths_pneumonia_notflu_incidence_prop` | Exact match |
| `deaths_covid_and_pneumonia_notflu_incidence_num` | `deaths_covid_and_pneumonia_notflu_incidence_num` | Exact match |
| `deaths_covid_and_pneumonia_notflu_incidence_prop` | `deaths_covid_and_pneumonia_notflu_incidence_prop` | Exact match |
| `deaths_pneumonia_or_flu_or_covid_incidence_num` | `deaths_pneumonia_or_flu_or_covid_incidence_num` | Exact match |
| `deaths_pneumonia_or_flu_or_covid_incidence_prop` | `deaths_pneumonia_or_flu_or_covid_incidence_prop` | Exact match |
| `deaths_percent_of_expected` | `deaths_percent_of_expected` | Exact match |

What changed in V5:

- **Source Identifier.** Renamed from `nchs-mortality` (hyphenated) to `nchs_mortality` (underscore) to match V5 source naming conventions.
- **Revision History.** Users can query past releases using `snapshot_date` or the `/archive/` endpoint.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The release date on which Delphi ingested the NCHS publication (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state` or `nation`). |
| `geo_value` | Primary Key | string | Location code (`us` for national, 2-letter state code). |
| `fill_method` | Primary Key | string | Always `source`. |
| `reference_time` | Primary Key | date | The Saturday week-ending date of the surveillance week (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded measurement. |

---

## Missingness & Privacy

NCHS suppresses values under two conditions:

- Counts between 1 and 9 are suppressed to protect privacy. These values appear as `null`.
- Weeks where provisional death counts fall below 50% of historical expected deaths are withheld due to low completeness.

Delphi does not impute suppressed or missing values.

---

## Limitations

- Deaths are tabulated by date of death rather than date of report. Recent weeks undercount actual mortality until all death certificates are submitted and processed.
- Reporting speed varies by state. Some jurisdictions submit records within days, while others take several weeks. Comparisons across states during the most recent weeks often reflect reporting delays rather than true differences in mortality.
- New York City is included in New York State totals and cannot be queried separately.
- Deaths pending investigation or toxicology results can cause delayed ICD-10 coding.

---

## Lag & Backfill

Completing, submitting, and coding death certificates creates delays between when a death occurs and when it appears in the data:

- Initial data for a given week is published 11 to 17 days after the week ends.
- Counts for past weeks increase over time as additional certificates are processed. Provisional all-cause counts typically take 6 to 8 weeks to reach 99% completeness ([Spencer et al., 2022](https://doi.org/10.1057/s41271-021-00309-7)). Specific causes may take longer.
- Weekly updates revise past weeks. Historical revisions are available through the `/archive/` endpoint or by querying with `snapshot_date`.

---

## Source and Licensing

This data was originally published by the National Center for Health Statistics (NCHS) on [data.cdc.gov](https://data.cdc.gov/National-Center-for-Health-Statistics/Provisional-COVID-19-Death-Counts-by-Week-Ending-D/r8kw-7aab/about_data),
and is made available here as a convenience to the forecasting community under
the terms of the original license. The NCHS places restrictions on how this
dataset may be used: you may not attempt to identify any individual included in
the data, whether by itself or through linking to other
individually identifiable data; you may only use the dataset for statistical
reporting and analysis. The full text of the [NCHS Data Use
Agreement](https://www.cdc.gov/nchs/data_access/restrictions.htm) is available
on their website.
