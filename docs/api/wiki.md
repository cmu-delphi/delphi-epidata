---
parent: Inactive Sources (Other)
grand_parent: Data Sources and Signals
title: Wikipedia Access
---

# Wikipedia Access
{: .no_toc}


| Attribute | Details |
| :--- | :--- |
| **Source Name** | `wiki` |
| **Data Source** | [Wikimedia pageviews](https://dumps.wikimedia.org/other/pagecounts-raw/) for health-related Wikipedia articles |
| **Geographic Levels** | Not applicable (article-based) |
| **Temporal Granularity** | Hourly, Daily, and Weekly (Epiweek) |
| **Available Articles** | [54 health-related articles](#available-articles) |
| **Reporting Cadence** | Inactive - No longer updated since 2021w11|
| **Temporal Scope Start** | 2007w50 (December 9th, 2007) |
| **License** | [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/) |


## Overview
{: .no_toc}

This data source measures public interest in health topics by tracking access counts for specific influenza-related articles on English-language Wikipedia. Delphi aggregates these counts from Wikimedia's public pageview dumps, providing a proxy for information-seeking behavior and public awareness of the flu.

General topics not specific to any particular endpoint are discussed in the
[API overview](README.md). Such topics include:
[contributing](README.md#contributing), [citing](README.md#citing), and
[data licensing](README.md#data-licensing).

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Estimation

Counts are extracted directly from Wikimedia's public pageviews dumps.

The available indicators include:
*   **`count`**: The number of pageviews for the specific article in the given language and time period.
*   **`total`**: The total number of pageviews for all articles in the specified language during the same time period.
*   **`value`**: The normalized pageview rate, calculated as `(count / total) * 1,000,000` (views per million).

Counts are aggregated by hour and then summed to daily or weekly totals. No smoothing is applied.

<!-- Source code: src/acquisition/wiki/wiki_extract.py -->

## Limitations

* Information-seeking behaviour does not always correlate perfectly with disease incidence.


# The API

The base URL is: <https://api.delphi.cmu.edu/epidata/wiki/>


## Parameters

### Required

| Parameter | Description | Type |
| --- | --- | --- |
| `articles` | articles | list of [articles](#available-articles) |
| `language` | language (currently `en`, `es`, and `pt` supported) | string |
| `dates` | dates (see [Date Formats](date_formats.html)) | `list` of dates |
| `epiweeks` | epiweeks (see [Date Formats](date_formats.html)) | `list` of epiweeks |

#### Available Articles

Articles are categorized by the disease or condition they are most closely related to. Note that some articles (like "fever" or "nausea") may overlap across categories.

##### Influenza (Flu)
<details markdown="1">
<summary>Click to expand</summary>

| Article Name |
|---|
| amantadine |
| antiviral_drugs |
| avian_influenza |
| canine_influenza |
| cat_flu |
| chills |
| common_cold |
| cough |
| equine_influenza |
| fatigue_(medical) |
| fever |
| flu_season |
| gastroenteritis |
| headache |
| hemagglutinin_(influenza) |
| human_flu |
| influenza |
| influenzalike_illness |
| influenzavirus_a |
| influenzavirus_c |
| influenza_a_virus |
| influenza_a_virus_subtype_h10n7 |
| influenza_a_virus_subtype_h1n1 |
| influenza_a_virus_subtype_h1n2 |
| influenza_a_virus_subtype_h2n2 |
| influenza_a_virus_subtype_h3n2 |
| influenza_a_virus_subtype_h3n8 |
| influenza_a_virus_subtype_h5n1 |
| influenza_a_virus_subtype_h7n2 |
| influenza_a_virus_subtype_h7n3 |
| influenza_a_virus_subtype_h7n7 |
| influenza_a_virus_subtype_h7n9 |
| influenza_a_virus_subtype_h9n2 |
| influenza_b_virus |
| influenza_pandemic |
| influenza_prevention |
| influenza_vaccine |
| malaise |
| myalgia |
| nasal_congestion |
| nausea |
| neuraminidase_inhibitor |
| orthomyxoviridae |
| oseltamivir |
| paracetamol |
| rhinorrhea |
| rimantadine |
| shivering |
| sore_throat |
| swine_influenza |
| viral_neuraminidase |
| viral_pneumonia |
| vomiting |
| zanamivir |

</details>

##### Norovirus (Noro)
<details markdown="1">
<summary>Click to expand</summary>

| Article Name |
|---|
| abdominal_pain |
| caliciviridae |
| dehydration |
| diarrhea |
| fecal–oral_route |
| foodborne_illness |
| gastroenteritis |
| intravenous_therapy |
| leaky_scanning |
| nausea |
| norovirus |
| oral_rehydration_therapy |
| rotavirus |
| shellfish |
| vomiting |

</details>

##### Dengue
<details markdown="1">
<summary>Click to expand</summary>

| Article Name |
|---|
| aedes |
| aedes_aegypti |
| arthralgia |
| blood_transfusion |
| dengue_fever |
| dengue_vaccine |
| dengue_virus |
| diarrhea |
| exanthem |
| fever |
| flavivirus |
| headache |
| hematuria |
| mosquito |
| mosquito-borne_disease |
| myalgia |
| nausea |
| nosebleed |
| paracetamol |
| petechia |
| rhinitis |
| thrombocytopenia |
| vomiting |

</details>



### Optional

| Parameter | Description | Type                   |
|-----------|-------------|------------------------|
| `hours`   | hours       | `list` of hours (0-23) |

{: .note}
> **Notes:**
> - Only one of `dates` and `epiweeks` is required. If both are provided, `epiweeks` is ignored.
> - `dates`, `epiweeks`, and `hours` are `None` by default.
> - `language` is `en` by default.

## Response

| Field               | Description                                                     | Type             |
|---------------------|-----------------------------------------------------------------|------------------|
| `result`            | result code: 1 = success, 2 = too many results, -2 = no results | integer          |
| `epidata`           | list of results                                                 | array of objects |
| `epidata[].article` | Wikipedia article name                                          | string           |
| `epidata[].count`   | article-specific pageview count for the requested period/hours  | integer          |
| `epidata[].total`   | total Wikipedia pageviews for the specified `language` (e.g., all English Wikipedia traffic) over the same period/hours | integer          |
| `epidata[].hour`    | hour (0-23) of access (-1 if not filtering by hour)            | integer          |
| `epidata[].date`    | date (yyyy-MM-dd)                                               | string           |
| `epidata[].epiweek` | epiweek                                                         | integer          |
| `epidata[].value`   | normalized pageview count (pageviews per million total language traffic): `(count / total) * 10^6` | float            |
| `message`           | `success` or error message                                      | string           |

# Example URLs

### Wikipedia Access article "influenza" on 2020w01
<https://api.delphi.cmu.edu/epidata/wiki/?language=en&articles=influenza&epiweeks=202001>

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "count": 6516,
      "total": 663604044,
      "hour": -1,
      "epiweek": 202001,
      "value": 9.81910834
    }
  ],
  "message": "success"
}
```

### Wikipedia Access article "influenza" on date 2020-01-01
<https://api.delphi.cmu.edu/epidata/wiki/?language=en&articles=influenza&dates=20200101>

```json
{
  "result": 1,
  "epidata": [
    {
      "article": "influenza",
      "date": "2020-01-01",
      "count": 676,
      "total": 82359844,
      "hour": -1,
      "value": 8.20788344
    }
  ],
  "message": "success"
}
```

# Code Samples

Libraries are available for [R](https://cmu-delphi.github.io/epidatr/) and [Python](https://cmu-delphi.github.io/epidatpy/).
The following samples show how to import the library and fetch Wikipedia Access data for article "influenza" in English for epiweeks `202001-202010` (10 weeks total) and hours 0 and 12.

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>

  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

Install the package using pip:
```bash
pip install -e "git+https://github.com/cmu-delphi/epidatpy.git#egg=epidatpy"
```

```python
# Import
from epidatpy import CovidcastEpidata, EpiDataContext, EpiRange
# Fetch data
epidata = EpiDataContext()
res = epidata.pub_wiki(articles=['influenza'], time_values=EpiRange(202001, 202010), time_type='week', language='en', hours=[0, 12])
print(res)
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

```R
library(epidatr)
# Fetch data
res <- pub_wiki(articles = "influenza", time_values = epirange(202001, 202010),
                time_type = "week", language = "en", hours = c(0, 12))
print(res)
```
  </div>

</div>

### Legacy Clients

We recommend using the modern client libraries mentioned above. Legacy clients are also available for [Python](https://pypi.org/project/delphi-epidata/), [R](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.R), and [JavaScript](https://github.com/cmu-delphi/delphi-epidata/blob/dev/src/client/delphi_epidata.js).

<div class="code-tabs">
  <div class="tab-header">
    <button class="active" data-tab="python">Python</button>
    <button data-tab="r">R</button>
    <button data-tab="js">JavaScript</button>
  </div>

  <div class="tab-content active" data-tab="python" markdown="1">

Optionally install the package using pip(env):
```bash
pip install delphi-epidata
```

Otherwise, place `delphi_epidata.py` from this repo next to your python script.

```python
# Import
from delphi_epidata import Epidata
# Fetch data
res = Epidata.wiki(['influenza'], Epidata.range(202001, 202010), {'time_type': 'week', 'language': 'en', 'hours': [0, 12]})
print(res['result'], res['message'], len(res['epidata']))
```
  </div>

  <div class="tab-content" data-tab="r" markdown="1">

Place `delphi_epidata.R` from this repo next to your R script.

```R
source("delphi_epidata.R")
# Fetch data
res <- Epidata$wiki(articles = list("influenza"), time_values = Epidata$range(202001, 202010), time_type = "week", options = list(language = "en", hours = list(0, 12)))
print(res$message)
print(length(res$epidata))
```
  </div>

  <div class="tab-content" data-tab="js" markdown="1">


```html
<!-- Imports -->
<script src="delphi_epidata.js"></script>
<!-- Fetch data -->
<script>
  EpidataAsync.wiki('influenza', EpidataAsync.range(202001, 202010), {time_type: 'week', language: 'en', hours: [0, 12]}).then((res) => {
    console.log(res.result, res.message, res.epidata != null ? res.epidata.length : 0);
  });
</script>
```
  </div>

</div>
