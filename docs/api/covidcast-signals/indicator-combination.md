---
title: Indicator Combination
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# Indicator Combination
{: .no_toc}

* **Source name:** `indicator-combination`

This source provides signals which are combinations of the other sources,
calculated or composed by Delphi. It is not a primary data source.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Statistical Combination Signals (Inactive)

The NMF combination signals were deactivated on March 17, 2021. Documentation for
these signals is still available on the page for 
[inactive indicator-combination signals](indicator-combination-inactive.md).

## Compositional Signals: Confirmed Cases and Deaths

* **Earliest issue available:** 7 July 2020
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [12 October 2020](../covidcast_changelog.md#indicator-combination)
* **Available for:** county, msa, hrr, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))

These signals combine the cases and deaths data from JHU and USA Facts. This is
a straight composition: the signals below use the [JHU signal data](jhu-csse.md)
for Puerto Rico, and the [USA Facts signal data](usa-facts.md) everywhere else.
Consult each signal's documentation for information about geographic reporting,
backfill, and other limitations.

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumulative_num` | Cumulative number of confirmed COVID-19 cases <br/> **Earliest date available:** 2020-02-20 |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumulative_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population <br/> **Earliest date available:** 2020-02-20 |
| `confirmed_incidence_num` | `confirmed_7dav_incidence_num` | Number of new confirmed COVID-19 cases, daily <br/> **Earliest date available:** 2020-02-20 |
| `confirmed_incidence_prop` | `confirmed_7dav_incidence_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily <br/> **Earliest date available:** 2020-02-20 |
| `deaths_cumulative_num` | `deaths_7dav_cumulative_num` | Cumulative number of confirmed deaths due to COVID-19 <br/> **Earliest date available:** 2020-02-20 |
| `deaths_cumulative_prop` | `deaths_7dav_cumulative_prop` | Cumulative number of confirmed due to COVID-19, per 100,000 population <br/> **Earliest date available:** 2020-02-20 |
| `deaths_incidence_num` | `deaths_7dav_incidence_num` | Number of new confirmed deaths due to COVID-19, daily <br/> **Earliest date available:** 2020-02-20 |
| `deaths_incidence_prop` | `deaths_7dav_incidence_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily <br/> **Earliest date available:** 2020-02-20 |
