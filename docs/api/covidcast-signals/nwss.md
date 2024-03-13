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
The project was launched in September 2020 and continues to today.
## Table of contents
{: .no_toc .text-delta}

1. TOC {:toc}

## 
The original source is measured at the level of [sample-site](https://www.cdc.gov/nwss/sampling.html), either at or upstream from a regional wastewater treatment plants (these are roughly at the county-level, but are not coterminous with counties); presently we do not provide the site-level or county-aggregated data, but will do so within the coming months.

To obtain either the state or national level signals from the sample-site level signals, we aggregate using population-served weighted sums, where the total population for a given `geo_value` is the total population served at sites with non-missing values. For example, if there are 3 sample sites in Washington on a particular day, then the numerator is the corresponding site population, and the denominator the sum of the population served by the 3 sample sites  (rather than the entire population of the state).

This source is derived from two API's: the NWSS [metric data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6/about_data) and the NWSS [concentration data](https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Concentration-in-Wastewater/g653-rqe2/about_data).
These sources combine several signals each, which we have broken into separate signals.
They vary across the post-processing method, the normalization method, and the underlying data provider.
## Post Processing methods
| Post-processing method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pcr\_conc\_smoothed    | PCR measurements (the exact method depends on the data provider), initially provided in virus concentrations per volume of input (type depends on normalization scheme below). This is then normalized as described below, then smoothed using a cubic spline, then aggregated to the given `geo_type` with a population-weighted sum.                                                                                                                              |
| detect\_prop\_15d      | The proportion of tests with SARS-CoV-2 detected, meaning a cycle threshold (Ct) value <40 for RT-qPCR or at least 3 positive droplets/partitions for RT-ddPCR, by sewershed over the prior 15-day period. The detection proportion is the 15-day rolling sum of SARS-CoV-2 detections divided by the 15-day rolling sum of the number of tests for each sample site and multiplying by 100, aggregated with a population weighted sum. The result is a percentage. |
| percentile             | This metric shows whether SARS-CoV-2 virus levels at a site are currently higher or lower than past historical levels at the same site. 0% means levels are the lowest they have been at the site; 100% means levels are the highest they have been at the site. Note that at either the state or national `geo_types`, this is not the percentile for overall state levels, but the average percentile across sites, weighted by population.                       |
| ptc\_15d               | The percent change in SARS-CoV-2 RNA levels over the 15 days preceding `timestamp`. It is the coefficient of the linear regression of the log-transformed unsmoothed PCR concentration, expressed as a percentage change.                                                                                                                                                                                                                                           |


## Normalization methods
| Normalization method | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Flow normalization   | This uses viral concentration times flow rate, divided by population served, which results in viral gene copies per person per day. It's applied to concentrations measured from unconcentrated wastewater (also labeled `raw_wastewater` in the socrata dataset's `key_plot_id`). It tracks the total number of individuals whose shedding behavior has changed.                                                                                                                                                                                                                                                                                          |
| microbial            | This divides by the concentration of one of several potential fecal biomarkers commonly found throughout the population. These include molecular indicators of either viruses or bacteria. The most common viral indicator comes from the pepper mild mottle virus (pmmov), a virus that infects plants that is commonly found in pepper products. The most common bacterial indicators come from Bacteroides HF183 and Lachnospiraceae Lachno3, both common gut bacteria. It's applied to sludge samples (also labeled `post_grit _removal` in the socrata dataset's `key_plot_id`), which have been concentrated in preparation for treatment. The resulting value is unitless, and tracks the proportion of individuals who's shedding behavior has changed. |
## Providers
In the fall of 2023, there was a major shift from Biobot as the primary commercial p
| Provider    | Available                | Description                                                                                                                                                                                                                                                    |
|-------------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| cdc\_verily | 2023/10/30-Today         | Data analyzed by [verily](https://verily.com/solutions/public-health/wastewater) on behalf of the CDC                                                                                                                                                          |
| nwss        | 2020/06/21-Today         | Data reported by the respective State, Territorial and Local public health agencies; the actual processing may be done by a private lab such as verily or biobot, or it may be done directly by the agency, or it may be processed by a partnering university. |
| wws         | 2021/12/26-Today         | Data analyzed by [Wastewater Scan](https://www.wastewaterscan.org/en), a Stanford/Emory nonprofit.                                                                                                                                                             |
| cdc\_biobot | 2020/06/21(?)-2023/10/30 | Data analyzed by [Biobot](https://biobot.io/) on behalf of the CDC.                                                                                                                                                                                                                                              |

These contain various derived signals described more below, as well as
aggregating across different methods of normalizing:

Flow normalization:

Microbial normalization:

To derive the state level data from the site-level data, we do a weighted sum
using the populations served.

| Signal | <br/> **Earliest date available:** |
|-----------------------------------------------|------------------------------------|
| `pcr_con_smoothed_cdc_verily_flow_population` | |
|                                               | |

## Estimation

Describe how any relevant quantities are estimated---both statistically and in
terms of the underlying features or inputs. (For example, if a signal is based
on hospitalizations, what specific types of hospitalization are counted?)

If you need mathematics, we use KaTeX; you can see its supported LaTeX
[here](https://katex.org/docs/supported.html). Inline math is done with *double*
dollar signs, as in $$x = y/z$$, and display math by placing them with
surrounding blank lines, as in

$$ \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}. $$

Note that the blank lines are essential.

### Standard Error

If this signal is a random variable, e.g. if it is a survey or based on
proportion estimates, describe here how its standard error is reported and the
nature of the random variation.

### Smoothing

If the smoothing is unusual or involves extra steps beyond a simple moving
average, describe it here.

## Limitations


NWSS is still expanding to get coverage nationwide: to get an idea of the extent of counties currently covered, see [this map](https://www.cdc.gov/nwss/progress.html).
At a particular point in time.


Any limitations in the interpretation of this signal, such as limits in its
geographic coverage, limits in its interpretation (symptoms in a survey aren't
always caused by COVID, our healthcare partner only is part of the market, there
may be a demographic bias in respondents, etc.), known inaccuracies, etc.

## Missingness

Describe *all* situations under which a value may not be reported, and what that
means. If the signal ever reports NA, describe what that means and how it is
different from missingness. For example:

When fewer than 100 survey responses are received in a geographic area on a
specific day, no data is reported for that area on that day; an API query for
all reported geographic areas on that day will not include it.

## Lag and Backfill

None of the signals suffer from significant lag; most are a day old

If this signal is reported with a consistent lag, describe it here.

If this signal is regularly backfilled, describe the reason and nature of the
backfill here.


Due to the [cubic spline smoothing](https://en.wikipedia.org/wiki/Smoothing_spline), any of the `pcr_conc_smoothed` signals may change in the 4th and smaller significant figure at intervals of approximately 1-3 days; outside of the most recent data where smoothing directly relies on newly added data-points, these revisions should have approximately a mean of zero. To reduce some of this variation, we have rounded to the 4th significant figure; this digit may still vary.


Whenever a new maximum occurs at a location, all historical data for a `percentile` signal has the potential to shift, potentially quite drastically.

## Source and Licensing

If the signal has specific licensing or sourcing that should be acknowledged,
describe it here. Also, include links to source websites for data that is
scraped or received from another source.
