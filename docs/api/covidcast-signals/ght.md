---
title: Google Health Trends
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Google Health Trends
{: .no_toc}

* **Source name:** `ght`
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** dma, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))

## Overview

This data source (`ght`) is based on Google searches, provided to us by Google
Health Trends. Using this search data, we estimate the volume of COVID-related
searches in a given location, on a given day. This signal is measured in
arbitrary units (its scale is meaningless); larger numbers represent higher
numbers of COVID-related searches.

| Signal | Description |
| --- | --- |
| `raw_search` | Google search volume for COVID-related searches, in arbitrary units that are normalized for population |
| `smoothed_search` | Google search volume for COVID-related searches, in arbitrary units that are normalized for population, smoothed in time as [described below](#smoothing) |

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

We query the Google Health Trends API for overall searcher interest in a set of
COVID-19 related terms about anosmia (lack of smell or taste), which emerged as
a symptom of the coronavirus. The specific terms are:

* "why cant i smell or taste"
* "loss of smell"
* "loss of taste"
* Anosmia generally, by querying for topics linked by Google to the anosmia item
  in the Freebase knowledge graph (ID `/m/0m7pl`)

The API provides data at the Nielsen Designated Marketing Area (DMA) level and
at the State level. This information reported by the API is unitless and
pre-normalized for population size; i.e., the time series obtained for New York
and Wyoming states are directly comparable. The public has access to a limited
view of such information through [Google Trends](https://trends.google.com).

DMA-level data are aggregated to the MSA and HRR level through
population-weighted averaging.

### Smoothing

The smoothed signal is produced using the following strategy. For each date, we
fit a local linear regression, using a Gaussian kernel, with only data on or
before that date. (This is equivalent to using a negative half normal
distribution as the kernel.) The bandwidth is chosen such that most of the
kernel weight is placed on the preceding seven days. The estimate for the data
is the local linear regression's prediction for that date.

## Limitations

When query volume in a region is below a certain threshold, set by Google, it is
reported as 0. Areas with low query volume hence exhibit jumps and
zero-inflation, as small variations in the signal can cause it to be sometimes
truncated to 0 and sometimes reported at its actual level.

Google does not describe the units of its reported numbers, so the scale is arbitrary.



