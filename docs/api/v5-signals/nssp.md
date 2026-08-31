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
| **Temporal Granularity** | Weekly (Epiweeks; Saturdays) |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | 2022-10-01 |
| **Date of Last Revision** | Versioned snapshot (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | `fill_method` |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The National Syndromic Surveillance Program (NSSP) monitors emergency department (ED) visits for respiratory illnesses across participating facilities in the United States. Ingestion processes weekly data published by the CDC, reporting percentages of ED visits associated with COVID-19, Influenza, RSV, and Acute Respiratory Illness (ARI).

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `pct_ed_visits_covid` | COVID-19 | Percentage | Percentage of ED visits with a discharge diagnosis of COVID-19. |
| `smoothed_pct_ed_visits_covid` | COVID-19 | Percentage (3-week average) | 3-week trailing smoothed percentage of ED visits with a discharge diagnosis of COVID-19. |
| `pct_ed_visits_influenza` | Influenza | Percentage | Percentage of ED visits with a discharge diagnosis of Influenza. |
| `smoothed_pct_ed_visits_influenza` | Influenza | Percentage (3-week average) | 3-week trailing smoothed percentage of ED visits with a discharge diagnosis of Influenza. |
| `pct_ed_visits_rsv` | RSV | Percentage | Percentage of ED visits with a discharge diagnosis of RSV. |
| `smoothed_pct_ed_visits_rsv` | RSV | Percentage (3-week average) | 3-week trailing smoothed percentage of ED visits with a discharge diagnosis of RSV. |
| `pct_ed_visits_combined` | Combined | Percentage | Percentage of ED visits with a discharge diagnosis of COVID-19, Influenza, or RSV. |
| `smoothed_pct_ed_visits_combined` | Combined | Percentage (3-week average) | 3-week trailing smoothed percentage of ED visits with a discharge diagnosis of COVID-19, Influenza, or RSV. |
| `pct_ed_visits_ari` | ARI | Percentage | Percentage of ED visits with a discharge diagnosis of acute respiratory illness. |

---

## Estimation

### Geographic Aggregation

Source files natively contain values for the nation (`nation`), counties (`county`), and Health Service Areas (`hsa_nci`). Delphi extracts these levels directly.

For other geographic levels, Delphi aggregates values using population weights:
- State (`state`), HHS regions (`hhs`), census regions (`census_region`), and census divisions (`census_division`) are aggregated from state records.
- Hospital Referral Regions (`hrr`) and Metropolitan Statistical Areas (`msa`) are aggregated from county records.

Because NSSP metrics are percentages, aggregating areas with missing subunits requires imputation strategies:
- Zero-fill (`zero`): Missing subunits are treated as zero during aggregation.
- Average-fill (`ave`): Aggregation is weighted only across reporting subunits.

### Temporal Handling

All weekly metrics align to the Saturday week-ending date (`time_value`).

### Smoothing

Smoothed signals are computed and published directly by the CDC using a 3-week trailing moving average.

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic granularity level (`nation`, `state`, `hhs`, `census_division`, `census_region`, `hrr`, `msa`, `county`, `hsa_nci`). |
| `geo_value` | Primary Key | Geographic entity code (e.g. `ca` for California, `06001` for Alameda County). |
| `fill_method` | Primary Key (Extra Key) | Imputation method used during aggregation (`source`, `zero`, `ave`). |
| `time_value` | Primary Key | Saturday week-ending date (`YYYY-MM-DD`). |
| `value` | Value Column | Percentage of ED visits (0–100). |

### Extra Keys

#### Imputation Methods (`fill_method`)

| Value | Description |
| :--- | :--- |
| `source` | Native reported data for nation, county, and HSA, plus direct state pass-through. |
| `zero` | Geographic aggregations where missing subunits are treated as zero. |
| `ave` | Geographic aggregations weighted only across subunits that reported data. |

### Example Query

```text
signal=pct_ed_visits_covid&geo_type=state&geo_values=tx&extra_keys=fill_method:source&time_values=2024-01-06
```

---

## Missingness & Privacy

The CDC suppresses values for facilities or counties with low patient volumes. Suppressed source values are treated as missing during ingestion and handled according to the selected `fill_method` in geographic aggregations.

---

## Limitations

Emergency department participation varies by state and healthcare facility network. Discharge diagnoses reflect clinical coding upon patient discharge and are not verified by centralized laboratory testing.

---

## Lag & Backfill

Weekly files are released with a lag of approximately one week. As facilities submit late encounter records, CDC revises historical weeks in subsequent snapshots.

---

## Source & Licensing

Data is published by the Centers for Disease Control and Prevention (CDC) National Syndromic Surveillance Program and is available in the public domain.

---

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **2024-11-01**. Initial release on Delphi V5 API.

</details>
