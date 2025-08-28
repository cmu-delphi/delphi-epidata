---
title: <i>inactive</i> Twitter Stream
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 2
---

# Twitter Stream

This is the API documentation for accessing the Twitter Stream (`twitter`)
endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Twitter Stream Data

Estimate of influenza activity based on analysis of language used in tweets.
 - Source: [HealthTweets](http://www.healthtweets.org/)
 - Temporal Resolution: Daily and weekly from 2011-12-01 (2011w48)
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), and [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt)); and by state/territory ([51](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt))
 - Restricted access: Delphi doesn't have permission to share this dataset

# The API

The base URL is: https://api.delphi.cmu.edu/epidata/twitter/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `locations` | locations | `list` of [region](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/regions.txt)/[state](https://github.com/cmu-delphi/delphi-epidata/blob/main/labels/states.txt) labels |
| `dates` | dates | `list` of dates |
| `epiweeks` | epiweeks | `list` of epiweeks |

Note:
- Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.

## Response

| Field     | Description                                                     | Type             |
|-----------|-----------------------------------------------------------------|------------------|
| `result`  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata` | list of results                                                 | array of objects |
| ...       | ...                                                             | ...              | <!-- TODO -->
| `message` | `success` or error message                                      | string           |

# Example URLs

### Twitter on 2015w01 (national)
https://api.delphi.cmu.edu/epidata/twitter/?auth=...&locations=nat&epiweeks=201501

```json
{
  "result":1,
  "epidata":[...],
  "message":"success"
}
```
# Citing the Survey
Researchers who use the Twitter Stream data for research are asked to credit and cite the survey in publications based on the data. Specifically, we ask that you cite our paper describing the survey:

  > Mark Dredze, Renyuan Cheng, Michael J Paul, David A Broniatowski. HealthTweets.org: A Platform for Public Health Surveillance using Twitter. AAAI Workshop on the World Wide Web and Public Health 
  > Intelligence, 2014.

<!-- TODO: fix -->

# Code Samples

<!-- TODO: fix -->
