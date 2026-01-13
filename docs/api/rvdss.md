---
title: Respiratory Virus Detections in Canada
parent: Data Sources and Signals
grand_parent: Other Endpoints (COVID-19 and Other Diseases)
nav_order: 1
---

# Respiratory Virus Detections in Canada

{: .no_toc}

-   **Source name:** `rvdss`
-   **Earliest issue available:** Epiweek 36 2013 (2013-09-07)
-   **Date of last change:** Never
-   **Available for:** province, lab, region, nation (see [Geography](#geography))
-   **Time type:** week (see [date format docs](../covidcast_times.md))
-   **License:** [Open Government Licence - Canada](#source-and-licensing)

This data source of respiratory virus detections in Canada is collected by the [Respiratory Virus Detection Surveillance System (RVDSS)](https://health-infobase.canada.ca/respiratory-virus-surveillance/about.html) and published by the Public Health Agency of Canada (PHAC). Laboratory tests for various respiratory illnesses are reported on a weekly basis by sentinel laboratories across Canada to the [Centre for Immunization and Respiratory Infectious Diseases (CIRID)](https://www.canada.ca/en/public-health/services/infectious-diseases/centre-immunization-respiratory-infectious-diseases-cirid.html), a subsidiary of PHAC. The data was originally reported in weekly online reports, but since June 2024, has changed to being reported through a dynamic dashboard.

**NOTE**: Human coronovirus (HCoV) refers to seasonal coronovirus, which differs from SARS-CoV-2, the novel pandemic coronovirus that causes COVID-19. SARS-CoV-2 (COVID-19) was not reported until the start of the 2022-2023 season.

## Table Keys

There are the meta-data columns used to uniquely identify data rows/points.

| Key          | Description                                                                                                                     |
|--------------|---------------------------------------------------------------------------------------------------------------------------------|
| `geo_value`  | The geographical location (see [Geography](#geography))                                                                         |
| `geo_type`   | The type of geographical location (see [Geography](#geography)) <br/> **Available types:** `lab`,`province`, `region`, `nation` |
| `time_value` | The end of the epiweek                                                                                                          |
| `time_type`  | Type of time value, only `week` available                                                                                       |
| `epiweek`    | Epidemiological week                                                                                                            |
| `issue`      | Issue/version date of the data (see [Data Versioning](#version) for full details)                                               |

## Signals

| Signal                         | Description                                                                                                                                                                              |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sarscov2_tests`               | Number of SARS-CoV-2 (COVID-19) laboratory tests <br/> **Earliest Date Available:** 2022-09-03                                                                                           |
| `sarscov2_positive_tests`      | Number of positive SARS-CoV-2 (COVID-19) laboratory tests <br/> **Earliest Date Available:** 2022-09-03                                                                                  |
| `sarscov2_pct_positive`        | Percentage of SARS-CoV-2 (COVID-19) laboratory tests that are positive <br/> **Earliest Date Available:** 2022-09-03                                                                     |
| `flu_tests`                    | Number of influenza laboratory tests. Tests for all influenza subtypes are included. <br/> **Earliest Date Available:** 2013-08-31                                                                                    |
| `flua_tests`                   | Number of influenza A laboratory tests. Since influenza tests normally are panels composed of subtests for influenza A and influenza B, we assume that the number of influenza A tests is always the same as the total number of influenza tests (`flu_tests`). This assumption has been validated on dates xx-xx, when RVDSS explicitly reported numbers of total, flu A, and flu B tests. This field is maintained for convenience. <br/> **Earliest Date Available:** 2013-08-31         |
| `flub_tests`                   | Number of influenza B laboratory tests. Since influenza tests normally are panels composed of subtests for influenza A and influenza B, we assume that the number of influenza B tests is always the same as the total number of influenza tests (`flu_tests`). This assumption has been validated on dates xx-xx, when RVDSS explicitly reported numbers of total, flu A, and flu B tests. This field is maintained for convenience.  <br/> **Earliest Date Available:** 2013-08-31         |
| `flu_positive_tests`           | Number of positive influenza laboratory tests. Positive test results for all influenza subtypes are included. <br/> **Earliest Date Available:** 2013-08-31                              |
| `flu_pct_positive`             | Percentage of influenza laboratory tests that are positive. Positive test results for all influenza subtypes are included. <br/> **Earliest Date Available:** 2013-08-31                 |
| `fluah1n1pdm09_positive_tests` | Number of positive influenza A(H1N1)pdm09 laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                 |
| `fluah3_positive_tests`        | Number of positive influenza A(H3N2) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                      |
| `fluauns_positive_tests`       | Number of positive influenza A (unsubtyped) laboratory tests <br/> **Earliest Date Available:** 2016-09-03                                                                               |
| `flua_positive_tests`          | Number of positive influenza A laboratory tests. This is the sum of influenza A(H1N1)pdm09 (`fluah1n1pdm09_positive_tests`), A(H3N2) (`fluah3_positive_tests`), and other (unsubtyped) (`fluauns_positive_tests`) positive tests. <br/> **Earliest Date Available:** 2013-08-31 |
| `flua_pct_positive`            | Percentage of influenza A laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                                                              |
| `flub_positive_tests`          | Number of positive influenza B laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                            |
| `flub_pct_positive`            | Percentage of influenza B laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                                                               |
| `rsv_tests`                    | Number of respiratory syncytial virus (RSV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                               |
| `rsv_positive_tests`           | Number of laboratory tests positive for RSV <br/> **Earliest Date Available:** 2013-08-31                                                                                                |
| `rsv_pct_positive`             | Percentage of RSV laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                                                                       |
| `hpiv_tests`                   | Number of human parainfluenza virus (HPIV) laboratory tests. Tests for all HPIV subtypes are included. <br/> **Earliest Date Available:** 2013-08-31                                                              |
| `hpiv1_positive_tests`         | Number of HPIV laboratory tests positive for HPIV-1 <br/> **Earliest Date Available:** 2013-08-31                                                                                        |
| `hpiv2_positive_tests`         | Number of HPIV laboratory tests positive for HPIV-2 <br/> **Earliest Date Available:** 2013-08-31                                                                                        |
| `hpiv3_positive_tests`         | Number of HPIV laboratory tests positive for HPIV-3 <br/> **Earliest Date Available:** 2013-08-31                                                                                        |
| `hpiv4_positive_tests`         | Number of HPIV laboratory tests positive for HPIV-4 <br/> **Earliest Date Available:** 2013-08-31                                                                                        |
| `hpivother_positive_tests`     | Number of HPIV laboratory tests positive for any other HPIV subtype <br/> **Earliest Date Available:** 2013-08-31                                                                        |
| `hpiv_positive_tests`          | Number of laboratory tests positive for any HPIV subtype. This is the sum of HPIV-1 (`hpiv1_positive_tests`), HPIV-2 (`hpiv2_positive_tests`), HPIV-3 (`hpiv3_positive_tests`), HPIV-4 (`hpiv4_positive_tests`), and other HPIV subtypes (`hpivother_positive_tests`) positive tests. <br/> **Earliest Date Available:** 2013-08-31                                                                                   |
| `hpiv_pct_positive`            | Percentage of HPIV laboratory tests that are positive. Positive test results for all HPIV subtypes are included. <br/> **Earliest Date Available:** 2013-08-31                                                                   |
| `adv_tests`                    | Number of adenovirus (ADV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                                |
| `adv_positive_tests`           | Number of positive ADV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                                    |
| `adv_pct_positive`             | Percentage of ADV laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                                                                       |
| `hmpv_tests`                   | Number of human metapneumovirus (hMPV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                    |
| `hmpv_positive_tests`          | Number of positive hMPV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                                   |
| `hmpv_pct_positive`            | Percentage of hMPV laboratory tests that are positive <br/>**Earliest Date Available:** 2013-08-31                                                                                       |
| `evrv_tests`                   | Number of enterovirus/rhinovirus (EV/RV) laboratory tests. Enterovirus and rhinovirus are both types of enteroviruses and [according to the US CDC](https://www.cdc.gov/nrevss/php/dashboard/index.html), "[m]ost diagnostic assays are not able to distinguish rhinoviruses from enteroviruses and have a combined single target for both viruses". <br/> **Earliest Date Available:** 2013-08-31                     |
| `evrv_positive_tests`          | Number of positive EV/RV laboratory tests <br/>**Earliest Date Available:** 2013-08-31                                                                                                   |
| `evrv_pct_positive`            | Percentage of EV/RV laboratory tests that are positive <br/>**Earliest Date Available:** 2013-08-31                                                                                      |
| `hcov_tests`                   | Number of human coronavirus (HCoV) laboratory tests. <br/> **Earliest Date Available:** 2013-08-31                                                                                       |
| `hcov_positive_tests`          | Number of positive HCoV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                                                                   |
| `hcov_pct_positive`            | Percentage of HCoV laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                                                                      |
| `year`                         | Current year <br/> **Earliest Date Available:** 2023-09-02                                                                                                                               |

## Table of contents

{: .no_toc .text-delta}

1.  TOC {:toc}

## Geography {#geography}

Unlike most other sources in the Delphi Epidata API, this data source reports data for Canada. This source is available for several geographic types, as follows. Specific regions can be requested using the `geo_value` parameter.

### Geo type `province`

One of the 10 provinces or three territories, abbreviated using [standard 2-letter alpha codes](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/enabling-interoperability/gc-enterprise-data-reference-standards/data-reference-standard-canadian-provinces-territories.html).

-   `nl`: Newfoundland and Labrador
-   `pe`: Prince Edward Island
-   `ns`: Nova Scotia
-   `nb`: New Brunswick
-   `qc`: Quebec
-   `on`: Ontario
-   `mb`: Manitoba
-   `sk`: Saskatchewan
-   `ab`: Alberta
-   `bc`: British Columbia
-   `yt`: Yukon
-   `nt`: Northwest Territories
-   `nu`: Nunavut

### Geo type `region`

The provinces and territories are also reported aggregated into six geographic regions:

-   `atlantic`: Newfoundland and Labrador, Prince Edward Island, Nova Scotia, and New Brunswick
-   `prairies`: Manitoba, Saskatchewan, and Alberta
-   `territories`: Nunavut, Northwest Territories, and Yukon
-   `on`: Ontario
-   `qc`: Quebec
-   `bc`: British Columbia

**NOTE**: Ontario, Quebec, and British Columbia are single-province regions, so data for these provinces is the same whether using `geo_type = region` or `geo_type = province`.

### Geo type `nation`

ISO 3166-1 alpha-2 [country codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). The only nation we have data on is Canada, abbreviated to `ca`.

### Geo type `lab`

The laboratories reporting lab tests. Only Ontario, Quebec, and occasionally Saskatchewan report counts for individual lab facilities.

**NOTE**: Over time, some laboratory networks were expanded and the responsible laboratories were renamed:

-   Children's Hospital of Eastern Ontario (CHEO) -\> Eastern Ontario Regional Laboratory Association (EORLA)
-   Sunnybrook Women’s College Health Sciences Centre -\> Shared Hospital Laboratory
-   Toronto Medical Laboratory -\> University Health Network/Mount Sinai Hospital

## Calculation of Percent Positive Lab Tests

For each respiratory virus, the number of lab tests and number of positive lab tests are reported. For convenience, we calculate the percentage of positive tests for a given virus as:

$$\text{Percent Positive Lab Tests} = \frac{\text{Number of Positive Tests}}{\text{Number of Tests}} \times 100$$

Percent positive lab tests ranges from 0-100%. For HPIV, total HPIV positive tests are not always reported, so we manually calculate them by summing up the positive tests for all HPIV subtypes:

$$
\text{HPIV Positive Tests} = \sum\text{HPIV}_\text{subtype}
$$

for subtype = 1,2,3,4 and other

Prior to the end of the 2023-2024 season, total tests and percent positivity were reported, but number of positive tests was not explicitly reported. For convenience, we manually calculated number of positive tests when only percent positive lab tests and number of lab tests were available.

$$\text{Number Positive Lab Tests} = \frac{\text{Percent Positive Lab Tests}}{100} \times \text{Number of Tests}$$

These values are not rounded, so some are not integers.

## Data Versioning {#version}

Epiweeks end on Saturday, and the data is usually updated the following Thursday or Friday.
The dashboard where data is currently published states when it was last updated, so we use that date as the version date.

We only started collecting data from this source in xx 2024, so historical data in our system is derived from archived weekly reports.
To make data prior to that date more useful, we reconstructed the source's version history.
We defined the version date of a particular data issue to be the date the report webpage was modified.
Historically, page-modified dates were generally 5 days after the end of an epiweek.
Occasionally, page-modified dates were larger than that -- sometimes much larger (up to a year).

Our understanding is that weekly reports were not modified after the fact and expect later modified dates to indicate changes in the text on the page rather than the data.
With that in mind, if the page-modified date was more than 14 days after the epiweek being reported, we set the version date to be 5 days after the end of epiweek being reported,
This should only be a consideration for the historic reports, as the new dashboard states when it was last updated.

## Limitations

This data reports the results of laboratory testing of respiratory viruses, which only represents a subset of people who may be sick. People with mild symptoms may be excluded, and there may be a delay between someone developing symptoms and the getting the results of a lab test.

Data comes from labs across Canada, and some provinces only have one reporting lab, with no further information, so there may be bias if it is easier or faster for people in more densely populated areas to have lab tests done than those in rural locations.

## Missingness

The source uses multiple terms used to denote missing data:

-   NC : Not collected
-   NR : Data not reported for current week
-   NA : Not available
-   Not tested

For convenience, we treat all these as NA, but there may be subtle differences.

For epiweeks 5 and 47 of the 2019-2020 season, the reports are empty, so data from these weeks are missing.

## Lag and Backfill

Data is reported around \~5 days after the end of an epiweek. For June-August 2025, the dashboard containing the data was updated every two weeks, so the lag during that period was larger.

The data experiences backfill as counts are finalized in subsequent weeks. The amount and impact of revisions depend on the virus.

Across all indicators, most (99%) observations have less than 3 revisions. `hpiv1_*`,`hpiv2_*`,`hpiv3_*` and `hpiv4_*` indicators have revisions even more rarely.

Across all indicators, the top 10% of observations (unique location-date pairs) with the largest relative spread have had values revised by 25-33% or more. However, 90% of observations with revisions are revised to within 20% of their final value (and stay within that 20% range) 1-3 weeks after the date an observation is being reported for. And 95% of observations with revisions are finalized within 3-4 weeks. So revisions that greatly impact a reported value happen soon after an observation is first reported.

Looking at the revision speed of specific indicators, `sarscov2_*` and `flub_*` indicators are finalized fairly fast (95% finalized after 12 days). `fluah3_positive_tests` and `adv_*` indicators are finalized fairly slowly (95% finalized after 30-40 days).

`flu_pct_positive`, `flua_pct_positive`, `fluah1n1pdm09_positive_tests` and related indicators have larger spread than other indicators. That is, \~70-90% of observations have more than 10% relative spread vs 20-30% in other indicators.

## Source and Licensing {#source-and-licensing}

This source is derived from PHAC's Respiratory Virus Detection Data, originally reported in [weekly reports](https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada.html), and currently reported in a [dynamic dashboard](https://health-infobase.canada.ca/respiratory-virus-surveillance/?source=rvdss).

The data is made available under the [Open Government Licence - Canada](https://open.canada.ca/en/open-government-licence-canada).

## Additional Resources

For a more detailed overview of respiratory surveillance in Canada, see this [page](https://www.canada.ca/en/public-health/services/diseases/flu-influenza/influenza-surveillance/about-fluwatch.html).
