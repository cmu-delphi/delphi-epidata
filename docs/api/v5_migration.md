---
title: V3/V4 to V5 Migration Guide
parent: Delphi V5 API
nav_order: 4
---

# V3/V4 to V5 Migration Guide

The legacy Epidata APIs, including the [V4 main endpoint (COVIDcast)](covidcast.md) and [V3 other endpoints](README.md), are transitioning to the [V5 API](v5.md). This transition is occurring source by source. All V3 and V4 sources will continue to operate until the migration is complete (tentatively scheduled for October 2026), and endpoints that are no longer updated will remain accessible on V3/V4. For new integrations, start directly on V5 and fall back to legacy endpoints only for sources that are not yet supported.

## Endpoint mapping

The single `covidcast` endpoint splits into several purpose-built V5 routes determined by query type. The "other endpoints" column highlights examples (`fluview`, `flusurv`, `wiki`) to illustrate differences across endpoints. Refer to each endpoint's documentation for specific behavior:

| Task | V4 (`covidcast`) | V3 (Other Endpoints) | V5 Equivalent |
| :--- | :--- | :--- | :--- |
| Fetch latest data or snapshot as of a past date | `covidcast` (default query or with `as_of`) | Endpoint-specific (`fluview` has no `as_of`) | [`/epidata/v5/snapshot/`](v5_api_queries.md#snapshot-parameters) |
| Fetch full revision history for a signal | `covidcast` with `issues` | Supported by some (`fluview`, `flusurv` with `issues`) | [`/epidata/v5/archive/`](v5_api_queries.md#archive-parameters) |
| Discover sources, signals, geo types, and date ranges | [`covidcast_meta`](covidcast_meta.md) | Shared [`meta`](01meta.md) for some `fluview` | [`/epidata/v5/metadata/`](v5_api_queries.md#metadata) |
| Access source-specific auxiliary tables | None | None | [`/epidata/v5/aux_data/`](v5_api_queries.md#auxiliary-data-parameters) |
| Filter by publication lag | `covidcast` with `lag` | Supported by some (`fluview`, `flusurv`) | None (compute `report_time - reference_time`) |

## Parameter changes

Most `covidcast` query parameters carry over to V5 with the same name, but some have been renamed, dropped, or added. Historical endpoints do not share parameter names with `covidcast`. Parameters for `fluview` are shown below as an example, but consult each endpoint's documentation for details:

| V4 Parameter (`covidcast`) | V3 (Other Endpoints, e.g. `fluview`) | V5 Equivalent | Notes |
| :--- | :--- | :--- | :--- |
| `data_source` | not exposed (identified by the endpoint URL, e.g. `/fluview/`) | `source` | Identifies the source dataset in V5 (replaces V4 `data_source` and endpoint names). |
| `signal` | none | `signal` | Identifies the specific signal name within the source. |
| `geo_type` | not exposed (`fluview` supports only `regions`) | `geo_type` | Specifies geographic resolution (e.g., `state`, `county`). |
| `geo_value` | `regions` for `fluview` | none | Removed in V5. Both `/snapshot/` and `/archive/` return all locations for the requested `geo_type`. Filter locations client-side. |
| `time_type` | not exposed (`fluview` is always `epiweeks`) | none | Removed in V5. All V5 endpoints use standard calendar dates (`reference_time`). |
| `time_values` | `epiweeks` for `fluview` | none | Removed in V5 queries. Fetch the full signal and filter by `reference_time` client-side. |
| `as_of` | none (`fluview` has no `as_of`) | `snapshot_date` | In V5, used only in `/snapshot/` to fetch data known as of a past date. Omit to return the latest data. |
| `issues` | `issues` (where supported) | `report_time_query` | In V5, used only in `/archive/`. Accepts a single date or comparison filter (e.g. `<2025-10-16>`). |
| `lag` | `lag` (where supported) | none | Removed in V5. Compute client-side as `report_time - reference_time`. |
| none | none | `fill_method` | New in V5. Selects the imputation method when aggregating sub-geographies (`source`, `fill_ave`, or `fill_zero`). See [Imputation](v5_api_queries.md#imputation-fill-methods). |
| none | none | `extra_keys` | New in V5. Filters on source-specific dimensions (such as `age_group:18-49`). |

## Response field changes

Response fields follow a similar pattern. In the table below, `fluview` serves as an example of an endpoint with custom fields. Field names vary by legacy endpoint (for example, `wiki` returns `article`, `count`, and `hour`):

| V4 Field (`covidcast`) | V3 (Other Endpoints, e.g. `fluview`) | V5 Field | Notes |
| :--- | :--- | :--- | :--- |
| `source` | not returned (identified by endpoint name) | dropped | Omitted in V5 responses because the source is already specified in the request. |
| `signal` | none (implicit from endpoint) | `signal` | Identifies the signal name in V5. |
| `value` | Endpoint-specific columns (e.g. `num_ili`, `wili`, `ili`) | `value` | Standardized metric value column across all V5 sources. |
| not returned (implicit from query) | not returned (implicit from endpoint) | `geo_type` | Explicitly included in V5 responses to identify geographic resolution. |
| `geo_value` | `region` for `fluview` | `geo_value` | Standardized location identifier across all V5 responses. |
| `time_value` | `epiweek` for `fluview` | `reference_time` | Standardized date in `YYYY-MM-DD` format representing the observation period. |
| `issue` | `issue` (where returned) | `report_time` | Standardized date in `YYYY-MM-DD` format representing when the data point was published (returned in `/archive/`). |
| `lag` | `lag` (where returned) | dropped | Omitted in V5 responses. Calculate client-side as `report_time - reference_time`. |
| `direction` | none | dropped | Deprecated in V4 and removed in V5. |
| `stderr`, `sample_size` | none | `ci_lower`, `ci_upper` | Expresses uncertainty as explicit confidence interval bounds on `value` when provided by the data source. |
| `missing_value`, `missing_stderr`, `missing_sample_size` | none | dropped | Replaced in V5 by `fill_method` variants and standard null values in `value`. |
| none | none | `fill_method` | Indicates which null-handling imputation method was applied (`source`, `fill_ave`, or `fill_zero`). |

Some sources also include extra columns, such as `age_group` for pophive and `nwss_source`, `sample_index`, and `pcr_target` for nwss.

## A query, before and after

Here is the same request fetching NHSN COVID admissions as known on 2024-12-07 for every state in both APIs:

V4:

```url
https://api.delphi.cmu.edu/epidata/covidcast/?data_source=nhsn&signal=confirmed_admissions_covid_ew&time_type=week&geo_type=state&geo_value=*&as_of=20241207
```

V5:

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=nhsn&signal=confirmed_admissions_covid_ew&geo_type=state&snapshot_date=2024-12-07
```

The V5 query omits `geo_value=*` because it always returns all locations for the requested `geo_type`. You can filter down to specific locations client-side after downloading.

## Revision history queries

Where you previously passed `issues` to `covidcast`, use [`/epidata/v5/archive/`](v5_api_queries.md#archive-parameters) with `report_time_query` instead:

```url
https://delphi.cmu.edu/epidata/v5/archive/?source=nssp&signal=pct_ed_visits_influenza&geo_type=state&report_time_query=<2025-10-16
```

## Updating your client

Both [`epidatr`](https://cmu-delphi.github.io/epidatr/) (R) and [`epidatpy`](https://cmu-delphi.github.io/epidatpy/) (Python) natively support V5 queries.

- **R users**. Update to the latest `epidatr` release and consult the [`epidatr` migration guide](https://cmu-delphi.github.io/epidatr/articles/migration-guide.html) for function mappings.
- **Python users**. Migrate to `epidatpy` using the [`epidatpy` migration guide](https://cmu-delphi.github.io/epidatpy/migration-guide.html). The legacy Python client (see [Client Libraries](client_libraries.md)) only supports V4 and will not receive V5 updates.

## Checking whether a source has moved

Query [`/epidata/v5/metadata/?source=<name>`](v5_meta.md) to check whether a source is available in V5. It returns available signals, geo types, and date ranges for `reference_time` and `report_time`. The `report_times` and `reference_times` sub-endpoints list full date histories when needed. New sources are announced on the [Delphi mailing list](https://lists.andrew.cmu.edu/mailman/listinfo/delphi-covidcast-api) as they are migrated.

