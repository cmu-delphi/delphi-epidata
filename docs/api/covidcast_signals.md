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

| Kind | Name | Source | Signal |
|---|---|---|---|
| Public Behavior | People Wearing Masks | [`fb-survey`](covidcast-signals/fb-survey.md) | `smoothed_wwearing_mask_7d` |
| Public Behavior | Vaccine Acceptance | [`fb-survey`](covidcast-signals/fb-survey.md) | `smoothed_wcovid_vaccinated_appointment_or_accept` |
| Public Behavior | COVID Symptom Searches on Google | [`google-symptoms`](covidcast-signals/google-symptoms.md) | `sum_anosmia_ageusia_smoothed_search` |
| Early Indicators | COVID-Like Symptoms | [`fb-survey`](covidcast-signals/fb-survey.md) | `smoothed_wcli` |
| Early Indicators | COVID-Like Symptoms in Community | [`fb-survey`](covidcast-signals/fb-survey.md) | `smoothed_whh_cmnty_cli` |
| Early Indicators | COVID-Related Doctor Visits | [`doctor-visits`](covidcast-signals/doctor-visits.md) | `smoothed_adj_cli` |
| Cases and Testing | COVID Cases | [`jhu-csse`](covidcast-signals/jhu-csse.md) | `confirmed_7dav_incidence_prop` |
| Late Indicators | COVID Hospital Admissions | [`hhs`](covidcast-signals/hhs.md) | `confirmed_admissions_covid_1d_prop_7dav` |
| Late Indicators | Deaths | [`jhu-csse`](covidcast-signals/jhu-csse.md) | `deaths_7dav_incidence_prop` |

## All Available Sources and Signals

Beyond the signals available on the COVIDcast dashboard, numerous other signals are
available through our [data export tool](https://delphi.cmu.edu/covidcast/export/) or directly through the API:
