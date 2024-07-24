---
title: Quidel Flu Tests (inactive)
parent: Other Endpoints
nav_order: 2
---

# Quidel Flu Tests (inactive)

These signals are inactive. They were updated until May 19, 2020.

* **Source name: `quidel`
* **Earliest issue available:** April 29, 2020
* **Last issued:** May 19, 2020
* **Number of data revisions since May 19, 2020:** 0
* **Date of last change:** Never
* **Available for:** msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))

## Overview

Data source based on flu lab tests, provided to us by Quidel, Inc. When a
patient (whether at a doctor’s office, clinic, or hospital) has COVID-like
symptoms, doctors may perform a flu test to rule out seasonal flu (influenza),
because these two diseases have similar symptoms. Using this lab test data, we
estimate the total number of flu tests per medical device (a measure of testing
frequency), and the percentage of flu tests that are *negative* (since ruling
out flu leaves open another cause---possibly covid---for the patient's
symptoms), in a given location, on a given day.

The number of flu tests conducted in individual counties can be quite small, so
we do not report these signals at the county level.

The flu test data is no longer updated as of May 19, 2020, as the number of flu
tests conducted during the summer (outside of the normal flu season) is quite
small.

| Signal | Description |
| --- | --- |
| `raw_pct_negative` | The percentage of flu tests that are negative, suggesting the patient's illness has another cause, possibly COVID-19 <br/> **Earliest date available:** 2020-01-31 |
| `smoothed_pct_negative` | Same as above, but smoothed in time <br/> **Earliest date available:** 2020-01-31 |
| `raw_tests_per_device` | The average number of flu tests conducted by each testing device; measures volume of testing <br/> **Earliest date available:** 2020-01-31 |
| `smoothed_tests_per_device` | Same as above, but smoothed in time <br/> **Earliest date available:** 2020-01-31 | 

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `epiweeks` | epiweeks | `list` of epiweeks |
| `locations` | locations | `list` of `hhs<#>` [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt) labels |

## Response

| Field     | Description                                                     | Type             |
|-----------|-----------------------------------------------------------------|------------------|
| `result`  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata` | list of results                                                 | array of objects |
| ...       | ...                                                             | ...              | <!-- TODO -->
| `message` | `success` or error message                                      | string           |