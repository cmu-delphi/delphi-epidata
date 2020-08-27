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
* `EndDatetime`: The time of the last activity by the respondent on the survey.
  If they submitted the survey, this is the time it was submitted. If the user
  did not complete the survey, their response may have been recorded
  automatically after a timeout; this is the time of their last activity, not of
  the recording. See the [response files](survey-files.md) documentation for
  details on the automatic recording of responses.
* `weight`: The survey weight calculated by Facebook, for demographically
  adjusting estimates. See the [weights documentation](weights.md) for details
  on how to use these weights.
* `wave`: Integer specifying the survey wave this respondent completed; see
  below for the full list.
* `UserLanguage`: Language the respondent completed the survey in.

Coding details for each survey wave follow.


## Wave 1

Wave 1 was first deployed on April 6, 2020. This was replaced by Wave 2, but
some responses still arrive from respondents who received a link before Wave 2
was deployed.

* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY_2020-04-06.pdf) (PDF)
* [Survey text and
  coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY_2020-04-06.docx) (Word)

**Warning:** Item A2 shows high missingness and strange values in Wave 1,
possibly due to incorrect validation in the Qualtrics survey. Item A2 should not
be used in Wave 1 data until this problem is understood.

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

### Summary of Changes

* Item A1 changed from

    > In the past 24 hours, **have you or anyone in your household** had any of
    > the following:

    to

    > In the past 24 hours, have **you or anyone in your household** experienced
    > any of the following:
* Item A2 changed to specify "fever, along with at least one other symptom in
  the above list" rather than simply "at least one symptom."
* Item A3 changed from

    > What is the ZIP Code of the city or town where you slept last night? [We
    > mean the place where you are currently staying. This may be different from
    > your usual residence.]

    to

    > What is your current ZIP code?
* Item A4, asking about others who are sick in the local community, added.
* Additional page breaks.

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

### Summary of Changes

* Now available in languages besides English, listed above. The language shown
  to the user defaults to the language they prefer on Facebook, if available,
  but a drop-down allows the user to select other languages.
* Consent text now mentions receiving "your language preference" from Facebook,
  to allow Qualtrics to select the appropriate translation automatically.
* Consent question now requires the respondent be located in the U.S.
* Item B2 now includes eye pain as a symptom.
* Item C5 moved to be asked before item C4.

## Wave 4

Wave 4 will be deployed in late August 2020. It will be available in English, as
well as

* *[translations to be completed]*

Draft files [final versions to be posted when available]:

* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_4.pdf)
  (PDF)
* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_4.docx)
  (Word)

### Summary of Changes

Wave 4 is a **major change** to the survey instrument. Some items have been
removed and several new items have been added. Please review the changes
carefully when you use responses from both waves.

Note that this changelog is a draft; as the survey instrument is finalized, this
changelog will be updated to include all final changes.

#### Consent Text

The survey consent text has been altered to more clearly indicate that

> Even if you are healthy, your responses may contribute to a better public
> health understanding of the spread of the coronavirus pandemic and its effects
> on public health and well-being. This may help improve our local and national
> responses to the pandemic and our understanding of how it has affected
> society.

This is broader than the prior text, which suggested the survey was only to
understand "where the coronavirus pandemic is moving", and ensures we obtain
consent for the full range of uses for the survey.

You **may need to advise your IRB** about the new consent language, depending on
your protocol.

#### New Items

* Following item B2, item B2c now asks which reported symptoms are "new or
  unusual" for the respondent. This is intended to distinguish symptoms of
  chronic conditions (such as allergies) from symptoms that may be COVID-related
  (or due to influenza or another condition).
* Item B7 now asks whether the respondent has sought medical care, such as
  visiting a doctor or urgent care clinic. This will allow researchers to
  understand how people seek medical care, and what fraction of people do so at
  any given time.
* Items B8, B10, B10a, B10b, B11, B12, and B12a more comprehensively ask about
  testing, including whether the respondent has *tried* to be tested but could
  not get a test, and why they were tested.
* Item C13 asks about specific activities, such as working or going to a
  restaurant, that the respondent may have done in the past 24 hours. Item C13a
  asks whether the respondent wore a mask while doing them.
* Item C14 asks "In the past 5 days, how often did you wear a mask when in
  public?"
* Item D6 now asks if the respondent is of Hispanic, Latino, or Spanish origin.
  Note that this item **may not be available** in individual response files
  until procedures to prevent reidentification of respondents are finalized.
* Item D7 now asks the respondent's race. Note that this item **may not be
  available** in individual response files until procedures to prevent
  reidentification of respondents are finalized.
* Item D8 asks for the highest level of school the respondent has completed.
* Item D9 asks if the respondent has worked for pay in the past 4 weeks, while
  items Q64 - Q80 ask the respondent to identify their occupation in a form
  based on the [Standard Occupational Classification
  System](https://en.wikipedia.org/wiki/Standard_Occupational_Classification_System).
  (Each respondent will only see two of these items; the first requests a broad
  category, the second a more detailed classification.)
* Item D10 asks if any of the respondent's work for pay in the past 4 weeks was
  outside their home.

#### Changed Items

* Item B2 now includes eye pain and chills as symptoms.
* Item B2b now asks how long the respondent has had one **unusual** symptom, if
  they report having one in item B2c. It no longer asks how long the respondent
  has had **any** reported symptom.
* Item C1 now separates type 1 and type 2 diabetes, coded separately. The coding
  for both is different from the original coding for "diabetes", so they can be
  analyzed separately.
* Item C8 now asks how often the respondent has "felt isolated from others",
  along with the existing items about anxiety and depression.

#### Removed Items

* Item A2b ("How many people are there in your household in total (including
  yourself)?") has been removed, as have items D3, D4, and D5. They have been
  replaced with item A5, which asks for the people in the household broken down
  by age, *including* the respondent.
* Items B3 and Q40, asking the temperature of respondents with fevers, have been
  removed.
* Item B4, asking if the respondent's cough involved mucus, has been removed.
* Item B5 ("Have you been tested for COVID-19 (coronavirus) for your current
  illness?") has been removed. It has been replaced with items B8-B12,
  described above.
* Item B6 is now subsumed by item B7.
* Item C2 ("Have you had a flu shot in the last 12 months?") was not being used
  by research partners and has been removed.
* Item C3 ("In the past 5 days, have you gone to work outside of your home?")
  has been replaced by a combination of items C13 and D9.
* Item C4 is replaced by items Q64, Q68, and Q69.
* Item C5 is replaced by items Q64, Q68, and Q69.
* Item C7 ("To what extent are you intentionally avoiding contact with other
  people?") is removed, replaced by the more specific items C13, C13a, and C14.
* Item Q36 ("How much of a threat would you say the coronavirus outbreak is to
  your household’s finances?") has been removed and replaced with item C15, for
  consistency with the international version of the survey.
* Item D1b ("Are you currently pregnant?") has been removed.
