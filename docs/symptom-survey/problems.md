---
title: Problems and Data Errors
parent: COVID Symptom Survey
nav_order: 7
---

# Problems and Data Errors
{: .no_toc}

Given the scale of the COVID Symptom Survey, we occasionally encounter data
errors or survey implementation problems that affect the interpretation of
results. All problems will be logged here.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

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
