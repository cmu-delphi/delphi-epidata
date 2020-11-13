---
title: SOURCE NAME
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# SOURCE NAME
{: .no_toc}

* **Source name:** `SOURCE-API-NAME`
* **First issued:** FIRST ISSUE DATE IN API
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

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

## Source

If the signal has specific licensing or sourcing that should be acknowledged,
describe it here. Also, include links to source websites for data that is
scraped or received from another source.

## Licensing

### For signals constructed by Delphi:

This data is provided under the terms of the [Creative Commons Attribution
license](https://creativecommons.org/licenses/by/4.0/). If you use this data,
you must cite [Delphi](https://delphi.cmu.edu/) COVIDcast API, preferably by
providing a link to this page.

### For signals republished from other sources:

This data is originally published by SOURCE NAME under the terms LICENSE. Cite
the source as

> SOURCE'S PREFERRED ATTRIBUTION.

If you use the Delphi COVIDcast API to access this data, we additionally request
you acknowledge us in your product or publication.

### For signals from the United States government:

This data is originally published by AGENCY NAME. As a work of the United States
Federal Government, it is in the public domain.

If you use the Delphi COVIDcast API to access this data, we request you
acknowledge us in your product or publication.
