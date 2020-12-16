---
title: Date Coding and Revisions
parent: COVIDcast Epidata API
nav_order: 5
---

# Date Coding and Revisions

Every observation in the COVIDcast Epidata API has two dates attached:

* `time_value`: The time the underlying events happened. For example, when a data
  source reports on COVID test results, the time value is the date the
  results were recorded by the testing provider.
* `issue`: The date the estimates were *issued*. For example, a COVID test
  result might be recorded on October 1st, but it may take several days for
  that report to be collected, aggregated, received by Delphi, and added to our
  database.  The *issue date* is when Delphi makes the data available.

For example, consider using our [doctor visits signal](covidcast-signals/doctor-visits.md),
which estimates the percentage of outpatient doctor visits that are
COVID-related, and consider a result row with `time_value = "2020-05-01"` for
`geo_value = "pa"`. This is an estimate for the percentage in Pennsylvania on
May 1, 2020, which was issued on May 5, 2020. The delay is due to the
aggregation of data by our source and the time taken by the API to ingest the
data provided. Later, the estimate for May 1st could be updated, perhaps because
additional visit data from May 1st arrived at our source and was reported to us.
This constitutes a new issue of the data, and would be reported with a new issue
date.

The format of the `time_value` and `issue` dates depends on the `time_type` API
parameter. Each data source is available for specified time types; check each
source's documentation for details on supported time types.

The available time types include:

* `day`: A daily observation. The `time_value` and `issue` are both reported
  with year, month, and day in `YYYYMMDD` format. (The [API clients](covidcast_clients.md)
  convert this into convenient date objects.)
* `week`: A weekly observation, recording events over 7 days. The `time_value`
  and `issue` are reported with a year and a week number ranging from 1 to 53,
  in `YYYYWW` format. These weeks are [MMWR
  weeks](https://wwwn.cdc.gov/nndss/document/MMWR_Week_overview.pdf) as defined
  by the National Notifiable Diseases Surveillance System, also known as
  "epiweeks". (The [API clients](covidcast_clients.md) convert these into date
  objects representing the first day of the MMWR week, and for those not using
  the clients, packages are available to convert MMWR weeks in many common
  programming languages.)
