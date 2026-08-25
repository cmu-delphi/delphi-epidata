---
title: Delphi V5 Sources and Signals
parent: Delphi V5 API
nav_order: 3
has_children: true
---

# Delphi V5 Sources and Signals

> **The legacy V4 API is being phased out.** See the [V4 to V5 Migration Guide](v5_migration.md) for guidance on migrating existing queries.
{: .warning }

## V4 to V5 Source Coverage

Not all V4 sources have migrated to V5. The table below lists available V5 sources as of August 25, 2026:

| V4 Source | V5 Source |
| :--- | :--- |
| `nssp` | `nssp` |
| `nhsn` | `nhsn` |
| `doctor-visits` | `claims_data_outpatient` |
| `hospital-admissions` | `claims_data_inpatient` |
| None (new in V5) | [`pophive`](v5-signals/epic-cosmos.md), [`nwss`](v5-signals/nwss.md), [`va_respiratory`](v5-signals/va_respiratory.md) |

All other sources remain V4-only. Because this documentation is updated periodically, query the [`/epidata/v5/metadata/`](v5_meta.md) endpoint (e.g. `https://delphi.cmu.edu/epidata/v5/metadata/`) to check live source availability in V5.

---

### National Syndromic Surveillance Program ED Visits (`nssp`)

| Attribute | Details |
| :--- | :--- |
| Data Source | Centers for Disease Control and Prevention (CDC) |
| Cadence | Weekly |
| Geographies | Nation, HHS region, HSA (NCI), HRR, MSA, State, County |

Weekly percentage of emergency department visits associated with respiratory pathogens.

---

### NHSN Respiratory Hospitalizations (`nhsn`)

| Attribute | Details |
| :--- | :--- |
| Data Source | National Healthcare Safety Network (NHSN) / CDC |
| Cadence | Weekly |
| Geographies | Nation, HHS region, State |

Weekly hospital respiratory admissions and bed usage reported to NHSN. 

---

### Epic Cosmos by Pophive ([`pophive`](v5-signals/epic-cosmos.md))

| Attribute | Details |
| :--- | :--- |
| Data Source | Epic Cosmos (via Pophive) |
| Cadence | Daily |
| Geographies | Nation, HHS region, State |
| Extra Key Columns | `age_group` |

Daily ED visit counts and percentages from Epic Cosmos, stratified by pathogen. The `age_group` extra key column enables age-stratified queries.

---

### NWSS Wastewater ([`nwss`](v5-signals/nwss.md))

| Attribute | Details |
| :--- | :--- |
| Data Source | National Wastewater Surveillance System (CDC) |
| Cadence | Daily / sample-based |
| Geographies | Sewershed |

---

### Outpatient Claims (`claims_data_outpatient`)

| Attribute | Details |
| :--- | :--- |
| Data Source | Medical insurance billing partners |
| Cadence | Daily |
| Geographies | Nation, HHS region, State, County, MSA, HRR |

Daily outpatient visit percentages derived from medical billing claims.
---

### Inpatient Claims (`claims_data_inpatient`)

| Attribute | Details |
| :--- | :--- |
| Data Source | Medical insurance billing partners |
| Cadence | Daily |
| Geographies | State, County, MSA, HRR |

Daily inpatient admissions derived from medical billing claims.
