---
title: Delphi V5 Sources and Signals
parent: Delphi V5 API
nav_order: 3
has_children: true
---

# Delphi V5 Sources and Signals

> **The legacy V4 API is being phased out.** See the [V4 to V5 Migration Guide](v5_migration.md) for guidance on migrating existing queries.
{: .warning }

## V5 Sources

| Source | Cadence | Geographies | Extra Key Columns |
| :--- | :--- | :--- | :--- |
| `nssp` | Weekly | National, HHS region, State | — |
| `nhsn` | Weekly | National, HHS region, State | — |
| [`pophive`](v5-signals/epic-cosmos.md) | Irregular (biweekly to monthly) | Nation, HHS region, State | `age_group` |
| [`nwss`](v5-signals/nwss.md) | Weekly | Sewershed | `nwss_source`, `sample_index` |
| `claims_outpatient` | Daily | State, County, MSA, HRR | — |
| `claims_inpatient` | Daily | State, County, MSA, HRR | — |

## V4 to V5 Source Coverage

Not all V4 sources have migrated to V5. The table below lists available V5 sources as of August 25, 2026:

| V4 Source | V5 Source |
| :--- | :--- |
| `nssp` | `nssp` |
| `nhsn` | `nhsn` |
| `doctor-visits` | `claims_outpatient` |
| `hospital-admissions` | `claims_inpatient` |
| None (new in V5) | [`pophive`](v5-signals/epic-cosmos.md), [`nwss`](v5-signals/nwss.md) |

All other sources remain V4-only. Because this documentation is updated periodically, query the [`/epidata/v5/metadata/`](v5_meta.md) endpoint (e.g. `https://delphi.cmu.edu/epidata/v5/metadata/`) to check live source availability in V5.
