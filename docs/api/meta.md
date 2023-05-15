---
title: Metadata
parent: Other Endpoints (COVID-19 and Other Diseases)
---

# API Metadata

This is the documentation of the API for accessing the API Metadata (`meta`) for `fluview`, `twitter`, `wiki`,
and `delphi` endpoints of the [Delphi](https://delphi.cmu.edu/)'s epidemiological data.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## API Metadata

... <!-- TODO -->

# The API

The base URL is: https://api.covidcast.cmu.edu/epidata/meta/

See [this documentation](README.md) for details on specifying epiweeks, dates, and lists.

## Parameters

None.

## Response

| Field     | Description                                                     | Type             |
|-----------|-----------------------------------------------------------------|------------------|
| `result`  | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata` | list of results                                                 | array of objects |
| ...       | ...                                                             | ...              | <!-- TODO -->
| `message` | `success` or error message                                      | string           |

# Example URLs

https://api.covidcast.cmu.edu/epidata/meta/

```json
{
  "result": 1,
  "epidata": [
    {
      "fluview": [
        {
          "latest_update": "2020-04-10",
          "latest_issue": 202014,
          "table_rows": 945920
        }
      ],
      "twitter": [
        {
          "latest_update": "2020-04-11",
          "num_states": 41,
          "table_rows": 132712
        }
      ],
      "wiki": [
        {
          "latest_update": "2020-04-12 07:00:00",
          "table_rows": 131585
        }
      ],
      "delphi": [
        {
          "system": "af",
          "first_week": 201541,
          "last_week": 201619,
          "num_weeks": 31
        },
        {
          "system": "eb",
          "first_week": 201441,
          "last_week": 201519,
          "num_weeks": 32
        },
        {
          "system": "ec",
          "first_week": 201441,
          "last_week": 202013,
          "num_weeks": 171
        },
        {
          "system": "sp",
          "first_week": 201441,
          "last_week": 201519,
          "num_weeks": 32
        },
        {
          "system": "st",
          "first_week": 201542,
          "last_week": 201949,
          "num_weeks": 123
        }
      ]
    }
  ],
  "message": "success"
}
```

# Code Samples

<!-- TODO: fix -->
