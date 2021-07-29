/*
This table stores various transformed, filtered, and aggregated views of
Delphi's COVID-19 surveillance streams.
*/

/*
`covidcast` stores daily sensor readings at various geographic resolutions.

Data is public.


+------------------------------+-------------+------+-----+---------+----------------+
| Field                        | Type        | Null | Key | Default | Extra          |
+------------------------------+-------------+------+-----+---------+----------------+
| id                           | int(11)     | NO   | PRI | NULL    | auto_increment |
| source                       | varchar(32) | NO   | MUL | NULL    |                |
| signal                       | varchar(64) | NO   |     | NULL    |                |
| time_type                    | varchar(12) | NO   |     | NULL    |                |
| geo_type                     | varchar(12) | NO   |     | NULL    |                |
| time_value                   | int(11)     | NO   |     | NULL    |                |
| geo_value                    | varchar(12) | NO   |     | NULL    |                |
| value_updated_timestamp      | int(11)     | NO   |     | NULL    |                |
| value                        | double      | NO   |     | NULL    |                |
| stderr                       | double      | YES  |     | NULL    |                |
| sample_size                  | double      | YES  |     | NULL    |                |
| direction_updated_timestamp  | int(11)     | NO   |     | NULL    | deprecated     |
| direction                    | int(11)     | YES  |     | NULL    | deprecated     |
| issue                        | int(11)     | NO   |     | NULL    |                |
| lag                          | int(11)     | NO   |     | NULL    |                |
| is_latest_issue              | binary(1)   | NO   |     | NULL    |                |
| is_wip                       | binary(1)   | YES  |     | NULL    |                |
| missing_value                | int(1)      | YES  |     | NULL    |                |
| missing_stderr               | int(1)      | YES  |     | NULL    |                |
| missing_sample_size          | int(1)      | YES  |     | NULL    |                |
+------------------------------+-------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `source`
  name of upstream data souce
- `signal`
  name of signal derived from upstream data
- `time_type`
  temporal resolution of the signal (e.g. day, week)
- `geo_type`
  spatial resolution of the signal (e.g. county, HRR, MSA, DMA, state)
- `time_value`
  time unit (e.g. date) over which underlying events happened
- `geo_value`
  a unique code for each location, depending on `geo_type`
  - county: FIPS 6-4 code
  - MSA: core based statistical area (CBSA) code for metropolitan statistical
    area (MSA)
  - HRR: hospital referral region (HRR) number
  - DMA: designated market area (DMA) code
  - state: two-letter state abbreviation
- `value_updated_timestamp`
  time when primary data (e.g. `value`) was last updated
- `value`
  value (statistic) derived from the underlying data source
- `stderr` (NULL when not applicable)
  standard error of the statistic with respect to its sampling distribution
- `sample_size` (NULL when not applicable)
  number of "data points" used in computing the statistic
- `direction_updated_timestamp`
  (deprecated) 0
- `direction`
  (deprecated) NULL
- `issue`
  the time_value of publication
- `lag`
  the number of time_type units between `time_value` and `issue`
- `is_latest_issue`
  flag which indicates whether or not the row corresponds to the latest issue for its key
- `is_wip`
  flag indicating that the signal is a 'work in progress'.  this should be True iff `signal` has a 'wip_' prefix.
- `missing_value`
  ~ENUM for the reason a `value` was deleted
- `missing_stderr`
  ~ENUM for the reason a `stderr` was deleted
- `missing_sample_size`
  ~ENUM for the reason a `sample_size` was deleted
*/

-- TODO: add WIP functionality to another table or something similar?
CREATE TABLE `data_reference` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `latest_datapoint_id` bigint(20) unsigned DEFAULT NULL, 
  `source` varchar(32) NOT NULL,
  `signal` varchar(64) NOT NULL,
  `time_type` varchar(12) NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `time_value` int(11) NOT NULL,
  `geo_value` varchar(12) NOT NULL,
  -- -----------`is_wip` binary(1) DEFAULT NULL,
  -- -----------`latest_value_updated_timestamp` int(11) NOT NULL,
  PRIMARY KEY(`id`),
  UNIQUE KEY (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`)
  -- -----------KEY `by_issue` (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`),
  -- -----------KEY `by_lag` (`source`, `signal`, `time_type`, `geo_type`, `geo_value`, `time_value`, `lag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `datapoint` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `data_reference_id` bigint(20) unsigned NOT NULL, 
  `asof` int(11) NOT NULL,
  `value_first_updated_timestamp` int(11) NOT NULL,
  -- NOTE: see comments in src/acquisition/covidcast/database.py re: `value_first_updated_timestamp`
  `value_updated_timestamp` int(11) NOT NULL,
  `value` double,
  `stderr` double,
  `sample_size` double,
  -- `stratification_type` int(11) DEFAULT NULL,
  -- `stratification_value` char(11) DEFAULT NULL,
  `lag` int(11) NOT NULL,
  `missing_value` int(1) DEFAULT 0,
  `missing_stderr` int(1) DEFAULT 0,
  `missing_sample_size` int(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY(`data_reference_id`, `asof`),
  FOREIGN KEY (`data_reference_id`) REFERENCES data_reference(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `data_reference` ADD FOREIGN KEY(`latest_datapoint_id`) REFERENCES datapoint(`id`);
-- NOTE: this is here because it completes our circular dependency
-- TODO: if possible, find a way so we don't have to alter the table

-- important index for computing metadata efficiently (dont forget to use a hint in your query!)
-- -----------CREATE INDEX `for_metadata` ON `covidcast` (`source`, `signal`, `is_latest_issue`);

/*
`covidcast_meta_cache` stores a cache of the `covidcast_meta` endpoint
response, e.g. for faster visualization load times.

Data is public.

This table must always contain exactly one row.

+-----------+----------+------+-----+---------+-------+
| Field     | Type     | Null | Key | Default | Extra |
+-----------+----------+------+-----+---------+-------+
| timestamp | int(11)  | NO   | PRI | NULL    |       |
| epidata   | longtext | NO   |     | NULL    |       |
+-----------+----------+------+-----+---------+-------+

- `timestamp`
  unix time in seconds when the cache was updated
- `response`
  JSON string containing a successful API response for `covidcast_meta`
*/

CREATE TABLE `covidcast_meta_cache` (
  `timestamp` int(11) NOT NULL,
  `epidata` LONGTEXT NOT NULL,
  PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
INSERT INTO covidcast_meta_cache VALUES (0, '');
