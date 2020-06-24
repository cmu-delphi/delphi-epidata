---
title: JHU Cases and Deaths
parent: Data Sources and Signals
grand_parent: COVIDcast API
---

# JHU Cases and Deaths

* **Source name:** `jhu-csse`
* **Number of data revisions since 19 May 2020:** 1
* **Date of last change:** [3 June 2020](../covidcast_changelog.md#jhu-csse)
* **Available for:** county, hrr, msa, state (see [geography coding docs](../covidcast_geography.md))

This data source of confirmed COVID-19 cases and deaths is based on reports made
available by the Center for Systems Science and Engineering at Johns Hopkins
University.

| Signal | 7-day average signal | Description |
| --- | --- | --- |
| `confirmed_cumulative_num` | `confirmed_7dav_cumul_num` | Cumulative number of confirmed COVID-19 cases |
| `confirmed_cumulative_prop` | `confirmed_7dav_cumul_prop` | Cumulative number of confirmed COVID-19 cases per 100,000 population |
| `confirmed_incidence_num` | `confirmed_7dav_incid_num` | Number of new confirmed COVID-19 cases, daily |
| `confirmed_incidence_prop` | `confirmed_7dav_incid_prop` | Number of new confirmed COVID-19 cases per 100,000 population, daily |
| `deaths_cumulative_num` | `deaths_7dav_cumul_num` | Cumulative number of confirmed deaths due to COVID-19 |
| `deaths_cumulative_prop` | `deaths_7dav_cumul_prop` | Cumulative number of confirmed due to COVID-19, per 100,000 population |
| `deaths_incidence_num` | `deaths_7dav_incid_num` | Number of new confirmed deaths due to COVID-19, daily |
| `deaths_incidence_prop` | `deaths_7dav_incid_prop` | Number of new confirmed deaths due to COVID-19 per 100,000 population, daily |

These signals are taken directly from the JHU CSSE [COVID-19 GitHub
repository](https://github.com/CSSEGISandData/COVID-19) without filtering,
smoothing, or changes. **Note:** JHU's data reports cumulative cases and deaths,
so our incidence signals are calculated by subtracting each day's cumulative
count from the previous day. Since cumulative figures are sometimes corrected or
amended by health authorities, this can sometimes result in negative incidence.
This should be interpreted purely as an artifact of data reporting and
correction.

Smoothed versions of all the signals above are available. These signals report
moving averages of the preceding 7 days, so e.g. the signal for June 7 is the
average of the underlying data for June 1 through 7, inclusive.
