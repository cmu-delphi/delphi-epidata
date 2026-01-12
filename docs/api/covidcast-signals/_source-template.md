---
title: SOURCE NAME
parent: Data Sources and Signals
grand_parent: Main Endpoint (COVIDcast)
---

# SOURCE NAME
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `SOURCE-API-NAME` |
| **Data Source** | [DATA SOURCE PROVIDER] |
| **Geographic Levels** | county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md)) |
| **Temporal Granularity** | day (see [date format docs](../covidcast_times.md)) |
| **Date of last data revision:** | Never (see [data revision docs](#changelog)) |
| **Temporal Scope Start** | DATE RELEASED TO API |
| **License** | [LICENSE NAME](../covidcast_licensing.md#APPLICABLE-SECTION) |

A brief description of what this source measures.

| Signal        | Description                                                                                              |
|---------------|----------------------------------------------------------------------------------------------------------|
| `signal_name` | Brief description of the signal, including the units it is measured in and any smoothing that is applied |

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

Your collapsible content goes here. You can still use **Markdown** inside.

</details>

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Describe how any relevant quantities are estimated---both statistically and in
terms of the underlying features or inputs. (For example, if a signal is based
on hospitalizations, what specific types of hospitalization are counted?)

If you need mathematics, we use KaTeX; you can see its supported LaTeX
[here](https://katex.org/docs/supported.html). Inline math is done with *double*
dollar signs, as in $$x = y/z$$, and display math by placing them with
surrounding blank lines, as in

$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}.
$$

Note that the blank lines are essential.

### Standard Error

If this signal is a random variable, e.g. if it is a survey or based on
proportion estimates, describe here how its standard error is reported and the
nature of the random variation.

### Smoothing

If the smoothing is unusual or involves extra steps beyond a simple moving
average, describe it here.

## Limitations

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

If this signal is reported with a consistent lag, describe it here.

If this signal is regularly backfilled, describe the reason and nature of the
backfill here.

## Source and Licensing

If the signal has specific licensing or sourcing that should be acknowledged,
describe it here. Also, include links to source websites for data that is
scraped or received from another source.
