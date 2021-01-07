---
title: Twitter Stream
parent: Epidata API (Other Diseases)
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
 - Spatial Resolution: National, [HHS regions](http://www.hhs.gov/iea/regional/), and [Census divisions](http://www.census.gov/econ/census/help/geography/regions_and_divisions.html) ([1+10+9](../../labels/regions.txt)); and by state/territory ([51](../../labels/states.txt))
 - Restricted access: Delphi doesn't have permission to share this dataset

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `auth` | password | string |
| `locations` | locations | `list` of [region](../../labels/regions.txt)/[state](../../labels/states.txt) labels |
| `dates` | dates | `list` of dates |
| `epiweeks` | epiweeks | `list` of epiweeks |

Note:
- Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| ... | ... | ... | <!-- TODO -->
| `message` | `success` or error message | string |

# Example URLs

### Twitter on 2015w01 (national)
https://delphi.cmu.edu/epidata/api.php?source=twitter&auth=...&locations=nat&epiweeks=201501

```json
{
  "result":1,
  "epidata":[...],
  "message":"success"
}
```

<!-- TODO: fix -->

# Code Samples

<!-- TODO: fix -->
