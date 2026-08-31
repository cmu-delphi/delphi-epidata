---
title: V5 Signal Documentation Standard
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_exclude: true
---

# V5 Signal Documentation Standard
{: .no_toc}

This guide outlines the structure, section titles, and writing guidelines for Delphi V5 data source documentation in `docs/api/v5-signals/<source>.md`.

---

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Standard Section Hierarchy

Every V5 data source page follows a consistent hierarchy to keep pages predictable and easy to navigate:

```
1. Jekyll Frontmatter (title, parent, grand_parent, nav_order)
2. Title and Summary Table
3. Table of Contents ({:toc})
4. Overview
5. Signals
6. Estimation
   ├── Geographic Aggregation (Optional)
   ├── Temporal Handling (Optional)
   ├── Normalization (Optional)
   ├── Smoothing (Optional)
   └── Uncertainty (Optional)
7. Schema
   ├── Columns (Optional)
   ├── Extra Keys (Required if extra_keys exist)
   ├── Auxiliary Tables (Required if aux_data exists)
   └── Example Query (Recommended)
8. Missingness & Privacy
9. Limitations
10. Lag & Backfill
11. Source & Licensing
12. Changelog (<details>)
```

---

## Section Guidelines

### 1. Frontmatter and Summary Table

Each document begins with Jekyll frontmatter followed by the dataset title and a summary table of core attributes.

```yaml
---
title: Short Name (e.g., PopHive Claims, VA Respiratory)
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: <integer>
---
```

Below the top-level heading, include a table summarizing key attributes:

| Attribute | Description |
| :--- | :--- |
| `Source Name` | Exact API source identifier (e.g., `pophive`, `va_respiratory`). |
| `Data Source` | Link to the upstream data provider or public portal. |
| `Geographic Levels` | Supported `geo_type` values (e.g., `nation`, `state`, `hhs`, `county`). |
| `Temporal Granularity` | Reporting frequency (e.g., daily or weekly, noting the week-ending day). |
| `Reporting Cadence` | How often Delphi updates the feed (e.g., daily, weekly on Fridays, or irregular). |
| `Temporal Scope Start` | Earliest available observation date in `YYYY-MM-DD` format. |
| `Date of Last Revision` | How revisions are handled (e.g., static snapshot or a 14-day rolling window). |
| `Extra Key Columns` | Any extra primary key columns (e.g., `age_group`, `fill_method`), or `None`. |
| `License` | Dataset license and link (e.g., Public Domain, CC BY 4.0). |

---

### 2. Overview

Provide a short summary in one or two paragraphs describing what the source measures, the reporting agency or partner, and the primary public health context.

---

### 3. Signals

Present all available signals in a markdown table. For sources covering a single domain, list the signal name, pathogen or condition, metric type (count, rate, or percentage), and a clear description. When a source provides distinct metric groups (such as case counts versus vaccination metrics), organize them under subheadings like `### Case Signals` or `### Vaccination Signals`. For sources built from combinatoric naming schemes (such as wastewater), separate the table into prefixes and suffixes and describe the combination rules.

---

### 4. Estimation

Describe the epidemiological and statistical methods used to produce each indicator from raw data.

Use dedicated subheadings when applicable:
- `### Geographic Aggregation` for crosswalking between geographic levels, facility catchment disaggregation, and population weighting.
- `### Temporal Handling` for reference date conventions and observation window definitions.
- `### Normalization` to specify the baseline population source used when converting raw counts into rates per 100,000.
- `### Smoothing` to explain rolling windows (such as a 7-day trailing average) and any adjustments made for reporting anomalies.
- `### Uncertainty` to document standard errors or confidence intervals. When providing mathematical formulas, use KaTeX notation with double dollar signs (`$$`) separated by blank lines.

---

### 5. Schema

Document the table schema and query structure so users understand how to fetch data from the endpoint.

Include:
- `### Columns` to list each column in the table, its role (such as primary key, extra key, or value column), and its description.
- `### Extra Keys` when the source uses additional dimensions like `age_group` or `fill_method`. Provide a table of valid values, explain how missing selections behave, and show sample query parameters.
- `### Auxiliary Tables` if the indicator serves companion metadata through the `/epidata/v5/aux_data/` endpoint.
- `### Example Query` with a clear, realistic request URL or code example.

---

### 6. Missingness & Privacy

Explain the conditions under which data points may be suppressed, missing, or imputed. Detail any small-cell suppression thresholds (such as masking counts below 10 for patient privacy), clarify whether suppressed records appear as `null` or are excluded, and describe how upward geographic aggregations handle missing subunits.

---

### 7. Limitations

Describe known caveats, potential biases, and interpretation limits. This includes coverage gaps, EHR platform market share representation, differences between clinical diagnosis dates and encounter dates, and demographic differences in the underlying patient population.

---

### 8. Lag & Backfill

Explain the operational timeline of the dataset. Note the typical lag between an event and its initial publication, and explain whether past records receive retroactive updates over time or remain static after publication.

---

### 9. Source & Licensing

Credit the upstream data owners, provide links to source documentation or terms of use, and specify the suggested citation format for downstream publications.

---

### 10. Changelog

Record significant updates, methodology changes, and initial release dates. Place this section at the bottom of the page within a collapsible `<details>` element to keep the main reference concise.

```markdown
## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **YYYY-MM-DD**. Description of update.

</details>
```

---

## Markdown Template

Below is a template you can copy and adapt when adding documentation for new V5 indicators:

````markdown
---
title: SOURCE TITLE
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 10
---

# DATASET NAME (V5)
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| Source Name | `source_id` |
| Data Source | [Data Provider Name](https://example.com) |
| Geographic Levels | `nation`, `state`, `hhs`, `county` |
| Temporal Granularity | Weekly (Epiweeks; Saturdays) / Daily |
| Reporting Cadence | Weekly / Daily |
| Temporal Scope Start | YYYY-MM-DD |
| Date of Last Revision | Never (see [Changelog](#changelog)) / Lookback window |
| Extra Key Columns | `extra_col_1` (or `None`) |
| License | [License Title](https://example.com/license) |

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

A brief description of what this data source measures, who collects it, and how it is used in surveillance.

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `signal_name_1` | COVID-19 | Count | Total confirmed counts over the reference period. |
| `signal_name_1_per_100k` | COVID-19 | Rate | Population-adjusted rate per 100,000 residents, including 90% confidence intervals (`ci_lower`, `ci_upper`). |

---

## Estimation

### Geographic Aggregation
Explain catchment disaggregation, county mappings, or rollups across geographic boundaries.

### Normalization
Specify the population baseline used for rate calculations.

### Smoothing
Describe rolling averages or smoothing windows applied to raw counts.

### Uncertainty
Detail confidence interval or standard error formulas:

$$
\hat{p} \pm z_{1-\alpha/2} \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}
$$

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic granularity level. |
| `geo_value` | Primary Key | Geographic entity identifier. |
| `time_value` | Primary Key | Reference date of the observation (`YYYY-MM-DD`). |
| `extra_col_1` | Primary Key (Extra Key) | Population subgroup identifier. |
| `value` | Value Column | Measured count, percentage, or rate. |
| `ci_lower` | Value Column | Lower bound of confidence interval (where applicable). |
| `ci_upper` | Value Column | Upper bound of confidence interval (where applicable). |

### Extra Keys

| Value | Description / Behavior |
| :--- | :--- |
| `all` | Combined population total (default when unspecified). |
| `subgroup_a` | Filter for subgroup A. |

### Example Query

`extra_keys=extra_col_1:subgroup_a`

---

## Missingness & Privacy

Describe small-cell suppression rules, null handling, and behavior when geographic subunits are missing.

---

## Limitations

Document sampling limitations, demographic representation biases, and reporting delays.

---

## Lag & Backfill

Explain reporting latency and whether historical observations receive retroactive updates.

---

## Source & Licensing

Data originates from [Data Provider Name](https://example.com).

Suggested citation:
> Data provided by [Data Provider Name], processed and served via the Delphi Epidata API.

---

## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **YYYY-MM-DD**. Initial release on Delphi V5 API.

</details>
````
