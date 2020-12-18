---
title: Department of Health & Human Services
parent: Data Sources and Signals
grand_parent: COVIDcast Epidata API
---

# SOURCE NAME
{: .no_toc}

* **Source name:** `hhs`
* **First issued:** TBD
* **Number of data revisions since 19 May 2020:** 0
* **Date of last change:** Never
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))
* **Time type:** day (see [date format docs](../covidcast_times.md))
* **License:** [Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/1-0/)

The U.S. Department of Health & Human Services (HHS) publishes several
datasets on patient impact and hospital capacity. Two of these
datasets are mirrored in Epidata at the following endpoints:

* [COVID-19 Hospitalization: States](../covid_hosp.md) - daily resolution, state aggregates
* [COVID-19 Hospitalization: Facilities](../covid_hosp_facilities.md) - weekly resolution, individual hospitals

Both datasets contain dozens of columns that break down hospital
resource usage in different ways.

This indicator makes available several commonly-used combinations of
those columns, aggregated geographically. In particular, we include
the sum of all adult and pediatric COVID-19 hospital admissions. This
sum is used as the "ground truth" for hospitalizations by the (Reich
lab COVID-19 forecast
hub](https://github.com/reichlab/covid19-forecast-hub/blob/master/data-processed/README.md#hospitalizations].


| Signal | Geography | Resolution | Description |
| --- | --- | --- | --- |
| `confirmed_admissions_1d` | state | 1 day | Sum of adult and pediatric confirmed COVID-19 hospital admissions occuring each day. |
| `sum_confirmed_suspected_admissions_1d` | state | 1 day | Sum of adult and pediatric confirmed and suspected COVID-19 hospital admissions occuring each day. |
| `confirmed_admissions_7d` | county, hrr, msa, state | 7 days | Sum of adult and pediatric confirmed COVID-19 hospital admissions occuring over a span of 7 days. |
| `sum_confirmed_suspected_admissions_7d` | county, hrr, msa, state | 7 days | Sum of adult and pediatric confirmed and suspected COVID-19 hospital admissions occuring over a span of 7 days. |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

### Statewise, daily resolution

Statewise daily resolution signals use the following four columns from
the HHS state timeseries dataset:

* `previous_day_admission_[adult|pediatric]_covid_[confirmed|suspected]`

The `confirmed` signal is the sum of the two `confirmed` columns: 

* adult
* pediatric

The `sum_confirmed_suspected` signal is the sum of all four columns:

* adult confirmed
* adult suspected
* pediatric confirmed
* pediatric suspected

The source data specifies that admissions occurred on the previous
day. We automatically adjust the date of each result so that
admissions are incident on that date.

### Facilitywise, 7-day resolution

Facilitywise 7-day resolution signals use the following four columns
from the HHS facilitywise dataset:

* `previous_day_admission_[adult|pediatric]_covid_[confirmed|suspected]_7_day_sum`

The `confirmed` signal is the sum of the two `confirmed` columns: 

* adult
* pediatric

The `sum_confirmed_suspected` signal is the sum of all four columns:

* adult confirmed
* adult suspected
* pediatric confirmed
* pediatric suspected

The source data specifies that admissions for the previous day are
summed over a seven-day period starting with the collection date. We
automatically adjust the date for each result so that admissions are
incident to the seven day period starting with that date.

The source data uses an unusual week definition (originally
Friday-Thursday; Thursday-Wednesday with our adjustment). Because this
definition does not match that used by epiweeks, this dataset uses
`time_type=day`. However, data will only ever be present for dates that
are the start of a seven-day collection period (ie Thursdays).

Facility-wise data is aggregated to other geographies using the facility's FIPS
code, if available, and the ZIP5 code of the facility otherwise.

## Limitations

TBD

## Lag and Backfill

TBD

## Source and Licensing

This indicator mirrors and lightly aggregates data originally
published by the U.S. Department of Health & Human Services under an
[Open Data Commons Open Database License
(ODbL)](https://opendatacommons.org/licenses/odbl/1-0/). The ODbL
permits sharing, transformation, and redistribution of data or derived
works so long as all public uses are distributed under the ODbL and 
attributed to the source. For more details, consult the official
license text.
