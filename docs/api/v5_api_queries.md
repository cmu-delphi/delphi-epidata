---
title: Manually Constructing V5 Queries
parent: Delphi V5 API
nav_order: 1
---

# Manually Constructing V5 Queries

The Delphi V5 API is hosted at `https://delphi.cmu.edu`. All endpoints are prefixed with `/epidata/v5/`. Interactive, endpoint-level documentation is available on the [Delphi V5 API Landing Page](https://delphi.cmu.edu/epidata/v5/docs).

By default, queries return a streaming CSV response. However, you can configure the output format to plain text. The API is designed to encourage users to download complete slices or snapshots and filter them client-side rather than executing complex filters inside the database.

---

## Main Endpoints

The V5 API exposes four primary categories of endpoints. Each category serves a distinct purpose for querying epidemiological data and discovering metadata.

* [Snapshot](#snapshot-parameters) (`/epidata/v5/snapshot/`) time travels to how a dataset looked at a specific point in time. It retrieves the state of the data as of a given release version.
* [Archive](#archive-parameters) (`/epidata/v5/archive/`) fetches all snapshots of a dataset prior to a point in time.
* [Auxiliary Data](#auxiliary-data-parameters) (`/epidata/v5/aux_data/`) accesses source-specific auxiliary tables containing metadata, laboratory protocols, or additional static keys (sewershed and facility details).
* [Metadata](#metadata-parameters) (prefixed with `/epidata/v5/metadata/`) provides endpoints for discovering available sources, signals, geographic types, valid ranges, and query statistics.

---

## Endpoint-Specific Parameters

Below are the detailed parameters, rules, and example queries for each endpoint.

### Snapshot Parameters

The `/epidata/v5/snapshot/` endpoint requires specific geographic boundaries to return data.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `source` | Required | The ID of the data source (e.g., `nssp`, `nhsn`, `nwss`). |
| `signal` | Required | The signal name. |
| `geo_type` | Required | The geographic resolution level (e.g., `state`, `county`). |
| `snapshot_date` | Optional | The release date (`YYYY-MM-DD`) of the snapshot. If omitted, the latest available release is returned. |
| `fill_method` | Optional | The imputation method (`source`, `fill_ave`, or `fill_zero`). Defaults to `source`. |
| `extra_keys` | Optional | Column filters for sources with extra dimensions (e.g., `age_group:18-49`). |
| `limit` | Optional | Maximum number of rows to return. Defaults to no limit. Pass `-1` to disable the limit (return all matching rows). |
| `columns` | Optional | A comma-separated list of columns to retrieve. See [Column Selection](#column-selection) for details. |
| `format` | Optional | The output format (`csv` or `text`). |
| `header` | Optional | Set to `false` to omit column headers from CSV output. |

#### Example Query
To fetch the state of the NHSN COVID admissions dataset as it was known on 2024-12-07:
```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=nhsn&signal=confirmed_admissions_covid_ew&geo_type=state&snapshot_date=2024-12-07
```

---

### Archive Parameters

The `/epidata/v5/archive/` endpoint streams version history. Unlike the snapshot endpoint, `geo_type` is optional.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `source` | Required | The ID of the data source. |
| `signal` | Required | The signal name. |
| `geo_type` | Optional | The geographic resolution level. |
| `fill_method` | Optional | The imputation method (`source`, `fill_ave`, or `fill_zero`). Defaults to `source`. |
| `extra_keys` | Optional | Column filters for sources with extra dimensions (e.g., `age_group:18-49`). |
| `report_time_query` | Optional | A release date filter using comparison operators, such as `=2024-12-07` (exact date), `<2025-10-16` (before date), or `>2025-10-16` (after date). Omitting this parameter scans the entire history. |
| `limit` | Optional | Maximum number of rows to return. Defaults to no limit. Pass `-1` to disable the limit (return all matching rows). |
| `use_pagination` | Optional | Set to `true` to enable sequential pagination. |
| `columns` | Optional | A comma-separated list of columns to retrieve. See [Column Selection](#column-selection) for details. |
| `format` | Optional | The output format. See [Format Options](#format-options) for choices. |
| `header` | Optional | Set to `false` to omit column headers from CSV output. |

#### Example Query
To stream the archive of weekly NSSP flu visits for Pennsylvania, selecting only the reference date, value, and location columns:
```url
https://delphi.cmu.edu/epidata/v5/archive/?source=nssp&signal=pct_ed_visits_influenza&geo_type=state&columns=reference_time,value,geo_value
```

---

### Auxiliary Data Parameters

The `/epidata/v5/aux_data/` endpoint allows retrieving static or metadata records tied to a source.

> **Note:** Auxiliary data is currently only available for the `nwss` data source.
{: .note}

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `source` | Required | The ID of the data source (e.g., `nwss`). |
| `filtered_keys` | Optional | Filters for key columns, formatted as comma-separated `column:value` pairs (e.g., `pcr_target:sars-cov-2`). |
| `report_time_query` | Optional | A release date filter using comparison operators (e.g., `<2025-10-16`). |
| `limit` | Optional | Maximum number of rows to return. Defaults to no limit. Pass `-1` to disable the limit (return all matching rows). |
| `use_pagination` | Optional | Set to `true` to enable pagination. |
| `columns` | Optional | A comma-separated list of columns to retrieve. See [Column Selection](#column-selection). |
| `format` | Optional | The output format (`csv` or `text`). |
| `header` | Optional | Set to `false` to omit column headers from CSV output. |

#### Example Query
To fetch the auxiliary facility metadata for the wastewater source:
```url
https://delphi.cmu.edu/epidata/v5/aux_data/?source=nwss
```

---

### Metadata

The metadata endpoints help you discover the available sources, signals, valid geographic ranges, and distinct values.

#### `/epidata/v5/metadata/`
Retrieves an aggregated summary of active sources.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `source` | Optional | Filter metadata to a specific source (e.g., `source=nssp`). |

#### `/epidata/v5/metadata/counts/`
Retrieves the total number of observations matching the query parameters.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `source` | Required | The ID of the data source. |
| `signal` | Required | The signal name. |
| `geo_type` | Optional | Geographic resolution level. |
| `fill_method` | Optional | Imputation method (`source`, `fill_ave`, or `fill_zero`). Defaults to `source`. |
| `extra_keys` | Optional | Column filters for extra dimensions (e.g., `age_group:18-49`). |
| `report_time_query` | Optional | A release date filter using operators (e.g., `=2024-12-07`). |

#### Other Sub-endpoints

| Endpoint | Required Parameters | Optional Parameters | Description |
| :--- | :--- | :--- | :--- |
| `/epidata/v5/metadata/geo_signals/` | `geo_type`, `geo_value` | None | Lists active signals for a location. |
| `/epidata/v5/metadata/report_times/` | `source` | None | Lists all publication/update dates. |
| `/epidata/v5/metadata/reference_times/` | `source` | None | Lists all valid event dates. |
| `/epidata/v5/metadata/extra_key_values/` | `source` | None | Lists valid values for extra dimensions. |
| `/epidata/v5/metadata/aux_schema/` | None | `source` | Retrieves database schema for auxiliary tables. |
| `/epidata/v5/metadata/api_version_hash/` | None | None | Returns the Git commit hash of the API server. |

<!-- TODO: document detailed request and response payloads for metadata endpoints -->
<!-- For detailed request and response payloads, see the [V5 Metadata Discovery Endpoints](v5_meta.md) documentation. -->

---

## Shared Query Features

These features and parameters apply uniformly across data and auxiliary endpoints.

### API Key & Authentication

Anyone may access public data anonymously. To authenticate and remove rate limits, you can pass your API key using one of the following methods.

| Method | Key Location & Format | Example |
| :--- | :--- | :--- |
| Query parameter | Pass `token` in the URL query string. | `curl "https://delphi.cmu.edu/epidata/v5/snapshot/?source=nhsn&signal=confirmed_admissions_covid_ew&geo_type=state&token=your_api_key"` |
| HTTP Header | Pass the key in a request header named `token`. | `curl -H "token: your_api_key" "https://delphi.cmu.edu/epidata/v5/snapshot/?source=nhsn&signal=confirmed_admissions_covid_ew&geo_type=state"` |

<!-- TODO: Pagination 
### Pagination & Link Headers

When querying `/epidata/v5/archive/` or `/epidata/v5/aux_data/` with pagination enabled (`use_pagination=true`), the server paginates the response to prevent memory issues. 
...
-->

### Column Selection

To reduce bandwidth, you can retrieve a subset of columns using the `columns` parameter with a comma-separated list of column names (e.g., `columns=reference_time,value`).

The standard columns returned by the API for `/archive/` and `/snapshot/` endpoints are:

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `signal` | string | The name of the requested signal. |
| `report_time` | date | The release or issue date when this data point was published (`YYYY-MM-DD`). |
| `geo_type` | string | Geographic level (e.g., `county`, `state`). |
| `geo_value` | string | Unique code for the location (e.g., FIPS, state abbreviation). |
| `fill_method` | string | Imputation method used to handle missing data (e.g., `source`, `fill_ave`, `fill_zero`). |
| `reference_time` | date | Reference date when the event occurred (`YYYY-MM-DD` or `YYYY-Www`). |
| `value` | float | The statistical estimate value. |
| *Source Extras* | variable | Any source-specific extra columns (e.g., `age_group` or `nwss_source`). |

### Imputation (Fill Methods)

When requesting data aggregated to higher geographic levels (e.g., aggregating county-level data to state or national levels), the pipeline must handle missing data in the sub-geographies. The `fill_method` parameter specifies how these missing values are handled:

| Fill Method | Description |
| :--- | :--- |
| `source` (Default) | No imputation is performed. The data is returned as reported directly by the source. |
| `fill_zero` | Missing sub-geographic values are treated as zero during geographic aggregation. |
| `fill_ave` | Missing sub-geographic values are filled with the population-weighted average of non-missing sibling geographies before aggregating. |

> **Note:** The availability and behavior of these fill methods may vary depending on the data source and specific indicators. Refer to the documentation for the specific data source.
{: .note}
