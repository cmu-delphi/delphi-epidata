---
title: Nickel ED, Inpatient, Outpatient EHR
parent: Delphi V5 Sources and Signals
grand_parent: Delphi V5 API
nav_order: 7
---

# Nickel ED, Inpatient, Outpatient EHR
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

This source measures the share of medical encounters associated with a variety of respiratory illnesses and diarrhea.
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
| `ari_pct_ed_7dav` | ILI, ARI | Percentage, 7-day window | Share of emergency department (ED) medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `ari_pct_ip_7dav` | ILI, ARI | Percentage, 7-day window | Share of inpatient medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |
| `ari_pct_op_7dav` | ILI, ARI | Percentage, 7-day window | Share of outpatient medical encounters associated with an acute respiratory illness diagnosis not attributed to COVID-19 or influenza. |


<!-- # Map between new and old names
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
'ari_pct_op_7dav' ~ 'resp_synd_op' -->


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

We get line-level EHR data from the data provider.
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

<h3> ICD-10 diagnosis codes </h3>

"Prefixes" are 3-character ICD-10 categories that match every included subcode, e.g. "J10" also matches J10.1, J10.81, etc.
All other codes match exactly.
<br>
<br>
Influenza prefixes: J09, J10, J11
<br>
URI: J06.9
<br>
Fever: R50.9
<br>
Cough or sore throat: J00, J01.9, J02.8, J02.9, J05.1, J20.9, R05, R05.1
<br>
RSV: B97.4, J12.1, J20.5, J21.0
<br>
COVID-19: U07.1, J12.82
<br>
Diarrhea prefixes: A00, A01, A02, A03, A04, A05, A06, A07, A08, A09, R19.7

 <h3> LOINC lab test codes </h3>

COVID-19: 94500-6, 94759-8, 94559-2, 95209-3, 94531-1, 94306-8, 94558-4, 96119-3, 94760-6, 94534-5, 94565-9, 94309-2, 60275-5, 95409-9, 94533-7, 94316-7, 94308-4, 96603-6, 95608-6, 94845-5, 97097-0, 94756-4
<br>
RSV: 40987-0, 82176-9, 76089-2, 40988-8, 31950-9, 92131-2, 72885-7, 80597-8, 80598-6, 5876-8, 77022-2, 30075-6, 85479-4, 30076-4, 68966-1, 91795-5, 92957-0, 77023-0, 5877-6, 14129-1, 33045-6, 77390-3, 5874-3, 55100-2
<br>
Influenza (includes influenza A/B panel tests): 34487-9, 40982-1, 43874-7, 43895-2, 82170-2, 82166-0, 92141-1, 92142-9, 76080-1, 76078-5, 31859-2, 31864-2, 82169-4, 82167-8, 80382-5, 80383-3, 82168-6, 44577-5, 46082-4, 46083-2, 55465-9, 85478-6, 77026-3, 77027-1, 77028-9, 92977-8, 55466-7, 5867-7, 49524-2, 22827-0, 49521-8, 85477-8, 5866-9, 5862-8, 92976-0, 40981-3, 48310-7, 44558-5, 44575-9, 44564-3, 5863-6, 6604-3, 38382-8, 44571-8, 76079-3, 38381-0, 53251-5, 49534-1, 62462-7, 72366-8, 48509-4, 24015-0, 72365-0, 44567-6, 33535-6, 61102-0, 72367-6, 72356-9, 6437-8

</details>


### Smoothing

For each geography, care setting, and age group, a 7-day trailing sum is taken of the patient count who had care associated with a pathogen or symptom, and of the total patient count.
The window must contain at least 5 of 7 days to produce a value.

### Temporal Handling

Dates refer to the clinical date of service.
Service dates before 2015-01-02 and service dates in the future are dropped.
Data for COVID signals is dropped for reference dates before March 1 2020.

We currently only keep the first 90 days of revisions for each observation, i.e. where the reporting lag is 90 days or less.
This may result in us missing some revisions, but should capture the vast majority and all significant revisions.
See [the Lag & Backfill section](lag--backfill) for more detail.

### Geographic Handling

The source data is reported in its raw form at by ZIP code.

All geographic levels (`county`, `msa`, `hrr`, `state`, `hhs`, `census_division`, `census_region`, `nation`) are built by assigning portions of each ZIP code value to component counties, and then summing raw daily counts across counties.
Numerators and denominators are aggregated separately.
Aggregation is performed on raw daily counts before computing 7-day sums, without imputation, so `fill_method` is always `source`.

---

## Schema

### Columns

| Column | [Key Type](../v5_api_queries.md#key-types-and-column-roles) | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `signal` | Primary Key | string | The name of the requested indicator. |
| `report_time` | Primary Key | datetime | Ingestion timestamp in UTC (`YYYY-MM-DD HH:MM:SS`). |
| `geo_type` | Primary Key | string | Geographic level (e.g., `county`, `state`). |
| `geo_value` | Primary Key | string | Unique code for the location (e.g., FIPS, state abbreviation). |
| `fill_method` | Primary Key | string | Imputation method used during geographic aggregation (`source`, `fill_ave`, or `fill_zero`). |
| `reference_time` | Primary Key | date | The date or surveillance period represented by the observation (`YYYY-MM-DD`). |
| `age_group` | Primary Key (Extra Key) | string | Age group category. |
| `value` | Value Column | float | The recorded measurement (e.g., count, percentage, rate, or statistical estimate). |
| `ci_lower` | Value Column | float | Lower bound of the 90% confidence interval. |
| `ci_upper` | Value Column | float | Upper bound of the 90% confidence interval. |

---

## Missingness & Privacy

Under the guarantees of differential privacy, we are _able_ to release values for all locations, even those with very small sample sizes.
However, we restrict locations from being reported when we consider them to be too noisy, sparse, or generally not useful.
For example, a signal for a given location with a confidence interval of 0-100% isn't useful and will not be reported.

Because of this, as of Nov 1 2026, we only report 119 counties, 58 HRRs, 64 MSAs, and 29 states.
These are not necessarily the most populous locations at a given geographic resolution since it depends on where participating facilities are located.
All locations are reported for higher geographic types (census division, census region, nation).

Observations with fewer than 5 days of data across the trailing 7-day window are suppressed due to data sparsity and omitted from publication.
Unobserved dates or geographies without reporting claims produce no records.
Both suppressed and unobserved values are omitted entirely from query responses rather than reported as `NULL`.

---

## Limitations

This source only includes data from medical facilities (hospitals and associated outpatient clinics) that are part of the 22 healthcare systems parterning with Nickel.
Not all facilities in the United States are included, and medical visits at those non-participating facilities are not captured.

The portion of the local population that's included in the particpating facilities varies by location.
At the state level, Ohio, Conneticut, and Virginia have the largest sample sizes.

Differences in local and facility coding habits and billing practices mean that absolute levels are not always comparable between different regions.
Trends within a single location over time are generally more reliable than spatial comparisons.

When healthcare systems or facilities join or leave the network, it can cause sharp changes in the sample sizes of the locations they are part of, especially if the facility makes up a large share of the medical care there.
Because facilities can have differences in coding practices and may see different types of patients, changes in the facility network can also change the long-term average of the estimate for a given pathogen or symptom.

We report data split by patient age, location of care, and encounter type (care setting).
All of these are missing in some portion of the source data.

Specifically, location of care is based on the provider's reported place of work in the NPI registry.
The registry we're using does not include all providers -- about 30% of providers in the visit data do not have location information available.
Providers can be added or change their NPI information at any point, but our copy of the registry may have a delay before syncing.
The provider's registered place of work could also be far away from the actual location of care.
For example, a provider employed by a private practice that is contracted by a hospital located in a different city, or a travel nurse.
Therefore, not all care can be linked to a location and locations may occasionally be incorrect.

Care setting is often unavailable in the source data, with observations being reported with `NULL` and `Other` encounter type.
For example, in the state of Kansas, about 80% of all encounters have `NULL` or `Other` encounter type.
Almost all of those are `NULL`.
In the state of Ohio, 2% of encounters are `NULL` but 25% are `Other`.
We exclude these observations from our estimates.
There's a strong relationship between `NULL`/`Other` encountertype frequency and location (state) of care.
We believe this is due to differences in coding between facilities.

Sample sizes are not published for this source.

---

## Lag & Backfill

Although this source reports daily data, the underlying dataset is only updated once a week (on Thursday night).
Therefore, estimates for a given date of service become available 1 to 7 days later.
This also means that revisions only come out once a week, so it's possible to have only poor quality data for the most recent Wednesday, e.g., until the next issue comes out.

Delphi runs daily updates across historical dates to incorporate late-arriving records.
We currently only keep the first 90 days of revisions for each observation, i.e. where the reporting lag is 90 days or less.
This may result in us missing some revisions, but should capture the vast majority and all significant revisions.

This source experiences substantial backfill over the first 3 issues (3 weeks).
Estimates for the most recent 21 days change significantly across subsequent revisions, often showing median shifts of 30 percent or more.
Data points older than about 30 days are generally stable, with subsequent median revisions under 1 percent.

Full revision histories can be queried through the [`/archive/`](../v5_api_queries.md) and [`/snapshot/`](../v5_api_queries.md) endpoints.

---

## Source and Licensing

De-identified EHR visit records contributed by Delphi health system partners.
This dataset is made available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
