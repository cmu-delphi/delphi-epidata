---
title: NWSS Wastewater
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 4
---

# National Wastewater Surveillance System (NWSS)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nwss` |
| **Data Source** | [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html) |
| **Geographic Levels** | `sewershed` |
| **Temporal Granularity** | Weekly |
| **Reporting Cadence** | Weekly (typically updated on Fridays) |
| **Temporal Scope Start** | 2020-01-14 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | `nwss_source`, `sample_index` |
| **License** | [U.S. Government Public Domain](https://www.usa.gov/government-works) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html) is a CDC-led effort to track the presence of SARS-CoV-2, influenza, RSV, Mpox, and Measles in wastewater throughout the United States. The project was launched in September 2020 and is ongoing. Delphi ingests un-versioned wastewater concentration data from several public Socrata API datasets provided by the CDC.

In the Delphi API, wastewater data is served at the `sewershed` level (individual treatment plant or grab sample site level).

---

## Indicators (Signals)

Wastewater signals are constructed by combining a pathogen prefix with a post-processing suffix in the format `<pathogen_prefix>_<suffix>`. For example, combining the prefix `covid` with the suffix `avg_conc_lin` constructs the signal `covid_avg_conc_lin`.

### Pathogen Prefixes

| Prefix | Pathogen | Target PCR | Socrata Endpoint |
| :--- | :--- | :--- | :--- |
| `covid` | COVID-19 | `sars-cov-2` | [j9g8-acpt](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-SARS-CoV-2/j9g8-acpt/about_data) |
| `flu` | Influenza A | `fluav` | [ymmh-divb](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Influenza-A/ymmh-divb/about_data) |
| `flu_h5` | Avian Influenza A (H5) | `fluav a h5` | [mtpu-urpp](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-H5-Influenza-A/mtpu-urpp/about_data) |
| `rsv` | RSV | `rsv` | [45cq-cw4i](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i/about_data) |
| `measles` | Measles | `mev_wt` | [akvg-8vrb](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Measles/akvg-8vrb/about_data) |
| `mpox_all` | Mpox (All Clades) | `hmpxv` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |
| `mpox_clade_i` | Mpox Clade I | `hmpxv clade i` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |
| `mpox_clade_ii` | Mpox Clade II | `hmpxv clade ii` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |
| `mpox_nvo` | Mpox Non-Variola Orthopoxvirus | `nvo` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |

### Metric Suffixes

| Suffix | Metric Type | Description |
| :--- | :--- | :--- |
| `avg_conc` | Average Concentration | Concentration of the PCR target back-calculated to unconcentrated sample basis |
| `avg_conc_lin` | Linearized Average Concentration | Concentration of the PCR target on a per sample amount basis where all values are on a linear (not log10) concentration basis |
| `flowpop_lin` | Flow-Population | Flow-population normalized concentration (copies/person/day) |
| `mic_lin` | Microbial | Microbial normalized concentration (unitless ratio) |

For more details on the columns, see one of the socrata endpoints, e.g. [RSV](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i/about_data) which provides descriptions of all columns.

---

## Estimation

### Metric Definition

Wastewater signals report target pathogen concentrations measured across municipal sewersheds. Upstream data sources provide concentrations either as unnormalized post-processed values or normalized indicators.

#### Post-Processing Methods

Unnormalized metrics report target pathogen concentrations back-calculated to the unconcentrated sample basis without adjustments for flow or population:

| Method | Suffix | Description |
| :--- | :--- | :--- |
| **Average Concentration** | `avg_conc` | Concentration of the PCR target back-calculated to unconcentrated sample basis. Non-detections are typically reported as zero. |
| **Linearized Average Concentration** | `avg_conc_lin` | Concentration of the PCR target on a per-sample amount basis where all values are on a linear (not log10) concentration basis. |

#### Normalization Methods

Direct viral concentration is not a robust indicator of the number and severity of cases in the sewershed. In wastewater systems that mix drainage and sewage, for example, the effluent will be significantly diluted whenever there is rain. In order to produce indicators that are more strongly related to pathogen levels, signals are corrected using two normalization approaches:

| Method | Suffix | Formula | Description |
| :--- | :--- | :---: | :--- |
| **Flow-population** | `flowpop_lin` | $$\frac{v \cdot r}{p}$$ | Applied to concentrations $$v$$ from raw wastewater, where $$r$$ is 24-hour flow rate and $$p$$ is population served. Values report viral gene copies per person per day, tracking the total number of individuals shedding the pathogen. |
| **Microbial** | `mic_lin` | $$\frac{v}{c_{\text{marker}}}$$ | Applied to concentrated sludge samples, dividing target concentration $$v$$ by fecal biomarker concentration $$c_{\text{marker}}$$ (such as PMMoV, *Bacteroides* HF183, or *Lachnospiraceae* Lachno3). Values are unitless ratios that track the proportion of individuals shedding the pathogen. |

### Temporal Handling

Dates refer to the sample collection date (`reference_time`), rather than the laboratory result or CDC report publication date.

### Geographic Handling

NWSS data is collected from wastewater monitoring sites within municipal sewer networks. Each facility or sampling location in the system is identified by a unique sewershed identifier code (`geo_value`), representing the geographic drainage area whose wastewater flows through that facility. For detail on site selection and surveillance methodology, see the [CDC NWSS data sources documentation](https://www.cdc.gov/wastewater/about/index.html#cdc_survey_profile_how_surveys_are_conducted-data-sources).

Because NWSS data is served exclusively at the native `sewershed` level with no spatial aggregation or imputation performed, the `fill_method` column is always `source`.

To map sewersheds to standard geographic regions, consult the [auxiliary metadata table](#auxiliary-tables) via the `/aux_data/` endpoint. Because sewersheds follow drainage basins rather than administrative borders, the auxiliary table provides intersecting location metadata—including the state (`state_territory`), primary county (`county_fips`), all intersected counties (`counties_served`), and the population served (`population_served`).

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | Signal identifier. |
| `report_time` | Primary Key | date | Publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (`sewershed`). |
| `geo_value` | Primary Key | string | Sewershed identifier code. |
| `fill_method` | Primary Key | string | Imputation method (`source`). |
| `nwss_source` | Primary Key (Extra Key) | string | Laboratory or reporting network provider. |
| `sample_index` | Primary Key (Extra Key) | string | Integer identifier mapped to the unique sample ID. |
| `reference_time` | Primary Key | date | Sample collection date (`YYYY-MM-DD`). |
| `pcr_target` | Value Column | string | Target pathogen or assay identifier. |
| `value` | Value Column | float | Measured concentration or normalized value. |

### Extra keys

Wastewater records depend on sample collection and laboratory dimensions:
- `nwss_source`: Identifies the testing network or data provider.
- `sample_index`: Disambiguates multiple samples or replicates collected on the same date for a sewershed.

Available data providers in `nwss_source` include:

| Provider | Reporting Window | Description |
| :--- | :--- | :--- |
| `CDC_Verily` | 2023-10-30 to present | Data analyzed by [Verily](https://verily.com/solutions/public-health/wastewater) on behalf of the CDC directly. |
| `State_Territory` | 2020-06-21 to present | Data reported by state, territorial, and local public health agencies. |
| `WastewaterSCAN` | 2021-12-26 to present | Data analyzed by [WastewaterSCAN](https://www.wastewaterscan.org/en) and shared with the NWSS. |
| `CDC_Biobot` | 2020 to 2023 | Data analyzed by [Biobot](https://biobot.io/) and shared with the NWSS. |

An unfiltered query returns rows across all provider and sample dimensions. Queries can filter to specific values using the `extra_keys` parameter (for example, `extra_keys=nwss_source:CDC_Verily` or `extra_keys=sample_index:1`).

### Auxiliary tables

Since wastewater treatment facilities have sample-specific traits (such as populations served and lab methodologies) that can change with time, this metadata is served in a companion table via the `/aux_data/` endpoint at `https://delphi.cmu.edu/epidata/v5/aux_data/?source=nwss`. For query parameters, filtering, and examples, see the [auxiliary data documentation](../v5_api_queries.md#auxiliary-data-parameters).

Records are identified by `report_time`, `geo_value`, `reference_time`, `nwss_source`, `sample_index`, and `pcr_target`.

Its value columns report facility demographics (`state_territory`, `county_fips`, `counties_served`, `population_served`), sample specifics (`sample_type`, `sample_matrix`, `sample_location`, `flow_rate`), laboratory methods (`concentration_method`, `extraction_method`, `major_lab_method`, `pcr_type`, `pcr_target_units`, `lod_sewage`), and pipeline metrics (`rec_eff_percent`).

---

## Missingness & Privacy

To protect privacy, the CDC does not report data for sewersheds serving fewer than 3,000 people. Data from facility-specific sampling locations, institution-specific sites, and tribal communities are also unavailable unless approved by the local jurisdiction.

Testing laboratories report non-detections as zero or values below the limit of detection. Unobserved collection dates or non-reporting facilities appear as absent rows rather than null values.

---

## Limitations

The NWSS is still expanding to get coverage nationwide, so it is currently an uneven sample; the largest signals above cover ~42 million people as of March 2024. Around 80% of the US is served by municipal wastewater collection systems, or around 272 million.

Data providers and laboratory methods changed over time. For example, the CDC transitioned its primary contract from Biobot to Verily in late 2023. Measurements across different providers differ in baseline levels and cannot be directly compared without adjustment.

---

## Lag & Backfill

These signals are released weekly, typically on Fridays, with approximately 4 to 7 days of latency. Historical data files are updated weekly as laboratories submit delayed samples or revised test results.

---

## Source and Licensing

This data source originates from the CDC [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html). Site-level data is provided un-versioned via the CDC Socrata open data portal across pathogen-specific endpoints: [SARS-CoV-2](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-SARS-CoV-2/j9g8-acpt) (`j9g8-acpt`), [Influenza A](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Influenza-A/ymmh-divb) (`ymmh-divb`), [H5 Influenza A](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-H5-Influenza-A/mtpu-urpp) (`mtpu-urpp`), [RSV](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i) (`45cq-cw4i`), [Mpox](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz) (`xpxn-rzgz`), and [Measles](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Measles/akvg-8vrb) (`akvg-8vrb`).

Wastewater data is collected from state, territorial, and local public health agencies, [Verily](https://verily.com/solutions/public-health/wastewater), and [WastewaterSCAN](https://www.wastewaterscan.org/en). Anyone seeking to use WastewaterSCAN data for research or non-public health purposes must contact the WastewaterSCAN team and follow their [citation policy](https://data.wastewaterscan.org/about/#18).

This public dataset is published under [U.S. Government Public Domain](https://www.usa.gov/government-works) terms.
