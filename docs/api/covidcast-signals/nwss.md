---
title: NWSS
parent: Data Sources and Signals
grand_parent: COVIDcast Main Endpoint
---

# 	National Wastewater Surveillance System (NWSS)
{: .no_toc}

* **Source name:** `nwss-wastewater`
* **Earliest issue available:** TODO: DATE RELEASED TO API
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** state, nation (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [Public Domain US Government](https://www.usa.gov/government-works)

The [National Wastewater Surveillance System (NWSS)](https://www.cdc.gov/nwss/index.html) is a CDC-led effort to track the presence of SARS-CoV-2 in wastewater throughout the United States.
The project was launched in September 2020 and is ongoing. The source data for this source is provided un-versioned via the Socrata API as the [NWSS Public SARS-CoV-2 Concentration in Wastewater Data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Concentration-in-Wastewater/g653-rqe2/about_data) and the [NWSS Public SARS-CoV-2 Wastewater Metric Data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6/about_data) containing signals derived from the concentration data.
Delphi modifies the source data in two ways: we split the data into separate signals based on provider, normalization, and post-processing method, and then aggregate it to higher geographic levels.

The source data is reported per [sampling site](https://www.cdc.gov/nwss/sampling.html), either at or upstream from a regional wastewater treatment plants (these are roughly at the county-level, but are not coterminous with counties). Presently we do not provide the site-level or county-aggregated data, but will do so within the coming months.

State and national level signals are calculated as weighted means of the site data. The weight assigned to a given input value is the population served by the corresponding wastewater treatment plant. Sites with missing values are implicitly treated as having a weight of 0 or a value equal to the group mean.

## Table of contents
{: .no_toc .text-delta}

1. TOC 
{:toc}

## Signal features
The signals vary across the underlying data provider, the normalization method, and the post-processing method.

### Providers
The NWSS acts as a coordinating body, receiving wastewater data through a number of providers. Data providers can change as the project has evolved.
Most recently, in autumn 2023, the primary direct commercial provider for the NWSS changed from [Biobot](https://biobot.io/) to [Verily](https://publichealth.verily.com/).
The following table shows the history of data providers:

| Provider | Available | Description |
|-|-|-|
| `cdc_verily` | 2023/10/30-Today | Data analyzed by [Verily](https://verily.com/solutions/public-health/wastewater) on behalf of the CDC directly. |
| `nwss` | 2020/06/21-Today | Data reported by the respective state, territorial, and local public health agencies; the actual processing may be done by a private lab such as Verily or Biobot, or the agency itself, or a partnering university. |
| `wws` | 2021/12/26-Today | Data analyzed by [Wastewater Scan](https://www.wastewaterscan.org/en), a Stanford/Emory nonprofit, and then shared with the NWSS. |
| `biobot` | ??-?? | Data analyzed by [Biobot](https://biobot.io/) and then shared with the NWSS. |

### Normalization methods
Direct viral concentration is not a robust indicator of the number and severity of cases in the sewershed.
In wastewater systems that mix drainage and sewage, for example, the effluent will be significantly diluted whenever there is rain.
In order to produce indicators that are more strongly related to COVID levels, signals are corrected in a few different ways.
The two approaches used in the NWSS datasets to normalize viral concentration are as follows:

| Normalization method | Description |
|-|-|
| `flow_population` | This is calculated as $$\frac{v\cdot r}{p}$$, where $$v$$ is measured viral concentration, $$r$$ is measured flow rate, and $$p$$ is population served. This normalization method is applied to concentrations $$v$$ measured from raw (unconcentrated) wastewater (labeled `raw_wastewater` in the Socrata dataset's `key_plot_id` field). The resulting value is in units of viral gene copies per person per day. It tracks the total number of individuals whose shedding behavior has changed. |
| `microbial` | This divides a measurement by the concentration of one of several potential fecal biomarkers. These are molecular indicators of either viruses or bacteria commonly found throughout the population. The most common viral indicator comes from the pepper mild mottle virus (PMMoV), a virus that infects plants and is commonly found in pepper products. The most common bacterial indicators come from Bacteroides HF183 and Lachnospiraceae Lachno3, both common gut bacteria. This normalization method is applied to sludge samples (labeled `post_grit_removal` in the Socrata dataset's `key_plot_id` field), which have been concentrated in preparation for treatment. The resulting value is unitless, and tracks the proportion of individuals who's shedding behavior has changed. |

### Post Processing methods
Regardless of normalization method, the daily wastewater data is noisy; to make the indicators more useful, the NWSS has provided versions of the data that are post-processed in different ways.

| Post-processing method | Description |
|-|-|
| `pcr_conc_smoothed` | PCR measurements (the exact method depends on the data provider), initially provided in virus concentrations per volume of input (type depends on the [normalization method](#normalization-methods)). This is then [smoothed](#smoothing) using a cubic spline, then [aggregated](#aggregation) to the given `geo_type` with a population-weighted sum. |
| `detect_prop_15d` | The proportion of tests with SARS-CoV-2 detected, meaning a cycle threshold (Ct) value <40 for RT-qPCR or at least 3 positive droplets/partitions for RT-ddPCR, by sewershed over the prior 15-day period. The detection proportion is the 15-day rolling sum of SARS-CoV-2 detections divided by the 15-day rolling sum of the number of tests for each sample site and multiplying by 100, aggregated with a population weighted sum. The result is a percentage. |
| `ptc_15d` | The percent change in SARS-CoV-2 RNA levels over the 15 days preceding `timestamp`. It is the coefficient of the linear regression of the log-transformed unsmoothed PCR concentration, expressed as a percentage change. Note that for county and higher level `geo_type`s, this is an average of the percentage change at each site, weighted by population, rather than the percentage change for the entire region. We recommend caution in the use of these signals at aggregated `geo_type`s. |
| `percentile` | This metric shows whether SARS-CoV-2 virus levels at a site are currently higher or lower than past historical levels at the same site. 20% means that 80% of observed values are higher than this value, while 20% are lower. 0% means levels are the lowest they have been at the site, while 100% means they are the highest. Note that at county or higher level `geo_type`s, this is not the percentile for overall state levels, but the *average percentile across sites*, weighted by population, which makes it difficult to meaningfully interpret. We do not recommended its use outside of the site level. |

### Full signal list
Not every triple of post processing method, provider, and normalization actually contains data. Here is a complete list of the actual signals, with the total population at all sites which report that signal, as of March 28, 2024:

| Signal                                         | First Date available | Population served on 03-28-24 |
|-|-|-|
| `prc_conc_smoothed_cdc_verily_flow_population` | 2023-11-13           | 3,321,873                     |
| `prc_conc_smoothed_cdc_verily_microbial`       | 2023-11-09           | 430,000                       |
| `prc_conc_smoothed_cdc_nwss_flow_population`   | 2020-07-05           | 800,704                       |
| `prc_conc_smoothed_cdc_nwss_microbial`         | 2020-08-25           | 822,992                       |
| `prc_conc_smoothed_cdc_wws_microbial`          | 2022-01-09           | 10,643,646                    |
| `detect_prop_15d_cdc_verily_flow_population`   | 2023-11-13           | 3,321,873                     |
| `detect_prop_15d_cdc_verily_microbial`         | 2024-01-09           | 527,710                       |
| `detect_prop_15d_cdc_nwss_flow_population`     | 2020-07-05           | 800,704                       |
| `detect_prop_15d_cdc_nwss_flow_microbial`      | 2021-08-25           | 3,046,772                     |
| `detect_prop_15d_cdc_wws_microbial`            | 2022-01-09           | 42,185,773                    |
| `ptc_15d_cdc_verily_flow_population`           | 2023-11-15           | 3,321,873                     |
| `ptc_15d_cdc_verily_microbial`                 | 2024-01-11           | 448,710                       |
| `ptc_15d_cdc_nwss_flow_population`             | 2020-07-12           | 800,704                       |
| `ptc_15d_cdc_nwss_microbial`                   | 2021-08-26           | 2,780,752                     |
| `ptc_15d_cdc_wws_microbial`                    | 2022-01-10           | 41,965,773                    |
| `percentile_cdc_verily_flow_population`        | 2023-11-13           | 3,321,873                     |
| `percentile_cdc_verily_microbial`              | 2024-01-09           | 527,710                       |
| `percentile_cdc_nwss_flow_population`          | 2021-12-02           | 800,704                       |
| `percentile_cdc_nwss_microbial`                | 2021-12-05           | 3,104,972                     |
| `percentile_cdc_wws_microbial`                 | 2022-01-09           | 42,185,773                    |

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

The `pcr_conc_smoothed` based signals all use smoothed splines to generate an average value at each location. Specifically, the smoothing uses [`smooth.spline`](https://www.rdocumentation.org/packages/stats/versions/3.6.2/topics/smooth.spline) from R, with `spar=0.5`, a smoothing parameter. If the value at time $$t_i$$ is given by $$y_i$$, for a function $$f$$ represented by splines this minimizes 

$$ \sum_i (y_i - f(t_i))^2 + 16 \frac{\mathrm{tr}(X'X)}{\mathrm{tr}(\Sigma)} \int \big|f^{''}(z)\big|^2~\mathrm{d}z$$

where $$X_{ij} = B_j(t_i)$$ and $$\Sigma_{ij} = \int B_j(t_i)$$ with $$B_j$$ the $$j$$th spline evaluated at $$t_i$$.

It is important to note that this means that the value at any point in time *depends on future values* up to and including the present day, so its use in historical evaluation is suspect.
This is only true for `pcr_conc_smoothed`; all other smoothing is done via simple 15 day trailing rolling sums.

## Limitations

The NWSS is still expanding to get coverage nationwide, so it is currently an uneven sample; the largest signals above cover ~42 million people as of March 2024. Around 80% of the US is served by municipal wastewater collection systems, or around 272 million. 

Standard errors and sample sizes are not applicable to these signals.

## Missingness

If a sample site has too few individuals, the NWSS does not provide the detailed data, so we cannot include it in our aggregations.

## Lag and Backfill

Due to collection, shipping, processing and reporting time, these signals are subject to some lag.
Typically, this is between 4-6 days.

The raw signals are not typically subject to revisions or backfill, but due to the [cubic spline smoothing](#smoothing), any of the `pcr_conc_smoothed` signals may change in the 4th and smaller significant figure at intervals of approximately 1-3 days; outside of the most recent data where smoothing directly relies on newly added data-points, these revisions should have approximately a mean of zero.
To reduce some of this variation, we have rounded to the 4th significant figure.
There is also the possibility of the post-processing being subject to significant revisions if bugs are discovered, though this occurs on an ad-hoc basis.

The `percentile` data is subject to potentially more extensive revision if the signal undergoes significant distributional shift. This results in less jitter in the signal but the meaning of the percentiles can change quite drastically if e.g. a new wave infects an order of magnitude more people.

## Source and Licensing

This indicator aggregates data originating from the [NWSS](https://www.cdc.gov/nwss/index.html).
The site-level data is provided un-versioned via the socrata api as the [metric data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6/about_data) and [concentration data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Concentration-in-Wastewater/g653-rqe2/about_data).
As described in the [Provider section](#providers), the NWSS is aggregating data from [Verily](https://verily.com/solutions/public-health/wastewater), State Territorial and Local public health agencies, [Wastewater Scan](https://www.wastewaterscan.org/en).

This data was originally published by the CDC, and is made available here as a convenience to the forecasting community under the terms of the original license, which is [U.S. Government Public Domain](https://www.usa.gov/government-copyright).


[^1]: These are not realistic values; they are merely chosen to make the example simple to explain.
[^2]: Further complicating this is that the percent change is measured via linear regression, rather than a simple difference. However, this doesn't change the fundamental interpretation, it merely makes the slope more robust to noise.
