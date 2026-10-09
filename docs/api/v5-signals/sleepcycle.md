---
title: Sleep Cycle Nocturnal Coughs
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 10
---

# Sleep Cycle Nocturnal Coughs
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `sleepcycle` |
| **Data Source** | Nocturnal cough rates from the [Sleep Cycle](https://sleepcycle.com) sleep-tracking app |
| **Geographic Levels** | `county`, `hrr`, `msa`, `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Daily |
| **Reporting Cadence** | Daily |
| **Temporal Scope Start** | 2023-01-07 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | None |
| **License** | TODO |


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

The source measures the frequency of moderately high and very high nocturnal cough rates.
It is built from de-identified data from the Sleep Cycle sleep tracking app, contributed by parent company Sleep Cycle.
Since the data captures symptoms, it can be used for many respiratory pathogens, including influenza and COVID-19, as well as other medical and environmental conditions that may contribute to coughing, for example, wildfire smoke.
This source is noised at the `epsilon = 1` level per user-day under [differential privacy (DP)](https://desfontain.es/blog/friendly-intro-to-differential-privacy.html).

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `pct_cough_2_plus_7dav` | N/A | Percentage, 7-day window | Percent of users who coughed 2 or more times an hour (on average) while sleeping. |
| `pct_cough_10_plus_7dav` | N/A | Percentage, 7-day window | Percent of users who coughed 10 or more times an hour (on average) while sleeping. |

---

## Estimation

### Metric Definition

To prevent reidentification of participating users, this dataset is noised in a way that makes it differentially private at the `epsilon = 1` level [per user per day](https://registry.opendp.org/trust-models/#:~:text=Unit%20of%20Privacy).
(What does `epsilon = 1` mean? See [discussion of "updated probability" here](https://desfontain.es/blog/differential-privacy-in-more-detail.html).)
We noise numerators for each indicator with `epsilon = 1/2` and sensitivity `delta = 1`.
This results in us applying Laplacian noise with `location = 0` and `scale = 2`.
The noise has units of counts.

New noise values are drawn for every county $$i$$ and time $$t$$.
Once a county $$i$$ and time $$t$$ key as a noise value assigned, that noise value is reused for every issue made to that county and time key's value.

Raw county numerators only are noised with randomly drawn DP-conforming noise before any geoaggregation or smoothing is performed.
Denominators are unnoised.

When a raw value is close to a natural threshold (for numerator, 0 or $$n_i$$) or the noise is relatively large, the noised value can become impossible (< 0, > $$n_i$$).
These values are left as-is until after geoaggregation, smoothing, and percentage calculation are done, after which impossible percentages are truncated to the closest boundary (0, 100).
Early truncation biases aggregated values.

For county $$i$$ and time $$t$$, with numerator count $$Y_{it}$$, denominator $$N_{it}$$, and DP noise $$\delta_{it}$$ (in count units),

$$
\hat{p}_{it} = 100 \cdot \frac{Y_{it} + \delta_{it}}{N_{it}}.
$$

These metrics only include users who used the app on a given day and agreed to share their data.
The numerator counts the number of users whose average hourly nocturnal cough rate was greater than `x`.
Average hourly cough rate for a user is calculated as total number of coughs while sleeping divided by total number of hours slept.
This includes any kind of sleep -- sleeping overnight, but also napping, increased sleeping while sick, etc.

For non-county location $$i$$ and time $$t$$, with estimated numerator count $$Y'_{it}$$, denominator $$N_{it}$$,

$$
\hat{p}_{it} = 100 \cdot \frac{Y'_{it}}{N_{it}}.
$$

Estimated numerator counts for non-county locations incorporate DP noise via the geoaggregation process.

### Smoothing

TODO check
For each geography, a 7-day trailing sum is taken of every noised numerator count and the total user count, from which the percentageis then calculated.
The window must contain at least 5 of 7 days to produce a value.
Smoothing is computed by Delphi.

### Uncertainty

This source provides 90% confidence intervals for all indicators via the `ci_lower` and `ci_upper` columns ($$z = 1.645$$). Because cough indicators are binomial percentages, [Wilson score intervals](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Wilson_score_interval) are used inflated by the DP noise variance. It is estimated as

$$
100 \cdot \frac{\hat{p} + \frac{z^2}{2N} \pm z \sqrt{\frac{\hat{p}(1 - \hat{p})}{N} + \frac{z^2}{4N^2} + c \left(1 + \frac{z^2}{N}\right)}}{1 + \frac{z^2}{N}}
$$

Subtracting gives `ci_lower` and adding gives `ci_upper`. Compared to a standard Wilson interval, the term $$c \left(1 + \frac{z^2}{N}\right)$$ inflates the interval to account for noise, where $$c = \frac{\sigma^2_{\text{noise}}}{N^2}$$ scales the numerator noise variance $$\sigma^2_{\text{noise}}$$ to proportion units.

This approach preserves nominal 90% coverage in the presence of differential privacy noise while keeping the intervals well-behaved near 0% and 100%.

### Temporal Handling

Observations cover single calendar days. Each value reflects nocturnal cough events recorded during sleep sessions attributed to that date.

- `reference_time` is the observation date (`YYYY-MM-DD`). For 7-day smoothed indicators (`_7dav`), `reference_time` marks the final date of the trailing 7-day window.
- `report_time` is the ingestion timestamp in UTC. Sleep Cycle refreshes data upstream approximately every four hours (six times per day). 

### Geographic Handling

Cough data arrives at one native geographic level: county (`county`).
Raw county numerators only are noised with DP-conforming noise before any geoaggregation or smoothing is performed.
Denominators are unnoised.

All other geographic levels (`msa`, `hrr`, `state`, `hhs`, `census_division`, `census_region`, `nation`) are built by directly summing daily county counts -- denominators and DP-noised numerators are aggregated separately.
Aggregation is performed on daily counts before computing 7-day sums, without imputation, so `fill_method` is always `source`.

This source has good coverage at the county level.
In the month of Sept 2026, values were reported for 3030 counties on at least one day.
However, we restrict locations from being reported when we consider them to be too noisy, sparse, or generally not useful.
See the Missingness & Privacy section for more information.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | datetime | Ingestion timestamp in UTC (`YYYY-MM-DD HH:MM:SS`). |
| `geo_type` | Primary Key | string | Geographic level (e.g., `county`, `state`). |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., FIPS, state abbreviation). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation (`source`, `fill_ave`, or `fill_zero`). |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation (`YYYY-MM-DD`). |
| `value` | Value Column | float | The recorded measurement (e.g., count, percentage, rate, or statistical estimate). |
| `ci_lower` | Value Column | float | Lower bound of the 90% confidence interval. |
| `ci_upper` | Value Column | float | Upper bound of the 90% confidence interval. |

---

## Missingness & Privacy

Under the guarantees of differential privacy, we are _able_ to release values for all locations, even with very small sample sizes.
However, we restrict locations from being reported when we consider them to be too noisy, sparse, or generally not useful.
For example, a signal for a given location with a confidence interval of 0-100% isn't useful and will not be reported.

Because of this, as of Oct 7 2026, we only report 258 counties, 151 HRRs, 136 MSAs, and 43 states.
All locations are reported for higher geographic types (census division, census region, nation).

TODO suppressed values appear as `null` or are omitted?

---

## Limitations

These indicators are calculated using only app users who used the app on a given day and agreed to share their data.

It's not clear how representative this data is of the general US population, for example, in terms of age and race/ethnicity.
Since it is phone app-based data collection, we might expect it to skew young and/or urban.

Sleep Cycle reports some demographics in [Appendix:Table 1 of this paper](https://assets-eu.researchsquare.com/files/rs-7977267/v1_covered_4baae827-ce58-4dd2-81b8-a59f647eb8c1.pdf?c=1764681187).
Note however that reporting demographics is optional and most users do not do it.
Demographics are likely subject to reporting bias.

We expect there to be day-of-week affects in the dataset.
For example, people tend to sleep in on the weekends.
Sick people are also more likely to sleep for a longer period of time.
It's not clear how that affects cough _rate_, however.

The use of differential privacy does increase the variance of the data, but it is done in an unbiased way that doesn't obscure medium to long-term trends.
It also doesn't obscure revision behavior, since the DP noise $$\delta_{it}$$ for county $$i$$ and time $$t$$ is reused for every issue made to that county and time's value.

Sleep Cycle also uses differential privacy to obscure user locations.
All latitude-longitude coordinates collected in the app are automatically perturbed with Laplacian noise on the user's phone.
The Laplacian noise has a standard deviation of about 500 meters.
This is small compared to the size of most [US counties](https://en.wikipedia.org/wiki/List_of_United_States_counties_and_county_equivalents) so we don't expect it to change estimates very much.
Counties are smaller in US territories and in the state of Virginia, so values for sub-state locations in those regions may have increased uncertainty.

---

## Lag & Backfill

Since this is digital surveillance, we expect revisions to be minimal within a matter of days.
We see revisions to indicator values within 24 hours of the first time an observation (location-date key) is reported.

The only source of revisions we expect outside of that is users re-connecting to the internet after a period of using the app offline, which would then send the last `n` days of their data to Sleep Cycle.
Thus, values for those days would be revised.
Although this is possible, it's unlikely that a user would be totally offline for more than a couple days.
In reality, we haven't yet seen any revisions that modify reference dates from a long time ago (more than 1 day).

Data is updated 6 times a day, and revisions within the first few updates are large.

Data is reported with less than 1 day of lag.
That is, we start getting reports of what happened on reference date `t` _on_ date `t`.
*Note*: This means that early versions of a value are based on _partial_ information.

---

## Source and Licensing

De-identified digital surveillance contributed by Sleep Cycle.
This dataset is made available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
It may not be used for commercial purposes.
TODO
