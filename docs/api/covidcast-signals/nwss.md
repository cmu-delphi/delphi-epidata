---
title: NWSS
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---

# 	National Wastewater Surveillance System (NWSS)
{: .no_toc}

* **Source name:** `nwss-wastewater`
* **Earliest issue available:** DATE RELEASED TO API
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** state, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [LICENSE NAME](../covidcast_licensing.md#APPLICABLE-SECTION)

The National Wastewater Surveillance System (nwss) is a CDC led effort to track the presence of SARS-CoV-2 in wastewater throughout the United States.
For more, see their [official page](https://www.cdc.gov/nwss/index.html).
The project was launched in September 2020 and is ongoing. The original data for this source is provided un-versioned via the socrata api as the [metric data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6/about_data) and [concentration data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Concentration-in-Wastewater/g653-rqe2/about_data).
This source modifies this data in two ways: first, it splits the data based on provider and normalization, and then it aggregates across `geo_values` so that the signals are available at the state and national level.
## Table of contents
{: .no_toc .text-delta}

1. TOC {:toc}

## Description
The original source is measured at the level of [sample-site](https://www.cdc.gov/nwss/sampling.html), either at or upstream from a regional wastewater treatment plants (these are roughly at the county-level, but are not coterminous with counties); presently we do not provide the site-level or county-aggregated data, but will do so within the coming months.

To generate either the state or national level signals from the sample-site level signals, we aggregate using population-served weighted sums, where the total population for a given `geo_value` is the total population served at sites with non-missing values. 
## Signal features
The signals vary across the underlying data provider, the normalization method, and the post-processing method.
### Providers
As a coordinating body, the NWSS receives wastewater data through a number of providers, which have changed as the project has evolved.
Most recently, in the fall of 2023, there was a major shift in the primary direct commercial provider for the NWSS from Biobot to Verily.
Presently, the Biobot data is not present at either socrata endpoint; we are providing a fixed snapshot that was present in November 2023.
The available column below indicates the first date that any location had data from that source.
| Provider     | Available             | Description                                                                                                                                                                                                  |
|--------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cdc_verily` | 2023/10/30-Today      | Data analyzed by [Verily](https://verily.com/solutions/public-health/wastewater) on behalf of the CDC directly.                                                                                              |
| `nwss`       | 2020/06/21-Today      | Data reported by the respective State, Territorial and Local Public Health Agencies; the actual processing may be done by a private lab such as Verily or Biobot, or the agency, or a partnering university. |
| `wws`        | 2021/12/26-Today      | Data analyzed by [Wastewater Scan](https://www.wastewaterscan.org/en), a Stanford/Emory nonprofit, and then shared with the NWSS.                                                                            |
| `cdc_biobot` | 2020/06/21-2023/10/30 | Data analyzed by [Biobot](https://biobot.io/) on behalf of the CDC.                                                                                                                                          |
### Normalization methods
Direct viral concentration is not a clear indicator of the number and severity of cases in the sewershed.
In mixed drainage/sewage systems for example, the effluent will be significantly diluted whenever there is rain.
There are a number of methods to normalize viral concentration to get a better indicator:
| Normalization method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `flow_population`    | This uses $$\frac{v\cdot r}{p}$$, where $$v$$ is viral concentration, $$r$$ is flow rate, and $$p$$ is population served. The resulting units are viral gene copies per person per day. It's applied to concentrations measured from unconcentrated wastewater (also labeled `raw_wastewater` in the socrata dataset's `key_plot_id`). It tracks the total number of individuals whose shedding behavior has changed.                                                                                                                                                                                                                                                                                                                                                                                               |
| `microbial`          | This divides by the concentration of one of several potential fecal biomarkers commonly found throughout the population. These include molecular indicators of either viruses or bacteria. The most common viral indicator comes from the pepper mild mottle virus (pmmov), a virus that infects plants that is commonly found in pepper products. The most common bacterial indicators come from Bacteroides HF183 and Lachnospiraceae Lachno3, both common gut bacteria. It's applied to sludge samples (also labeled `post_grit _removal` in the socrata dataset's `key_plot_id`), which have been concentrated in preparation for treatment. The resulting value is unitless, and tracks the proportion of individuals who's shedding behavior has changed. |
### Post Processing methods
Regardless of normalization method, the daily wastewater data is noisy; to make the indicators more useful, the NWSS has provided different methods of post-processing the data:
| Post-processing method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pcr_conc_smoothed`    | PCR measurements (the exact method depends on the data provider), initially provided in virus concentrations per volume of input (type depends on the [normalization method](#Normalization-methods)). This is then [smoothed](#Smoothing) using a cubic spline, then [aggregated](#Aggregation) to the given `geo_type` with a population-weighted sum.                                                                                                                                                                                                               |
| `detect_prop_15d`      | The proportion of tests with SARS-CoV-2 detected, meaning a cycle threshold (Ct) value <40 for RT-qPCR or at least 3 positive droplets/partitions for RT-ddPCR, by sewershed over the prior 15-day period. The detection proportion is the 15-day rolling sum of SARS-CoV-2 detections divided by the 15-day rolling sum of the number of tests for each sample site and multiplying by 100, aggregated with a population weighted sum. The result is a percentage.                                                                                  |
| ptc\_15d               | The percent change in SARS-CoV-2 RNA levels over the 15 days preceding `timestamp`. It is the coefficient of the linear regression of the log-transformed unsmoothed PCR concentration, expressed as a percentage change. Note that for county and higher level `geo_type`s, this is an average of the percentage change at each site, weighted by population, rather than the percentage change for the entire region. We recommend caution in the use of these signals at aggregated `geo_type`s.                                                  |
| `percentile`           | This metric shows whether SARS-CoV-2 virus levels at a site are currently higher or lower than past historical levels at the same site. 20% means that 80% of observed values are higher than this value, while 20% are lower. 0% means levels are the lowest they have been at the site, while 100% means they are the highest. Note that at county or higher level `geo_type`s, this is not the percentile for overall state levels, but the *average percentile across sites*, weighted by population, which makes it difficult to meaningfully interpret. We do not recommended its use outside of the site level. |

### Full signal list
Not every triple of post processing method, provider, and normalization actually contains data. Here is a complete list of the actual signals:
| Signal                                         |   |
| `prc_conc_smoothed_cdc_verily_flow_population` |   |
| `prc_conc_smoothed_cdc_verily_microbial`       |   |
| `prc_conc_smoothed_cdc_nwss_flow_population`   |   |
| `prc_conc_smoothed_cdc_verily_microbial`       |   |
| `prc_conc_smoothed_cdc_wws_microbial`          |   |
| `detetct_prop_15d_cdc_verily_flow_population`  |   |
| `detetct_prop_15d_cdc_verily_microbial`        |   |
| `detetct_prop_15d_cdc_nwss_flow_population`    |   |
| `detetct_prop_15d_cdc_verily_microbial`        |   |
| `detetct_prop_15d_cdc_wws_microbial`           |   |
| `ptc_15d_cdc_verily_flow_population`           |   |
| `ptc_15d_cdc_verily_microbial`                 |   |
| `ptc_15d_cdc_nwss_flow_population`             |   |
| `ptc_15d_cdc_verily_microbial`                 |   |
| `ptc_15d_cdc_wws_microbial`                    |   |
| `percentile_cdc_verily_flow_population`        |   |
| `percentile_cdc_verily_microbial`              |   |
| `percentile_cdc_nwss_flow_population`          |   |
| `percentile_cdc_verily_microbial`              |   |
| `percentile_cdc_wws_microbial`                 |   |

What is missing? `wws` only normalizes using `microbial` measures, so the 5 different post-processing methods are not present for `*_wws_flow_population`.
## Estimation
### Aggregation
For any given day and signal, we do a population weighted sum of the target signal, with the weight depending only on non-missing and non-zero sample sites for that day in particular. For example, say $$p_i$$ is the population at sample site $$i$$; if there are 3 sample sites in Washington on a particular day, then the weight at site $$i$$ is $$\frac{p_i}{p_1+p_2+p_3}$$. If the next day there are only 2 sample locations, the weight at site $$i$$ becomes $$\frac{p_i}{p_1+p_2}$$.

For `ptc_15d`, the percent change in RNA levels, this average is somewhat difficult to interpret, since it is the average of the percentage changes, rather than  the percentage change in the average.
For example, say we have two sample sites, with initial levels at 10 and 100, and both see a increase of 10[^1].
Their respective percentage increases are 10% and 100%, so the average percent increase is 55%.
Contrast this with the average level, which goes from 55 to 65, for an 18% percent increase in the average[^2].

`percentile` has a similar difficulty, although it is a more involved calculation that uses all other values in the time series, rather than just a 15 day window.



### Smoothing

The `pcr_conc_smoothed` based signals all use smoothed splines to generate the averaged value at each location. Specifically, the smoothing uses [`smooth.spline`](https://www.rdocumentation.org/packages/stats/versions/3.6.2/topics/smooth.spline) from R, with `spar=0.5`, a smoothing parameter. Specifically, if the value at time $$t_i$$ is given by $$y_i$$, for a function $$f$$ represented by splines this minimizes 

$$ \sum_i (y_i - f(t_i))^2 + 16 \frac{\mathrm{tr}(X'X)}{\mathrm{tr}(\Sigma)} \int \big|f^{''}(z)\big|^2~\mathrm{d}z$$

where $$X_{ij} = B_j(t_i)$$ and $$\Sigma_{ij} = \int B_j(t_i)$$ where $$B_j$$ is $$j$$th spline evaluated at $$t_i$$.

It is important to note that this means that the value at any point in time depends on future values up to and including the present day, so its use in historical evaluation is suspect.
This is only true for `pcr_conc_smoothed`; all other smoothing is done via 15 day rolling sums.

## Limitations


The NWSS is still expanding to get coverage nationwide: to get an idea of the extent of counties currently covered, see [this map](https://www.cdc.gov/nwss/progress.html).

Standard errors and sample sizes are not applicable to these signals.

## Missingness

If a sample site has too few individuals, the NWSS does not provide the detailed data, so we cannot include it in our aggregations.

## Lag and Backfill

Due to collection, shipping, processing and reporting time, these signals are subject to some lag.
Typically, this is between 4-6 days.

The raw signals are not typically subject to revisions or backfill, but due to the [cubic spline smoothing](#Smoothing), any of the `pcr_conc_smoothed` signals may change in the 4th and smaller significant figure at intervals of approximately 1-3 days; outside of the most recent data where smoothing directly relies on newly added data-points, these revisions should have approximately a mean of zero.
To reduce some of this variation, we have rounded to the 4th significant figure.
There is also the possibility of the post-processing being subject to significant revisions if bugs are discovered.

Finally, whenever a new maximum occurs at a location, all historical data for a `percentile` signal has the potential to shift, potentially drastically.

## Source and Licensing

This indicator aggregates data originating from the [NWSS](https://www.cdc.gov/nwss/index.html).
The site-level data is provided un-versioned via the socrata api as the [metric data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6/about_data) and [concentration data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Concentration-in-Wastewater/g653-rqe2/about_data).
As described in the [Provider section](#Providers), the NWSS is aggregating data from [Verily](https://verily.com/solutions/public-health/wastewater), State Territorial and Local public health agencies, [Wastewater Scan](https://www.wastewaterscan.org/en), and [Biobot](https://biobot.io/).


[^1]: These are not realistic values; they are merely chosen to make the example simple to explain.
[^2]: Further complicating this is that the percent change is measured via linear regression, rather than a simple difference. However, this doesn't change the fundamental interpretation, it merely makes the slope more robust to noise.
