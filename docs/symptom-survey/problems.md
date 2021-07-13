---
title: Problems and Data Errors
parent: COVID-19 Trends and Impact Survey
nav_order: 8
---

# Problems and Data Errors
{: .no_toc}

Given the scale of the COVID-19 Trends and Impact Survey (CTIS), we occasionally
encounter data errors or survey implementation problems that affect the
interpretation of results. All problems will be logged here.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Incorrect Coding in Documentation

We found a Qualtrics bug that affects the exported text of the survey (but not
the survey instrument or underlying data). This bug affects questions where
response options are carried forward from the previous question.

For example, item C13 on waves 4-8 asked respondents to select which activities
they did in the previous 24 hours. Since item C13a asked respondents if they wore a 
mask while doing those activities, it was set up to carry forward response options 
from C13 so that the wording and numerical coding of response options matched 
between the two items.

The numerical coding of responses in C13 was not consecutive, but the 
documentation of C13a suggested that responses to it *were* coded consecutively. 
However, in the microdata made available to users with data access, the coding of
C13 and C13a is identical. It is the Qualtrics-exported document giving the coding 
that is in error.

We updated the [coding documentation](coding.md) on June 15, 2021 to correct the
documented coding of all affected items. The discrepancies that were caught and
fixed in the documentation are listed below:

- Items C13 and C13a, waves 4-8 and 10. The "None of the above" response option
  is affected, though this cannot normally be selected in C13a.
- Items B2 and B2c, wave 11. The "Stuffy or runny nose" response option is
  affected. The documentation suggested that it was coded as 20 in B2 and 6 on
  B2c, but it is actually consistently coded as 20 in both items.

## Mistranslation of Distances (May 2021)

In Wave 11, all items were re-translated to ensure consistency of the
translations. The new item H1, on social distancing, is:

> When out in public in the past 7 days, how many people maintained a distance
> of at least 6 feet from others?

In French, it was translated to read as follows:

> Lorsque vous êtes sorti(e) au cours des 7 derniers jours, combien de personnes
> ont maintenu une distance d’au moins 6 mètres entre elles ?

This incorrectly translated 6 feet to 6 meters. On June 7, 2021 at 9:50am
Pacific time, we corrected the text to read:

> Lorsque vous êtes sorti(e) au cours des 7 derniers jours, combien de personnes
> ont maintenu une distance d’au moins 2 mètres entre elles ?

This problem only affected the French translation. The `UserLanguage` column in
the survey data files indicates the translation used by each respondent to
complete the survey.

## Election-Related Sample Size Decreases (Nov 2020)

Sample sizes decreased in the days following the 2020 US presidential election.
During this time period, Facebook prioritized providing users with
election-related information, which led to fewer people seeing invitations to
the survey. Sample sizes returned to their pre-election baselines in mid-to-late
November.

## Missing Item C15 in Data Files (Nov 18, 2020)

In [Wave 4](coding.md), we added item C15, which asks respondents "How worried
are you about your household's finances for the next month?" Unfortunately, our
code that produces the [individual data files](survey-files.md) inadvertently
omitted this item.

We've now corrected this problem and reissued the data files that include
Wave 4. If you have access to the SFTP server containing microdata, you'll find
new response files with names such as

    cvid_responses_2020_10_31_recordedby_2020_11_16.csv.gz

where "recorded by 2020-11-16" means they were issued on November 16th. Older
versions with prior "recordedby" dates were created before this mistake was
corrected.

The monthly data files, with names such as 2020-11.csv.gz, use the reissued data
and are not affected by this problem.

## Unintended Highlighted Answer Choices (Feb 19, 2021)

Some respondents reported that certain multiple-choice questions displayed the
first response option highlighted in red. This occurred when a matrix-table
question is followed by a single-choice question. This problem only affected
respondents completing the survey on mobile devices; after completing the last
item in the matrix table question, Qualtrics automatically moved them to the
single-choice question and highlighted the first answer choice.

We have put in page breaks after the matrix-table questions that have seem to
resolve the issue. However, data collected before the problem was fixed may be
biased by the highlighting of the answer choice.

Listed below are the survey waves and items that were possibly affected:

* Wave 8 from February 8, 2021 – February 19, 2021:
  * Item V9 (How concerned are you that you would experience a side effect from
    a COVID-19 vaccination?)
  * Item C9 (How worried do you feel that you or someone in your immediate
    family might become seriously ill from COVID-19?)
* Wave 7 from January 12, 2021 – January 28, 2021:
  * Item V9 (How concerned are you that you would experience a side effect from
    a COVID-19 vaccination?)
  * Item C9 (How worried do you feel that you or someone in your immediate
    family might become seriously ill from COVID-19?)
* Waves 1, 4, 5, and 6:
  * Item C9 (How worried do you feel that you or someone in your immediate
    family might become seriously ill from COVID-19?)
