---
title: Response Files
parent: COVID Symptom Survey
nav_order: 1
---

# Response Files
{: .no_toc}

Users with access to the [COVID symptom survey](./index.md) individual response data
should have received SFTP credentials for a private server where the data are
stored. This documentation describes the survey data available on that server.

You must sign a Data Use Agreement with Facebook and with CMU to gain
access to the individual survey responses. If you have not done so, aggregate data is available
[through the COVIDcast API](../api/covidcast-signals/fb-survey.md).

Important updates for data users, including corrections to data or updates on
data processing delays, are posted as `OUTAGES.txt` in the SFTP server directory
where the data is hosted.

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

## Naming Conventions

All dates in filenames are of the form `YYYY_mm_dd`.

Cumulative files:

	cvid_responses_{from}_-_{to}.csv.gz

Incremental files:

	cvid_responses_{for}_recordedby_{recorded}.csv

`from`, `to`, and `for` refer to the day the survey response was started, in the
Pacific time zone (UTC - 7). `recorded` refers to the day survey data was
retrieved; see the [lag policy](#lag-policy) for more details.

Every day, we write response files for *all* days of data, with today's
`recorded` date. You need only load the most recent set of `recorded` files to
obtain all survey responses; the older versions are available to track any
changes in file formats or slight changes from late-arriving responses, as
described in the lag policy.

## Conditions Responses are Recorded

The survey was configured to record responses under two sets of circumstances:

1. The user taking the survey clicked submit, or
2. The user taking the survey left the survey unattended for 4 hours.

An abandoned survey as in (2) is automatically closed and recorded, and the user
is not permitted to reopen it.

Responses qualify for inclusion in these files if they meet the following conditions:
* answered "yes" to age consent
* answered a minimum of 2 additional questions, where to “answer” a numeric
  open-ended question (A2, A2b, B2b, Q40, C10_1_1, C10_2_1, C10_3_1, C10_4_1,
  D3, D4, D5) means to provide any number (floats okay) and to “answer” a radio
  button question is to provide a selection

We do not require the user to have completed the survey, or to have seen all
pages of the survey.

## Collisions

One thing we haven't been able to fully fix is the problem of people forwarding
the survey link to their friends. Due to constraints on the implementation of
the survey, we are not able to determine whether a survey response tagged with a
particular unique identifier was submitted by the user Facebook originally
associated with that identifier, or by some other person. A small number of
unique identifiers (~20/day) wind up having more than one survey response
(sometimes as many as 80) associated with them.

This is a problem because survey links contain a unique identifier that is
provided to Facebook to calculate the [survey weights](weights.md); if multiple
users complete a survey, the weights will only correspond to the user who
initially clicked the link on Facebook, not any other people who may have
received the link.

The best way we have found to address this issue is to take the response with
the *earliest* start time, and remove all other responses. This sometimes
interacts with survey lag (see section below) to require us to swap out small
numbers of survey responses from past days with a response that was started
earlier, but recorded later. All updates are reflected in the Last Modified date
tracked by the sftp server.

## Lag Policy

We do not retrieve survey responses until they have been recorded. In a small
number of cases, a survey is not recorded on the same day it was started.
However, weights are only produced for identifiers with at least one recorded
response by 4:00AM the following morning. This captures the vast majority of
respondents. In the first 1.5 million survey responses, only 45 responses were
excluded using these criteria. Among those excluded, the maximum open time
observed was four days.

Once a weight has been generated for a unique identifier, CMU continues to
retrieve survey responses for that identifier in case one comes in with an
earlier starting time. If it does, CMU will replace the individual response data
in the appropriate file with the response that was started earlier. We expect
all response files to stabilize after four days.
