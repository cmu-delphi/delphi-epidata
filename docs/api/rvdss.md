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
-   **License:** **Open Government Licence - Canada**

This data source of respiratory virus detections in Canada is collected by the [Respiratory Virus Detection Surveillance System](https://health-infobase.canada.ca/respiratory-virus-surveillance/?source=rvdss) (RVDSS) and published by the Public Health Agency of Canada (PHAC). Laboratory tests for various respiratory illnesses from various sentinel laboratories across Canada are reported on a weekly basis year-round to the [Centre for Immunization and Respiratory Infectious Diseases (CIRID)](https://www.canada.ca/en/public-health/services/infectious-diseases/centre-immunization-respiratory-infectious-diseases-cirid.html), Public Health Agency of Canada. The data was originally scraped when weekly online reports, but since June 2024, has been reported on a dynamic dashboard.

NOTE: Pandemic COVID-19 is not reported in this data source.

| Signal                         | Description                                                                                                                                 |
|----------------------|-------------------------------------------------|
| `sarscov2_tests`               | Number of SARS-CoV-2 laboratory tests <br/> **Earliest Date Available:** 2022-09-03                                                         |
| `sarscov2_positive_tests`      | Number of Positive SARS-CoV-2 laboratory tests <br/> **Earliest Date Available:** 2022-09-03                                                |
| `sarscov2_pct_positive`        | Percentage of SARS-CoV-2 laboratory tests that are positive <br/> **Earliest Date Available:** 2022-09-03                                   |
| `flu_tests`                    | Number of Influenza laboratory tests (for all subtypes) <br/> **Earliest Date Available:** 2013-08-31                                       |
| `flua_tests`                   | Number of Influenza A laboratory tests (Same as `flu_tests`, just maintained for convenience) <br/> **Earliest Date Available:** 2013-08-31 |
| `flub_tests`                   | Number of Influenza B laboratory tests (Same as `flu_tests`, just maintained for convenience) <br/> **Earliest Date Available:** 2013-08-31 |
| `flu_positive_tests`           | Number of positive Influenza laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                 |
| `flu_pct_positive`             | Percentage of Influenza laboratory tests that are positive (for all subtypes) <br/> **Earliest Date Available:** 2013-08-31                 |
| `fluah1n1pdm09_positive_tests` | Number of positive Influenza A(H1N1)pdm09 laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                    |
| `fluah3_positive_tests`        | Number of positive Influenza A(H3N2) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                         |
| `fluauns_positive_tests`       | Number of positive Influenza A (Unsubtyped)laboratory tests <br/> **Earliest Date Available:** 2016-09-03                                   |
| `flua_positive_tests`          | Number of positive Influenza A laboratory tests (for all subtypes) <br/> **Earliest Date Available:** 2013-08-31                            |
| `flua_pct_positive`            | Percentage of Influenza A laboratory tests that are positive (for all subtypes) <br/> **Earliest Date Available:** 2013-08-31               |
| `flub_positive_tests`          | Number of positive Influenza B laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                               |
| `flub_pct_positive`            | Percentage of Influenza B laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                  |
| `rsv_tests`                    | Number of Respiratory Syncytial Virus (RSV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                  |
| `rsv_positive_tests`           | Number of positive RSV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                       |
| `rsv_pct_positive`             | Percentage of RSV laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                          |
| `hpiv_tests`                   | Number of Human Parainfluenza Virus (HPIV) laboratory tests (for all subtypes)<br/> **Earliest Date Available:** 2013-08-31                 |
| `hpiv1_positive_tests`         | Number of positive HPIV-1 laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                    |
| `hpiv2_positive_tests`         | Number of positive HPIV-2 laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                    |
| `hpiv3_positive_tests`         | Number of positive HPIV-3 laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                    |
| `hpiv4_positive_tests`         | Number of positive HPIV-4 laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                    |
| `hpivother_positive_tests`     | Number of positive other HPIV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                |
| `hpiv_positive_tests`          | Number of positive HPIV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                      |
| `hpiv_pct_positive`            | Percentage of HPIV laboratory tests that are positive (for all subtypes) <br/> **Earliest Date Available:** 2013-08-31                      |
| `adv_tests`                    | Number of Adenovirus (ADV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                   |
| `adv_positive_tests`           | Number of positive ADV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                       |
| `adv_pct_positive`             | Percentage of ADV laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                          |
| `hmpv_tests`                   | Number of Human Metapneumovirus (hMPV)laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                        |
| `hmpv_positive_tests`          | Number of positive hMPV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                      |
| `hmpv_pct_positive`            | Percentage of hMPV laboratory tests that are positive <br/>**Earliest Date Available:** 2013-08-31                                          |
| `evrv_tests`                   | Number of Enterovirus/Rhinovirus (EV/RV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                     |
| `evrv_positive_tests`          | Number of positive EV/RV laboratory tests <br/>**Earliest Date Available:** 2013-08-31                                                      |
| `evrv_pct_positive`            | Percentage of EV/RV laboratory tests that are positive <br/>**Earliest Date Available:** 2013-08-31                                         |
| `hcov_tests`                   | Number of Human Coronavirus (HCoV) laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                           |
| `hcov_positive_tests`          | Number of positive HCoV laboratory tests <br/> **Earliest Date Available:** 2013-08-31                                                      |
| `hcov_pct_positive`            | Percentage of HCoV laboratory tests that are positive <br/> **Earliest Date Available:** 2013-08-31                                         |
| `week`                         | Current epidemiological week number <br/> **Earliest Date Available:** 2023-09-02                                                           |
| `weekorder`                    | Week number in the current season <br/> **Earliest Date Available:** 2023-09-02                                                             |
| `year`                         | Current year <br/> **Earliest Date Available:** 2023-09-02                                                                                  |
| `region`                       | Region the `geo_value` (see [Geography](#geography))<br/> **Earliest Date Available:** 2023-09-02                                           |

## Table of contents

{: .no_toc .text-delta}

1.  TOC {:toc}

## Geography {#geography}

Unlike most other sources in the Delphi Epidata API, this data source is Canadian. The `geo_value` argument specifies which geographic level to get data for, and accepts the following:

**`province`**: One of the 10 provinces or three territories, abbreviated using [internationally approved 2-letter alpha codes](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/enabling-interoperability/gc-enterprise-data-reference-standards/data-reference-standard-canadian-provinces-territories.html)

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

**`lab`:** The laboratories reporting lab tests. As a note, only Ontario, Quebec and occasionally Saskatchewan have counts from dis-aggregated labs.

-   **NOTE**: Over time, some laboratories were expanded and renamed:

    -   CHEO -\> EORLA

    -   Sunnybrook Women’s College HSC -\> Shared Hospital Laboratory

    -   Toronto Medical Laboratory -\> University Health Network/Mount Sinai Hospital

**`region`:** The provinces and territories are also sometimes aggregated into six geographic regions:

-   `atlantic`: Newfoundland and Labrador, Prince Edward Island, Nova Scotia and New Brunswick

-   `prairies`: Manitoba, Saskatchewan and Alberta

-   `territories`: Nunavut, Northwest Territories and Yukon

-   `on`: Ontario

-   `qc`: Quebec

-   `bc`: British Columbia

**Nation:** ISO 3166-1 alpha-2 [country codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). The only nation we have data on is Canada, abbreviated to `ca`

**NOTE**: Some of the regions are just stand alone provinces. In this cases:

-   BC, Ontario and Quebec are provinces, but are also their own regions, so data relating to these provinces with `geo_type = region` and `geo_type = province` are the same.

## Calculation of Percent Positive Lab Tests

For each respiratory virus, the number of lab tests and number of positive lab tests are reported. For convenience, we calculate the percentage of positive tests for a given virus as:

$$\text{Percent Positive Lab Tests} = \frac{\text{Number of Positive Tests}}{\text{Number of Tests}} \times 100$$

Percent positive lab tests ranges from 0-100%. For HPIV, total HPIV positive tests are not always reported, so we manually calculate them by summing up the positive tests for all HPIV subtypes:

$$
\text{HPIV Positive Tests} = \sum\text{HPIV}_\text{subtype}
$$

for subtype = 1,2,3,4 and other

For most of the historic data before the end of the 2023-2024 season, number of positive tests were manually calculated when only percent positive lab tests and number of lab tests were available:

$$\text{Number Positive Lab Tests} = \frac{\text{Percent Positive Lab Tests}}{100} \times \text{Number of Tests}$$

These were not rounded, so there are some decimal values.

## Data Versioning

Epiweeks end on Saturday, and the data is usually updated the following Thursday or Friday. While the data was being reported with weekly reports, the version/issue was the date the webpage was modified. If this date was more than 14 days after the epiweek being reported, we set the version to 5 days after the end of epiweek being reported, as this is usually when the data is updated. This should only be a consideration for the historic reports, as the new dashboard states when it was last updated.

## Limitations

This data reports the results of laboratory testing of respiratory viruses, which only represents a subset of people who may be sick. People with mild symptoms may be excluded, and there may be a delay between someone developing symptoms and the getting the results of a lab test.

Data comes from labs across Canada, and some provinces only have one reporting lab, with no further information, so there may be bias if it is easier/faster for people in more densely populated areas to have lab tests done than those in rural locations.

## Missingness

There are multiple abbreviations/terms used to denote missing data:

-   N.C : Not collected
-   N.R : Data not reported for current week
-   N.A : Not available
-   Not tested

For convenience, we treat all these as NA, but there may be subtle differences.

For epiweeks 5 and 47 of the 2019-2020 season, the reports are empty, so data from these weeks are missing.

## Lag and Backfill

Data is reported around \~5 days after the end of an epiweek, up to and including the epiweek, so there is usually a lag of around 5 days. For June-August 2025, the dashboard containing the data was updated biweekly, so there was additional lag.

The data experiences backfill as counts are finalized in subsequent weeks:

-   Across all indicators, the top 10% observations with the largest relative spread have had values revised by 25-33% or more.

-   `flu_pct_positive`, `flua_pct_positive`, `fluah1n1pdm09_positive_tests` and related indicators have larger spread between updates (\~70-90% of obs have more than 10% relative spread vs 20-30% in other signals).

-   `hpiv1_`,`hpiv2_`,`hpiv3_` and `hpiv4_` indicators rarely have revisions, and across all indicators, most observations have less than 3 revisions (99% of observations).

-   Across all indicators, 90% of observations with revisions are revised to within 20% of their final value (and stay within that 20% range) 1-3 weeks after the time_value the obs is being reported for.

-   95% of observations with revisions are finalized within 3-4 weeks of the time_value.`sarscov2_*` and `flub_*` indicators are finalized fairly fast (95% finalized after 12 days). `fluah3_positive_tests` and `adv_*` indicators are finalized fairly slowly (95% finalized after 30-40 days).

## Source and Licensing

This source is derived from the respiratory virus detection data reported by PHAC, originally reported in [weekly reports](https://www.canada.ca/en/public-health/services/surveillance/respiratory-virus-detections-canada.html), and currently reported in a [dynamic dashboard](https://health-infobase.canada.ca/respiratory-virus-surveillance/?source=rvdss). It has been collected and processed for forecasting convenience.

The data is made available under the [Open Government Licence - Canada](https://open.canada.ca/en/open-government-licence-canada).
