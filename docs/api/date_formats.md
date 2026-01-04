---
title: Date Formats
parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 901
---

# Date Formats
{: .no_toc}

This page documents the valid date and time formats accepted by various API endpoints.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Epiweeks

Epiweeks (Epidemiological Weeks) use the [U.S. CDC definition](https://ndc.services.cdc.gov/wp-content/uploads/MMWR_week_overview.pdf). That is, the first epiweek each year is the week, starting on a Sunday, containing January 4.

**Format:** `YYYYWW`
*   `YYYY`: Four-digit year
*   `WW`: Two-digit week (01-53)

Example: `201501` represents the first epiweek of 2015.

See [this page](https://www.cmmcp.org/mosquito-surveillance-data/pages/epi-week-calendars-2008-2020) for more information and calendars.

## Dates

Dates generally follow the ISO 8601 basic format, but without hyphens.

**Format:** `YYYYMMDD`
*   `YYYY`: Four-digit year
*   `MM`: Two-digit month (01-12)
*   `DD`: Two-digit day (01-31)

Example: `20150201` represents February 1st, 2015.

## Specifying Lists and Ranges

Many API parameters accept lists of values or ranges.

`list` parameters consist of a comma-separated list of individual values or, for numeric parameters (like epiweeks or dates), a hyphenated range of values.

**Examples:**

*   **Single Value:** `param=201530`
*   **List of Values:** `param=201401,201501,201601`
*   **Range:** `param=200501-200552`
*   **Mixed List and Range:** `param=201440,201501-201510`
*   **Date Range:** `param=20070101-20071231`
