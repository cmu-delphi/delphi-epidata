---
title: NaN Missing Codes
parent: COVIDcast Epidata API
nav_order: 5
---

# Missing Value Coding

Occasionally, data will be missing from our database and will be explicitly coded as NaN.
In these cases, we strive to supply our best-known reason for the value to be missing by
providing an integer code in the corresponding `missing_` column (i.e. `missing_value`
corresponds to the `value` column). The integer codes are as follows

| Code | Name | Description |
| --- | --- | --- |
| 0 | DEFAULT | This is the default value for when the entry is not missing. |
| 1 | NOT APPLICABLE | This value is used when the field is not expected to have a value (e.g. stderr for a signal that is not estimated from a sample). |
| 2 | REGION EXCEPTION | This value is used when the field is not reported because the particular indicator does not serve the geographical region requested. |
| 3 | PRIVACY | This value is used when the field has been censored for data privacy reasons. This could be due to reasons such as low sample sizes or simply a requirement from our data partners. |
| 4 | DELETED | This value is used when the field was present in previous issues, but is no longer reported. Deletions can arise due to reasons such as bug fixes or changing censorship requirements. |
| 5 | UNKNOWN | This value is used when the field is missing, but does not fall into any of the categories above. |

These codes are supplied as part of the `delphi_utils` Python library (see [here](https://pypi.org/project/delphi-utils/)).
