---
title: Doctor Visits
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# Doctor Visits

* **Source name:** `indicator-combination`
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source is based on information about outpatient visits, provided to us
by healthcare partners. Using this outpatient data, we estimate the percentage
of COVID-related doctor's visits in a given location, on a given day.

| Signal | Description |
| --- | --- |
| `smoothed_cli` | Estimated percentage of outpatient doctor visits primarily about COVID-related symptoms, based on data from healthcare partners, smoothed in time using a Gaussian linear smoother |
| `smoothed_adj_cli` | Same, but with systematic day-of-week effects removed (so that every day "looks like" a Monday)|

Day-of-week effects are removed by fitting a model to all data in the United
States; the model includes a fixed effect for each day of the week, except
Monday. Once these effects are estimated, they are subtracted from each
geographic area's time series. This removes day-to-day variation that arises
solely from clinic schedules, work schedules, and other variation in doctor's
visits that arise solely because of the day of week.

## Lag and Backfill

Note that because doctor's visits may be reported to our healthcare partners
several days after they occur, these signals are typically available with
several days of lag. This means that estimates for a specific day are only
available several days later.

The amount of lag in reporting can vary, and not all visits are reported with
the same lag. After we first report estimates for a specific date, further data
may arrive about outpatients visits on that date. When this occurs, we issue new
estimates for those dates. This means that a reported estimate for, say, June
10th may first be available in the API on June 14th and subsequently revised on
June 16th.

## Limitations

This data source is based on outpatient visit data provided to us by healthcare
partners. Our partners can report on a portion of the United States healthcare
market, but not all of it, and so this source only represents those visits known
to our partners. Their coverage and market share may vary across the United
States.
