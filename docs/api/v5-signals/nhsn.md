---
title: NHSN Hospitalizations
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 2
---

# NHSN Respiratory Hospitalizations
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nhsn` |
| **Data Source** | [National Healthcare Safety Network (NHSN)](https://www.cdc.gov/nhsn/index.html) via [HealthData.gov](https://healthdata.gov/) |
| **Geographic Levels** | `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Week, ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2020-08-08 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

> This source reproduces the legacy V4 [`nhsn`](../covidcast-signals/nhsn.md) source, itself the continuation of the earlier [`hhs`](../covidcast-signals/hhs.md) hospitalization source. V5 expands coverage from raw admission counts to the complete NHSN metric suite (including bed capacity and occupancy, current inpatient and ICU census, age-stratified admissions, population-adjusted rates, and hospital reporting compliance), adds census-level aggregation, and folds the preliminary dataset into each signal's revision history rather than publishing separate `_prelim` signals. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Healthcare Safety Network (NHSN) collects weekly respiratory admission, inpatient and ICU census, bed capacity, and reporting compliance metrics from acute care hospitals across the United States. Delphi ingests the weekly Hospital Respiratory Data release published by the CDC on HealthData.gov, covering COVID-19, influenza, and RSV admissions, patient census, bed occupancy, reporting coverage, and seasonal cumulative totals.

All 319 active indicators defined in the upstream CDC dataset schema are ingested and standardized into Delphi's unified V5 schema.

---

## Indicators (Signals)

### Primary Indicators

The table below highlights the primary headline indicators for respiratory admissions, bed occupancy, inpatient census, and reporting facility counts, along with their corresponding upstream CDC field names:

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_ew` | `totalconfc19newadm` | COVID-19 | Count | Total COVID-19 hospital admissions during the reporting week. |
| `confirmed_admissions_flu_ew` | `totalconfflunewadm` | Influenza | Count | Total influenza hospital admissions during the reporting week. |
| `confirmed_admissions_rsv_ew` | `totalconfrsvnewadm` | RSV | Count | Total RSV hospital admissions during the reporting week. |
| `confirmed_admissions_covid_cumulative_ew` | `totalconfc19newadmcumulativeseasonalsum` | COVID-19 | Cumulative Count | Cumulative season-to-date confirmed COVID-19 hospital admissions (since week 40). |
| `confirmed_admissions_flu_cumulative_ew` | `totalconfflunewadmcumulativeseasonalsum` | Influenza | Cumulative Count | Cumulative season-to-date confirmed influenza hospital admissions (since week 40). |
| `confirmed_admissions_rsv_cumulative_ew` | `totalconfrsvnewadmcumulativeseasonalsum` | RSV | Cumulative Count | Cumulative season-to-date confirmed RSV hospital admissions (since week 40). |
| `confirmed_admissions_cumulative_ew` | `totalconfnewadmcumulativeseasonalsum` | Combined | Cumulative Count | Cumulative season-to-date total respiratory hospital admissions across all three pathogens. |
| `inpatient_beds_ew` | `numinptbeds` | — | Count | Total number of inpatient beds (Wednesday snapshot). |
| `inpatient_beds_occupied_ew` | `numinptbedsocc` | — | Count | Number of occupied inpatient beds (Wednesday snapshot). |
| `inpatient_beds_occupied_pct_ew` | `pctinptbedsocc` | — | Percentage | Percentage of inpatient beds occupied (Wednesday snapshot). |
| `icu_beds_ew` | `numicubeds` | — | Count | Total number of ICU beds (Wednesday snapshot). |
| `icu_beds_occupied_ew` | `numicubedsocc` | — | Count | Number of occupied ICU beds (Wednesday snapshot). |
| `icu_beds_occupied_pct_ew` | `pcticubedsocc` | — | Percentage | Percentage of ICU beds occupied (Wednesday snapshot). |
| `covid_inpatients_ew` | `totalconfc19hosppats` | COVID-19 | Count | Total patients hospitalized with COVID-19 (Wednesday snapshot). |
| `flu_inpatients_ew` | `totalconffluhosppats` | Influenza | Count | Total patients hospitalized with influenza (Wednesday snapshot). |
| `rsv_inpatients_ew` | `totalconfrsvhosppats` | RSV | Count | Total patients hospitalized with RSV (Wednesday snapshot). |
| `covid_icu_patients_ew` | `totalconfc19icupats` | COVID-19 | Count | Total ICU patients with COVID-19 (Wednesday snapshot). |
| `flu_icu_patients_ew` | `totalconffluicupats` | Influenza | Count | Total ICU patients with influenza (Wednesday snapshot). |
| `rsv_icu_patients_ew` | `totalconfrsvicupats` | RSV | Count | Total ICU patients with RSV (Wednesday snapshot). |
| `hosprep_confirmed_admissions_covid_ew` | `totalconfc19newadmhosprep` | COVID-19 | Facility Count | Number of acute care hospitals reporting COVID-19 admissions. |
| `hosprep_confirmed_admissions_flu_ew` | `totalconfflunewadmhosprep` | Influenza | Facility Count | Number of acute care hospitals reporting influenza admissions. |
| `hosprep_confirmed_admissions_rsv_ew` | `totalconfrsvnewadmhosprep` | RSV | Facility Count | Number of acute care hospitals reporting RSV admissions. |

### Indicator Families

Beyond headline totals, the `nhsn` source publishes 319 indicators. Expand each subsection below for the complete indicator catalog with upstream CDC field names.

#### 1. Bed Capacity and Occupancy

Bed metrics capture hospital capacity and utilization across inpatient and ICU settings (adult, pediatric, and total), reported as Wednesday snapshots.

<details markdown="1">
<summary><strong>Bed Capacity and Occupancy Counts</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `inpatient_beds_ew` | `numinptbeds` | — | Count | Number of Inpatient Beds (Wednesday snapshot) |
| `inpatient_beds_adult_ew` | `numinptbedsadult` | — | Count | Number of Adult Inpatient Beds |
| `inpatient_beds_ped_ew` | `numinptbedsped` | — | Count | Number of Pediatric Inpatient Beds |
| `icu_beds_ew` | `numicubeds` | — | Count | Number of ICU Beds |
| `icu_beds_adult_ew` | `numicubedsadult` | — | Count | Number of Adult ICU Beds |
| `icu_beds_ped_ew` | `numicubedsped` | — | Count | Number of Pediatric ICU Beds |
| `inpatient_beds_occupied_ew` | `numinptbedsocc` | — | Count | Number of Inpatient Beds Occupied (Wednesday snapshot) |
| `inpatient_beds_occupied_adult_ew` | `numinptbedsoccadult` | — | Count | Number of Adult Inpatient Beds Occupied |
| `inpatient_beds_occupied_ped_ew` | `numinptbedsoccped` | — | Count | Number of Pediatric Inpatient Beds Occupied |
| `icu_beds_occupied_ew` | `numicubedsocc` | — | Count | Number of ICU Beds Occupied |
| `icu_beds_occupied_adult_ew` | `numicubedsoccadult` | — | Count | Number of Adult ICU Beds Occupied |
| `icu_beds_occupied_ped_ew` | `numicubedsoccped` | — | Count | Number of Pediatric ICU Beds Occupied |

</details>

<details markdown="1">
<summary><strong>Bed Occupancy Rates</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `inpatient_beds_occupied_pct_ew` | `pctinptbedsocc` | — | Percentage | Percent Inpatient Beds Occupied (Wednesday snapshot) |
| `inpatient_beds_occupied_adult_pct_ew` | `pctinptbedsoccadult` | — | Percentage | Percent Adult Inpatient Beds Occupied (Wednesday snapshot) |
| `inpatient_beds_occupied_ped_pct_ew` | `pctinptbedsoccped` | — | Percentage | Percent Pediatric Inpatient Beds Occupied (Wednesday snapshot) |
| `icu_beds_occupied_pct_ew` | `pcticubedsocc` | — | Percentage | Percent ICU Beds Occupied (Wednesday snapshot) |
| `icu_beds_occupied_adult_pct_ew` | `pcticubedsoccadult` | — | Percentage | Percent Adult ICU Beds Occupied (Wednesday snapshot) |
| `icu_beds_occupied_ped_pct_ew` | `pcticubedsoccped` | — | Percentage | Percent Pediatric ICU Beds Occupied (Wednesday snapshot) |
| `inpatient_beds_covid_pct_ew` | `pctconfc19inptbeds` | COVID-19 | Percentage | Percent Inpatient Beds Occupied by COVID-19 Patients |
| `inpatient_beds_covid_adult_pct_ew` | `pctconfc19inptbedsadult` | COVID-19 | Percentage | Percent Adult Inpatient Beds Occupied by COVID-19 Patients |
| `inpatient_beds_covid_ped_pct_ew` | `pctconfc19inptbedsped` | COVID-19 | Percentage | Percent Pediatric Inpatient Beds Occupied by COVID-19 Patients |
| `icu_beds_covid_pct_ew` | `pctconfc19icubeds` | COVID-19 | Percentage | Percent ICU Beds Occupied by COVID-19 Patients |
| `icu_beds_covid_adult_pct_ew` | `pctconfc19icubedsadult` | COVID-19 | Percentage | Percent Adult ICU Beds Occupied by COVID-19 Patients |
| `icu_beds_covid_ped_pct_ew` | `pctconfc19icubedsped` | COVID-19 | Percentage | Percent Pediatric ICU Beds Occupied by COVID-19 Patients |
| `inpatient_beds_flu_pct_ew` | `pctconffluinptbeds` | Influenza | Percentage | Percent Inpatient Beds Occupied by Influenza Patients |
| `inpatient_beds_flu_adult_pct_ew` | `pctconffluinptbedsadult` | Influenza | Percentage | Percent Adult Inpatient Beds Occupied by Influenza Patients |
| `inpatient_beds_flu_ped_pct_ew` | `pctconffluinptbedsped` | Influenza | Percentage | Percent Pediatric Inpatient Beds Occupied by Influenza Patients |
| `icu_beds_flu_pct_ew` | `pctconffluicubeds` | Influenza | Percentage | Percent ICU Beds Occupied by Influenza Patients |
| `icu_beds_flu_adult_pct_ew` | `pctconffluicubedsadult` | Influenza | Percentage | Percent Adult ICU Beds Occupied by Influenza Patients |
| `icu_beds_flu_ped_pct_ew` | `pctconffluicubedsped` | Influenza | Percentage | Percent Pediatric ICU Beds Occupied by Influenza Patients |
| `inpatient_beds_rsv_pct_ew` | `pctconfrsvinptbeds` | RSV | Percentage | Percent Inpatient Beds Occupied by RSV Patients |
| `inpatient_beds_rsv_adult_pct_ew` | `pctconfrsvinptbedsadult` | RSV | Percentage | Percent Adult Inpatient Beds Occupied by RSV Patients |
| `inpatient_beds_rsv_ped_pct_ew` | `pctconfrsvinptbedsped` | RSV | Percentage | Percent Pediatric Inpatient Beds Occupied by RSV Patients |
| `icu_beds_rsv_pct_ew` | `pctconfrsvicubeds` | RSV | Percentage | Percent ICU Beds Occupied by RSV Patients |
| `icu_beds_rsv_adult_pct_ew` | `pctconfrsvicubedsadult` | RSV | Percentage | Percent Adult ICU Beds Occupied by RSV Patients |
| `icu_beds_rsv_ped_pct_ew` | `pctconfrsvicubedsped` | RSV | Percentage | Percent Pediatric ICU Beds Occupied by RSV Patients |

</details>

#### 2. Current Hospital Census

Wednesday snapshot counts of hospitalized patients with confirmed COVID-19, influenza, or RSV infection across all ages, adult, and pediatric strata.

<details markdown="1">
<summary><strong>Current Inpatient and ICU Census</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `covid_inpatients_adult_ew` | `numconfc19hosppatsadult` | COVID-19 | Count | Number of Adult Patients Hospitalized with COVID-19 |
| `covid_inpatients_ped_ew` | `numconfc19hosppatsped` | COVID-19 | Count | Number of Pediatric Patients Hospitalized with COVID-19 |
| `covid_inpatients_ew` | `totalconfc19hosppats` | COVID-19 | Count | Total Patients Hospitalized with COVID-19 |
| `covid_icu_patients_adult_ew` | `numconfc19icupatsadult` | COVID-19 | Count | Number of Adult ICU Patients Hospitalized with COVID-19 |
| `covid_icu_patients_ped_ew` | `numconfc19icupatsped` | COVID-19 | Count | Number of Pediatric ICU Patients Hospitalized with COVID-19 |
| `covid_icu_patients_ew` | `totalconfc19icupats` | COVID-19 | Count | Total ICU Patients Hospitalized with COVID-19 |
| `covid_inpatients_icu_pct_ew` | `pctconfc19hosppatsicu` | COVID-19 | Percentage | Percent Hospitalized Patients with COVID-19 in the ICU |
| `covid_inpatients_adult_icu_pct_ew` | `pctconfc19hosppatsicuadult` | COVID-19 | Percentage | Percent Hospitalized Adult Patients with COVID-19 in the ICU |
| `covid_inpatients_ped_icu_pct_ew` | `pctconfc19hosppatsicuped` | COVID-19 | Percentage | Percent Hospitalized Pediatric Patients with COVID-19 in the ICU |
| `flu_inpatients_adult_ew` | `numconffluhosppatsadult` | Influenza | Count | Number of Adult Patients Hospitalized with Influenza |
| `flu_inpatients_ped_ew` | `numconffluhosppatsped` | Influenza | Count | Number of Pediatric Patients Hospitalized with Influenza |
| `flu_inpatients_ew` | `totalconffluhosppats` | Influenza | Count | Total Patients Hospitalized with Influenza |
| `flu_icu_patients_adult_ew` | `numconffluicupatsadult` | Influenza | Count | Number of Adult ICU Patients Hospitalized with Influenza |
| `flu_icu_patients_ped_ew` | `numconffluicupatsped` | Influenza | Count | Number of Pediatric ICU Patients Hospitalized with Influenza |
| `flu_icu_patients_ew` | `totalconffluicupats` | Influenza | Count | Total ICU Patients Hospitalized with Influenza |
| `flu_inpatients_icu_pct_ew` | `pctconffluhosppatsicu` | Influenza | Percentage | Percent Hospitalized Patients with Influenza in the ICU |
| `flu_inpatients_adult_icu_pct_ew` | `pctconffluhosppatsicuadult` | Influenza | Percentage | Percent Hospitalized Adult Patients with Influenza in the ICU |
| `flu_inpatients_ped_icu_pct_ew` | `pctconffluhosppatsicuped` | Influenza | Percentage | Percent Hospitalized Pediatric Patients with Influenza in the ICU |
| `rsv_inpatients_adult_ew` | `numconfrsvhosppatsadult` | RSV | Count | Number of Adult Patients Hospitalized with RSV |
| `rsv_inpatients_ped_ew` | `numconfrsvhosppatsped` | RSV | Count | Number of Pediatric Patients Hospitalized with RSV |
| `rsv_inpatients_ew` | `totalconfrsvhosppats` | RSV | Count | Total Patients Hospitalized with RSV |
| `rsv_icu_patients_adult_ew` | `numconfrsvicupatsadult` | RSV | Count | Number of Adult ICU Patients Hospitalized with RSV |
| `rsv_icu_patients_ped_ew` | `numconfrsvicupatsped` | RSV | Count | Number of Pediatric ICU Patients Hospitalized with RSV |
| `rsv_icu_patients_ew` | `totalconfrsvicupats` | RSV | Count | Total ICU Patients Hospitalized with RSV |
| `rsv_inpatients_icu_pct_ew` | `pctconfrsvhosppatsicu` | RSV | Percentage | Percent Hospitalized Patients with RSV in the ICU |
| `rsv_inpatients_adult_icu_pct_ew` | `pctconfrsvhosppatsicuadult` | RSV | Percentage | Percent Hospitalized Adult Patients with RSV in the ICU |
| `rsv_inpatients_ped_icu_pct_ew` | `pctconfrsvhosppatsicuped` | RSV | Percentage | Percent Hospitalized Pediatric Patients with RSV in the ICU |

</details>

#### 3. New Admissions by Age Group

Weekly counts of new confirmed patient admissions are reported across 10 age brackets (0–4, 5–17, pediatric total, 18–49, 50–64, 65–74, 75+, adult total, unknown age, and total all ages) for COVID-19, influenza, and RSV.
In the near future these will be migrated to long-format with age group as a key column.

<details markdown="1">
<summary><strong>New Hospital Admissions by Age Group</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_0_4_ew` | `numconfc19newadmped0to4` | COVID-19 | Count | Number of Pediatric COVID-19 Admissions, 0–4 years |
| `confirmed_admissions_covid_5_17_ew` | `numconfc19newadmped5to17` | COVID-19 | Count | Number of Pediatric COVID-19 Admissions, 5–17 years |
| `confirmed_admissions_covid_ped_ew` | `totalconfc19newadmped` | COVID-19 | Count | Total Pediatric COVID-19 Admissions |
| `confirmed_admissions_covid_18_49_ew` | `numconfc19newadmadult18to49` | COVID-19 | Count | Number of Adult COVID-19 Admissions, 18–49 years |
| `confirmed_admissions_covid_50_64_ew` | `numconfc19newadmadult50to64` | COVID-19 | Count | Number of Adult COVID-19 Admissions, 50–64 years |
| `confirmed_admissions_covid_65_74_ew` | `numconfc19newadmadult65to74` | COVID-19 | Count | Number of Adult COVID-19 Admissions, 65–74 years |
| `confirmed_admissions_covid_75_ew` | `numconfc19newadmadult75plus` | COVID-19 | Count | Number of Adult COVID-19 Admissions, 75+ years |
| `confirmed_admissions_covid_adult_ew` | `totalconfc19newadmadult` | COVID-19 | Count | Total Adult COVID-19 Admissions |
| `confirmed_admissions_covid_unk_age_ew` | `numconfc19newadmunk` | COVID-19 | Count | Number of COVID-19 Admissions, Unknown Age |
| `confirmed_admissions_covid_ew` | `totalconfc19newadm` | COVID-19 | Count | Total COVID-19 Admissions |
| `confirmed_admissions_flu_0_4_ew` | `numconfflunewadmped0to4` | Influenza | Count | Number of Pediatric Influenza Admissions, 0–4 years |
| `confirmed_admissions_flu_5_17_ew` | `numconfflunewadmped5to17` | Influenza | Count | Number of Pediatric Influenza Admissions, 5–17 years |
| `confirmed_admissions_flu_ped_ew` | `totalconfflunewadmped` | Influenza | Count | Total Pediatric Influenza Admissions |
| `confirmed_admissions_flu_18_49_ew` | `numconfflunewadmadult18to49` | Influenza | Count | Number of Adult Influenza Admissions, 18–49 years |
| `confirmed_admissions_flu_50_64_ew` | `numconfflunewadmadult50to64` | Influenza | Count | Number of Adult Influenza Admissions, 50–64 years |
| `confirmed_admissions_flu_65_74_ew` | `numconfflunewadmadult65to74` | Influenza | Count | Number of Adult Influenza Admissions, 65–74 years |
| `confirmed_admissions_flu_75_ew` | `numconfflunewadmadult75plus` | Influenza | Count | Number of Adult Influenza Admissions, 75+ years |
| `confirmed_admissions_flu_adult_ew` | `totalconfflunewadmadult` | Influenza | Count | Total Adult Influenza Admissions |
| `confirmed_admissions_flu_unk_age_ew` | `numconfflunewadmunk` | Influenza | Count | Number of Influenza Admissions, Unknown Age |
| `confirmed_admissions_flu_ew` | `totalconfflunewadm` | Influenza | Count | Total Influenza Admissions |
| `confirmed_admissions_rsv_0_4_ew` | `numconfrsvnewadmped0to4` | RSV | Count | Number of Pediatric RSV Admissions, 0–4 years |
| `confirmed_admissions_rsv_5_17_ew` | `numconfrsvnewadmped5to17` | RSV | Count | Number of Pediatric RSV Admissions, 5–17 years |
| `confirmed_admissions_rsv_ped_ew` | `totalconfrsvnewadmped` | RSV | Count | Total Pediatric RSV Admissions |
| `confirmed_admissions_rsv_18_49_ew` | `numconfrsvnewadmadult18to49` | RSV | Count | Number of Adult RSV Admissions, 18–49 years |
| `confirmed_admissions_rsv_50_64_ew` | `numconfrsvnewadmadult50to64` | RSV | Count | Number of Adult RSV Admissions, 50–64 years |
| `confirmed_admissions_rsv_65_74_ew` | `numconfrsvnewadmadult65to74` | RSV | Count | Number of Adult RSV Admissions, 65–74 years |
| `confirmed_admissions_rsv_75_ew` | `numconfrsvnewadmadult75plus` | RSV | Count | Number of Adult RSV Admissions, 75+ years |
| `confirmed_admissions_rsv_adult_ew` | `totalconfrsvnewadmadult` | RSV | Count | Total Adult RSV Admissions |
| `confirmed_admissions_rsv_unk_age_ew` | `numconfrsvnewadmunk` | RSV | Count | Number of RSV Admissions, Unknown Age |
| `confirmed_admissions_rsv_ew` | `totalconfrsvnewadm` | RSV | Count | Total RSV Admissions |

</details>

<details markdown="1">
<summary><strong>Admissions Age-Mix Percentages</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_adult_pct_ew` | `pctconfc19newadmadult` | COVID-19 | Percentage | Percent Adult COVID-19 Admissions |
| `confirmed_admissions_covid_ped_pct_ew` | `pctconfc19newadmped` | COVID-19 | Percentage | Percent Pediatric COVID-19 Admissions |
| `confirmed_admissions_flu_adult_pct_ew` | `pctconfflunewadmadult` | Influenza | Percentage | Percent Adult Influenza Admissions |
| `confirmed_admissions_flu_ped_pct_ew` | `pctconfflunewadmped` | Influenza | Percentage | Percent Pediatric Influenza Admissions |
| `confirmed_admissions_rsv_adult_pct_ew` | `pctconfrsvnewadmadult` | RSV | Percentage | Percent Adult RSV Admissions |
| `confirmed_admissions_rsv_ped_pct_ew` | `pctconfrsvnewadmped` | RSV | Percentage | Percent Pediatric RSV Admissions |

</details>

<details markdown="1">
<summary><strong>Admissions per 100,000 Population</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_0_4_per100k_ew` | `numconfc19newadmped0to4per100k` | COVID-19 | Rate per 100k | Pediatric COVID-19 Admissions, 0–4 yrs, per 100k |
| `confirmed_admissions_covid_5_17_per100k_ew` | `numconfc19newadmped5to17per100k` | COVID-19 | Rate per 100k | Pediatric COVID-19 Admissions, 5–17 yrs, per 100k |
| `confirmed_admissions_covid_ped_per100k_ew` | `totalconfc19newadmpedper100k` | COVID-19 | Rate per 100k | Total Pediatric COVID-19 Admissions per 100k |
| `confirmed_admissions_covid_18_49_per100k_ew` | `numconfc19newadmadult18to49per100k` | COVID-19 | Rate per 100k | Adult COVID-19 Admissions, 18–49 yrs, per 100k |
| `confirmed_admissions_covid_50_64_per100k_ew` | `numconfc19newadmadult50to64per100k` | COVID-19 | Rate per 100k | Adult COVID-19 Admissions, 50–64 yrs, per 100k |
| `confirmed_admissions_covid_65_74_per100k_ew` | `numconfc19newadmadult65to74per100k` | COVID-19 | Rate per 100k | Adult COVID-19 Admissions, 65–74 yrs, per 100k |
| `confirmed_admissions_covid_75_per100k_ew` | `numconfc19newadmadult75plusper100k` | COVID-19 | Rate per 100k | Adult COVID-19 Admissions, 75+ yrs, per 100k |
| `confirmed_admissions_covid_adult_per100k_ew` | `totalconfc19newadmadultper100k` | COVID-19 | Rate per 100k | Total Adult COVID-19 Admissions per 100k |
| `confirmed_admissions_covid_per100k_ew` | `totalconfc19newadmper100k` | COVID-19 | Rate per 100k | Total COVID-19 Admissions per 100k |
| `confirmed_admissions_flu_0_4_per100k_ew` | `numconfflunewadmped0to4per100k` | Influenza | Rate per 100k | Pediatric Influenza Admissions, 0–4 yrs, per 100k |
| `confirmed_admissions_flu_5_17_per100k_ew` | `numconfflunewadmped5to17per100k` | Influenza | Rate per 100k | Pediatric Influenza Admissions, 5–17 yrs, per 100k |
| `confirmed_admissions_flu_ped_per100k_ew` | `totalconfflunewadmpedper100k` | Influenza | Rate per 100k | Total Pediatric Influenza Admissions per 100k |
| `confirmed_admissions_flu_18_49_per100k_ew` | `numconfflunewadmadult18to49per100k` | Influenza | Rate per 100k | Adult Influenza Admissions, 18–49 yrs, per 100k |
| `confirmed_admissions_flu_50_64_per100k_ew` | `numconfflunewadmadult50to64per100k` | Influenza | Rate per 100k | Adult Influenza Admissions, 50–64 yrs, per 100k |
| `confirmed_admissions_flu_65_74_per100k_ew` | `numconfflunewadmadult65to74per100k` | Influenza | Rate per 100k | Adult Influenza Admissions, 65–74 yrs, per 100k |
| `confirmed_admissions_flu_75_per100k_ew` | `numconfflunewadmadult75plusper100k` | Influenza | Rate per 100k | Adult Influenza Admissions, 75+ yrs, per 100k |
| `confirmed_admissions_flu_adult_per100k_ew` | `totalconfflunewadmadultper100k` | Influenza | Rate per 100k | Total Adult Influenza Admissions per 100k |
| `confirmed_admissions_flu_per100k_ew` | `totalconfflunewadmper100k` | Influenza | Rate per 100k | Total Influenza Admissions per 100k |
| `confirmed_admissions_rsv_0_4_per100k_ew` | `numconfrsvnewadmped0to4per100k` | RSV | Rate per 100k | Pediatric RSV Admissions, 0–4 yrs, per 100k |
| `confirmed_admissions_rsv_5_17_per100k_ew` | `numconfrsvnewadmped5to17per100k` | RSV | Rate per 100k | Pediatric RSV Admissions, 5–17 yrs, per 100k |
| `confirmed_admissions_rsv_ped_per100k_ew` | `totalconfrsvnewadmpedper100k` | RSV | Rate per 100k | Total Pediatric RSV Admissions per 100k |
| `confirmed_admissions_rsv_18_49_per100k_ew` | `numconfrsvnewadmadult18to49per100k` | RSV | Rate per 100k | Adult RSV Admissions, 18–49 yrs, per 100k |
| `confirmed_admissions_rsv_50_64_per100k_ew` | `numconfrsvnewadmadult50to64per100k` | RSV | Rate per 100k | Adult RSV Admissions, 50–64 yrs, per 100k |
| `confirmed_admissions_rsv_65_74_per100k_ew` | `numconfrsvnewadmadult65to74per100k` | RSV | Rate per 100k | Adult RSV Admissions, 65–74 yrs, per 100k |
| `confirmed_admissions_rsv_75_per100k_ew` | `numconfrsvnewadmadult75plusper100k` | RSV | Rate per 100k | Adult RSV Admissions, 75+ yrs, per 100k |
| `confirmed_admissions_rsv_adult_per100k_ew` | `totalconfrsvnewadmadultper100k` | RSV | Rate per 100k | Total Adult RSV Admissions per 100k |
| `confirmed_admissions_rsv_per100k_ew` | `totalconfrsvnewadmper100k` | RSV | Rate per 100k | Total RSV Admissions per 100k |

</details>

<details markdown="1">
<summary><strong>Week-over-Week Percent Change in Admissions</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_0_4_chg_pct_ew` | `numconfc19newadmped0to4pctchg` | COVID-19 | Percentage change | % Change Pediatric COVID-19 Admissions, 0–4 yrs, from Prior Week |
| `confirmed_admissions_covid_5_17_chg_pct_ew` | `numconfc19newadmped5to17pctchg` | COVID-19 | Percentage change | % Change Pediatric COVID-19 Admissions, 5–17 yrs, from Prior Week |
| `confirmed_admissions_covid_ped_chg_pct_ew` | `totalconfc19newadmpedpctchg` | COVID-19 | Percentage change | % Change Total Pediatric COVID-19 Admissions from Prior Week |
| `confirmed_admissions_covid_18_49_chg_pct_ew` | `numconfc19newadmadult18to49pctchg` | COVID-19 | Percentage change | % Change Adult COVID-19 Admissions, 18–49 yrs, from Prior Week |
| `confirmed_admissions_covid_50_64_chg_pct_ew` | `numconfc19newadmadult50to64pctchg` | COVID-19 | Percentage change | % Change Adult COVID-19 Admissions, 50–64 yrs, from Prior Week |
| `confirmed_admissions_covid_65_74_chg_pct_ew` | `numconfc19newadmadult65to74pctchg` | COVID-19 | Percentage change | % Change Adult COVID-19 Admissions, 65–74 yrs, from Prior Week |
| `confirmed_admissions_covid_75_chg_pct_ew` | `numconfc19newadmadult75pluspctchg` | COVID-19 | Percentage change | % Change Adult COVID-19 Admissions, 75+ yrs, from Prior Week |
| `confirmed_admissions_covid_adult_chg_pct_ew` | `totalconfc19newadmadultpctchg` | COVID-19 | Percentage change | % Change Total Adult COVID-19 Admissions from Prior Week |
| `confirmed_admissions_covid_chg_pct_ew` | `totalconfc19newadmpctchg` | COVID-19 | Percentage change | % Change Total COVID-19 Admissions from Prior Week |
| `confirmed_admissions_flu_0_4_chg_pct_ew` | `numconfflunewadmped0to4pctchg` | Influenza | Percentage change | % Change Pediatric Influenza Admissions, 0–4 yrs, from Prior Week |
| `confirmed_admissions_flu_5_17_chg_pct_ew` | `numconfflunewadmped5to17pctchg` | Influenza | Percentage change | % Change Pediatric Influenza Admissions, 5–17 yrs, from Prior Week |
| `confirmed_admissions_flu_ped_chg_pct_ew` | `totalconfflunewadmpedpctchg` | Influenza | Percentage change | % Change Total Pediatric Influenza Admissions from Prior Week |
| `confirmed_admissions_flu_18_49_chg_pct_ew` | `numconfflunewadmadult18to49pctchg` | Influenza | Percentage change | % Change Adult Influenza Admissions, 18–49 yrs, from Prior Week |
| `confirmed_admissions_flu_50_64_chg_pct_ew` | `numconfflunewadmadult50to64pctchg` | Influenza | Percentage change | % Change Adult Influenza Admissions, 50–64 yrs, from Prior Week |
| `confirmed_admissions_flu_65_74_chg_pct_ew` | `numconfflunewadmadult65to74pctchg` | Influenza | Percentage change | % Change Adult Influenza Admissions, 65–74 yrs, from Prior Week |
| `confirmed_admissions_flu_75_chg_pct_ew` | `numconfflunewadmadult75pluspctchg` | Influenza | Percentage change | % Change Adult Influenza Admissions, 75+ yrs, from Prior Week |
| `confirmed_admissions_flu_adult_chg_pct_ew` | `totalconfflunewadmadultpctchg` | Influenza | Percentage change | % Change Total Adult Influenza Admissions from Prior Week |
| `confirmed_admissions_flu_chg_pct_ew` | `totalconfflunewadmpctchg` | Influenza | Percentage change | % Change Total Influenza Admissions from Prior Week |
| `confirmed_admissions_rsv_0_4_chg_pct_ew` | `numconfrsvnewadmped0to4pctchg` | RSV | Percentage change | % Change Pediatric RSV Admissions, 0–4 yrs, from Prior Week |
| `confirmed_admissions_rsv_5_17_chg_pct_ew` | `numconfrsvnewadmped5to17pctchg` | RSV | Percentage change | % Change Pediatric RSV Admissions, 5–17 yrs, from Prior Week |
| `confirmed_admissions_rsv_ped_chg_pct_ew` | `totalconfrsvnewadmpedpctchg` | RSV | Percentage change | % Change Total Pediatric RSV Admissions from Prior Week |
| `confirmed_admissions_rsv_18_49_chg_pct_ew` | `numconfrsvnewadmadult18to49pctchg` | RSV | Percentage change | % Change Adult RSV Admissions, 18–49 yrs, from Prior Week |
| `confirmed_admissions_rsv_50_64_chg_pct_ew` | `numconfrsvnewadmadult50to64pctchg` | RSV | Percentage change | % Change Adult RSV Admissions, 50–64 yrs, from Prior Week |
| `confirmed_admissions_rsv_65_74_chg_pct_ew` | `numconfrsvnewadmadult65to74pctchg` | RSV | Percentage change | % Change Adult RSV Admissions, 65–74 yrs, from Prior Week |
| `confirmed_admissions_rsv_75_chg_pct_ew` | `numconfrsvnewadmadult75pluspctchg` | RSV | Percentage change | % Change Adult RSV Admissions, 75+ yrs, from Prior Week |
| `confirmed_admissions_rsv_adult_chg_pct_ew` | `totalconfrsvnewadmadultpctchg` | RSV | Percentage change | % Change Total Adult RSV Admissions from Prior Week |
| `confirmed_admissions_rsv_chg_pct_ew` | `totalconfrsvnewadmpctchg` | RSV | Percentage change | % Change Total RSV Admissions from Prior Week |

</details>

#### 4. Seasonal Cumulative Admissions

Cumulative seasonal total admissions starting from week 40 through week 39 of the subsequent year:

<details markdown="1">
<summary><strong>Cumulative Seasonal Admissions</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `confirmed_admissions_covid_cumulative_ew` | `totalconfc19newadmcumulativeseasonalsum` | COVID-19 | Cumulative count | Cumulative Seasonal Total Confirmed New COVID-19 Admissions |
| `confirmed_admissions_flu_cumulative_ew` | `totalconfflunewadmcumulativeseasonalsum` | Influenza | Cumulative count | Cumulative Seasonal Total Confirmed New Influenza Admissions |
| `confirmed_admissions_rsv_cumulative_ew` | `totalconfrsvnewadmcumulativeseasonalsum` | RSV | Cumulative count | Cumulative Seasonal Total Confirmed New RSV Admissions |
| `confirmed_admissions_cumulative_ew` | `totalconfnewadmcumulativeseasonalsum` | Combined | Cumulative count | Cumulative Seasonal Total Confirmed New Respiratory Admissions (COVID-19, Influenza, RSV) |

</details>

#### 5. Hospital Reporting Compliance Metrics

Facility reporting compliance metrics covering reporting hospital counts, jurisdiction coverage percentages, week-over-week coverage changes, and threshold flags.

<details markdown="1">
<summary><strong>Hospital Reporting Facility Counts</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `hosprep_inpatient_beds_ew` | `numinptbedshosprep` | — | Facility count | N Hospitals Reporting Inpatient Beds |
| `hosprep_inpatient_beds_occupied_ew` | `numinptbedsocchosprep` | — | Facility count | N Hospitals Reporting Inpatient Beds Occupied |
| `hosprep_icu_beds_ew` | `numicubedshosprep` | — | Facility count | N Hospitals Reporting ICU Beds |
| `hosprep_icu_beds_occupied_ew` | `numicubedsocchosprep` | — | Facility count | N Hospitals Reporting ICU Beds Occupied |
| `hosprep_covid_inpatients_ew` | `totalconfc19hosppatshosprep` | COVID-19 | Facility count | N Hospitals Reporting Total COVID-19 Inpatients |
| `hosprep_flu_inpatients_ew` | `totalconffluhosppatshosprep` | Influenza | Facility count | N Hospitals Reporting Total Influenza Inpatients |
| `hosprep_rsv_inpatients_ew` | `totalconfrsvhosppatshosprep` | RSV | Facility count | N Hospitals Reporting Total RSV Inpatients |
| `hosprep_covid_icu_patients_ew` | `totalconfc19icupatshosprep` | COVID-19 | Facility count | N Hospitals Reporting COVID-19 ICU Patients |
| `hosprep_flu_icu_patients_ew` | `totalconffluicupatshosprep` | Influenza | Facility count | N Hospitals Reporting Influenza ICU Patients |
| `hosprep_rsv_icu_patients_ew` | `totalconfrsvicupatshosprep` | RSV | Facility count | N Hospitals Reporting RSV ICU Patients |
| `hosprep_confirmed_admissions_covid_ped_ew` | `totalconfc19newadmpedhosprep` | COVID-19 | Facility count | N Hospitals Reporting Pediatric COVID-19 Admissions |
| `hosprep_confirmed_admissions_covid_adult_ew` | `totalconfc19newadmadulthosprep` | COVID-19 | Facility count | N Hospitals Reporting Adult COVID-19 Admissions |
| `hosprep_confirmed_admissions_covid_ew` | `totalconfc19newadmhosprep` | COVID-19 | Facility count | N Hospitals Reporting COVID-19 Admissions |
| `hosprep_confirmed_admissions_flu_ped_ew` | `totalconfflunewadmpedhosprep` | Influenza | Facility count | N Hospitals Reporting Pediatric Influenza Admissions |
| `hosprep_confirmed_admissions_flu_adult_ew` | `totalconfflunewadmadulthosprep` | Influenza | Facility count | N Hospitals Reporting Adult Influenza Admissions |
| `hosprep_confirmed_admissions_flu_ew` | `totalconfflunewadmhosprep` | Influenza | Facility count | N Hospitals Reporting Influenza Admissions |
| `hosprep_confirmed_admissions_rsv_ped_ew` | `totalconfrsvnewadmpedhosprep` | RSV | Facility count | N Hospitals Reporting Pediatric RSV Admissions |
| `hosprep_confirmed_admissions_rsv_adult_ew` | `totalconfrsvnewadmadulthosprep` | RSV | Facility count | N Hospitals Reporting Adult RSV Admissions |
| `hosprep_confirmed_admissions_rsv_ew` | `totalconfrsvnewadmhosprep` | RSV | Facility count | N Hospitals Reporting RSV Admissions |
| `hosprep_inpatient_beds_occupied_pct_ew` | `pctinptbedsocchosprep` | — | Facility count | N Hospitals Reporting % Inpatient Beds Occupied |
| `hosprep_icu_beds_occupied_pct_ew` | `pcticubedsocchosprep` | — | Facility count | N Hospitals Reporting % ICU Beds Occupied |
| `hosprep_inpatient_beds_covid_pct_ew` | `pctconfc19inptbedshosprep` | COVID-19 | Facility count | N Hospitals Reporting % Inpatient Beds Occ. by COVID-19 |
| `hosprep_inpatient_beds_flu_pct_ew` | `pctconffluinptbedshosprep` | Influenza | Facility count | N Hospitals Reporting % Inpatient Beds Occ. by Influenza |
| `hosprep_inpatient_beds_rsv_pct_ew` | `pctconfrsvinptbedshosprep` | RSV | Facility count | N Hospitals Reporting % Inpatient Beds Occ. by RSV |
| `hosprep_icu_beds_covid_pct_ew` | `pctconfc19icubedshosprep` | COVID-19 | Facility count | N Hospitals Reporting % ICU Beds Occ. by COVID-19 |
| `hosprep_icu_beds_flu_pct_ew` | `pctconffluicubedshosprep` | Influenza | Facility count | N Hospitals Reporting % ICU Beds Occ. by Influenza |
| `hosprep_icu_beds_rsv_pct_ew` | `pctconfrsvicubedshosprep` | RSV | Facility count | N Hospitals Reporting % ICU Beds Occ. by RSV |
| `hosprep_inpatient_beds_occupied_adult_pct_ew` | `pctinptbedsoccadulthosprep` | — | Facility count | N Hospitals Reporting % Adult Inpatient Beds Occupied |
| `hosprep_inpatient_beds_occupied_ped_pct_ew` | `pctinptbedsoccpedhosprep` | — | Facility count | N Hospitals Reporting % Pediatric Inpatient Beds Occupied |
| `hosprep_icu_beds_occupied_adult_pct_ew` | `pcticubedsoccadulthosprep` | — | Facility count | N Hospitals Reporting % Adult ICU Beds Occupied |
| `hosprep_icu_beds_occupied_ped_pct_ew` | `pcticubedsoccpedhosprep` | — | Facility count | N Hospitals Reporting % Pediatric ICU Beds Occupied |
| `hosprep_inpatient_beds_covid_adult_pct_ew` | `pctconfc19inptbedsadulthosprep` | COVID-19 | Facility count | N Hospitals Reporting % Adult Inpatient Beds Occ. by COVID-19 |
| `hosprep_inpatient_beds_covid_ped_pct_ew` | `pctconfc19inptbedspedhosprep` | COVID-19 | Facility count | N Hospitals Reporting % Pediatric Inpatient Beds Occ. by COVID-19 |
| `hosprep_icu_beds_covid_adult_pct_ew` | `pctconfc19icubedsadulthosprep` | COVID-19 | Facility count | N Hospitals Reporting % Adult ICU Beds Occ. by COVID-19 |
| `hosprep_icu_beds_covid_ped_pct_ew` | `pctconfc19icubedspedhosprep` | COVID-19 | Facility count | N Hospitals Reporting % Pediatric ICU Beds Occ. by COVID-19 |
| `hosprep_inpatient_beds_flu_adult_pct_ew` | `pctconffluinptbedsadulthosprep` | Influenza | Facility count | N Hospitals Reporting % Adult Inpatient Beds Occ. by Influenza |
| `hosprep_inpatient_beds_flu_ped_pct_ew` | `pctconffluinptbedspedhosprep` | Influenza | Facility count | N Hospitals Reporting % Pediatric Inpatient Beds Occ. by Influenza |
| `hosprep_icu_beds_flu_adult_pct_ew` | `pctconffluicubedsadulthosprep` | Influenza | Facility count | N Hospitals Reporting % Adult ICU Beds Occ. by Influenza |
| `hosprep_icu_beds_flu_ped_pct_ew` | `pctconffluicubedspedhosprep` | Influenza | Facility count | N Hospitals Reporting % Pediatric ICU Beds Occ. by Influenza |
| `hosprep_inpatient_beds_rsv_adult_pct_ew` | `pctconfrsvinptbedsadulthosprep` | RSV | Facility count | N Hospitals Reporting % Adult Inpatient Beds Occ. by RSV |
| `hosprep_inpatient_beds_rsv_ped_pct_ew` | `pctconfrsvinptbedspedhosprep` | RSV | Facility count | N Hospitals Reporting % Pediatric Inpatient Beds Occ. by RSV |
| `hosprep_icu_beds_rsv_adult_pct_ew` | `pctconfrsvicubedsadulthosprep` | RSV | Facility count | N Hospitals Reporting % Adult ICU Beds Occ. by RSV |
| `hosprep_icu_beds_rsv_ped_pct_ew` | `pctconfrsvicubedspedhosprep` | RSV | Facility count | N Hospitals Reporting % Pediatric ICU Beds Occ. by RSV |
| `hosprep_covid_inpatients_icu_pct_ew` | `pctconfc19hosppatsicuhosprep` | COVID-19 | Facility count | N Hospitals Reporting % COVID-19 Inpatients in ICU |
| `hosprep_covid_inpatients_adult_icu_pct_ew` | `pctconfc19hosppatsicuadulthosprep` | COVID-19 | Facility count | N Hospitals Reporting % Adult COVID-19 Inpatients in ICU |
| `hosprep_covid_inpatients_ped_icu_pct_ew` | `pctconfc19hosppatsicupedhosprep` | COVID-19 | Facility count | N Hospitals Reporting % Pediatric COVID-19 Inpatients in ICU |
| `hosprep_flu_inpatients_icu_pct_ew` | `pctconffluhosppatsicuhosprep` | Influenza | Facility count | N Hospitals Reporting % Influenza Inpatients in ICU |
| `hosprep_flu_inpatients_adult_icu_pct_ew` | `pctconffluhosppatsicuadulthosprep` | Influenza | Facility count | N Hospitals Reporting % Adult Influenza Inpatients in ICU |
| `hosprep_flu_inpatients_ped_icu_pct_ew` | `pctconffluhosppatsicupedhosprep` | Influenza | Facility count | N Hospitals Reporting % Pediatric Influenza Inpatients in ICU |
| `hosprep_rsv_inpatients_icu_pct_ew` | `pctconfrsvhosppatsicuhosprep` | RSV | Facility count | N Hospitals Reporting % RSV Inpatients in ICU |
| `hosprep_rsv_inpatients_adult_icu_pct_ew` | `pctconfrsvhosppatsicuadulthosprep` | RSV | Facility count | N Hospitals Reporting % Adult RSV Inpatients in ICU |
| `hosprep_rsv_inpatients_ped_icu_pct_ew` | `pctconfrsvhosppatsicupedhosprep` | RSV | Facility count | N Hospitals Reporting % Pediatric RSV Inpatients in ICU |

</details>

<details markdown="1">
<summary><strong>Hospital Reporting Coverage Percentages</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `hosprep_pct_inpatient_beds_ew` | `numinptbedsperchosprep` | — | Percentage | % Hospitals Reporting Inpatient Beds |
| `hosprep_pct_inpatient_beds_occupied_ew` | `numinptbedsoccperchosprep` | — | Percentage | % Hospitals Reporting Inpatient Beds Occupied |
| `hosprep_pct_icu_beds_ew` | `numicubedsperchosprep` | — | Percentage | % Hospitals Reporting ICU Beds |
| `hosprep_pct_icu_beds_occupied_ew` | `numicubedsoccperchosprep` | — | Percentage | % Hospitals Reporting ICU Beds Occupied |
| `hosprep_pct_covid_inpatients_ew` | `totalconfc19hosppatsperc` | COVID-19 | Percentage | % Hospitals Reporting COVID-19 Inpatients |
| `hosprep_pct_flu_inpatients_ew` | `totalconffluhosppatsperc` | Influenza | Percentage | % Hospitals Reporting Influenza Inpatients |
| `hosprep_pct_rsv_inpatients_ew` | `totalconfrsvhosppatsperc` | RSV | Percentage | % Hospitals Reporting RSV Inpatients |
| `hosprep_pct_covid_icu_patients_ew` | `totalconfc19icupatsperchosprep` | COVID-19 | Percentage | % Hospitals Reporting COVID-19 ICU Patients |
| `hosprep_pct_flu_icu_patients_ew` | `totalconffluicupatsperchosprep` | Influenza | Percentage | % Hospitals Reporting Influenza ICU Patients |
| `hosprep_pct_rsv_icu_patients_ew` | `totalconfrsvicupatsperchosprep` | RSV | Percentage | % Hospitals Reporting RSV ICU Patients |
| `hosprep_pct_confirmed_admissions_covid_ped_ew` | `totalconfc19newadmpedper` | COVID-19 | Percentage | % Hospitals Reporting Pediatric COVID-19 Admissions |
| `hosprep_pct_confirmed_admissions_covid_adult_ew` | `totalconfc19newadmadultp` | COVID-19 | Percentage | % Hospitals Reporting Adult COVID-19 Admissions |
| `hosprep_pct_confirmed_admissions_covid_ew` | `totalconfc19newadmperchosprep` | COVID-19 | Percentage | % Hospitals Reporting COVID-19 Admissions |
| `hosprep_pct_confirmed_admissions_flu_ped_ew` | `totalconfflunewadmpedper` | Influenza | Percentage | % Hospitals Reporting Pediatric Influenza Admissions |
| `hosprep_pct_confirmed_admissions_flu_adult_ew` | `totalconfflunewadmadultp` | Influenza | Percentage | % Hospitals Reporting Adult Influenza Admissions |
| `hosprep_pct_confirmed_admissions_flu_ew` | `totalconfflunewadmperchosprep` | Influenza | Percentage | % Hospitals Reporting Influenza Admissions |
| `hosprep_pct_confirmed_admissions_rsv_ped_ew` | `totalconfrsvnewadmpedper` | RSV | Percentage | % Hospitals Reporting Pediatric RSV Admissions |
| `hosprep_pct_confirmed_admissions_rsv_adult_ew` | `totalconfrsvnewadmadultp` | RSV | Percentage | % Hospitals Reporting Adult RSV Admissions |
| `hosprep_pct_confirmed_admissions_rsv_ew` | `totalconfrsvnewadmperchosprep` | RSV | Percentage | % Hospitals Reporting RSV Admissions |
| `hosprep_pct_inpatient_beds_occupied_pct_ew` | `pctinptbedsoccperchosprep` | — | Percentage | % Hospitals Reporting % Inpatient Beds Occupied |
| `hosprep_pct_icu_beds_occupied_pct_ew` | `pcticubedsoccperchosprep` | — | Percentage | % Hospitals Reporting % ICU Beds Occupied |
| `hosprep_pct_inpatient_beds_covid_pct_ew` | `pctconfc19inptbedsperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Inpatient Beds Occ. by COVID-19 |
| `hosprep_pct_inpatient_beds_flu_pct_ew` | `pctconffluinptbedsperchosprep` | Influenza | Percentage | % Hospitals Reporting % Inpatient Beds Occ. by Influenza |
| `hosprep_pct_inpatient_beds_rsv_pct_ew` | `pctconfrsvinptbedsperchosprep` | RSV | Percentage | % Hospitals Reporting % Inpatient Beds Occ. by RSV |
| `hosprep_pct_icu_beds_covid_pct_ew` | `pctconfc19icubedsperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % ICU Beds Occ. by COVID-19 |
| `hosprep_pct_icu_beds_flu_pct_ew` | `pctconffluicubedsperchosprep` | Influenza | Percentage | % Hospitals Reporting % ICU Beds Occ. by Influenza |
| `hosprep_pct_icu_beds_rsv_pct_ew` | `pctconfrsvicubedsperchosprep` | RSV | Percentage | % Hospitals Reporting % ICU Beds Occ. by RSV |
| `hosprep_pct_inpatient_beds_occupied_adult_pct_ew` | `pctinptbedsoccadultperchosprep` | — | Percentage | % Hospitals Reporting % Adult Inpatient Beds Occupied |
| `hosprep_pct_inpatient_beds_occupied_ped_pct_ew` | `pctinptbedsoccpedperchosprep` | — | Percentage | % Hospitals Reporting % Pediatric Inpatient Beds Occupied |
| `hosprep_pct_icu_beds_occupied_adult_pct_ew` | `pcticubedsoccadultperchosprep` | — | Percentage | % Hospitals Reporting % Adult ICU Beds Occupied |
| `hosprep_pct_icu_beds_occupied_ped_pct_ew` | `pcticubedsoccpedperchosprep` | — | Percentage | % Hospitals Reporting % Pediatric ICU Beds Occupied |
| `hosprep_pct_inpatient_beds_covid_adult_pct_ew` | `pctconfc19inptbedsadultperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Adult Inpatient Beds Occ. by COVID-19 |
| `hosprep_pct_inpatient_beds_covid_ped_pct_ew` | `pctconfc19inptbedspedperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Pediatric Inpatient Beds Occ. by COVID-19 |
| `hosprep_pct_icu_beds_covid_adult_pct_ew` | `pctconfc19icubedsadultperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Adult ICU Beds Occ. by COVID-19 |
| `hosprep_pct_icu_beds_covid_ped_pct_ew` | `pctconfc19icubedspedperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Pediatric ICU Beds Occ. by COVID-19 |
| `hosprep_pct_inpatient_beds_flu_adult_pct_ew` | `pctconffluinptbedsadultperchosprep` | Influenza | Percentage | % Hospitals Reporting % Adult Inpatient Beds Occ. by Influenza |
| `hosprep_pct_inpatient_beds_flu_ped_pct_ew` | `pctconffluinptbedspedperchosprep` | Influenza | Percentage | % Hospitals Reporting % Pediatric Inpatient Beds Occ. by Influenza |
| `hosprep_pct_icu_beds_flu_adult_pct_ew` | `pctconffluicubedsadultperchosprep` | Influenza | Percentage | % Hospitals Reporting % Adult ICU Beds Occ. by Influenza |
| `hosprep_pct_icu_beds_flu_ped_pct_ew` | `pctconffluicubedspedperchosprep` | Influenza | Percentage | % Hospitals Reporting % Pediatric ICU Beds Occ. by Influenza |
| `hosprep_pct_inpatient_beds_rsv_adult_pct_ew` | `pctconfrsvinptbedsadultperchosprep` | RSV | Percentage | % Hospitals Reporting % Adult Inpatient Beds Occ. by RSV |
| `hosprep_pct_inpatient_beds_rsv_ped_pct_ew` | `pctconfrsvinptbedspedperchosprep` | RSV | Percentage | % Hospitals Reporting % Pediatric Inpatient Beds Occ. by RSV |
| `hosprep_pct_icu_beds_rsv_adult_pct_ew` | `pctconfrsvicubedsadultperchosprep` | RSV | Percentage | % Hospitals Reporting % Adult ICU Beds Occ. by RSV |
| `hosprep_pct_icu_beds_rsv_ped_pct_ew` | `pctconfrsvicubedspedperchosprep` | RSV | Percentage | % Hospitals Reporting % Pediatric ICU Beds Occ. by RSV |
| `hosprep_pct_covid_inpatients_icu_pct_ew` | `pctconfc19hosppatsicuperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % COVID-19 Inpatients in ICU |
| `hosprep_pct_covid_inpatients_adult_icu_pct_ew` | `pctconfc19hosppatsicuadultperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Adult COVID-19 Inpatients in ICU |
| `hosprep_pct_covid_inpatients_ped_icu_pct_ew` | `pctconfc19hosppatsicupedperchosprep` | COVID-19 | Percentage | % Hospitals Reporting % Pediatric COVID-19 Inpatients in ICU |
| `hosprep_pct_flu_inpatients_icu_pct_ew` | `pctconffluhosppatsicuperchosprep` | Influenza | Percentage | % Hospitals Reporting % Influenza Inpatients in ICU |
| `hosprep_pct_flu_inpatients_adult_icu_pct_ew` | `pctconffluhosppatsicuadultperchosprep` | Influenza | Percentage | % Hospitals Reporting % Adult Influenza Inpatients in ICU |
| `hosprep_pct_flu_inpatients_ped_icu_pct_ew` | `pctconffluhosppatsicupedperchosprep` | Influenza | Percentage | % Hospitals Reporting % Pediatric Influenza Inpatients in ICU |
| `hosprep_pct_rsv_inpatients_icu_pct_ew` | `pctconfrsvhosppatsicuperchosprep` | RSV | Percentage | % Hospitals Reporting % RSV Inpatients in ICU |
| `hosprep_pct_rsv_inpatients_adult_icu_pct_ew` | `pctconfrsvhosppatsicuadultperchosprep` | RSV | Percentage | % Hospitals Reporting % Adult RSV Inpatients in ICU |
| `hosprep_pct_rsv_inpatients_ped_icu_pct_ew` | `pctconfrsvhosppatsicupedperchosprep` | RSV | Percentage | % Hospitals Reporting % Pediatric RSV Inpatients in ICU |

</details>

<details markdown="1">
<summary><strong>Week-over-Week Change in Hospital Reporting Coverage</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `abs_chg_hosprep_pct_inpatient_beds_ew` | `numinptbedsperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting Inpatient Beds from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_occupied_ew` | `numinptbedsoccperchospre` | — | Percentage points change | Abs. Change in % Hospitals Reporting Inpatient Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_ew` | `numicubedsperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting ICU Beds from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_occupied_ew` | `numicubedsoccperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting ICU Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_covid_inpatients_ew` | `totalconfc19hosppatsperc_1` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting COVID-19 Inpatients from Prior Week |
| `abs_chg_hosprep_pct_flu_inpatients_ew` | `totalconffluhosppatsperc_1` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting Influenza Inpatients from Prior Week |
| `abs_chg_hosprep_pct_rsv_inpatients_ew` | `totalconfrsvhosppatsperc_1` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting RSV Inpatients from Prior Week |
| `abs_chg_hosprep_pct_covid_icu_patients_ew` | `totalconfc19icupatsperch` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting COVID-19 ICU Patients from Prior Week |
| `abs_chg_hosprep_pct_flu_icu_patients_ew` | `totalconffluicupatsperch` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting Influenza ICU Patients from Prior Week |
| `abs_chg_hosprep_pct_rsv_icu_patients_ew` | `totalconfrsvicupatsperch` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting RSV ICU Patients from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_covid_ped_ew` | `totalconfc19newadmpedper_1` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting Pediatric COVID-19 Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_covid_adult_ew` | `totalconfc19newadmadultp_1` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting Adult COVID-19 Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_covid_ew` | `totalconfc19newadmpercho` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting COVID-19 Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_flu_ped_ew` | `totalconfflunewadmpedper_1` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting Pediatric Influenza Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_flu_adult_ew` | `totalconfflunewadmadultp_1` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting Adult Influenza Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_flu_ew` | `totalconfflunewadmpercho` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting Influenza Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_rsv_ped_ew` | `totalconfrsvnewadmpedper_1` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting Pediatric RSV Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_rsv_adult_ew` | `totalconfrsvnewadmadultp_1` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting Adult RSV Admissions from Prior Week |
| `abs_chg_hosprep_pct_confirmed_admissions_rsv_ew` | `totalconfrsvnewadmpercho` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting RSV Admissions from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_occupied_pct_ew` | `pctinptbedsoccperchospre` | — | Percentage points change | Abs. Change in % Hospitals Reporting % Inpatient Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_occupied_pct_ew` | `pcticubedsoccperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting % ICU Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_covid_pct_ew` | `pctconfc19inptbedspercho` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Inpatient Beds Occ. by COVID-19 from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_flu_pct_ew` | `pctconffluinptbedspercho` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Inpatient Beds Occ. by Influenza from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_rsv_pct_ew` | `pctconfrsvinptbedspercho` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Inpatient Beds Occ. by RSV from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_covid_pct_ew` | `pctconfc19icubedsperchos` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % ICU Beds Occ. by COVID-19 from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_flu_pct_ew` | `pctconffluicubedsperchos` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % ICU Beds Occ. by Influenza from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_rsv_pct_ew` | `pctconfrsvicubedsperchos` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % ICU Beds Occ. by RSV from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_occupied_adult_pct_ew` | `pctinptbedsoccadultperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting % Adult Inpatient Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_occupied_ped_pct_ew` | `pctinptbedsoccpedperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric Inpatient Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_occupied_adult_pct_ew` | `pcticubedsoccadultperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting % Adult ICU Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_occupied_ped_pct_ew` | `pcticubedsoccpedperchosprepabschg` | — | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric ICU Beds Occupied from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_covid_adult_pct_ew` | `pctconfc19inptbedsadultperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Adult Inpatient Beds Occ. by COVID-19 from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_covid_ped_pct_ew` | `pctconfc19inptbedspedperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric Inpatient Beds Occ. by COVID-19 from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_covid_adult_pct_ew` | `pctconfc19icubedsadultperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Adult ICU Beds Occ. by COVID-19 from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_covid_ped_pct_ew` | `pctconfc19icubedspedperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric ICU Beds Occ. by COVID-19 from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_flu_adult_pct_ew` | `pctconffluinptbedsadultperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Adult Inpatient Beds Occ. by Influenza from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_flu_ped_pct_ew` | `pctconffluinptbedspedperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric Inpatient Beds Occ. by Influenza from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_flu_adult_pct_ew` | `pctconffluicubedsadultperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Adult ICU Beds Occ. by Influenza from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_flu_ped_pct_ew` | `pctconffluicubedspedperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric ICU Beds Occ. by Influenza from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_rsv_adult_pct_ew` | `pctconfrsvinptbedsadultperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Adult Inpatient Beds Occ. by RSV from Prior Week |
| `abs_chg_hosprep_pct_inpatient_beds_rsv_ped_pct_ew` | `pctconfrsvinptbedspedperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric Inpatient Beds Occ. by RSV from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_rsv_adult_pct_ew` | `pctconfrsvicubedsadultperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Adult ICU Beds Occ. by RSV from Prior Week |
| `abs_chg_hosprep_pct_icu_beds_rsv_ped_pct_ew` | `pctconfrsvicubedspedperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric ICU Beds Occ. by RSV from Prior Week |
| `abs_chg_hosprep_pct_covid_inpatients_icu_pct_ew` | `pctconfc19hosppatsicuperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % COVID-19 Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_covid_inpatients_adult_icu_pct_ew` | `pctconfc19hosppatsicuadultperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Adult COVID-19 Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_covid_inpatients_ped_icu_pct_ew` | `pctconfc19hosppatsicupedperchosprepabschg` | COVID-19 | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric COVID-19 Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_flu_inpatients_icu_pct_ew` | `pctconffluhosppatsicuperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Influenza Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_flu_inpatients_adult_icu_pct_ew` | `pctconffluhosppatsicuadultperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Adult Influenza Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_flu_inpatients_ped_icu_pct_ew` | `pctconffluhosppatsicupedperchosprepabschg` | Influenza | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric Influenza Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_rsv_inpatients_icu_pct_ew` | `pctconfrsvhosppatsicuperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % RSV Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_rsv_inpatients_adult_icu_pct_ew` | `pctconfrsvhosppatsicuadultperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Adult RSV Inpatients in ICU from Prior Week |
| `abs_chg_hosprep_pct_rsv_inpatients_ped_icu_pct_ew` | `pctconfrsvhosppatsicupedperchosprepabschg` | RSV | Percentage points change | Abs. Change in % Hospitals Reporting % Pediatric RSV Inpatients in ICU from Prior Week |

</details>

<details markdown="1">
<summary><strong>Reporting Threshold Flags</strong></summary>

| Indicator Name | CDC Field Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| `flag_hosprep_covid_admissions_above80pct_ew` | `totalconfc19newadmperchosprepabove80pct` | COVID-19 | Binary flag (0/1) | % Hospitals Reporting Total New COVID-19 Admissions Above 80% |
| `flag_hosprep_covid_admissions_above90pct_ew` | `totalconfc19newadmperchosprepabove90pct` | COVID-19 | Binary flag (0/1) | % Hospitals Reporting Total New COVID-19 Admissions Above 90% |
| `flag_hosprep_flu_admissions_above80pct_ew` | `totalconfflunewadmperchosprepabove80pct` | Influenza | Binary flag (0/1) | % Hospitals Reporting Total New Influenza Admissions Above 80% |
| `flag_hosprep_flu_admissions_above90pct_ew` | `totalconfflunewadmperchosprepabove90pct` | Influenza | Binary flag (0/1) | % Hospitals Reporting Total New Influenza Admissions Above 90% |
| `flag_hosprep_rsv_admissions_above80pct_ew` | `totalconfrsvnewadmperchosprepabove80pct` | RSV | Binary flag (0/1) | % Hospitals Reporting Total New RSV Admissions Above 80% |
| `flag_hosprep_rsv_admissions_above90pct_ew` | `totalconfrsvnewadmperchosprepabove90pct` | RSV | Binary flag (0/1) | % Hospitals Reporting Total New RSV Admissions Above 90% |

</details>

---

## Estimation

### Metric Definition

Signals correspond to source fields in the upstream CDC NHSN Hospital Respiratory Data release (see the [CDC Socrata dataset `ua7e-t2fy`](https://data.cdc.gov/Public-Health-Surveillance/Weekly-Hospital-Respiratory-Data-HRD-Metrics-by-Ju/ua7e-t2fy/about_data)). In each table above, the "CDC Field Name" column records the original column identifier (`fieldName`) from the CDC dataset. Metrics fall into several distinct families:

- **Counts**. Raw counts (e.g., `confirmed_admissions_*_ew`, `*_inpatients_*_ew`, `inpatient_beds_*_ew`, `hosprep_*_ew`, `*_cumulative_ew`).
- **Percentages**. Ratios multiplied by 100. Identified by `_pct_` in the signal name (e.g., `inpatient_beds_occupied_pct_ew`, `confirmed_admissions_*_pct_ew`, `*_inpatients_icu_pct_ew`).
- **Rates per 100,000 Population**. Confirmed new admissions normalized per 100,000 population, calculated using U.S. Census Bureau population estimates (with national rates incorporating U.S. territories). Identified by `_per100k_` (e.g., `confirmed_admissions_*_per100k_ew`).
- **Week-over-Week Percent Change**. Relative percent change in weekly admissions compared to the prior week. Identified by `_chg_pct_` (e.g., `confirmed_admissions_*_chg_pct_ew`).
- **Reporting Coverage Percentages**. Percentage of total active facilities in the jurisdiction submitting data for each metric. Identified by `hosprep_pct_` (e.g., `hosprep_pct_*_ew`).
- **Absolute Percentage Points Change**. Week-over-week absolute change in facility reporting coverage percentage points. Identified by the prefix `abs_chg_` (e.g., `abs_chg_hosprep_pct_*_ew`).
- **Reporting Threshold Flags**. Binary indicator variables taking value `1` if jurisdiction hospital reporting coverage meets or exceeds the threshold (80% or 90%), and `0` otherwise. Identified by the prefix `flag_` (e.g., `flag_hosprep_*_ew`).

### Temporal Handling

All signals are reported weekly and labeled by the Saturday week-ending date (`reference_time`). The time window represented depends on the metric:

- **New admissions** are measured across the full 7-day surveillance week (Sunday through Saturday).
- **Bed capacity, occupancy, and patient census** represent single-day snapshot values captured on Wednesday of the reporting week.

The CDC publishes a preliminary weekly file about 4 days after the reference week ends (Wednesday), followed by a finalized file 2 to 3 days later (Friday or Saturday). Both releases share the same signal names and are distinguished by publication date (`report_time`). Default snapshot queries return the latest finalized values, while earlier preliminary releases remain accessible by specifying a past `snapshot_date` or through the `/archive/` endpoint.

### Geographic Handling

The source file carries values for states (`state`), HHS regions (`hhs`), and the nation (`nation`), which Delphi reads directly from the upstream CDC file.

Census divisions (`census_division`) and census regions (`census_region`) are derived from state values:
- Count metrics are summed directly across member states based on the [U.S. Census Bureau regions and divisions](https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf).
- Rate and percentage metrics are aggregated using population-weighted averages based on 2020 U.S. Census state populations.
- Week-over-week percentage change signals are omitted from census division and census region roll-ups.

Values are ingested directly or aggregated without imputation, so `fill_method` is always `source`.

---

## Relationship to V4

The V4 `nhsn` source published admission counts for nation, HHS regions, and state. The signal names that overlap remain the same in the V4 to V5 transition.

| V4 Signal | V5 Signal | Notes |
| :--- | :--- | :--- |
| `confirmed_admissions_covid_ew` | `confirmed_admissions_covid_ew` | Exact match |
| `confirmed_admissions_flu_ew` | `confirmed_admissions_flu_ew` | Exact match |
| `confirmed_admissions_rsv_ew` | `confirmed_admissions_rsv_ew` | Exact match |
| `hosprep_confirmed_admissions_covid_ew` | `hosprep_confirmed_admissions_covid_ew` | Exact match |
| `hosprep_confirmed_admissions_flu_ew` | `hosprep_confirmed_admissions_flu_ew` | Exact match |
| `hosprep_confirmed_admissions_rsv_ew` | `hosprep_confirmed_admissions_rsv_ew` | Exact match |
| `confirmed_admissions_covid_ew_prelim` | `confirmed_admissions_covid_ew` | Folded into revision history via `report_time` |
| `confirmed_admissions_flu_ew_prelim` | `confirmed_admissions_flu_ew` | Folded into revision history via `report_time` |
| `confirmed_admissions_rsv_ew_prelim` | `confirmed_admissions_rsv_ew` | Folded into revision history via `report_time` |
| `hosprep_confirmed_admissions_covid_ew_prelim` | `hosprep_confirmed_admissions_covid_ew` | Folded into revision history via `report_time` |
| `hosprep_confirmed_admissions_flu_ew_prelim` | `hosprep_confirmed_admissions_flu_ew` | Folded into revision history via `report_time` |
| `hosprep_confirmed_admissions_rsv_ew_prelim` | `hosprep_confirmed_admissions_rsv_ew` | Folded into revision history via `report_time` |
| *(not available)* | *(313 additional signals)* | New in V5 |

What changed in V5:

- **New Signals.** V5 expands the signal catalog from 6 basic admission counts to 319 comprehensive indicators.
- **Expanded Geographies.** V5 adds census divisions and census regions.
- **Preliminary Data.** The CDC publishes a preliminary weekly file a few days ahead of the finalized file. V4 presented the preliminary file as separate `_prelim` signals. V5 writes both files to the same signal names, so the preliminary numbers appear as an earlier release and the finalized numbers supersede them on the next update. Read a past `snapshot_date`, or use the `/archive/` endpoint, to recover the preliminary values.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`state`, `hhs`, `census_division`, `census_region`, `nation`). |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., `ca` for California, `us` for national). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation, always `source` for this source. |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation, labeled by Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded measurement. |

---

## Missingness & Privacy

The source applies no cell suppression or volume masking. All reported counts and percentages are published directly without privacy thresholds.

Unobserved values reflect facility non-reporting and changes in reporting mandates over time:

- Reference dates before December 1, 2020 predate routine data quality review procedures, such as automated exclusion of invalid values and systematic error correction. Data from this early period may contain anomalies.
- Reference dates through April 30, 2024 reflect a federal reporting mandate instituted by the Department of Health and Human Services.
- Reference dates between May 1, 2024 and October 31, 2024 fall into a voluntary reporting interval following the expiration of the original federal mandate. Facility participation dropped significantly during these months, meaning reported admissions undercount total admissions.
- Reference dates beginning November 1, 2024 reflect the current federal reporting mandate established under updated CMS conditions of participation.

Missing hospital reports are not imputed. In census division and region roll-ups, missing states are omitted from the sum.

---

## Limitations

NHSN collects data from acute care hospitals. Psychiatric, rehabilitation, and religious non-medical facilities are excluded.

Hospital counts reflect the NHSN unique hospital identifier rather than the CMS certification number. Only facilities designated as active reporters are included.

Admissions during the voluntary reporting window from May 1, 2024 through October 31, 2024 are incomplete because many hospitals did not submit data.

RSV data collected before November 1, 2024 has low completeness. Only a small fraction of hospitals voluntarily reported RSV admissions prior to the November 2024 mandate, undercounting true admissions by an estimated two orders of magnitude. The CDC [RSV-NET](https://www.cdc.gov/rsv/php/surveillance/rsv-net.html) surveillance network offers a more reliable historical benchmark for RSV admissions during that period.

Administration of this surveillance system moved from HHS Protect to NHSN in late 2023. Comparisons across the transition indicate that COVID-19 and influenza figures are largely consistent between both systems. Notable discrepancies exist for a few states, with Georgia until 2023, Louisiana, Nevada, Puerto Rico in late 2020, and Tennessee reporting lower counts in legacy HHS Protect files than in NHSN.

These indicators reflect direct census counts from reporting hospitals rather than statistical samples. Standard errors and sample sizes do not apply.

---

## Lag & Backfill

The CDC publishes preliminary weekly data on Wednesdays, approximately 4 days after the reference week ends. Finalized weekly files publish on Fridays or Saturdays, 6 to 7 days after the reference week ends. In V5, preliminary data is ingested first and then superseded by finalized data under the same signal name.

The CDC continuously updates data for prior weeks as facilities submit late or corrected reports. Most revisions occur within 2 months of initial release. Older data rarely changes.

Approximately 20 percent of values reported within the preceding 2 months undergo revisions. These adjustments usually occur only once or twice per observation. Revisions generally increase reported counts as late submissions arrive, with a median difference of 2 percent between initial and final values.

Large revisions occur occasionally when a facility submits bulk retrospective corrections. Revision volume also varies geographically. For example, Texas experiences more frequent revisions than most states but with small shifts, typically with a median change below 0.1 percent. Other states, including Idaho, New Hampshire, Hawaii, and North Dakota, have exhibited higher percentage volatility when revised.

---

## Source and Licensing

This dataset is published by the CDC via HealthData.gov under [Public Domain U.S. Government](https://www.usa.gov/government-works) terms.
