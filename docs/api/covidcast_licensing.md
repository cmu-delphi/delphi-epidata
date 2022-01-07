---
title: COVIDcast Data Licensing
parent: COVIDcast Epidata API
nav_order: 2
---

# Licensing for Delphi's COVID-19 Data Streams

When you use data from Delphi's COVIDcast Epidata API, we ask that you attribute
the source and follow the terms of the data's licensing agreement. The API
contains some data streams produced internally by Delphi, which should be
attributed to Delphi, and some republished from other sources, which should be
credited. See below for details.

## Novel Data

These data streams include data produced novelly by Delphi and intentionally and
openly surfaced by Delphi through this API.

We request you attribute our data as follows:

> Data from Delphi COVIDcast. Obtained via the Delphi Epidata API.
> <https://cmu-delphi.github.io/delphi-epidata/api/covidcast.html>

Academic publications may cite our paper:

> Alex Reinhart, Logan Brooks, Maria Jahja, Aaron Rumack, Jingjing Tang, et al.
> (2021). "An open repository of real-time COVID-19 indicators". *Proceedings of
> the National Academy of Sciences* 118 (51) e2111452118.
> <https://doi.org/10.1073/pnas.2111452118>

### Creative Commons: Attribution

These data sources are provided under the terms of the [Creative Commons
Attribution license](https://creativecommons.org/licenses/by/4.0/):

* [Doctor Visits](covidcast-signals/doctor-visits.md)
* [Hospital Admissions](covidcast-signals/hospital-admissions.md)
* [Indicator Combination](covidcast-signals/indicator-combination-inactive.md): signals
  with names beginning `nmf_*`
* [Quidel](covidcast-signals/quidel.md)
* [COVID-19 Trends and Impact Survey](covidcast-signals/fb-survey.md)

You may use this data for any purpose, provided you attribute us as the original
source, as shown above.

### Creative Commons: Attribution-NonCommercial

These data sources are provided under the terms of the [Creative Commons
Attribution-NonCommercial
license](https://creativecommons.org/licenses/by-nc/4.0/):

* [Change Healthcare](covidcast-signals/chng.md)

You may not use this data for commercial purposes, but all other uses are
permitted, provided you attribute us as the original source.

## Republished Data

These data streams are essentially mirrors of their respective sources, and are
published here subject to the original license provided by the source:

* [Google Health Trends](covidcast-signals/ght.md)
* [Indicator Combination](covidcast-signals/indicator-combination-inactive.md): cases and
  deaths signals
* [JHU Cases and Deaths](covidcast-signals/jhu-csse.md)
* [SafeGraph Mobility](covidcast-signals/safegraph.md)
* [USAFacts Cases and Deaths](covidcast-signals/usafacts.md)
* [Department of Health & Human Services](covidcast-signals/hhs.md)

More information on the license for each source is available on their respective
documentation pages.

If you use the Delphi's COVIDcast Epidata API to access this data, we
additionally request you [acknowledge us](README.md#citing) in your product or
publication.
