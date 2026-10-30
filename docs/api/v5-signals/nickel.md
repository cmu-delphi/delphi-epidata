---
title: Nickel ED, Inpatient, Outpatient EHR
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 7
---

# Inpatient Claims
{: .no_toc}

| Attribute | Details |
| :--- | :--- |
| **Source Name** | `nickel` |
| **Data Source** | De-identified medical visits from Delphi health system partners |
| **Geographic Levels** | `county`, `hrr`, `msa`, `state`, `hhs`, `census_division`, `census_region`, `nation` |
| **Temporal Granularity** | Daily, by date of service |
| **Reporting Cadence** | Weekly (Fridays) |
| **Temporal Scope Start** | 2010-01-07; the COVID signals begin 2020-03-01 |
| **Temporal Scope End** | Ongoing |
| **Extra Key Columns** | `age_group` |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Overview

This source measures the share of medical encounters associated with a variety of respiratory illnesses, or diarrhea.
It is built from de-identified electronic health record (EHR) visit records contributed by Delphi health system partners.
The data covers COVID-19, influenza, respiratory syncytial virus (RSV), diarrhea, and a non-specific combination of respiratory symptoms (previously referred to as influenza-like illness (ILI)).

---

## Indicators (Signals)

| Indicator Name | Pathogen or Disease | Metric Type | Description |
| :--- | :--- | :--- | :--- |
| `covid_pct_ed_7dav` | COVID-19 | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with COVID-19. History for this signal begins 2020-03-01. |
| `covid_pct_ip_7dav` | COVID-19 | Percentage, 7-day window | Share of inpatient medical encounters associated with COVID-19. History for this signal begins 2020-03-01. |
| `covid_pct_op_7dav` | COVID-19 | Percentage, 7-day window | Share of outpatient medical encounters associated with COVID-19. History for this signal begins 2020-03-01. |
| `diarrhea_pct_ed_7dav` | Diarrhea | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with diarrhea. |
| `diarrhea_pct_ip_7dav` | Diarrhea | Percentage, 7-day window | Share of inpatient medical encounters associated with diarrhea. |
| `diarrhea_pct_op_7dav` | Diarrhea | Percentage, 7-day window | Share of outpatient medical encounters associated with diarrhea. |
| `influenza_pct_ed_7dav` | Influenza | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with influenza. |
| `influenza_pct_ip_7dav` | Influenza | Percentage, 7-day window | Share of inpatient medical encounters associated with influenza. |
| `influenza_pct_op_7dav` | Influenza | Percentage, 7-day window | Share of outpatient medical encounters associated with influenza. |
| `ari_pct_ed_7dav` | ILI | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `ari_pct_ip_7dav` | ILI | Percentage, 7-day window | Share of inpatient medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `ari_pct_op_7dav` | ILI | Percentage, 7-day window | Share of outpatient medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `rsv_pct_ed_7dav` | RSV | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with RSV. |
| `rsv_pct_ip_7dav` | RSV | Percentage, 7-day window | Share of inpatient medical encounters associated with RSV. |
| `rsv_pct_op_7dav` | RSV | Percentage, 7-day window | Share of outpatient medical encounters associated with RSV. |


'covid_pct_ed_7dav' ~ 'covid_ed'
'covid_pct_ip_7dav' ~ 'covid_ip'
'covid_pct_op_7dav' ~ 'covid_op'
'diarrhea_pct_ed_7dav' ~ 'diarrhea_ed'
'diarrhea_pct_ip_7dav' ~ 'diarrhea_ip'
'diarrhea_pct_op_7dav' ~ 'diarrhea_op'
'influenza_pct_ed_7dav' ~ 'influenza_ed'
'influenza_pct_ip_7dav' ~ 'influenza_ip'
'influenza_pct_op_7dav' ~ 'influenza_op'
'ari_pct_ed_7dav' ~ 'resp_synd_ed'
'ari_pct_ip_7dav' ~ 'resp_synd_ip'
'ari_pct_op_7dav' ~ 'resp_synd_op'
'rsv_pct_ed_7dav' ~ 'rsv_ed'
'rsv_pct_ip_7dav' ~ 'rsv_ip'
'rsv_pct_op_7dav' ~ 'rsv_op'


---

## Estimation

### Metric Definition

A given county $$i$$, service date $$t$$, and extra keys $$k$$, composed here of age group and care setting, has numerator count $$Y_{itk}$$, denominator $$N_{itk}$$, and DP noise $$\delta_{itk}$$ (in count units),

$$
\hat{p}_{itk} = 100 \cdot \frac{Y_{itk} + \delta_{itk}}{N_{itk}}.
$$

A given non-county location $$j$$, service date $$t$$, and extra keys $$k$$, has estimated numerator count $$Y'_{jtk}$$ and denominator $$N_{jtk}$$, such that

$$
\hat{p}_{jtk} = 100 \cdot \frac{Y'_{jtk}}{N_{jtk}}.
$$

Estimated numerator count $$Y'_{jtk}$$ for a non-county location incorporates DP noise via the geoaggregation process such that for a non-county location $$j$$ composed of $$I$$ component counties,

$$
Y'_{jtk} = \sum_{i \in I}{Y_{itk} + \delta_{itk}}.
$$

Smoothed values for a key are computed over a trailing 7-day window $$W_s = \{s-6, \dots, s\}$$, with $$N_{itk}$$ total medical encounters in that location, age group, and care setting on a given day, and $$Y_{itk}^p$$ encounters associated with disease or condition $$p$$.
The 7-day average percentage published for a date $$s$$ is then

$$
\hat{p}_{isk}^p = 100 \cdot \frac{\sum_{t \in W_s} Y_{itk}^p}{\sum_{t \in W_s} N_{itk}},
$$

computed only when at least 5 days in the window are available.

### Differential Privacy

To prevent reidentification of patients, this dataset is noised in a way that makes it differentially private at the $$\text{epsilon} = \frac{5}{3}$$ level [per patient per day](https://registry.opendp.org/trust-models/#:~:text=Unit%20of%20Privacy).
(What does `epsilon` mean? See [discussion of "updated probability" here](https://desfontain.es/blog/differential-privacy-in-more-detail.html).)
Because the average patient doesn't get that much medical care in a year ([3-4 office visits per year](https://www.cdc.gov/nchs/fastats/physician-visits.htm), although likely varies widely by age, general health, and other factors), this corresponds to a high level of privacy over the course of a year as well.

We noise numerators for each indicator with `epsilon = 1/3` and sensitivity `delta = 1`.
This results in us applying Laplacian noise with `location = 0` and `scale = 3`.
The noise has units of counts.

New noise values are drawn for every county $$i$$, service date $$t$$, and extra key $$k$$ (age group + care setting).
Once a given key has a noise value assigned, that noise value is reused for every issue made to that county-service date-key's value.

Only raw county numerators are noised with randomly drawn DP-conforming noise.
This is done before any geoaggregation or smoothing is performed.
Denominators are left unnoised.

When a raw value is close to a natural threshold (for numerator, 0 or $$N_{jtk}$$) or the noise is relatively large, the noised value can become impossible (< 0, > $$N_{jtk}$$).
These values are left as-is until after geoaggregation, smoothing, and percentage calculation are done, after which impossible percentages are truncated to the closest boundary (0, 100).
Early truncation biases aggregated values.

### Qualifying conditions

Each

The raw claims feed categorizes unique daily outpatient visits into five mutually exclusive count categories based on primary ICD-10 diagnosis codes. When a patient encounter carries multiple qualifying diagnosis codes on the same date, priority is assigned in descending order of diagnostic specificity: Flu, COVID-like, Flu-like, then Mixed.

<details>
<summary><b>My section header in bold</b></summary>

Any folded content here. It requires an empty line just above it.

</details>

###


The raw claims feed categorizes unique daily hospital admissions into five mutually exclusive count categories based on primary ICD-10 diagnosis codes. When a patient admission carries multiple qualifying diagnosis codes on the same date, priority is assigned in descending order of diagnostic specificity: **Flu**, **COVID-like**, **Flu-like**, then **Mixed**.

| Category | Primary ICD-10 Codes | Description |
| :--- | :--- | :--- |
| **Denominator** | All | Total count of all unique inpatient admission claims. |
| **Flu** | `J09*`, `J10*`, `J11*` | Confirmed influenza diagnoses (`*` includes all subcodes). |
| **COVID-like** | `U07.1`, `U07.2`, `B97.29`, `J12.81`, `Z03.818`, `B34.2`, `J12.89` | Confirmed or suspected COVID-19 diagnoses. |
| **Flu-like** | `J22`, `B34.9` | Unspecified acute lower-respiratory infections and unspecified viral infections. Correlated with respiratory illness but not specific to influenza; tracked COVID-19 early in the pandemic before specific codes were widely adopted. |
| **Mixed** | `Z20.828`, `J12.9` | Suspected exposure to other viral communicable diseases and viral pneumonia, unspecified. |

#### Signal Composition

These raw categories map to the three published V5 indicators as follows:

- **COVID-19 (`pct_claims_covid`):**
  - *Before 2021-06-01:* Sums `COVID-like` and `Flu-like` counts over the denominator. The `Flu-like` (unspecified lower-respiratory) category tracked COVID-19 closely during the early pandemic while specific codes were not yet in widespread use.
  - *From 2021-06-01 onward:* Uses `COVID-like` counts only over the denominator.
- **Influenza (`pct_claims_flu`):** Uses the confirmed `Flu` count over the denominator across the entire series.
- **Other ARI (`pct_ari_other`):** Published from 2022-08-01 onward. Combines the `Mixed` and `Flu-like` counts over the denominator, capturing acute respiratory illness encounters not attributed to COVID-19 or confirmed influenza.

### Smoothing

For each geography, a 7-day trailing sum is taken of every diagnosis count and the total claim count. The window must contain at least 5 of 7 days to produce a value.

### Temporal Handling

Dates refer to the clinical date of service. Claims dated to the first calendar day of any month are dropped, because submission batching inflates that day. Service dates before 2019-10-01, and service dates in the future, are also dropped.

Data starts in Jan 2010, but with very small sample size. Much more useful after 2015. See "Rplot22" for example of variance over time.

Data for COVID signals is dropped if the reference date is before March 1 2020.

Only keep up to lag 96

### Geographic Handling

Claims arrive at two native geographic levels: county (`county`) and Hospital Referral Region (`hrr`). HRR values are served as reported.

All other geographic levels (`msa`, `state`, `hhs`, `census_division`, `census_region`, `nation`) are built by directly summing raw daily county counts (numerators and denominators are aggregated separately). Aggregation is performed on raw daily counts before computing 7-day sums, without imputation, so `fill_method` is always `source`.

---

## Relationship to V4

The V4 `hospital-admissions` source used the same health system claims and published a single COVID-19 percentage, through `smoothed_covid19_from_claims` and its day-of-week-adjusted twin `smoothed_adj_covid19_from_claims`.

| V4 Signal | V5 Signal | Notes |
| :--- | :--- | :--- |
| `smoothed_covid19_from_claims` | `claims_inpatient_adm_pct_claims_covid` | Replaced smoothed Jeffreys estimator with 7-day trailing ratio |
| `smoothed_adj_covid19_from_claims` | *(not available)* | Day-of-week adjustment discontinued |
| `smoothed_covid19` | *(not available)* | Discontinued in V4 |
| `smoothed_adj_covid19` | *(not available)* | Discontinued in V4 |
| *(not available)* | `claims_inpatient_adm_pct_claims_flu` | New in V5 |
| *(not available)* | `claims_inpatient_adm_pct_ari_other` | New in V5 (available from 2022-08-01) |

What changed in V5:

- **Expanded Geographies.** V4 served nation, state, county, HRR, and MSA. V5 adds HHS regions, census divisions, and census regions.
- **Broader Signal Set.** V5 adds influenza and other-ARI percentages next to COVID-19, and drops the combined electronic-record-and-claims variant that V4 froze in 2020.
- **Revised Estimator.** V4 applied a Jeffreys-style $$\frac{Y + 0.5}{N + 1}$$ correction, a backwards-padding step that widened the averaging window until a 500-visit threshold was met, a Poisson day-of-week adjustment, and a Gaussian linear smoother. V5 replaces all of it with the 7-day trailing sum from [Metric Definition](#metric-definition).

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | date | The publication or release date (`YYYY-MM-DD`). |
| `geo_type` | Primary Key | string | Geographic level (e.g., `county`, `state`, `nation`); see the summary table above for the full list. |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., `pa` for Pennsylvania, `42003` for Allegheny County). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation, always `source` for this source. |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation (`YYYY-MM-DD`, date of service). |
| `value` | Value Column | float | The recorded percentage of medical encounters over the trailing 7-day window. |

---

## Missingness & Privacy

To protect patient privacy, observations with fewer than 100 total claims across the trailing 7-day window are suppressed and omitted from publication. Windows with fewer than 5 days of data are withheld due to data sparsity and are likewise omitted. Missing days within an otherwise-qualifying window (at least 5 days and at least 100 claims) do not block publication.

Unobserved dates or geographies without reporting claims produce no records. Both suppressed and unobserved values are omitted entirely from query responses rather than reported as `null`.

---

## Limitations

This source only captures admissions from healthcare facilities that partner with Delphi, which does not cover all hospitals in the United States. Coverage density varies across states and counties.

The data reflects insured patients admitted to participating inpatient facilities. Uninsured individuals and admissions at non-participating institutions are not represented.

Standard errors and sample sizes are not published for this source.

Differences in local coding habits, billing practices, and facility participation mean that absolute levels are not always comparable across different regions. Trends within a single location over time are generally more reliable than spatial comparisons.

---

## Lag & Backfill

Hospital admissions are reported with several days of lag, so estimates for a given date of service typically become available 3 to 7 days later.

Insurance claims experience substantial backfill over several weeks as facilities and payers submit and process claims on varying schedules. Delphi runs daily updates across historical dates to incorporate late-arriving records.

Estimates for the most recent 7 to 13 days change significantly across subsequent revisions, often showing median shifts of 10 percent or more. Data points older than 57 days are generally stable, with subsequent median revisions under 1 percent. Full revision histories can be queried through the [`/archive/`](../v5_api_queries.md) and [`/snapshot/`](../v5_api_queries.md) endpoints. Delphi documented the empirical behavior of this backfill process in a [blog post on claims backfill](https://delphi.cmu.edu/blog/2020/11/05/a-syndromic-covid-19-indicator-based-on-insurance-claims-of-outpatient-visits/#backfill).

---

## Source and Licensing

De-identified medical billing claims contributed by Delphi health system partners. This dataset is made available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
