---
title: Delphi V5 Sources and Signals
parent: Delphi V5 API
nav_order: 3
has_children: true
---

# Delphi V5 Sources and Signals


### National Syndromic Surveillance Program ED Visits ([`nssp`](v5-signals/nssp.md))

| Attribute | Details |
| :--- | :--- |
| Data Source | Centers for Disease Control and Prevention (CDC) |
| Cadence | Weekly |
| Geographies | Nation, HHS region, HSA (NCI), HRR, MSA, State, County |

Weekly percentage of emergency department visits associated with respiratory pathogens.

---

### NHSN Respiratory Hospitalizations ([`nhsn`](v5-signals/nhsn.md))

| Attribute | Details |
| :--- | :--- |
| Data Source | National Healthcare Safety Network (NHSN) / CDC |
| Cadence | Weekly |
| Geographies | Nation, HHS region, State |

Weekly hospital respiratory admissions and bed usage reported to NHSN. 

---

### Epic Cosmos by Pophive ([`pophive`](v5-signals/pophive.md))

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

### Outpatient Claims ([`claims_data_outpatient`](v5-signals/claims_data_outpatient.md))

| Attribute | Details |
| :--- | :--- |
| Data Source | Medical insurance billing partners |
| Cadence | Daily |
| Geographies | Nation, HHS region, State, County, MSA, HRR |

Daily outpatient visit percentages derived from medical billing claims.
---

### Inpatient Claims ([`claims_data_inpatient`](v5-signals/claims_data_inpatient.md))

| Attribute | Details |
| :--- | :--- |
| Data Source | Medical insurance billing partners |
| Cadence | Daily |
| Geographies | State, County, MSA, HRR |

Daily inpatient admissions derived from medical billing claims.
