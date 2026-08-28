---
title: V5 Metadata Discovery Endpoints
parent: Delphi V5 API
nav_order: 2
---

# V5 Metadata Discovery Endpoints

The V5 API provides metadata endpoints under `https://delphi.cmu.edu/epidata/v5/metadata/` to explore available sources, signals, geographies, schemas, and date ranges.

| Endpoint | Description | Parameters | Example Query |
| :--- | :--- | :--- | :--- |
| [`/epidata/v5/metadata/`](https://delphi.cmu.edu/epidata/v5/metadata/) | Overview of active sources, signals, geographic levels, and date ranges. | `source` (optional) | [`?source=nssp`](https://delphi.cmu.edu/epidata/v5/metadata/?source=nssp) |
| [`geo_signals/`](https://delphi.cmu.edu/epidata/v5/metadata/geo_signals/) | Active sources and signals available for a given location. | `geo_type` (required)<br>`geo_value` (required) | [`?geo_type=state&geo_value=pa`](https://delphi.cmu.edu/epidata/v5/metadata/geo_signals/?geo_type=state&geo_value=pa) |
| [`report_times/`](https://delphi.cmu.edu/epidata/v5/metadata/report_times/) | Sorted list of publication dates (`report_time`). | `source` (required)<br>`signal` (optional) | [`?source=nssp`](https://delphi.cmu.edu/epidata/v5/metadata/report_times/?source=nssp) |
| [`reference_times/`](https://delphi.cmu.edu/epidata/v5/metadata/reference_times/) | Sorted list of observation dates (`reference_time`). | `source` (required)<br>`signal` (optional) | [`?source=nssp`](https://delphi.cmu.edu/epidata/v5/metadata/reference_times/?source=nssp) |
| [`extra_key_values/`](https://delphi.cmu.edu/epidata/v5/metadata/extra_key_values/) | Distinct values for source-specific extra dimension columns. | `source` (required)<br>`signal` (optional) | [`?source=nwss`](https://delphi.cmu.edu/epidata/v5/metadata/extra_key_values/?source=nwss) |
| [`aux_schema/`](https://delphi.cmu.edu/epidata/v5/metadata/aux_schema/) | Column names and SQL data types for auxiliary tables. | `source` (optional) | [`?source=nwss`](https://delphi.cmu.edu/epidata/v5/metadata/aux_schema/?source=nwss) |
| [`api_version_hash/`](https://delphi.cmu.edu/epidata/v5/metadata/api_version_hash/) | Current Git commit hash of the running API server. | None | [`api_version_hash/`](https://delphi.cmu.edu/epidata/v5/metadata/api_version_hash/) |

