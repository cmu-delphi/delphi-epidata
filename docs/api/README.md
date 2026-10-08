---
title: Other Endpoints (V3)
has_children: true
nav_order: 4
---

# Other Endpoints (V3)

> **Active endpoints are part of the legacy V3 API, which is being phased out.** See the [V4 to V5 Migration Guide](v5_migration.md) for details on the Delphi V5 transition.
{: .warning }

This is the home of [Delphi](https://delphi.cmu.edu/)'s epidemiological data
API for tracking infectious diseases such as influenza, dengue,
and norovirus. Note that additional data, including most COVID-19 signals, is
available in the [main Epidata API (formerly known as COVIDcast)](covidcast.md).

## Table of Contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Contributing

If you are interested in contributing:

- For development of the API itself, see the
  [development guide](../epidata_development.md).
- To suggest changes, additions, or other ways to improve,
  [open an issue](https://github.com/cmu-delphi/delphi-epidata/issues/new)
  describing your idea.

## Citing

We hope that this API is useful to others outside of our group, especially for
epidemiological and other scientific research. If you use this API and would
like to cite it, we would gratefully recommend the following copy:

> David C. Farrow,
> Logan C. Brooks,
> Aaron Rumack,
> Ryan J. Tibshirani,
> Roni Rosenfeld
> (2015).
> _Delphi Epidata API_.
> <https://github.com/cmu-delphi/delphi-epidata>

## Data Licensing

Several datasets surfaced through this API are carefully curated mirrors of data
acquired from various external parties. Such data is subject to its original
licensing, where applicable.

Any data which is produced novelly by Delphi and is intentionally and openly
surfaced by Delphi through this API is hereby licensed
[CC BY](https://creativecommons.org/licenses/by/4.0/) except where otherwise
noted. Endpoints, as specified by the `endpoint` parameter, which are known to
wholly or partially serve data under this license include:

- `covidcast`
- `covidcast_meta`
- `delphi`
- `dengue_nowcast`
- `dengue_sensors`
- `meta*`
- `nowcast`
- `sensors`

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

Please note that our `endpoint` parameters were previously referenced as `source` in our API. New users will now use the `endpoint` parameter when accessing our data. If you are a returning or continuous user you do not have to make any changes, as the parameter `source` still works as usual.

---

# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/>

## Specifying Epiweeks, Dates, and Lists

Formatting for epiweeks is YYYYWW and for dates is YYYYMMDD.

See [Date Formats](date_formats.html) for full details on specifying epiweeks, dates, lists, and ranges.

`list` parameters consist of a comma-separated list of individual values or, for numeric parameters, a hyphenated range of values.


## Universal Parameters

The only universally required parameter is `endpoint`, which must be one of the supported source names listed below, e.g., `fluview`.

## Source-Specific Parameters

The parameters available for each source are documented in each linked source-specific API page.

<!-- TODO: check existing descriptions -->

### COVID-19 Data

| Endpoint | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`covidcast`](covidcast.md) | COVIDCast | Delphi's COVID-19 surveillance streams. | no |
| [`covidcast_meta`](covidcast_meta.md) | COVIDCast Metadata | Metadata for Delphi's COVID-19 surveillance streams. | no |
| [`covid_hosp`](covid_hosp.md) | COVID-19 Hospitalization | COVID-19 Reported Patient Impact and Hospital Capacity. | no |

### Influenza Data

| Endpoint | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`cdc`](cdc.md) | CDC Page Hits | CDC total and by topic webpage visits. | yes |
| [`delphi`](delphi.md) | Delphi's Forecast | Delphi's ILINet outpatient doctor visits forecasts. | no |
| [`ecdc_ili`](ecdc_ili.md) | ECDC ILI | ECDC ILI data from the ECDC website. | no |
| [`flusurv`](flusurv.md) | FluSurv | FluSurv-NET data (flu hospitaliation rates) from CDC. | no |
| [`fluview`](fluview.md) | FluView | Influenza-like illness (ILI) from U.S. Outpatient Influenza-like Illness Surveillance Network (ILINet). | no |
| [`fluview_meta`](fluview_meta.md) | FluView Metadata | Summary data about [`fluview`](fluview.md). | no |
| [`fluview_clinical`](fluview_clinical.md) | FluView Clinical | Clinical flu data. | no |
| [`gft`](gft.md) | Google Flu Trends | Estimate of influenza activity based on volume of certain search queries. Google has discontinued Flu Trends, and this is now a static endpoint. | no |
| [`ght`](ght.md) | Google Health Trends | Estimate of influenza activity based on volume of certain search queries. | yes |
| [`kcdc_ili`](kcdc_ili.md) | KCDC ILI | KCDC ILI data from KCDC website. | no |
| [`meta`](meta.md) | API Metadata | Metadata for `fluview`, `twitter`, `wiki`, and `delphi`. | no |
| [`nidss_flu`](nidss_flu.md) | NIDSS Flu | Outpatient ILI from Taiwan's National Infectious Disease Statistics System (NIDSS). | no |
| [`nowcast`](nowcast.md) | ILI Nearby | A nowcast of U.S. national, regional, and state-level (weighted) percent ILI, available seven days (regionally) or five days (state-level) before the first ILINet report for the corresponding week. | no |
| [`quidel`](quidel.md) | Quidel | Data provided by Quidel Corp., which contains flu lab test results. | yes |
| [`sensors`](sensors.html) | Delphi's Digital Surveillance Sensors | Influenza and dengue digital surveillance sensors. | partially |
| [`twitter`](twitter.md) | Twitter Stream | Estimate of influenza activity based on analysis of language used in tweets from [HealthTweets](http://HealthTweets.org/). | yes |
| [`wiki`](wiki.md) | Wikipedia Access Logs | Number of page visits for selected English, Influenza-related wikipedia articles. | no |

### Dengue Data

| Endpoint | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`dengue_nowcast`](dengue_nowcast.md) | Delphi's Dengue Nowcast | Delphi's PAHO dengue nowcasts (North and South America). | no |
| [`dengue_sensors`](dengue_sensors.md) | Delphi's Dengue Digital Surveillance Sensors | PAHO dengue digital surveillance sensors (North and South America). | yes |
| [`nidss_dengue`](nidss_dengue.md) | NIDSS Dengue | NIDSS dengue cases (Taiwan). | no |
| [`paho_dengue`](paho_dengue.md) | PAHO Dengue | PAHO dengue data (North and South America). | no |

### Norovirus Data

| Endpoint | Name | Description | Restricted? |
| --- | --- | --- | --- |
| [`meta_norostat`](meta_norostat.md) | NoroSTAT Metadata | Metadata for the NoroSTAT endpoint. | yes |
| [`norostat`](norostat.md) | NoroSTAT | CDC NoroSTAT norovirus outbreaks. | yes |

### Deprecated
* `ilinet` - replaced by [`fluview`](fluview.md)
* `signals` - replaced by [`sensors`](sensors.md)
* `stateili` - replaced by [`fluview`](fluview.md)

# Data retirement

This API no longer produces or serves data with a time value after **2026-09-22**; it is being
retired in favor of cast-api / epidata-etl. See the [Delphi V5 API](v5.md) and the
[V4 to V5 Migration Guide](v5_migration.md) for where to get data past that date. Every response carries `Deprecation`, `Sunset`, and
`Link: <https://cmu-delphi.github.io/delphi-epidata/api/v5.html>; rel="successor-version"` headers,
plus an `X-Delphi-Epidata-Retirement` header explaining the change.

A request whose time values (`epiweeks`, `dates`, `time_values`, `date`, `window`, `start_day`,
`end_day`, `issues`, `publication_dates`, `collection_weeks`, `as_of`, ...) lie *entirely* after the
cutoff is rejected with HTTP `410 Gone` and a dedicated result code of `-3`, so that it is
distinguishable from an ordinary parameter error (`-1`) or a genuinely empty result set (`-2`):

```json
{
  "result": -3,
  "message": "this API no longer provides data with time values after 2026-09-22; it has been retired in favor of cast-api / epidata-etl. see https://cmu-delphi.github.io/delphi-epidata/api/v5.html",
  "epidata": []
}
```

As with other errors, requests using the `classic` or `tree` output formats receive HTTP `200` with
the same body. Requests that only *overlap* the cutoff — for example
`epiweeks=202001-202652` or `time_values=*` — are still served normally, returning whatever data
exists up to the cutoff.
An `as_of` after the cutoff is rejected on purpose, although it would select the same data as a
request without `as_of`: a request for a version after the cutoff gets the retirement message.

# Example URLs

### FluView on 2015w01 (national)
<https://api.delphi.cmu.edu/epidata/fluview/?regions=nat&epiweeks=201501>

```json
{
  "result": 1,
  "epidata": [
    {
      "release_date": "2017-10-24",
      "region": "nat",
      "issue": 201740,
      "epiweek": 201501,
      "lag": 143,
      "num_ili": 31483,
      "num_patients": 771835,
      "num_providers": 1958,
      "num_age_0": 7160,
      "num_age_1": 9589,
      "num_age_2": null,
      "num_age_3": 8072,
      "num_age_4": 3614,
      "num_age_5": 3048,
      "wili": 4.21374,
      "ili": 4.07898
    }
  ],
  "message": "success"
}
```

### Wikipedia Access article "influenza" on 2020w01
<https://api.delphi.cmu.edu/epidata/wiki/?language=en&articles=influenza&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "count": 6516,
      "total": 663604044,
      "hour": -1,
      "epiweek": 202001,
      "value": 9.81910834
    }
  ],
  "message": "success"
}
```

# Code Samples

To access our Epidata API, visit our [Epidata API Client Libraries](client_libraries.md). For anyone looking for COVIDCast data in particular, please visit our purpose-built [COVIDCast Libraries](covidcast_clients.md) instead.

# Related Work

Please visit our [related works](../related_work.md) page for more information.
