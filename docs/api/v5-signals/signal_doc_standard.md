---
title: V5 Signal Documentation Standard
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_exclude: true
---

# V5 Signal Documentation Standard
{: .no_toc}

This guide describes the structure, section titles, and writing conventions for Delphi V5 data source documentation in `docs/api/v5-signals/<source>.md`.

---

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Section hierarchy

Every V5 source page follows the same order so pages stay predictable:

```
1. Frontmatter and summary table
2. Lineage callout            which V4 or V3 source this reproduces, or "new in V5"
3. Table of contents
4. Overview
5. Signals
6. Estimation
   ├── Geographic Aggregation   (when the source is aggregated or crosswalked)
   ├── Temporal Handling        (only when it does more than name the week-ending day)
   ├── Smoothing                (when a rolling window is applied)
   ├── Metric Definition        (the formula that turns raw data into the signal)
   └── Uncertainty              (confidence intervals, or an explicit "none")
7. Relationship to V4           (or V3; omit for sources with no predecessor)
8. Schema
   ├── Columns
   ├── Fill methods             (when the source has more than one aggregation path)
   ├── Extra keys               (only for real extra dimensions such as age_group)
   ├── Auxiliary tables         (when the source serves an /aux_data/ table)
   └── Example query
9. Missingness & Privacy
10. Limitations
11. Lag & Backfill
12. Changelog                   (optional; only when there is a real change to record)
```

Keep a section only when it has something to say. A one-line "aligns to Saturday" belongs in the summary table, not in its own subheading. Do not add a Changelog with a placeholder "initial release" entry, and do not add a standalone "Source & Licensing" section; the license lives in the summary table, and a citation line goes in the Overview only when the license requires attribution.

---

## Section guidelines

### 1. Frontmatter and summary table

Jekyll frontmatter, then the dataset title, then a table of core attributes.

```yaml
---
title: Short Name (e.g. NSSP ED Visits, VA Respiratory)
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: <integer>
---
```

| Attribute | Description |
| :--- | :--- |
| `Source Name` | API source identifier (e.g. `nssp`, `va_respiratory`). |
| `Data Source` | Link to the upstream provider or portal. |
| `Geographic Levels` | Supported `geo_type` values. |
| `Temporal Granularity` | Frequency of the data, with the week-ending day for weekly sources. |
| `Reporting Cadence` | How often Delphi updates the feed. |
| `Temporal Scope Start` | Earliest observation date, `YYYY-MM-DD`. |
| `Date of Last Revision` | How revisions work (static, rolling window, revised on backfill). |
| `Extra Key Columns` | Real extra key columns (e.g. `age_group`), or `None`. `fill_method` is a core column, not an extra key. |
| `License` | License and link. |

### 2. Lineage callout

Immediately after the summary table, add a `{: .note }` blockquote stating whether the source reproduces a legacy endpoint. This mirrors the "Heads up" callout on the V4 page.

For a migrated source:

```markdown
> This source reproduces the legacy V4 COVIDcast [`<source>`](../covidcast-signals/<source>.md) source.
> One sentence on what changed. See [Relationship to V4](#relationship-to-v4).
{: .note }
```

For a source with no predecessor:

```markdown
> This source is new in V5. It has no V4 COVIDcast or classic Epidata predecessor.
{: .note }
```

### 3. Overview

One or two paragraphs: what the source measures, who collects it, and the surveillance context. Add a single citation sentence here only if the license requires attribution.

### 4. Signals

A markdown table listing each signal with its pathogen or condition, metric type (count, rate, percentage), and a short description. Group with subheadings (`### Case Signals`, `### Vaccination Signals`) when a source spans distinct metric families. For combinatoric naming schemes such as wastewater, give the prefix and suffix tables and the combination rule.

### 5. Estimation

Describe how raw data becomes each signal.

`### Geographic Aggregation` covers crosswalking, catchment disaggregation, and population weighting, including which levels are native and which are derived.

`### Temporal Handling` is only needed when the source drops days, shifts reference dates, or uses season-to-date accumulation. Skip it if the only fact is the week-ending day.

`### Smoothing` explains any rolling window and who computes it (Delphi or the upstream provider).

`### Metric Definition` gives the formula. State it in words and in KaTeX, using `$$` on its own lines for display math and `$$...$$` inline. Define every symbol, name the estimator (for example a windowed positivity ratio or a population-weighted mean), and cite the standard form it follows.

`### Uncertainty` documents confidence intervals or standard errors. If the source has none, say so in one line.

### 6. Relationship to V4

For a migrated source, a short section on how the V5 method differs from the V4 (or V3) one. Cover the estimator, the signal set, the geographies, and revision handling. Keep it to what changed; the query-level mechanics belong in the [V4 to V5 Migration Guide](../v5_migration.md). Omit this section entirely for sources with no predecessor.

### 7. Schema

`### Columns` lists each column, its key role, and its meaning.

`### Fill methods` is included when the source computes more than one aggregation path. Give the `fill_method` values (`source`, `fill_zero`, `fill_ave`) and what each does. If the source has a single path, say so in one line instead.

`### Extra keys` is for genuine extra dimensions such as `age_group`. Give the valid values and how an unfiltered query behaves.

`### Auxiliary tables` documents any companion table served through `/epidata/v5/aux_data/`.

`### Example query` gives one realistic V5 request URL. Use the `/snapshot/` or `/archive/` form with `source`, `signal`, and `geo_type`; V5 does not take `geo_value` or `time_values`.

### 8. Missingness & Privacy

Suppression thresholds, whether suppressed points read as `null` or are dropped, and how aggregation treats missing sub-units.

### 9. Limitations

Interpretation caveats: coverage gaps, market-share bias, coding versus laboratory confirmation, demographic skew.

### 10. Lag & Backfill

Typical lag from event to first publication, and whether past values revise or stay fixed.

### 11. Changelog

Optional. Include only when there is a real methodology change or a meaningful ingestion-start date to record. Place it at the bottom in a collapsible block.

```markdown
## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **YYYY-MM-DD**. Description of the change.

</details>
```

---

## Template

Copy and adapt this when adding a new V5 source page.

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
| **Source Name** | `source_id` |
| **Data Source** | [Provider](https://example.com) |
| **Geographic Levels** | `nation`, `state`, `hhs`, `county` |
| **Temporal Granularity** | Weekly, week ending Saturday |
| **Reporting Cadence** | Weekly |
| **Temporal Scope Start** | YYYY-MM-DD |
| **Date of Last Revision** | Revised on backfill (see [Lag & Backfill](#lag--backfill)) |
| **Extra Key Columns** | None |
| **License** | [License](https://example.com/license) |

> This source reproduces the legacy V4 COVIDcast [`source_id`](../covidcast-signals/source_id.md) source. One sentence on what changed. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

What the source measures, who collects it, and how it is used.

---

## Signals

| Signal Name | Pathogen | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `signal_name` | COVID-19 | Percentage | Short description. |

---

## Estimation

### Geographic Aggregation

Which levels are native and which are derived, and the weighting used.

### Metric Definition

For a location $$i$$ and time $$t$$, with numerator count $$Y_{it}$$ and denominator $$N_{it}$$,

$$
\hat{p}_{it} = 100 \cdot \frac{Y_{it}}{N_{it}}.
$$

### Uncertainty

Confidence interval formula, or "This source publishes no standard errors, sample sizes, or confidence intervals."

---

## Relationship to V4

How the V5 method differs from the V4 estimator, signal set, geographies, and revision handling. Omit this section for a source with no predecessor.

---

## Schema

### Columns

| Column | Key Type | Description |
| :--- | :--- | :--- |
| `signal` | Primary Key | Signal identifier. |
| `geo_type` | Primary Key | Geographic level. |
| `geo_value` | Primary Key | Geographic entity code. |
| `fill_method` | Primary Key | Aggregation path. |
| `time_value` | Primary Key | Reference date (`YYYY-MM-DD`). |
| `value` | Value Column | Measured count, percentage, or rate. |

### Fill methods

`source`, `fill_zero`, `fill_ave`, and what each does. Or one line if the source has a single path.

### Example Query

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=source_id&signal=signal_name&geo_type=state
```

---

## Missingness & Privacy

Suppression rules, null handling, and behaviour when sub-units are missing.

---

## Limitations

Sampling limits, representativeness, and reporting delays.

---

## Lag & Backfill

Reporting latency and whether historical values revise.
````
