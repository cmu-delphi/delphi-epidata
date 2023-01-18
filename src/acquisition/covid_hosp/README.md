# HHS COVID-19 Patient Impact and Hospital Capacity

HHS has four (as of writing) datasets relating to patient impact and hospital
capacity, collectively referred to as "covid_hosp" here. In short, they are:

- [COVID-19 **Reported** Patient Impact and Hospital Capacity by **State Timeseries**](https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-state-timeseries)

    A _daily_ timeseries of ~60 fields for US states, updated ~weekly. This is
    a weekly roll-up of "COVID-19 **Reported** Patient Impact and Hospital
    Capacity by **State**", over all weeks.

    See [acquisition details](state_timeseries/README.md).

- [COVID-19 **Reported** Patient Impact and Hospital Capacity by **State**](https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-state)

    A _daily_ snapshot of ~60 fields for US states, updated ~daily. This is a
    daily snapshot of "COVID-19 **Reported** Patient Impact and Hospital
    Capacity by **State Timeseries**", for the most recently available date.
    Because it's per day, rather than week, it's the most up-to-date source of
    _reported, state-level_ data. However, since the data is preliminary, it is
    subject to greater missingness and larger revisions.

    See [acquisition details](state_daily/README.md).

- [COVID-19 **Estimated** Patient Impact and Hospital Capacity by **State**](https://healthdata.gov/dataset/covid-19-estimated-patient-impact-and-hospital-capacity-state)

    An early _estimate_ of "COVID-19 **Reported** Patient Impact and Hospital
    Capacity by **State**". This dataset currently seems to lack a data
    dictionary.

    We do not yet acquire this data source.

- [COVID-19 **Reported** Patient Impact and Hospital Capacity by **Facility**](https://healthdata.gov/dataset/covid-19-reported-patient-impact-and-hospital-capacity-facility)

    A _weekly_ timeseries of ~90 fields for individual healthcare facilities,
    updated ~weekly. Compared to "COVID-19 **Reported** Patient Impact and
    Hospital Capacity by **State Timeseries**", this dataset has lower temporal
    resolution (weekly vs daily) but greatly increased geographic resolution
    (street address vs state).

    See [acquisition details](facility/README.md).


# common acquisition overview

Last updated: 2022-01-18 (delayed update; significant changes to acquisition
procedure were made in spring 2021 but weren't tracked here)

1. Fetch the dataset's archive information in JSON format.
1. Determine the most recent issue added to the database. Filter the archive
  information to a list of all updates published after the most recent acquired
  issue and before today. If no updates match, then stop here; otherwise
  continue.
1. Download each matching update in CSV format as determined by the archive
  entry's `url` field. Merge all updates for each issue date into a single
  dataset for that issue.
1. In a single transaction, insert the metadata and the dataset into database.

# [wip] automatic schema updater

HHS adds new columns a couple of times a year. Manually adding a handful of
columns to a list of 100+ existing ones (which are of course not in alphabetical
order) and threading through variations in column names and data types for CSV
vs SQL vs Python is a significant and error-prone chore, so we're working on a
way to have the system suggest these code changes automatically.

Desired workflow: Run a command that produces updated copies of the following files:

- `src/ddl/covid_hosp.sql`
- `src/acquisition/covid_hosp/state_timeseries/database.py`
- `src/acquisition/covid_hosp/state_daily/database.py`
- `src/acquisition/covid_hosp/facility/database.py`

... and produces a migration file to add any new columns found:
- `src/ddl/migrations/covid_hosp_vX-vY.sql`

Optional: ... and checks all changes into a new branch and creates a pull request for human review.

Status of this work: Unfinished; needs significant design attention.

Rough flow of the current prototype:
1. Extract information about existing columns from database.py
2. Annotate column listing using information extracted from covid_hosp.sql
3. Compare to column listing provided by HHS and extract hits (columns we already know about) and misses (new columns)
   1. Guess the SQL and Python types for new columns
   1. Shorten the SQL names for new columns if needed
4. Merge misses for tables that collect changes from multiple sources
5. Generate a migration file with merged misses

Still todo:
6. Generate `covid_hosp.sql`
7. Generate `database.py`

Challenge: There are two database tables, but three data sources. Both
state-timeseries and state-daily store their data in the state-timeseries table,
labeling which rows came from which source using the `record_type`
column. Changes to state-timeseries source data must be filed in the shared
state-timeseries DDL and the unshared state-timeseries database.py. Changes to
state-daily source data must be filed in the shared state-timeseries DDL
(ideally having no mismatches with changes to state-timeseries source data) and
in the unshared state-daily database.py. The facilities dataset is similar
enough that we want to share a lot of the code behaviors, but different enough
to make true generalizations awkward and present surprise new corner cases if
you don't test with both datasets.

Challenge: We probably want to avoid renaming existing columns or accidentally
assigning them new types. This means parsing the existing DDL files to extract
the SQL names and types. There are loads of libraries in Python for parsing
DDLs; I found at least 4 of them that don't do everything we
need. `mo_sql_parsing` doesn't do everything we _want_(it can't handle
comments), but it does do all the absolutely-required stuff. For extracting the
Python names and types of existing columns, we could either parse database.py or
just load the class object.

Challenge: New columns in the CSV file often have names that exceed the maximum
allowed column name length in MySQL. We want shortened column names to remain
human-readable. We also want to shorten names consistently: sets of columns that
describe the same data (e.g. the metric and its related coverage, numerator, and
denominator; different age groups of the same metric) should ideally be spelled
the same so that humans trying to diagnose problems in the database or its
contents aren't constantly tripping over small differences in spelling. The
current prototype uses a token Trie for this but that might be overkill?

Challenge: HHS uses its own language to specify data type information, which has
a sloppy mapping to Python and SQL types. The current prototype has a heuristic
for guessing the type information.

Nonchallenge: [A previous prototype](https://github.com/cmu-delphi/delphi-epidata/issues/747#issuecomment-1241255856)
put a lot of effort into generating ASCII tables and other human-readable
descriptions. These should be considered low priority and/or unnecessary. Make
it work first, then make it interpretable.
