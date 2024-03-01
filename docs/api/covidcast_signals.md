---
title: Data Sources and Signals
parent: COVIDcast Main Endpoint
nav_order: 2
has_children: true
---

# Delphi's COVID-19 Data Sources and Signals

Delphi's COVID-19 Surveillance Streams data includes the following data sources.
Data from most of these sources is typically updated daily. You can use the
[`covidcast_meta`](covidcast_meta.md) endpoint to get summary information
about the ranges of the different attributes for the different data sources.

The API for retrieving data from these sources is described in the
[COVIDcast endpoint documentation](covidcast.md). Changes and corrections to
data from this endpoint are listed in the [changelog](covidcast_changelog.md).

To obtain many of these signals and update them daily, Delphi has written
extensive software to obtain data from various sources, aggregate the data,
calculate statistical estimates, and format the data to be shared through the
COVIDcast endpoint of the Delphi Epidata API. This code is 
[open source and available on GitHub](https://github.com/cmu-delphi/covidcast-indicators),
and contributions are welcome.

## COVIDcast Dashboard Signals

The following signals are currently displayed on [the public COVIDcast
dashboard](https://delphi.cmu.edu/covidcast/):


| Kind            | Name                                    | Source                                      | Signal                                          |
|-----------------|-----------------------------------------|---------------------------------------------|-------------------------------------------------|
| Public Behavior | Symptom Searches (Smell and Taste) on Google | [google-symptoms](covidcast-signals/google-symptoms.md) | `s05_smoothed_search`                           |
| Public Behavior | Symptom Searches (Common Cold) on Google   | [google-symptoms](covidcast-signals/google-symptoms.md) | `s02_smoothed_search`                           |
| Early Indicators| COVID-Related Doctor Visits               | [doctor-visits](covidcast-signals/doctor-visits.md)   | `smoothed_adj_cli`                              |
| Early Indicators| Lab-Confirmed Flu in Doctor Visits        | [chng](covidcast-signals/chng.md)                     | `smoothed_adj_outpatient_flu`                   |
| Late Indicators | COVID Hospital Admissions                 | [hhs](covidcast-signals/hhs.md)                       | `confirmed_admissions_covid_1d_prop_7dav`       |
| Late Indicators | Flu Hospital Admissions                   | [hhs](covidcast-signals/hhs.md)                       | `confirmed_admissions_influenza_1d_prop_7dav`   |
| Late Indicators | COVID Deaths                              | [nchs-mortality](covidcast-signals/nchs-mortality.md) | `deaths_covid_incidence_prop`                   |



## All Available Sources and Signals

Beyond the signals available on the COVIDcast dashboard, numerous other signals are
available through our [data export tool](https://delphi.cmu.edu/covidcast/export/) or directly through the API:
