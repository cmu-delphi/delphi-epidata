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
2. Lineage callout            which V4 or V3 source this reproduces (omit for new sources)
3. Table of contents
4. Overview
5. Indicators
6. Estimation
   ├── Geographic Aggregation   (when the source is aggregated or crosswalked; discuss fill_method here)
   ├── Temporal Handling        (only when it does more than name the week-ending day)
   ├── Smoothing                (when a rolling window is applied)
   ├── Metric Definition        (the formula that turns raw data into the signal)
   └── Uncertainty              (confidence intervals, or an explicit "none")
7. Relationship to V4           (or V3; omit for sources with no predecessor)
8. Schema
   ├── Columns
   ├── Fill methods             (when the source has multiple paths; refer to Geographic Aggregation)
   ├── Extra keys               (only for real extra dimensions such as age_group)
   ├── Auxiliary tables         (when the source serves an /aux_data/ table)
   └── Example query
9. Missingness & Privacy
10. Limitations
11. Lag & Backfill
12. Changelog                   (optional; only include if there are necessary changes to flag)
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
| `Temporal Scope End` | Latest observation date: `Ongoing` for active feeds, or `YYYY-MM-DD` if reporting stopped. |
| `Extra Key Columns` | Real extra key columns (e.g. `age_group`), or `None`. `fill_method` is a core column, not an extra key. |
| `License` | License and link. |

### 2. Lineage callout

When a source reproduces a legacy endpoint, add a `{: .note }` blockquote immediately after the summary table. This mirrors the "Heads up" callout on the V4 page. Omit this callout entirely for new sources with no predecessor.

```markdown
> This source reproduces the legacy V4 COVIDcast [`<source>`](../covidcast-signals/<source>.md) source.
> One sentence on what changed. See [Relationship to V4](#relationship-to-v4).
{: .note }
```

### 3. Table of contents

Include the standard Just the Docs Jekyll table of contents block:

```markdown
## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}
```

### 4. Overview

One or two paragraphs: what the source measures, who collects it, and the surveillance context. Add a single citation sentence here only if the license requires attribution.

### 5. Indicators

A markdown table listing each indicator with its pathogen or disease, metric type (count, rate, percentage), and a short description. Group with subheadings when a source spans distinct metric families. For combinatoric naming schemes such as wastewater, give the prefix and suffix tables and the combination rule.

### 6. Estimation

Describe how raw data becomes each signal.

`### Geographic Aggregation` covers crosswalking, catchment disaggregation, and population weighting, including which levels are native and which are derived. Discuss `fill_method` here when the source computes more than one aggregation or missingness path (`source`, `fill_zero`, `fill_ave`).

`### Temporal Handling` is only needed when the source drops days, shifts reference dates, or uses season-to-date accumulation. Skip it if the only fact is the week-ending day.

`### Smoothing` explains any rolling window and who computes it (Delphi or the upstream provider).

`### Metric Definition` gives the formula. State it in words and in KaTeX, using `$$` on its own lines for display math and `$$...$$` inline. Define every symbol, name the estimator (for example a windowed positivity ratio or a population-weighted mean), and cite the standard form it follows.

`### Uncertainty` documents confidence intervals or standard errors. If the source has none, say so in one line.

### 7. Relationship to V4 (or V3)

For a migrated source, a short section on how the V5 method differs from the V4 (or V3) one. Cover the estimator, the signal set, the geographies, and revision handling. Keep it to what changed; the query-level mechanics belong in the [V4 to V5 Migration Guide](../v5_migration.md). Omit this section entirely for sources with no predecessor.

### 8. Schema

`### Columns` lists each column, its key role, its data type (such as `string`, `date`, or `float`), and its meaning (a markdown table is preferred).

`### Fill methods` is included when the source computes more than one aggregation path. Provide a brief reference pointing to [Geographic Aggregation](#geographic-aggregation) where the definitions and behavior are detailed.

`### Extra keys` is for genuine extra dimensions such as `age_group`. Give the valid values and how an unfiltered query behaves.

`### Auxiliary tables` documents any companion table served through `/epidata/v5/aux_data/`.

`### Example query` gives one realistic V5 request URL. Use the `/snapshot/` or `/archive/` form with `source`, `signal`, and `geo_type`; V5 does not take `geo_value` or `time_values`.

### 9. Missingness & Privacy

Distinguish clearly between suppressed values and unobserved values.

For suppression, explain the privacy rules and thresholds that mask data, such as cell counts below 10 or minimum denominator cutoffs. State whether suppressed points appear as `null` or are omitted from the output.

For unobserved values, describe why data was not collected or reported, such as non-participating facilities, transmission outages, or voluntary reporting periods. State whether unobserved periods or geographies appear as `null` or are absent from the dataset.

Document the treatment of missing sub-units during geographic roll-ups under [Geographic Aggregation](#geographic-aggregation) rather than in this section.

### 10. Limitations

Interpretation caveats: coverage gaps, market-share bias, coding versus laboratory confirmation, demographic skew.

### 11. Lag & Backfill

Typical lag from event to first publication, and whether past values revise or stay fixed.

### 12. Changelog

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
| **Temporal Scope End** | Ongoing (or YYYY-MM-DD) |
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

## Indicators

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `signal_name` | COVID-19 | Percentage | Short description. |

---

## Estimation

### Geographic Aggregation

Which levels are native and which are derived, the weighting used, and `fill_method` choices (`source`, `fill_zero`, `fill_ave`) when multiple aggregation paths exist.

### Metric Definition

For a location $$i$$ and time $$t$$, with numerator count $$Y_{it}$$ and denominator $$N_{it}$$,

$$
\hat{p}_{it} = 100 \cdot \frac{Y_{it}}{N_{it}}.
$$

### Uncertainty

Confidence interval formula, or "This source publishes no standard errors, sample sizes, or confidence intervals."

---

## Relationship to V4 (or V3)

How the V5 method differs from the V4 (or V3) estimator, signal set, geographies, and revision handling. Omit this section for a source with no predecessor.

---

## Schema

### Columns

| Column | Key Type | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | Signal identifier. |
| `geo_type` | Primary Key | string | Geographic level. |
| `geo_value` | Primary Key | string | Geographic entity code. |
| `fill_method` | Primary Key | string | Aggregation path. |
| `time_value` | Primary Key | date | Reference date (`YYYY-MM-DD`). |
| `value` | Value Column | float | Measured count, percentage, or rate. |

### Fill methods

See [Geographic Aggregation](#geographic-aggregation) for details on `source`, `fill_zero`, and `fill_ave`.

### Example Query

```url
https://delphi.cmu.edu/epidata/v5/snapshot/?source=source_id&signal=signal_name&geo_type=state
```

---

## Missingness & Privacy

Explain privacy rules and thresholds, such as cell counts below 10, and state whether suppressed values appear as `null` or are omitted.

Describe causes of non-reporting, such as facility non-participation, and state whether unobserved rows appear as `null` or are omitted.

---

## Limitations

Sampling limits, representativeness, and reporting delays.

---

## Lag & Backfill

Reporting latency and whether historical values revise.
````
