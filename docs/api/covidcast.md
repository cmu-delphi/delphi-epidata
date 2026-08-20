---
title: Main Endpoint (COVIDcast)
has_children: true
nav_order: 3
---

# Main Epidata API

This legacy Epidata API endpoint was formerly called COVIDcast.

This is the documentation for accessing all Delphi's indicators via the `covidcast` endpoint of [Delphi](https://delphi.cmu.edu/)'s
epidemiological data API. This API provides data on the spread and impact of infectious diseases, including COVID-19, across the United States, most of which is available at the
county level and updated daily. This data powers our public [COVIDcast
map](https://delphi.cmu.edu/covidcast/) which includes testing, cases, and death data,
as well as unique healthcare and survey data Delphi acquires through its
partners. Many additional data sources and pathogen indicator types are available. The API allows users to select specific signals and download data for
selected geographical areas. For a comprehensive look at the sources, signals, and geographic regions available through the API, please visit [EpiPortal](https://delphi.cmu.edu/epiportal/?hosted_by_delphi=on).


> **Get updates:** Delphi operates a [mailing list](https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api) for users of the main Epidata API. We will use the list to announce API changes, corrections to data, and new features; API users may also use the mailing list to ask general questions about its use. If you use the API, we strongly encourage you to [subscribe](https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api).
{: .important }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Licensing
Like all other Delphi Epidata datasets, our data is freely available to the public. However, our indicators include data from many different sources, with data licensing handled separately for each source. For a summary of the licenses used and a list of the indicators each license applies to, we suggest users visit our [licensing](covidcast_licensing.md) page. Licensing information is also summarized on each indicator's details page.
We encourage academic users to [cite](README.md#citing) the data if they
use it in any publications. Our [data ingestion
code](https://github.com/cmu-delphi/covidcast-indicators) and [API server
code](https://github.com/cmu-delphi/delphi-epidata) is open-source, and
contributions are welcome. Further documentation on Delphi's APIs is available
in the [API overview](README.md).

## Accessing the Data

Our [COVIDcast site](https://delphi.cmu.edu/covidcast/) provides an interactive
visualization of a select set of the data signals available and relevant
during the COVID-19 pandemic, and provides a data export feature to download
any data range as a CSV file.

Several [API clients are available](covidcast_clients.md) for common programming
languages, so you do not need to construct API calls yourself to obtain
COVIDcast data. Once you install the appropriate client for your programming
language, accessing data is as easy as:

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

```python
from epidatpy import EpiDataContext, EpiRange

epidata = EpiDataContext()
apicall = epidata.pub_covidcast(
    data_source="fb-survey",
    signals="smoothed_cli",
    geo_type="county",
    time_type="day",
    geo_values="*",
    time_values=EpiRange(20200501, 20200507),
)
data = apicall.df()
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```r
library(epidatr)

data <- pub_covidcast('fb-survey', 'smoothed_cli', 'county', 'day', geo_values = '06001',
                     time_values = c(20200401, 20200405:20200414))
```
  </div>
</div>

[The API clients](covidcast_clients.md) have extensive documentation providing
further examples.

Alternatively, users can [manually construct URLs and parse responses to access data](covidcast_api_queries.md).

## Data Sources and Signals

The API provides multiple data sources, each with several signals. Each source
represents one provider of data, such as a medical testing provider or a symptom
survey, and each signal represents one quantity computed from data provided by
that source. Our sources provide detailed data about infectious disease related topics,
including confirmed cases, symptom-related search queries, hospitalizations,
outpatient doctor's visits, and other sources. Many of these are publicly
available *only* through the main Epidata API.

Update cadence varies by source, reflecting what is most relevant for each
pathogen and context. You can use the
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

### COVIDcast Dashboard Signals

The following signals are currently displayed on [the public COVIDcast
dashboard](https://delphi.cmu.edu/covidcast/):

| Kind | Name | Source | Signal |
|---|---|---|---|
| Public Behavior | People Wearing Masks | [`fb-survey`](covidcast-signals/covid-trends-and-impact-survey.md) | `smoothed_wwearing_mask_7d` |
| Public Behavior | Vaccine Acceptance | [`fb-survey`](covidcast-signals/covid-trends-and-impact-survey.md) | `smoothed_wcovid_vaccinated_appointment_or_accept` |
| Public Behavior | COVID Symptom Searches on Google | [`google-symptoms`](covidcast-signals/google-symptoms.md) | `sum_anosmia_ageusia_smoothed_search` |
| Early Indicators | COVID-Like Symptoms | [`fb-survey`](covidcast-signals/covid-trends-and-impact-survey.md) | `smoothed_wcli` |
| Early Indicators | COVID-Like Symptoms in Community | [`fb-survey`](covidcast-signals/covid-trends-and-impact-survey.md) | `smoothed_whh_cmnty_cli` |
| Early Indicators | COVID-Related Doctor Visits | [`doctor-visits`](covidcast-signals/doctor-visits.md) | `smoothed_adj_cli` |
| Cases and Testing | COVID Cases | [`jhu-csse`](covidcast-signals/jhu-csse.md) | `confirmed_7dav_incidence_prop` |
| Late Indicators | COVID Hospital Admissions | [`hhs`](covidcast-signals/hhs.md) | `confirmed_admissions_covid_1d_prop_7dav` |
| Late Indicators | Deaths | [`jhu-csse`](covidcast-signals/jhu-csse.md) | `deaths_7dav_incidence_prop` |

### All Available Sources and Signals

Beyond the signals available on the COVIDcast dashboard, numerous other  signals are
available through our [data export tool](https://delphi.cmu.edu/covidcast/export/) or directly through the API.