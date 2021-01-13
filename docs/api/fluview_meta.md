---
title: FluView metadata
parent: Epidata API (Other Diseases)
---

# FluView metadata

This is the API documentation for accessing the FluView metadata
(`fluview_meta`) endpoint of [Delphi](https://delphi.cmu.edu/)'s epidemiological
data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## FluView Metadata

Returns information about the [`fluview` endpoint](fluview.md).

# The API

The base URL is: https://delphi.cmu.edu/epidata/api.php

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

There are no parameters for this endpoint.

## Response

| Field | Description | Type |
| --- | --- | --- |
| `result` | result code: 1 = success, 2 = too many results, -2 = no results | integer |
| `epidata` | list of results | array of objects |
| `epidata[].latest_update` | date when data was last updated | string |
| `epidata[].latest_issue` | most recent "issue" (epiweek) in the data | integer |
| `epidata[].table_rows` | total number of rows in the table | integer |
| `message` | `success` or error message | string |

# Example URLs

### FluView Metadata
https://delphi.cmu.edu/epidata/api.php?endpoint=fluview_meta

```json
{
  "result": 1,
  "epidata": [
    {
      "latest_update": "2020-04-24",
      "latest_issue": 202016,
      "table_rows": 957673
    }
  ],
  "message": "success"
}
```
