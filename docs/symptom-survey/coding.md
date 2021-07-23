---
title: Questions and Coding
parent: COVID-19 Trends and Impact Survey
nav_order: 6
---

# Questions and Coding
{: .no_toc}

The COVID-19 Trends and Impacts Survey (CTIS) has been deployed in several waves.
We have tried to ensure the coding of waves is consistent. This page provides
the full survey text and coding schemes.


## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Basic Coding Rules

All response choices are recorded numerically starting from 1, in displayed
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

The following columns were added beginning when Wave 4 was deployed:

* `wave`: Integer specifying the survey wave this respondent completed; see
  below for the full list.
* `UserLanguage`: Language the respondent completed the survey in.
- `fips`: The *primary* county FIPS code corresponding to the ZIP code selected
  by the respondent. Note that ZIP codes can cross county and even state
  boundaries; if a respondent's ZIP is in multiple counties, the FIPS reported
  in this column corresponds to the county the ZIP overlaps most with. If a ZIP
  is not more than 50% in any one county, or if their reported ZIP code cannot
  be found, `NA` is reported.

Beginning in Wave 11, the `module` column indicates which module the respondent
was randomly assigned to. See the [survey modules and randomization](modules.md)
information for more details.

Coding details for each survey wave follow.

## Privacy Restrictions

To prevent respondents from being identifiable in the response data, responses
with ZIP codes with populations of 100 or fewer have their location set to `NA`.
This affects item A3 in the individual response files. (This change was
implemented with the introduction of Wave 4. Previously, all ZIPs were
reported.)

Invalid ZIP codes are preserved unchanged, and these rows are reported in the
individual response files with their invalid ZIPs.

Additionally, beginning in wave 4, items D6 and D7 ask respondents for race and
ethnicity. These columns are **not** available in the microdata files due to
reidentification concerns. However, contingency tables that aggregate by race
and other demographic variables [are available](contingency-tables.md).

## Comprehensive Codebook

The [codebook](codebook.csv) describes availability of metadata and question
fields by survey version. A row is included for each field available in the
microdata files for a given survey wave.

If a field is available for multiple waves, it is listed separately for each
version. Items that were included in non-contiguous survey waves have entries
only for those waves that they appeared in, with interceding waves not listed.

Values are missing (`NA`) for columns not relevant to a given field. For
example, metadata fields do not correspond to survey items and thus do not
have question text or answer choices defined.

Available columns:

* `wave`: Integer specifying the survey wave that field is available for or item was asked in.
* `variable`: Field name as it appears in the microdata. For most survey items, this corresponds to question name. Each subquestion of a matrix item is listed seperately. For these, `variable` is the question name followed by the subquestion number, e.g. A1_3 for the third subquestion of item A3.
* `replaces`: Question name of previous version of survey item, if any. Different versions of a given question may vary in wording, referenced time frame, or in other ways; refer to item text for specfics.
* `description`: Brief description of the meaning of a field or survey item.
* `question`: Survey item text.
* `matrix_subquestion`: Subquestion text for a matrix item.
* `choices`: JSON-formatted map of answer codes and response choice text.
* `type`: Survey item format; one of "Matrix" (several questions with the same question stem are displayed together with the same answer choices), "Text" (free text entry), "Multiple Choice" (particpant can select only one answer choice), or "Multiselect" (respondent can select one or more answer choices).
* `display_logic`: Conditions a respondent has to satisfy to be shown an item. For example, this can require a specific answer on a single previous item or a set of previous items, or that a previous item was displayed.
* `response_option_randomization`: How answer choices are displayed for a given question. Answer choice order can be fixed ("none"), reversed ("scale reversal", e.g. for Likert scales) or shuffled ("randomized") between respondents.
* `group_of_respondents_item_was_shown_to`: Module-based subset of respondents item was asked of. One of "all" (if item was included in the [Daily Core](modules.md) and asked of all respondents), "Module A", or "Module B".


## Wave 1

Wave 1 was first deployed on April 6, 2020. This was replaced by Wave 2, but
some responses still arrive from respondents who received a link before Wave 2
was deployed.

* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY_2020-04-06.pdf) (PDF)
* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_TODEPLOY_2020-04-06.docx) (Word)

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

### Changed Items

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

### Changed Items

* Now available in languages besides English, listed above. The language shown
  to the user defaults to the language they prefer on Facebook, if available,
  but a drop-down allows the user to select other languages.
* Consent text now mentions receiving "your language preference" from Facebook,
  to allow Qualtrics to select the appropriate translation automatically.
* Consent question now requires the respondent be located in the U.S.
* Item B2 now includes eye pain as a symptom.
* Item C5 moved to be asked before item C4.

## Wave 4

Wave 4 was first deployed September 8, 2020. It is available in English, as well
as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_4.pdf)
  (PDF)
* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_4.docx)
  (Word)

Wave 4 is a **major change** to the survey instrument. Some items have been
removed and several new items have been added. Please review the changes
carefully when you use responses from both waves.

### Consent Text

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

### New Items

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

### Changed Items

* Item B2 now includes eye pain and chills as symptoms.
* Item B2b now asks how long the respondent has had one **unusual** symptom, if
  they report having one in item B2c. It no longer asks how long the respondent
  has had **any** reported symptom.
* Item C1 now separates type 1 and type 2 diabetes, coded separately. The coding
  for both is different from the original coding for "diabetes", so they can be
  analyzed separately.
* Item C8 now asks how often the respondent has "felt isolated from others",
  along with the existing items about anxiety and depression.

### Removed Items

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

## Wave 5

Wave 5 was deployed on November 24, 2020. Deployment was phased: a fraction of
users were invited to take Wave 4, while the majority were invited to Wave 5, so
data users can determine if changes in responses are due to survey revisions or
to population changes at the same time. Wave 5 is available in English, as well
as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_5.pdf)
  (PDF)
* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_5.docx)
  (Word)

Wave 5 contains minor changes to the survey instrument and a few new items.
Please review the changes carefully when you use responses from multiple waves
of this survey.

### Consent Text

The survey consent text has been altered to encourage respondents to answer the
survey, even if they have already taken it before:

> We encourage you to complete the survey each time you are invited, even if you
> have participated before. Completing the survey again will help us understand
> how the situation is changing.

Wave 5 now clearly states that the data may be shared and aggregates publicly when
released:

> The de-identified results of this survey may be used for our future studies or
> shared with other investigators for their research studies. Results published
> by us and other researchers will be in aggregate and will not identify
> individual respondents or their responses.

### New Items

* Item C16 asks respondents to estimate how many people are wearing masks in
  their community.
* Item C7 was previously asked in Waves 1-3; it asks respondents the extent they
  are avoiding other people.
* Item C17 asks whether respondents have received a flu vaccine. The time frame
  and responses are adapted to specify the current seasonal flu vaccine. A more
  general version inquiry about the flu vaccine appeared in Wave 1-3 as item C2.
* Items E1-E3 ask about household children and their education during the
  pandemic. These items appear for respondents who indicate there is a child in
  their household under the age of 18. E1 asks respondents to indicate the
  current grade level(s) the child(ren) in their household. Item E2 asks the
  respondents if the child(ren) are attending in-person classes part time or
  full time. Item E3 asks respondents what measures are applied to prevent the
  spread of COVID-19 when the child(ren) attend in-person classes (e.g.
  mandatory, mask wearing, closed communal areas).
  * **Note:** Soon after survey deployment, we discovered that the translations
    for French, Brazilian Portuguese, and Spanish (not Latin America) translated
    these questions to use terms appropriate for education systems in those
    countries, rather than education in the US. We disabled the question in
    these translations, and are preparing updated translations that use the
    correct terms.

### Changed Items

* Item B2 now includes headaches and changes in sleep as symptoms.
* Item D8 now includes the option of Master’s degree (unfortunately omitted in
  Wave 4) and has examples of professional degree for clarification.

### Removed Items

* There are no items from Wave 4 that were removed in the Wave 5 version of
  this survey.


## Wave 6

Wave 6 was deployed on December 19, 2020. It is available in English, as well as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and coding](waves/CMU Survey Wave 6.pdf) (PDF)
* [Survey text and coding](waves/CMU Survey Wave 6.docx) (Word)

Wave 6 is a minor change to the survey instrument with the addition of a few new
items regarding COVID-19 vaccine intent. We intend to expand the scope of our
questions in the next wave after the beginning of the year. Please review the
changes carefully when you use responses from multiple waves of this survey.

### New Items

* Item V3 asks respondents how likely they would choose to be vaccinated, if
  they were offered a COVID vaccine.
* Item V4 asks respondents if their intent to get a vaccination would change
  based on recommendations from different sources (e.g. friends and family,
  health workers, organizations). **Note:** Between December 19 and December 23,
  2020, non-English translations of this question labeled the answer choices
  inconsistently with the English version. We corrected this on December 23, and
  reissued the affected microdata files to delete responses to V4 by respondents
  seeing an affected translation. The corrected question is labeled V4a in the
  Qualtrics survey, but appears in the microdata files as V4. Because we
  reissued the affected data, you should not need to make any changes to your
  analysis.
* **Note:** Items V1 and V2 are shown in the Qualtrics files. These ask the
  respondent if they have received a COVID vaccination. However, due to
  reidentification concerns, these items were **disabled** in the display logic,
  and were not displayed to or asked of respondents. On January 6, 2021, item V1
  was enabled, and V3 and V4 were made conditional on respondents not answering
  "yes" to V1. Item V2 remains disabled in the display logic.

## Wave 7

Wave 7 was deployed on January 12, 2021. It is available in English, as well as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_7.pdf) (PDF)
* [Survey text and coding](waves/Survey_of_COVID-Like_Illness_-_Wave_7.docx) (Word)

Wave 7 includes minor modifications to the existing questions regarding COVID -19
vaccination. We intend to expand the scope of our questions in the next wave at
the end of January 2021. Please review the changes carefully when you use
responses from multiple waves of this survey.

### Changed Items

* Slight changes to the wording of questions V1, V2, V3, and V4.
* Item V2 was included in Wave 6 but not shown to respondents. We have enabled
  item V2 for Wave 7.

### New Items

* Item V9 asks if respondents are concerned about a side effect from the
  COVID-19 vaccination. We ask it of all respondents, regardless of whether they
  have already received a vaccination.

### Notes

* This wave configures numeric answer items to require answers to be ≥0. We did this
  via JavaScript by setting the `min = "0"` attribute on the input box.
  While this should prevent respondents from accidentally entering negative
  numbers, those who deliberately want to enter negative numbers can bypass the
  restriction.

## Wave 8

Wave 8 was deployed on February 8, 2021. It is available in English, as well as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and coding](waves/CMU Survey Wave 8.pdf) (PDF)
* [Survey text and coding](waves/CMU Survey Wave 8.docx) (Word)

Wave 8 expands the scope of the survey items about COVID-19 vaccinations. These
new items were meant to capture reasons for vaccine hesitancy among respondents.

### Changed Items

* Answer options for items C1, on chronic medical conditions, have been revised
  and expanded.
* Answer options for the occupation questions, including Q64, Q68, Q69, and Q71,
  were revised and expanded for clarity. Please review the changes carefully
  when you use responses from multiple waves of this survey, since they may
  shift which occupations respondents choose.
* C14a is a revision of item C14, changed from "the past 5 days" to "the past
  7 days" to be consistent with other items on CTIS.
  C14a replaces C14.
* C17a is a revision of item C17, which asked respondents if they have had a
  flu vaccination since June 2020. C17a changed the date to July 1, 2020 and
  simplified the wording.
* In item V4, the "local health workers" category was changed to read "Doctors
  and other health professionals you go to for medical care".

### New Items

* Item V2a ask respondents that have received a COVID-19 vaccine and indicated
  that they have not had 2 doses of the vaccine whether they intend to get the
  required doses.
* Items V5a-V5d and V6 were added to capture reasons for respondents not
  wanting to get a COVID-19 vaccine. The questions are displayed based on the
  respondents' answers to V2a and V3.
* Item D1b was previously removed in wave 4 and asks respondents that identify
  as not male if they are currently pregnant.
* Item D11 ask respondents if they smoke cigarettes.

## Wave 9

Wave 9 was skipped to synchronize our numbering with the international survey
administered by the University of Maryland.

## Wave 10

Wave 10 was deployed on March 2, 2021. For the following 7 days, 15% of
respondents (selected at random) continued to receive Wave 8, allowing for
comparisons of responses between the two waves. Wave 10 is available in English,
as well as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:
* [Survey text and coding](waves/CMU Survey Wave 10.pdf) (PDF)
* [Survey text and coding](waves/CMU Survey Wave 10.docx) (Word)

Wave 10 further expands the scope of survey items about COVID-19 vaccination.
These new items were meant to capture reasons for vaccine hesistancy among
respondents and gauge access. Other items were revised or replaced. Please
review the changes carefully when you use responses from multiple waves of this
survey.

### New Items

* Item V11 ask respondents if they have an appointment to receive a COVID-19
  vaccine.
* Item V12 ask respondents if they have tried to get an appointment to receive a
  COVID-19 vaccine.
* Item V13 ask respondents how informed they feel about how they will be able to
  get a COVID-19 vaccine.
* Item V14 asks respondent when they think they will be able to get a COVID-19
  vaccine.

### Changed Items

* Item A1 now includes description of fever in Celsius as well as Fahrenheit.
* Item A5 was changed to say "from 18 to 64 years old" instead of "between 18
  and 64 years old".
* The instructions following the question text in items B2 and D7 was changed to
  be consistent with all other multiple response questions and reads "Please
  select all that apply."
* Item B10a was changed to remind the respondent "You answered that you have
  been tested for coronavirus (COVID-19) in the past 14 days."
* Items B10b, C13a, C13b, was changed to now state “in the past 14 days”, versus
  the previous version that stated “in last 14 days”.
* Item B10b response options were changed to provide more specificity. Blood
  donation was added to the option “I was tested while receiving other medical
  care, such as surgery” and a “None of the above” response option was added to
  be consistent with other questions.
* Item V2a was changed to say "recommended doses"; previous versions said
  "required doses" (V2).
* Items V5a-V5d question wording was changed to better match the question stem
  (V3). For example, if respondents selected for Item V3 (“If a vaccine to
  prevent COVID-19 were offered to you today, would you choose to get
  vaccinated?”) response option 2 (“Yes, probably”). The following question
  would be V5a (“Which of the following, is any, are reasons that you only
  probably would choose to get the COVID-19 vaccine?”).
* Item V9 was made conditional on respondents not answering "yes" to V1.
* Item C13 was replaced with item C13b, which asks specifically whether the
  activities occurred indoors. Item C13a was similarly replaced with item C13c
  to reflect mask use during those indoor activities.
* Items C6 and C8 were changed to refer to the past 7 days, rather than the past
  5 days, to be consistent with other items on the survey. They were renamed to
  C6a and C8a to reflect this change.
* Typos were fixed in Q67 and Q78.

### Removed Items

* Item B2b (“For how many days have you had at least one new or unusual
  symptom?”) was removed.
* Item C11 (“In the past 24 hours, have you had direct contact with anyone who
  recently tested positive for COVID-19 (coronavirus)?”), and the follow-up
  question, item C12 (“Was this person a member of your household?”), were
  removed.
* Item A3b (“In which state are you currently staying?”) was removed.
  Respondents are asked their ZIP code in item A3, and while some ZIP codes
  cross state lines, we judged the duplication was not necessary.

## Wave 11

Wave 11 was deployed on May 20, 2021. For the following 14 days, 15% of
respondents (selected at random) continued to receive Wave 10, allowing for
comparisons of responses between the two waves. It is available in English, as
well as

* Simplified Chinese
* English (UK)
* Spanish (Latin America)
* Spanish
* French
* Brazilian Portuguese
* Vietnamese

Files:

* [Survey text and coding](waves/CMU Survey Wave 11.pdf) (PDF)
* [Survey text and coding](waves/CMU Survey Wave 11.docx) (Word)

Wave 11 is a major revision of the survey instrument. There are several new
items expanding the scope of COVID-19 vaccines, beliefs, knowledge, and norms;
major revisions to some of the existing items; and several minor revisions that
consists of grammar and style changes for consistency. Please review the changes
carefully when you use responses from multiple waves of this survey.

In this wave, we introduced a module structure to the survey. All respondents
see "daily core" items, and are then randomly selected to receive either
questions in Module A or Module B. Half of respondents will see each module. See
the [survey modules and randomization documentation](modules.md) for details.

### New Items

#### Daily Core

* Item B2b was previously removed in Wave 8 and has been reinstated. It asks
  respondents how many days they have had new and unusual symptoms.
* Item B13 asks respondents "As far as you know, have you ever had coronavirus
  (COVID-19)?"
* Items V15a and V15b ask respondents the barriers they experience to getting
  the COVID-19 vaccine.
* Item V16 asks respondents when they will try to get a COVID-19 vaccine.
* Item D12 asks respondents what language they most often speak at home.

#### Module A

Module A includes items on beliefs, norms, and knowledge & information.

Belief items:

* Item G1 asks respondents how much they worry about catching COVID-19.
* Item G2 asks respondents how effective social distancing is for preventing the
  spread of COVID-19.
* Item G3 asks respondents how effective wearing a face mask is for preventing
  the spread of COVID-19.

Norms items:

* Item H1 asks respondents when they were in public in the past 7 days, how many
  people maintained at least 6 feet from others. *Note:* The French translation
  of this item was initially incorrect. See the [error log](problems.md#mistranslation-of-distances-may-2021)
  for details on the fix.
* Item H2 asks respondents when they were in public in the past 7 days, how many
  people wore face masks.
* Item H3 asks respondents thinking about their friends and family, how many
  have gotten a COVID-19 vaccine.

Knowledge & information items:

* Item I1 asks respondents whether they think the statement “Getting the
  COVID-19 vaccine means that you can stop wearing a mask around people outside
  your household” is true or false.
* Item I2 asks respondents whether they think the statement “Children cannot get
  COVID-19” is true or false.
* Item I3 asks respondents whether they think the statement “COVID-19 was
  deliberately created by a small group of people who secretly manipulate world
  events” is true or false.
* Item I4 asks respondents whether they think the statement “COVID-19 pandemic
  is being exploited” is true or false.
* Item I7 asks respondents to indicate what COVID-19 topics they would like more
  information about.
* Item I5 asks respondents in the past 7 days, from which sources did they
  receive news and information about COVID-19.
* Item I6 asks respondents to indicate how much they trust the sources to
  provide them with accurate news and information about COVID-19.

#### Module B

Module B includes well-being, healthcare, and parenting items.

Well-being:

* Item C18a and C18b are major revisions of a previous item C8a. To improve user
  experience on mobile devices, the matrix format was taken out and the first
  two sub-questions were reformatted into individual Likert scale questions.
  * Item C18a asks respondents in the past 7 days, how often they felt nervous,
    anxious or on edge.
  * Item C18b asks respondents in the past 7 days, how often they have felt
    depressed.

Healthcare:

* Item K1 asks respondents in the past year if they have delayed or not sought
  medical care because of cost.
* Item K2 asks respondents how much they agree or disagree with the statement,
  “People of my race are treated fairly in a healthcare setting.”

Parenting:

* Item E4 ask respondents, “Will you choose to get a COVID-19 vaccine for your
  child or children when they are eligible?”

### Changed Items

Major revisions include significant wording changes, display logic changes, and
changes to which respondents are asked the items, or any changes that are
anticipated to change the respondent’s answer to the question. For user ease,
the variable name will be changed (e.g. X1→X1a) if a major revision occurs, to
distinguish the version of the variable from the previous wave and the revised
variable in the current wave.

* Item B10c asks respondents “Did your most recent test find that you have
  COVID-19?” and replaces item B10a “You answered that you have been tested for
  coronavirus (COVID-19) in the past 14 days. Did this test find that you have
  coronavirus (COVID-19)?” from the previous wave.
* Item V11a “Do you have an appointment to receive a COVID-19 vaccine?” is now
  asked of all respondents that did not select “yes” to item V1 “Have you had a
  COVID-19 vaccination?”
  * In the previous wave, item V11 “Do you have an appointment to receive a
    COVID-19 vaccine?” was asked of respondents who reported “Yes, definitely”
    or “Yes, probably” to item V3 “If a vaccine to prevent COVID-19 were offered
    to you today, would you choose to get vaccinated?”
* Item V3a “If a vaccine to prevent COVID-19 were offered to you today, would
  you choose to get vaccinated?” is now asked of all respondents that did not
  select “yes” to item V1 “Have you had a COVID-19 vaccination?” and did not
  select “yes” to item V11a “Do you have an appointment to receive a COVID-19
  vaccine?”
  * In the previous wave, item V3 “If a vaccine to prevent COVID-19 were offered
    to you today, would you choose to get vaccinated?” was asked of all
    respondents that did not select “yes” to item V1 “Have you had a COVID-19
    vaccination?”
* Item V12a asks respondents “Have you tried to a get a COVID-19 vaccine?” and
  replaces item V12 “Have you tried to get an appointment to receive a COVID-19
  vaccine?” from the previous wave. This item is asked of respondents who did
  not select “yes” to item V1 “Have you had a COVID-19 vaccination?” and did not
  select “yes” to item V11a “Do you have an appointment to receive a COVID-19
  vaccine?” and did not select “No, definitely not” to item V3a “If a vaccine to
  prevent COVID-19 were offered to you today, would you choose to get
  vaccinated?”
  * In the previous wave, item V12 “Have you tried to get an appointment to
    receive a COVID-19 vaccine?” was asked of respondents who reported “Yes,
    definitely” or “Yes, probably” to item V3 “If a vaccine to prevent COVID-19
    were offered to you today, would you choose to get vaccinated?” and those
    respondents that did not select “yes” to item V11a “Do you have an
    appointment to receive a COVID-19 vaccine?”
* Item C7a ask respondent “In the past 7 days, how often did you intentionally
  avoid contact with other people?” and replaces item C7 “To what extent are you
  intentionally avoiding contact with other people?” from the previous wave. In
  version, this item also has a different response scale.

Minor revisions include changes made to formatting, grammar, addition and/or
removal of response options. These changes have been classified as minor as they
are not anticipated to change the respondent’s answer.

* Slight format (i.e. removing bolding) and wording changes (i.e. coronavirus
  was changed to COVID-19) occurred for items: A2, A4, B10, B10b, B12, B12a,
  V5a-c, V6, C6, D10, and Q64 – Q80 (occupation questions).
* Items B2 and B2c response options: “nasal congestion”, “runny nose”, “eye
  pain”, and “changes in sleep” were removed. The response option “stuffy or
  runny nose” was added and coded to be a new, distinct response option.
* Item B10b response options: “I attended a large outdoor event or gathering”
  and “I was in a crowded indoor environment” were removed. The response option
  “It was required for domestic or international travel” was added.
* Item B12a response option, “I am worried about bad things happening to me or
  my family (including discrimination, government policies, or social stigma)”
  was removed. The response option “I am worried about being exposed to COVID-19
  at the testing location” was added.
* For items V5a-c, response options: “I am concerned about having an allergic
  reaction to a COVID-19 vaccine”, “My doctor has not recommended it”, “I
  don’t trust COVID-19 vaccines”, “I have a health condition and am concerned
  about the safety of the vaccine for people with my condition”, and “I am
  currently/planning to be pregnant and/or breastfeeding and do not want to get
  vaccinated at this time” were removed.
* Item C13c response option “none of the above” was added to allow respondents
  who engaged in activities (C13b) to report if they did not wear a mask during
  any of those activities.
* Item C1 response option “auto immune disorder such as rheumatoid arthritis or
  Crohn’s disease” was removed.

### Removed Items

* Item B7 (“Have you sought medical care for your recent unusual symptoms?”) has
  been removed.
* Item B8 (“Have you ever been tested for coronavirus (COVID-19)?”) has been
  removed.
* Item B11 (“Have you ever tested positive for coronavirus (COVID-19)?” has been
  removed.
* Item B12 (“Have you wanted to be tested for coronavirus (COVID-19) at any time
  in the last 14 days?”) has been removed.
* Item B12a (“Do any of the following reasons describe why you haven’t been
  tested for coronavirus (COVID-19) in the last 14 days?”) has been removed.
* Item V2a (“Did you receive (or do you plan to receive) all required doses?”)
  has been removed.
* Item V5d (“Which of the following, is any, are reasons that you don’t plan to
  receive all recommended doses of a COVID-19 vaccine?”) has been removed.
* Item V13 (“How informed do you feel about how you will be able to get a
  COVID-19 vaccine?”) was removed.
* Item V14 (“When do you think you will be able to get a COVID-19 vaccine?”) was
  removed.
* Item V4a (“Would you be more or less likely to get a COVID-19 vaccination if
  it were recommended to you by each of the following: ”) was removed.
* Item C8a, subitem 3 (“In the past 7 days, how often have you felt isolated
  from others?”) was removed. Subitems 1 and 2 were reformatted to individual
  Likert scale questions, see items C18a and C18b under new items.
* Item C10 (“In the past 24 hours, with how many people have you had direct
  contact, outside of your household?”) was removed.
* Item C9 (“How worried do you feel that you or someone in your immediate family
  might become seriously ill from CVOID-19?”) was removed.
* Item C17a (“Have you had a seasonal flu vaccination since July 1, 2020?”) was
  removed.

### Notes

* The following survey items were rearranged for better survey flow and/or
  allocated to specific modules:
  * Daily core: A3, V11a, C6a, C14a, and D8
  * Module B: C15, C1, D11, and D1b
* For survey items with response options in Likert scales or multiple answers,
  random scale reversal and randomization of response options will be set where
  applicable. Randomization of response options was added to B10b starting with
  Wave 11.
