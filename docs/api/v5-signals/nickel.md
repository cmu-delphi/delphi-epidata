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
| `rsv_pct_ed_7dav` | RSV | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with RSV. |
| `rsv_pct_ip_7dav` | RSV | Percentage, 7-day window | Share of inpatient medical encounters associated with RSV. |
| `rsv_pct_op_7dav` | RSV | Percentage, 7-day window | Share of outpatient medical encounters associated with RSV. |
| `ari_pct_ed_7dav` | ILI | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `ari_pct_ip_7dav` | ILI | Percentage, 7-day window | Share of inpatient medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `ari_pct_op_7dav` | ILI | Percentage, 7-day window | Share of outpatient medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |


'covid_pct_ed_7dav' ~ 'covid_ed'
'covid_pct_ip_7dav' ~ 'covid_ip'
'covid_pct_op_7dav' ~ 'covid_op'
'diarrhea_pct_ed_7dav' ~ 'diarrhea_ed'
'diarrhea_pct_ip_7dav' ~ 'diarrhea_ip'
'diarrhea_pct_op_7dav' ~ 'diarrhea_op'
'influenza_pct_ed_7dav' ~ 'influenza_ed'
'influenza_pct_ip_7dav' ~ 'influenza_ip'
'influenza_pct_op_7dav' ~ 'influenza_op'
'rsv_pct_ed_7dav' ~ 'rsv_ed'
'rsv_pct_ip_7dav' ~ 'rsv_ip'
'rsv_pct_op_7dav' ~ 'rsv_op'
'ari_pct_ed_7dav' ~ 'resp_synd_ed'
'ari_pct_ip_7dav' ~ 'resp_synd_ip'
'ari_pct_op_7dav' ~ 'resp_synd_op'


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

### Observation Assignment

We get line-level EMR data from the data provider.
To turn it into aggregate estimates, we mark each medical visit as being associated with one or more pathogens, happening in a particular location, and happening in a particular care setting.
We mark each patient as belonging to a particular age bin.

#### Date of care

Each medical visit is included in aggregate estimates only for the date that the visit occurred or the patient was admitted.

#### Care setting

The line-level data is already tagged with the type of medical encounter.
We group these as follows to create inpatient, outpatient, and emergency categories.

- Inpatient `ip`: inpatient
- Outpatient `op`: telehealth, ambulatory visit, other ambulatory visit
- Emergency department `ed`: emergency department, observational stay

#### Location of care

Because facility identity is obscured in the raw data, it is not totally clear where a medical visit happened.
We have patient home region, but this has a few problems.
It isn't fine-resolution and the format is incompatible with our geoaggregation procedure.
It is also possible that a patient is getting care outside of their home region, e.g. while travelling.

For those reasons, it is more accurate and feasible to use the location of care.
For each medical visit, we identify the medical provider who provided the care, and link them to the National Provider Identifier (NPI) registry.
We use the provider's registered work location as the location of care.

#### Age buckets

We use patient birth _year_ to group patients into the following age bins:

- 0-4
- 5-17
- 18-49
- 50-64
- 65+

Patient birth dates are not available, so patient ages are defined as advancing on January 1 of every year.
That means that age bucket composition changes for all age buckets on January 1.

#### Qualifying conditions

We mark each medical visit as being associated with one or more pathogen categories through that patient's primary ICD-10 diagnosis codes and LOINC test codes.
As of November 1 2026, we look for diarrhea, influenza, COVID-19, RSV, and ARI (acute respiratory illness).

Respiratory diseases can be contagious and symptoms can be present for 2 weeks.
Since affected patients could seek care near the beginning _or_ the end of that period, we consider a given medical encounter as associated with a pathogen if that patient had any relevant diagnosis or positive lab test in the window two weeks before to two weeks after the encounter date.
The diagnosis or positive lab test can occur in a different care setting than the encounter itself.

Therefore, an encounter is associated with a respiratory pathogen if that patient received any relevant diagnoses or positive lab tests within ±2 weeks of the encounter date.
An encounter is associated with ARI (acute respiratory illness) if that patient received a URI (upper respiratory illness) diagnosis or received diagnoses of fever with either of cough or sore throat within ±2 weeks of the encounter date.
An encounter is associated with diarrhea if the patient received a relevant diagnoses at that particular encounter.

When a patient encounter is associated with multiple qualifying diagnosis codes, the encounter is considered associated with all of them.

An encounter that _is_ associated with a relevant diagnosis or positive lab test is then counted in the numerator (number of patients affected by a pathogen/symptom) on the date the encounter happened, as well as in the denominator.
If not associated with such a diagnosis or lab test, the encounter is only counted in the denominator (number of total patients) on the date the encounter happened.

We count each patient only once per day, although it's possible for a patient to have multiple medical encounters on the same day.

<details>
<summary><b>ICD10 diagnosis codes and LOINC lab test codes used</b></summary>

# ICD10 diagnosis codes

"Prefixes" are 3-character ICD-10 categories that match every included subcode, e.g. "J10" also matches J10.1, J10.81, etc.
All other codes match exactly.

- Influenza prefixes
  - J09
  - J10
  - J11
- URI
  - J06.9
- Fever
  - R50.9
- Cough or sore throat
  - J00
  - J01.9
  - J02.8
  - J02.9
  - J05.1
  - J20.9
  - R05
  - R05.1
- RSV
  - B97.4
  - J12.1
  - J20.5
  - J21.0
- COVID-19
  - U07.1
  - J12.82
- Diarrhea prefixes
  - A00
  - A01
  - A02
  - A03
  - A04
  - A05
  - A06
  - A07
  - A08
  - A09
  - R19.7

# LOINC lab test codes

- COVID-19
  - 94500-6
  - 94759-8
  - 94559-2
  - 95209-3
  - 94531-1
  - 94306-8
  - 94558-4
  - 96119-3
  - 94760-6
  - 94534-5
  - 94565-9
  - 94309-2
  - 60275-5
  - 95409-9
  - 94533-7
  - 94316-7
  - 94308-4
  - 96603-6
  - 95608-6
  - 94845-5
  - 97097-0
  - 94756-4
- RSV
  - 40987-0
  - 82176-9
  - 76089-2
  - 40988-8
  - 31950-9
  - 92131-2
  - 72885-7
  - 80597-8
  - 80598-6
  - 5876-8
  - 77022-2
  - 30075-6
  - 85479-4
  - 30076-4
  - 68966-1
  - 91795-5
  - 92957-0
  - 77023-0
  - 5877-6
  - 14129-1
  - 33045-6
  - 77390-3
  - 5874-3
  - 55100-2
- Influenza (includes influenza A/B panel tests)
  - 34487-9
  - 40982-1
  - 43874-7
  - 43895-2
  - 82170-2
  - 82166-0
  - 92141-1
  - 92142-9
  - 76080-1
  - 76078-5
  - 31859-2
  - 31864-2
  - 82169-4
  - 82167-8
  - 80382-5
  - 80383-3
  - 82168-6
  - 44577-5
  - 46082-4
  - 46083-2
  - 55465-9
  - 85478-6
  - 77026-3
  - 77027-1
  - 77028-9
  - 92977-8
  - 55466-7
  - 5867-7
  - 49524-2
  - 22827-0
  - 49521-8
  - 85477-8
  - 5866-9
  - 5862-8
  - 92976-0
  - 40981-3
  - 48310-7
  - 44558-5
  - 44575-9
  - 44564-3
  - 5863-6
  - 6604-3
  - 38382-8
  - 44571-8
  - 76079-3
  - 38381-0
  - 53251-5
  - 49534-1
  - 62462-7
  - 72366-8
  - 48509-4
  - 24015-0
  - 72365-0
  - 44567-6
  - 33535-6
  - 61102-0
  - 72367-6
  - 72356-9
  - 6437-8

</details>

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
