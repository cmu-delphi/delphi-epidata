---
title: SOURCE NAME
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# SOURCE NAME
{: .no_toc}

* **Source name:** `SOURCE-API-NAME`
* **First issued:** DATE RELEASED TO API
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [LICENSE NAME](../covidcast_licensing.md#APPLICABLE-SECTION)

A brief description of what this source measures.

| Signal | Description |
| --- | --- |
| `signal_name` | Brief description of the signal, including the units it is measured in and any smoothing that is applied |

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

## Lag and Backfill

If this signal is reported with a consistent lag, describe it here.

If this signal is regularly backfilled, describe the reason and nature of the
backfill here.

## Source and Licensing

If the signal has specific licensing or sourcing that should be acknowledged,
describe it here. Also, include links to source websites for data that is
scraped or received from another source.
