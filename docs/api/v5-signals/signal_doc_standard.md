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
5. Indicators (Signals)
6. Estimation
   ├── Metric Definition        (the formula that turns raw data into the signal)
   ├── Smoothing                (when a rolling window is applied)
   ├── Uncertainty              (optional; when confidence intervals or standard errors are reported)
   ├── Temporal Handling        (reference time basis, week alignment, or date-filtering rules)
   ├── Geographic Units         (optional; when the source uses custom units such as facility catchments or sampling sites)
   └── Geographic Aggregation   (when the source is aggregated or crosswalked; discuss fill_method here)
7. Relationship to V4 or V3    (use V4 for endpoints from V4, V3 for all other legacy endpoints; omit for new sources)
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
13. Source and Licensing
```

Keep a section only when it has something to say. Do not add a Changelog with a placeholder "initial release" entry.

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
> This source reproduces the legacy V4 [`<source>`](../covidcast-signals/<source>.md) source.
> One sentence on what changed. See [Relationship to V4](#relationship-to-v4).
{: .note }
```

Or for a source reproducing a V3 endpoint (all legacy endpoints other than V4):

```markdown
> This source reproduces the legacy V3 [`<source>`](../<source>.md) source.
> One sentence on what changed. See [Relationship to V3](#relationship-to-v3).
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

### 5. Indicators (Signals)

A markdown table listing each indicator (signal) with its pathogen or disease, metric type (count, rate, percentage), and a short description. Group with subheadings when a source spans distinct metric families. For combinatoric naming schemes such as wastewater, give the prefix and suffix tables and the combination rule.

### 6. Estimation

Describe how raw data becomes each signal.

`### Metric Definition` gives the formula. State it in words and in KaTeX, using `$$` on its own lines for display math and `$$...$$` inline. Define every symbol, name the estimator (for example a windowed positivity ratio or a population-weighted mean), and cite the standard form it follows.

`### Smoothing` explains any rolling window and who computes it (Delphi or the upstream provider).

`### Uncertainty` is optional. Document confidence intervals or standard errors when available, or omit this section if the source publishes none.

`### Temporal Handling` documents the reference time basis (e.g. date of service vs. date of report), week-ending alignment, drop rules (e.g. dropping first-of-month batching artifacts), and holiday adjustments.

`### Geographic Units` is optional. Use it when the source defines custom or source-specific geographic units (such as VA facility catchment areas or NWSS wastewater sampling sites and sewersheds). Describe what the unit represents, how sites or facilities are identified, and how their boundaries are defined. Omit this section when the source uses only standard administrative levels (nation, state, county, HHS regions).

`### Geographic Aggregation` covers crosswalking, catchment disaggregation, and population weighting, including which levels are native and which are derived. Discuss `fill_method` here when the source computes more than one aggregation or missingness path (`source`, `fill_zero`, `fill_ave`).

### 7. Relationship to V4 or V3

For a migrated source, name the section `## Relationship to V4` if the predecessor was in V4, or `## Relationship to V3` if it was in V3 (all legacy endpoints other than V4 belong to V3). Do not mention that V4 is the former COVIDcast. Cover the estimator, the indicator set, the geographies, and revision handling. Keep it to what changed; the query-level mechanics belong in the [V4 to V5 Migration Guide](../v5_migration.md). Omit this section entirely for sources with no predecessor.

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

Optional. Include only when there is a real methodology change or a meaningful ingestion-start date to record. Place it in a collapsible block.

```markdown
## Changelog

<details markdown="1">
<summary>Click to expand</summary>

- **YYYY-MM-DD**. Description of the change.

</details>
```

### 13. Source and Licensing

Upstream provider details, dataset origin, licensing terms, and any attribution or citation requirements required by the data contributor.

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

> This source reproduces the legacy V4 [`source_id`](../covidcast-signals/source_id.md) source. One sentence on what changed. See [Relationship to V4](#relationship-to-v4).
{: .note }

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

What the source measures, who collects it, and how it is used.

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `signal_name` | COVID-19 | Percentage | Short description. |

---

## Estimation

### Metric Definition

For location $$i$$ and time $$t$$, with numerator count $$Y_{it}$$ and denominator $$N_{it}$$,

$$
\hat{p}_{it} = 100 \cdot \frac{Y_{it}}{N_{it}}.
$$

### Smoothing

Rolling window explanation and who computes it (Delphi or upstream provider). Omit if unwindowed.

### Uncertainty

Confidence interval formula. Omit this section if the source publishes no standard errors, sample sizes, or confidence intervals.

### Temporal Handling

Reference time basis, week-ending alignment, date shifts, or accumulation rules.

### Geographic Units

Optional. Describe source-specific geographic units (such as facility catchment areas or sampling sites) and how they are defined. Omit if the source uses only standard geographic levels.

### Geographic Aggregation

Which levels are native and which are derived, the weighting used, and `fill_method` choices (`source`, `fill_zero`, `fill_ave`) when multiple aggregation paths exist.

---

## Relationship to V4

How the V5 method differs from the V4 (or V3) estimator, indicator set, geographies, and revision handling. Name the section `## Relationship to V3` if reproducing a V3 endpoint. Omit this section entirely for a source with no predecessor.

---

## Schema

### Columns

| Column | Key Type | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | Signal identifier. |
| `report_time` | Primary Key | date | Publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level. |
| `geo_value` | Primary Key | string | Geographic entity code. |
| `fill_method` | Primary Key | string | Aggregation path. |
| `reference_time` | Primary Key | date | Reference date (`YYYY-MM-DD`). |
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

---

## Source and Licensing

Data provenance, licensing terms, and any required citations or terms of use.
````
