# Legacy tables

## state_ili

Unlike most of the other data sources, the state-level ILINet data isn't
updated automatically. The data was obtained around 2015-09-10 from the various
states' websites, linked here: http://www.cdc.gov/flu/weekly/
This data was re-obtained around June 2016, and uploaded 2016-11-14. The
process is lossy, and so the two version don't entirely agree. Because of this,
we now also store a version tag with the data.
The `state_ili` table stores this data:
````
+---------+-------------+------+-----+---------+----------------+
| Field   | Type        | Null | Key | Default | Extra          |
+---------+-------------+------+-----+---------+----------------+
| id      | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek | int(11)     | NO   | MUL | NULL    |                |
| state   | varchar(12) | NO   | MUL | NULL    |                |
| ili     | double      | NO   |     | NULL    |                |
| version | int(11)     | NO   | MUL | NULL    |                |
+---------+-------------+------+-----+---------+----------------+
````
* id: unique identifier for each record
* epiweek: the epiweek during which the data was collected
* state: two-letter U.S. state abbreviation
* ili: percent ILI
* version: 1 => 2015-09; 2 => 2016-06

## fluview_state

Similarly, we received a one-time data dump from the CDC containing true
state-level ILINet data. The data was received on 2016-02-17 and uploaded to
the database on 2016-02-18. This data is not to be distributed outside of
the DELPHI group---and maybe not even within the group---without prior
discussion.
The `fluview_state` table stores this data (similar to the `fluview` table):
````
+---------------+---------+------+-----+---------+----------------+
| Field         | Type    | Null | Key | Default | Extra          |
+---------------+---------+------+-----+---------+----------------+
| id            | int(11) | NO   | PRI | NULL    | auto_increment |
| epiweek       | int(11) | NO   | MUL | NULL    |                |
| state         | char(2) | NO   | MUL | NULL    |                |
| num_ili       | int(11) | YES  |     | NULL    |                |
| num_patients  | int(11) | YES  |     | NULL    |                |
| num_providers | int(11) | YES  |     | NULL    |                |
| ili           | double  | YES  |     | NULL    |                |
| num_age_0     | int(11) | YES  |     | NULL    |                |
| num_age_1     | int(11) | YES  |     | NULL    |                |
| num_age_2     | int(11) | YES  |     | NULL    |                |
| num_age_3     | int(11) | YES  |     | NULL    |                |
| num_age_4     | int(11) | YES  |     | NULL    |                |
| num_age_5     | int(11) | YES  |     | NULL    |                |
+---------------+---------+------+-----+---------+----------------+
````
* id: unique identifier for each record
* epiweek: the epiweek during which the data was collected
* state: two-letter U.S. state abbreviation
* num_ili: the number of ILI cases (numerator)
* num_patients: the total number of patients (denominator)
* num_providers: the number of reporting healthcare providers
* ili: percent ILI
* num_age_0: number of cases in ages 0-4
* num_age_1: number of cases in ages 5-24
* num_age_2: number of cases in ages 25-64
* num_age_3: number of cases in ages 25-49
* num_age_4: number of cases in ages 50-64
* num_age_5: number of cases in ages 65+

## gft

Google stopped producing GFT after 2015w32, so the table is no longer being
updated. For convenience, the data dictionary from the GFT updater is copied
here:
`gft` is the table where the data is stored.
````
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| location | varchar(64) | NO   | MUL | NULL    |                |
| num      | int(11)     | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
````
* id: unique identifier for each record
* epiweek: the epiweek during which the data was collected
* location: where the data was collected (region, state, or city)
* num: the value, roughly corresponding to ILI * 1000

# Legacy changelog

Ongoing changes are visible in the git repository.

* 2017-12-03
  + added source `quidel`
* 2017-02-07
  + added source `flusurv`
* 2016-11-15
  + support `version` for data from `ilinet_state`
* 2016-11-12
  * remove hardcoded secrets
* 2016-04-16
  * function `get_region_states` instead of hardcoded arrays
  * use new cdc data from table `cdc_extract`
* 2016-04-09
  * filter out unreasonable twitter rows
* 2016-04-07
  + added sources `cdc` and `sensors`
* 2016-04-06
  + added source `stateili`
* 2016-04-02
  + census regions for source `twitter`
* 2016-02-18
  + include more fields from `fluview` in `ilinet`
  + include optional `auth` parameter for CDC-provided state-level ILI
  * properly handle (don't cast) SQL `NULL` in `execute_query`
* 2016-01-18
  + added source `meta`
* 2015-12-15
  + added source `nowcast`
* 2015-12-11
  + added source `signals`
* 2015-12-03
  * move passwords to $AUTH variable
  + added source `ght`
2015* -11-19
  * using the new `forecasts` table for source `delphi`
* 2015-10-02
  + source `delphi` uses the `forecasts` table
* 2015-09-15
  + static placeholder for source `delphi`
* 2015-09-14
  + storing basic analytics in table `api_analytics`
  * patched SQL injection vulnerability in `get_nidss_dengue`
  * fixed a collation problem with the `nidss_dengue` table (see https://stackoverflow.com/questions/1008287/illegal-mix-of-collations-mysql-error)
* 2015-09-11
  + added source `ilinet`
* 2015-09-04
  + in `wiki`, added field `value` (1e6 * count / total)
* 2015-08-20
  + added source `nidss_dengue`
  * renamed source `nidss` to `nidss_flu`
* 2015-08-12
  * fixed SQL typo for daily wiki
* 2015-08-11
  + using `wiki_meta` for better performance and total hits
* 2015-08-10
  + added source `nidss`
* 2015-08-04
  + added message for invalid `auth`
* 2015-07-31
  + added `auth` parameter for twitter
* 2015-06-24
  + fully supporting twitter dataset
  + fully supporting wiki dataset
  + several utility methods to reduce duplicated code
  * heavy refactoring, additional documentation
* 2015-06-23
  + query fluview by specific lag
  + finished GFT support
  * rearranged get_fluview parameters
* 2015-06-08
  + basic support for the GFT dataset
* 2015-06-04
  + enabled multiple values and ranges
  + optional sort field
  + more documentation
* 2015-06-01
  * changes to fluview parameter names
  - removed all authentication code (most was commented out already)
* 2014-??-??
  * original version
