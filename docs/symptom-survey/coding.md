---
title: Questions and Coding
parent: COVID Symptom Survey
nav_order: 3
---

# Questions and Coding
{: .no_toc}

The symptom surveys have been deployed in several waves. We have tried to ensure
the coding of waves is consistent. This page provides the full survey text and
coding schemes.


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Basic Coding Rules

All choice responses are recorded numerically starting from 1, in displayed
order from left to right and top to bottom. When the respondent is allowed to
select multiple responses, these are shown separated by commas, such as `2,4,6`.
Questions left blank or with invalid responses are recorded in the CSV files as
`NA`.

Timestamps are provided in Pacific time (UTC-7). The following metadata columns
describe each survey response:

* `StartDatetime`: The time the respondent began the survey.
* `EndDatetime`: The time the respondent's responses were recorded. This either
  means the respondent finished the survey or their response was recorded
  because they abandoned the survey; see the [response files](survey-files.md)
  documentation for details.
* `weight`: The survey weight calculated by Facebook, for demographically
  adjusting estimates. See the [weights documentation](weights.md) for details
  on how to use these weights.

Coding details for each survey wave follow.


## Wave 1

Wave 1 was first deployed on April 6, 2020. This was replaced by Wave 2, but
some responses still arrive from respondents who received a link before Wave 2
was deployed.

* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY_2020-04-06.pdf) (PDF)
* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY_2020-04-06.docx) (Word)

## Wave 2

Wave 2 was first deployed on April 15, 2020. This was replaced by Wave 3, but
some responses still arrive from respondents who received a link before Wave 3
was deployed.

* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY__-_US_Expansion.pdf)
  (PDF)
* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY__-_US_Expansion.docx)
  (Word)

## Wave 3

Wave 3 was first deployed on May 21, 2020. It is available in English, as well
as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY-_US_Expansion_-_With_Translations.pdf)
  (PDF)
* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY-_US_Expansion_-_With_Translations.docx)
  (Word)
