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


| Name | Id | Signal | Unit | UnitShort | noMaps | ExtendedColorScale | Levels | Overrides | SignalTooltip | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Symptom Searches (Smell and Taste) on Google | google-symptoms | s05_smoothed_search | scaled search volume | | true | | | | Google search volume of COVID-related symptom searches about smell and taste | Using Google Symptoms Searches, Delphi obtains the average of Google search volumes for searches related to anosmia (loss of smell), ageusia (loss of taste), and dysgeusia (altered or impaired taste) in each area, since they emerged as unusual symptoms that can be indicative of COVID-19. Note that the average of the three symptom search volumes is not equivalent to the search volume of their union. According to Google, the estimates are not comparable across regions since the values are normalized by population and scaled by region-specific maximum popularity (and for this reason, we omit beehive grids and choropleth maps of this signal on the dashboard). |
| Symptom Searches (Common Cold) on Google | google-symptoms | s02_smoothed_search | scaled search volume | | true | | | | Google search volume of COVID-related symptom searches about common cold | Using Google Symptoms Searches, Delphi obtains the average of Google search volumes for searches related to nasal congestion, post nasal drip, rhinorrhea, sinusitis, rhinitis, and common cold in each area. These symptoms have shown positive correlation with reported COVID cases, especially since Omicron was declared a variant of concern by the World Health Organization. Note that the average search volume of these symptoms is not equivalent to the search volume of their union. According to Google, the estimates are not comparable across regions since the values are normalized by population and scaled by region-specific maximum popularity (and for this reason, we omit beehive grids and choropleth maps of this signal on the dashboard). |
| COVID-Related Doctor Visits | doctor-visits | smoothed_adj_cli | per 100 visits | | | | | | Percentage of daily doctor visits that are due to COVID-like symptoms | Delphi receives aggregated statistics from health system partners on COVID-related outpatient doctor visits, derived from ICD codes found in insurance claims. Using this data, we estimate the percentage of daily doctor’s visits in each area that are due to COVID-like illness. Note that these estimates are based only on visits by patients whose data is accessible to our partners. |
| Lab-Confirmed Flu in Doctor Visits | chng | smoothed_adj_outpatient_flu | per 100 visits | | | | | | Percentage of daily doctor visits that are due to lab-confirmed influenza | Delphi receives aggregated statistics from Change Healthcare, Inc. on lab-confirmed influenza outpatient doctor visits, derived from ICD codes found in insurance claims. Using this data, we estimate the percentage of daily doctor’s visits in each area that resulted in a diagnosis of influenza. Note that these estimates are based only on visits by patients whose insurance claims are accessible to Change Healthcare. |
| COVID Hospital Admissions | hhs | confirmed_admissions_covid_1d_prop_7dav | | | | true | [nation, state, county] | County: Id: hospital-admissions Signal: smoothed_adj_covid19_from_claims | Confirmed COVID-19 hospital admissions per 100,000 people | This data shows the number of hospital admissions with lab-confirmed COVID-19 each day. At the state level and above, we show data from the Report on Patient Impact and Hospital Capacity published by the US Department of Health & Human Services (HHS). At the county and metro level, we show data from the Community Profile Report published by the Data Strategy Execution Workgroup. |
| Flu Hospital Admissions | hhs | confirmed_admissions_influenza_1d_prop_7dav | | | | true | [nation, state] | | Confirmed influenza hospital admissions per 100,000 people | This data shows the number of hospital admissions with lab-confirmed influenza each day. We source this data from the Report on Patient Impact and Hospital Capacity published by the US Department of Health & Human Services (HHS). |
| COVID Deaths | nchs-mortality | deaths_covid_incidence_prop | | | | | | | Newly reported COVID-19 deaths per 100,000 people, based on NCHS mortality data. | This data shows the number of COVID-19 deaths newly reported each week. The signal is based on COVID-19 death counts compiled and made public by [the National Center for Health Statistics](https://www.cdc.gov/nchs/nvss/vsrr/COVID19/index.htm). |

## All Available Sources and Signals

Beyond the signals available on the COVIDcast dashboard, numerous other signals are
available through our [data export tool](https://delphi.cmu.edu/covidcast/export/) or directly through the API:
