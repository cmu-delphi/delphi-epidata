---
title: Response Files
parent: COVID Symptom Survey
nav_order: 3
---

# Response Files
{: .no_toc}

Users with access to the [COVID Symptom Survey](./index.md) individual response
data should have received SFTP credentials for a private server where the data
are stored. To connect to the server, see the [server access documentation](server-access.md).
This documentation describes the survey data available on that server.

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

## Available Data Files

We provide two types of data files, daily and monthly. Users who need the most
up-to-date data should use the daily files, while those who want to conduct
retrospective analyses using many months of data may find the monthly files more
convenient.

### Daily Files

Each day, we write CSV files with names following this pattern:

	cvid_responses_{for}_recordedby_{recorded}.csv.gz

Dates in incremental filenames are of the form `YYYY_mm_dd`. `for` refers to the
day the survey response was started, in the Pacific time zone (UTC -
7). `recorded` refers to the day survey data was retrieved; see the [lag
policy](#lag-policy) for more details. Each file is compressed with gzip, and
the standard `gunzip` command on Linux or Mac can decompress it.

Every day, we write response files for all recent days of data, with today's
`recorded` date. For each `for` date, you need only load the most recent
`recorded` file to obtain all survey responses; the older versions are available
to track any changes in file formats or slight changes from late-arriving
responses, as described in the [lag policy below](#lag-policy).

For data users who use R to load and process data, we provide a [`get_survey_df`
function](survey-utils.R) to read a directory of CSV files (such as those
provided on the SFTP server), select the correct files, and read them into a
single data frame for use.

### Monthly Files

Several days after the end of each month, we produce "rollup" files containing
all survey responses from that month. These are in two forms.

First, the monthly CSV files have filenames in the form

    {YYYY}-{mm}.csv.gz

and contain all valid responses for that month. These are produced from the
daily files, by taking the data with the most recent `recorded` date for each
day of the month. Because these files are large (typically over 300 MB), they
are compressed with gzip; the standard `gunzip` command on macOS or Linux can
decompress them. (macOS can also decompress these files through Finder
automatically; on Windows, free programs like [7-zip](https://www.7-zip.org/)
can decompress gzip files.) Users doing historical analyses of the survey data
should start with these files, since they provide the easiest way to get all the
necessary data, without accidentally including duplicate results.

Second, we produce monthly tarballs containing the daily `.csv.gz` files for
that month, with names in the form

	{YYYY}-{mm}.tar

Similar to the monthly CSV files, they contain only the files with the most
recent `recorded` date for each day. These archives can be unpacked using the
standard `tar` command. The unpacked files are described in [Daily
Files](#daily-files) above.

## Conditions Responses are Recorded

The survey is configured to record responses under two sets of circumstances:

1. The user taking the survey reached the end of the survey, or
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
earlier starting time. If it does, CMU will write a new daily CSV file
containing the response with the earlier starting time (and not the later
response), as [described above](#daily-files). We expect all response files to
stabilize after four days.
