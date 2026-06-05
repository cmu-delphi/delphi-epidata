---
title: NWSS Wastewater
parent: V5 Sources and Signals
grand_parent: Delphi V5 API
---

# National Wastewater Surveillance System (NWSS)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nwss` |
| **Data Source** | [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html) |
| **Geographic Levels** | sewershed (see [geographic coding](../covidcast_geography.md)) |
| **Temporal Granularity** | Daily (sample collection dates) (see [date format docs](../covidcast_times.md)) |
| **Reporting Cadence** | Weekly (typically updated on Fridays) |
| **Date of last data revision:** | Never (see [data revision docs](#changelog)) |
| **Temporal Scope Start** | 2020-07-05 |
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

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

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
| `wws` | 2021/12/26-Today | Data analyzed by [Wastewater Scan](https://www.wastewaterscan.org/en), a Stanford/Emory nonprofit, and then shared with the NWSS. |
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

### Post Processing methods

Regardless of normalization method, the daily wastewater data is noisy; to make the indicators more useful, the NWSS has provided versions of the data that are post-processed in different ways.

| Method | Suffix | Scale | Description |
|---|---|---|---|
| **Average Concentration (log-transformed)** | `avg_conc` | Logarithmic ($$\log_{10}$$ copies/L) | Replicates are averaged and log-transformed. |
| **Average Concentration (linear scale)** | `_avg_conc_lin` | Linear (copies/L) | Replicates are averaged on a linear scale. |


### Full signal list

Here is the complete list of available signals for the active sewershed-level `nwss` source:

| Signal | Pathogen | Metric Type | Description |
|---|---|---|---|
| `covid_avg_conc` | COVID-19 | Average Concentration | Log-average concentration of SARS-CoV-2. |
| `covid_avg_conc_lin` | COVID-19 | Average Concentration | Linear average concentration of SARS-CoV-2. |
| `covid_flowpop_lin` | COVID-19 | Flow-Population | Flow-population normalized concentration of SARS-CoV-2. |
| `covid_mic_lin` | COVID-19 | Microbial | Microbial normalized concentration of SARS-CoV-2. |
| `flu_avg_conc` | Influenza | Average Concentration | Log-average concentration of Influenza A. |
| `flu_avg_conc_lin` | Influenza | Average Concentration | Linear average concentration of Influenza A. |
| `flu_flowpop_lin` | Influenza | Flow-Population | Flow-population normalized concentration of Influenza A. |
| `flu_mic_lin` | Influenza | Microbial | Microbial normalized concentration of Influenza A. |
| `flu_h5_avg_conc` | Avian Flu (H5) | Average Concentration | Log-average concentration of H5 Influenza A. |
| `flu_h5_avg_conc_lin` | Avian Flu (H5) | Average Concentration | Linear average concentration of H5 Influenza A. |
| `flu_h5_flowpop_lin` | Avian Flu (H5) | Flow-Population | Flow-population normalized concentration of H5 Influenza A. |
| `flu_h5_mic_lin` | Avian Flu (H5) | Microbial | Microbial normalized concentration of H5 Influenza A. |
| `rsv_avg_conc` | RSV | Average Concentration | Log-average concentration of RSV. |
| `rsv_avg_conc_lin` | RSV | Average Concentration | Linear average concentration of RSV. |
| `rsv_flowpop_lin` | RSV | Flow-Population | Flow-population normalized concentration of RSV. |
| `rsv_mic_lin` | RSV | Microbial | Microbial normalized concentration of RSV. |
| `measles_avg_conc` | Measles | Average Concentration | Log-average concentration of Measles. |
| `measles_avg_conc_lin` | Measles | Average Concentration | Linear average concentration of Measles. |
| `measles_flowpop_lin` | Measles | Flow-Population | Flow-population normalized concentration of Measles. |
| `measles_mic_lin` | Measles | Microbial | Microbial normalized concentration of Measles. |
| `mpox_all_avg_conc` | Mpox | Average Concentration | Log-average concentration of Mpox (all clades). |
| `mpox_all_avg_conc_lin` | Mpox | Average Concentration | Linear average concentration of Mpox (all clades). |
| `mpox_all_flowpop_lin` | Mpox | Flow-Population | Flow-population normalized concentration of Mpox (all clades). |
| `mpox_all_mic_lin` | Mpox | Microbial | Microbial normalized concentration of Mpox (all clades). |
| `mpox_clade_i_avg_conc` | Mpox Clade I | Average Concentration | Log-average concentration of Mpox Clade I. |
| `mpox_clade_i_avg_conc_lin` | Mpox Clade I | Average Concentration | Linear average concentration of Mpox Clade I. |
| `mpox_clade_i_flowpop_lin` | Mpox Clade I | Flow-Population | Flow-population normalized concentration of Mpox Clade I. |
| `mpox_clade_i_mic_lin` | Mpox Clade I | Microbial | Microbial normalized concentration of Mpox Clade I. |
| `mpox_clade_ii_avg_conc` | Mpox Clade II | Average Concentration | Log-average concentration of Mpox Clade II. |
| `mpox_clade_ii_avg_conc_lin` | Mpox Clade II | Average Concentration | Linear average concentration of Mpox Clade II. |
| `mpox_clade_ii_flowpop_lin` | Mpox Clade II | Flow-Population | Flow-population normalized concentration of Mpox Clade II. |
| `mpox_clade_ii_mic_lin` | Mpox Clade II | Microbial | Microbial normalized concentration of Mpox Clade II. |
| `mpox_nvo_avg_conc` | Mpox NVO | Average Concentration | Log-average concentration of Non-variola orthopoxvirus. |
| `mpox_nvo_avg_conc_lin` | Mpox NVO | Average Concentration | Linear average concentration of Non-variola orthopoxvirus. |
| `mpox_nvo_flowpop_lin` | Mpox NVO | Flow-Population | Flow-population normalized concentration of Non-variola orthopoxvirus. |
| `mpox_nvo_mic_lin` | Mpox NVO | Microbial | Microbial normalized concentration of Non-variola orthopoxvirus. |

## Estimation

### Aggregation

The `nwss` source serves sewershed-level directly as reported by the facilities and laboratories. This preserves the local resolution of the data without introducing smoothing or aggregation assumptions.


## Limitations

The NWSS is still expanding to get coverage nationwide, so it is currently an uneven sample; the largest signals above cover ~42 million people as of March 2024. Around 80% of the US is served by municipal wastewater collection systems, or around 272 million. 

Standard errors and sample sizes are not applicable to these signals.

<!-- TODO: cubic spline method may change over time -->

## Missingness

If a sample site has too few individuals, the NWSS does not provide the detailed data, so we cannot include it in our aggregations.

## Lag and Backfill

Due to collection, shipping, processing and reporting time, these signals are subject to some lag.
Typically, this is between 4-6 days.

## Source and Licensing

This indicator aggregates data originating from the [NWSS](https://www.cdc.gov/nwss/index.html).
The site-level data is provided un-versioned via the Socrata API across pathogen-specific datasets: [SARS-CoV-2](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-SARS-CoV-2/j9g8-acpt) (`j9g8-acpt`), [Influenza A](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Influenza-A/ymmh-divb) (`ymmh-divb`), [H5 Influenza A / Avian Flu](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-H5-Influenza-A/mtpu-urpp) (`mtpu-urpp`), [RSV](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-RSV/45cq-cw4i) (`45cq-cw4i`), [Mpox](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Mpox/xpxn-rzgz) (`xpxn-rzgz`), and [Measles](https://data.cdc.gov/Public-Health-Surveillance/CDC-Wastewater-Data-for-Measles/akvg-8vrb) (`akvg-8vrb`).


The NWSS is aggregating data from [Verily](https://verily.com/solutions/public-health/wastewater), State Territorial and Local public health agencies, and [Wastewater Scan](https://www.wastewaterscan.org/en).

This data was originally published by the CDC, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).

