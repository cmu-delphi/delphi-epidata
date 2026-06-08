---
title: NWSS Wastewater
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
---

# National Wastewater Surveillance System (NWSS)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nwss` |
| **Data Source** | [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html) |
| **Geographic Levels** | sewershed (see [Sampling Sites](#sampling-sites)) |
| **Temporal Granularity** | Weekly |
| **Reporting Cadence** | Weekly (typically updated on Fridays) |
| **Date of last data revision:** | Never (see [data revision docs](#changelog)) |
| **Temporal Scope Start** | 2020-01-14 |
| **License** | [Public Domain US Government](https://www.usa.gov/government-works) |

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

No changes so far.

</details>

## Overview
{: .no_toc}

The [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html) is a CDC-led effort to track the presence of SARS-CoV-2, influenza, RSV, Mpox, and Measles in wastewater throughout the United States.
The project was launched in September 2020 and is ongoing. Delphi ingests un-versioned wastewater concentration data from several public Socrata API datasets provided by the CDC.

In the Delphi API, wastewater data is served at the `sewershed` level (individual treatment plant or grab sample site level).

## Sampling Sites

NWSS data is collected from wastewater monitoring sites within the sewer network. Each facility in the system is identified by a unique sewershed identifier, which represents the geographic area whose wastewater flows through that facility.

The CDC coordinates data collection across a national network of public health laboratories and contracted testing providers. For more detail on how sampling sites are selected and how surveys are conducted, see the [CDC NWSS data sources documentation](https://www.cdc.gov/wastewater/about/index.html#cdc_survey_profile_how_surveys_are_conducted-data-sources).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Available Signals

Wastewater signals are constructed by combining a pathogen prefix with a post-processing suffix in the format `<pathogen_prefix>_<suffix>`. For example, combining the prefix `covid` with the suffix `avg_conc_lin` constructs the signal `covid_avg_conc_lin`.

### Pathogen Prefixes

| Prefix | Pathogen | Target PCR | Socrata endpoint |
|---|---|---|---|
| `covid` | COVID-19 | `sars-cov-2` | [j9g8-acpt](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-SARS-CoV-2/j9g8-acpt/about_data) |
| `flu` | Influenza | `fluav` | [ymmh-divb](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Influenza-A/ymmh-divb/about_data) |
| `flu_h5` | Avian Flu | `fluav a h5` | [mtpu-urpp](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-H5-Influenza-A/mtpu-urpp/about_data) |
| `rsv` | RSV | `rsv` | [45cq-cw4i](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i/about_data) |
| `measles` | Measles | `mev_wt` | [akvg-8vrb](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Measles/akvg-8vrb/about_data) |
| `mpox_all` | Mpox (All Clades) | `hmpxv` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |
| `mpox_clade_i` | Mpox Clade I | `hmpxv clade i` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |
| `mpox_clade_ii` | Mpox Clade II | `hmpxv clade ii` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |
| `mpox_nvo` | Mpox NVO | `nvo` | [xpxn-rzgz](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz/about_data) |


### Suffixes

| Suffix | Metric Type | Description |
|---|---|---|
| `avg_conc` | Average Concentration | Concentration of the PCR target back-calculated to unconcentrated sample basis |
| `avg_conc_lin` | Average Concentration | Concentration of the PCR target on a per sample amount basis where all values are on a linear (not log10) concentration basis |
| `flowpop_lin` | Flow-Population | Flow-population normalized concentration (copies/person/day) |
| `mic_lin` | Microbial | Microbial normalized concentration (unitless ratio) |

For more details on the columns, see one of the socrata endpoints, e.g. [RSV](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i/about_data) which provides descriptions of all columns.

## Source-Specific Keys

Wastewater data has unique properties, including multiple facilities, replicate samples, and laboratory PCR targets. To support this granularity, the V5 table schema includes:

| Column | Key Type | Description |
|---|---|---|
| `nwss_source` | Primary Key (Extra Key) | The data provider or laboratory network that analyzed/reported the sample (see [Providers](#providers)). |
| `sample_index` | Primary Key (Extra Key) | An integer identifier mapped to the original sample's unique ID (`sample_id`). |
| `pcr_target` | Value Column (Extra Value) | The target pathogen or organism analyzed in the sample (e.g., `sars-cov-2`, `fluav`, `rsv`). Include to join onto the auxiliary metadata table|


## Auxiliary Metadata Table

Since wastewater treatment facilities have sample-specific traits (such as populations served and lab methodologies) that can change with time, this metadata is served in a companion table via the `/aux_data/` endpoint at `https://delphi.cmu.edu/epidata/v5/aux_data/?source=nwss`.

The table is keyed by `report_time`, `geo_value`, `time_value`, `nwss_source`, `sample_index`, and `pcr_target`.

Its value columns report facility demographics (`state_territory`, `county_fips`, `counties_served`, `population_served`), sample specifics (`sample_type`, `sample_location`, `flow_rate`), laboratory methods (`concentration_method`, `extraction_method`, `major_lab_method`, `pcr_type`, `pcr_target_units`, `lod_sewage`), and pipeline metrics (`rec_eff_percent`, `pipeline_run_id`).


## Signal features
The signals vary across the underlying data provider, the normalization method, and the post-processing method.

### Providers
The NWSS acts as a coordinating body, receiving wastewater data through a number of providers. Data providers can change as the project has evolved.
Most recently, in autumn 2023, the primary direct commercial provider for the NWSS changed from [Biobot](https://biobot.io/) to [Verily](https://publichealth.verily.com/). Measurement method and thus meaning varies by provider. Data from different providers varies widely in magnitude for the same nominal reporting units.
The following table shows the history of data providers:

| Provider | Available | Description |
|-|-|-|
| `cdc_verily` | 2023/10/30-Today | Data analyzed by [Verily](https://verily.com/solutions/public-health/wastewater) on behalf of the CDC directly. |
| `nwss` | 2020/06/21-Today | Data reported by the respective state, territorial, and local public health agencies; the actual processing may be done by a private lab such as Verily or Biobot, or the agency itself, or a partnering university. |
| `wws` | 2021/12/26-Today | Data analyzed by [Wastewater Scan](https://www.wastewaterscan.org/en), a Stanford/Emory nonprofit, and then shared with the NWSS. Use of this data outside of public health decision making requires contacting WastewaterSCAN Anyone seeking to use the database for other purposes or for research is required to contact the WastewaterSCAN / SCAN team (email: [wwscan_stanford_emory@lists.stanford.edu](mailto:wwscan_stanford_emory@lists.stanford.edu)) and any use of the data should be cited appropriately (https://data.wastewaterscan.org/about/#18).|
| `biobot` | 2020-2023 | Data analyzed by [Biobot](https://biobot.io/) and then shared with the NWSS. |

### Normalization methods

Direct viral concentration is not a robust indicator of the number and severity of cases in the sewershed.
In wastewater systems that mix drainage and sewage, for example, the effluent will be significantly diluted whenever there is rain.
In order to produce indicators that are more strongly related to pathogen levels, signals are corrected in a few different ways.
The two approaches used in the NWSS datasets to normalize viral concentration are as follows:

| Normalization method | Description | Signal Suffix |
|---|---|---|
| **Flow-population** | This is calculated as $$\frac{v\cdot r}{p}$$, where $$v$$ is measured viral concentration, $$r$$ is measured flow rate, and $$p$$ is population served. This normalization method is applied to concentrations $$v$$ measured from raw (unconcentrated) wastewater. The resulting value is in units of viral gene copies per person per day. It tracks the total number of individuals whose shedding behavior has changed. | `_flowpop` |
| **Microbial** | This divides a measurement by the concentration of one of several potential fecal biomarkers. These are molecular indicators of either viruses or bacteria commonly found throughout the population. The most common viral indicator comes from the pepper mild mottle virus (PMMoV), a virus that infects plants and is commonly found in pepper products. The most common bacterial indicators come from Bacteroides HF183 and Lachnospiraceae Lachno3, both common gut bacteria. This normalization method is applied to sludge samples, which have been concentrated in preparation for treatment. The resulting value is unitless, and tracks the proportion of individuals whose shedding behavior has changed. | `_mic` |

### Post-processing methods

Regardless of normalization method, the daily wastewater data is noisy; to make the indicators more useful, the NWSS provides versions of the data that are post-processed in different ways:

| Method | Suffix | Description |
|---|---|---|
| **Average Concentration** | `avg_conc` | Concentration of the PCR target back-calculated to unconcentrated sample basis. Non-detections are typically reported as zero. |
| **Linearized Average Concentration** | `avg_conc_lin` | Concentration of the PCR target on a per sample amount basis where all values are on a linear (not log10) concentration basis. |

## Estimation

### Aggregation

The `nwss` source serves sewershed-level directly as reported by the facilities and laboratories. This preserves the local resolution of the data without introducing smoothing or aggregation assumptions.


## Limitations

The NWSS is still expanding to get coverage nationwide, so it is currently an uneven sample; the largest signals above cover ~42 million people as of March 2024. Around 80% of the US is served by municipal wastewater collection systems, or around 272 million. 

Standard errors and sample sizes are not applicable to these signals.

<!-- TODO: cubic spline method may change over time -->

## Missingness

If a sample site has too few individuals, the NWSS does not provide the detailed data, so we cannot include it in our aggregations.

Also, data from sewersheds serving fewer than 3,000 people, as well as data from facility or institution specific sampling locations and tribal communities, are generally not available unless approved by the local jurisdiction.

## Lag and Backfill

Due to collection, shipping, processing and reporting time, these signals are subject to some lag.
Typically, this is between 4-6 days.

## Source and Licensing

This indicator aggregates data originating from the [NWSS](https://www.cdc.gov/nwss/index.html).
The site-level data is provided un-versioned via the Socrata API across pathogen-specific datasets: [SARS-CoV-2](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-SARS-CoV-2/j9g8-acpt) (`j9g8-acpt`), [Influenza A](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Influenza-A/ymmh-divb) (`ymmh-divb`), [H5 Influenza A / Avian Flu](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-H5-Influenza-A/mtpu-urpp) (`mtpu-urpp`), [RSV](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i) (`45cq-cw4i`), [Mpox](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz) (`xpxn-rzgz`), and [Measles](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Measles/akvg-8vrb) (`akvg-8vrb`).


The NWSS is aggregating data from [Verily](https://verily.com/solutions/public-health/wastewater), State Territorial and Local public health agencies, and [Wastewater Scan](https://www.wastewaterscan.org/en).

The WastewaterSCAN data were collected as part of the [WastewaterSCAN]([Wastewater Scan](https://www.wastewaterscan.org/en)) / SCAN project, a partnership between Stanford University, Emory University, and Verily funded philanthropically through a gift to Stanford University, and then shared with the NWSS. Anyone seeking to use the database for other purposes or for research is required to contact the WastewaterSCAN / SCAN team (email: [wwscan_stanford_emory@lists.stanford.edu](mailto:wwscan_stanford_emory@lists.stanford.edu)) and any use of the data should be cited appropriately (as described [here](https://data.wastewaterscan.org/about/#18)).

This data was originally published by the CDC, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).

