USE epidata;
/*
This table stores various sensors of Delphi's COVID-19 surveillance streams for nowcasting.
*/

/*
`covidcast_nowcast` stores daily sensor readings at various geographic resolutions.

Data is not intended for public consumption at the time and is undocumented, but the endpoint is public.

+------------------------------+-------------+------+-----+---------+----------------+
| Field                        | Type        | Null | Key | Default | Extra          |
+------------------------------+-------------+------+-----+---------+----------------+
| id                           | int(11)     | NO   | PRI | NULL    | auto_increment |
| source                       | varchar(32) | NO   | MUL | NULL    |                |
| signal                       | varchar(64) | NO   |     | NULL    |                |
| sensor_name                  | varchar(64) | NO   |     | NULL    |                |
| time_type                    | varchar(12) | NO   |     | NULL    |                |
| geo_type                     | varchar(12) | NO   |     | NULL    |                |
| time_value                   | int(11)     | NO   |     | NULL    |                |
| geo_value                    | varchar(12) | NO   |     | NULL    |                |
| value_updated_timestamp      | int(11)     | NO   |     | NULL    |                |
| value                        | double      | NO   |     | NULL    |                |
| issue                        | int(11)     | NO   |     | NULL    |                |
| lag                          | int(11)     | NO   |     | NULL    |                |
+------------------------------+-------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `source`
  name of upstream data souce
- `signal`
  name of signal derived from upstream data
- `sensor_name`
  name of sensor derived from specific source and signal.
- `time_type`
  temporal resolution of the signal (e.g. day, week)
- `geo_type`
  spatial resolution of the signal (e.g. county, HRR, MSA, DMA, state)
- `time_value`
  time unit (e.g. date) over which underlying events happened
- `geo_value`
  a unique code for each location, depending on `geo_type`
  - county: FIPS 6-4 code
  - nation: 2 letter nation code
  - state: two-letter state abbreviation
- `value_updated_timestamp`
  time when primary data (e.g. `value`) was last updated
- `value`
  sensor value derived from underlying indicator
- `issue`
  the time_value of publication
- `lag`
  the number of time_type units between `time_value` and `issue`
*/

CREATE TABLE `covidcast_nowcast` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` varchar(32) NOT NULL,
  `signal` varchar(64) NOT NULL,
  `sensor_name` varchar(64) NOT NULL,
  `time_type` varchar(12) NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `time_value` int(11) NOT NULL,
  `geo_value` varchar(12) NOT NULL,
  -- "primary" values are derived from the upstream data source
  `value_updated_timestamp` int(11) NOT NULL,
  `value` double NOT NULL,
  `issue` int(11) NOT NULL,
  `lag` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  -- for uniqueness, and also fast lookup of all locations on a given date
  UNIQUE KEY (`source`, `signal`, `sensor_name`, `time_type`, `geo_type`, `time_value`, `geo_value`, `issue`),
  -- for fast lookup of a time-series for a given location
  KEY `by_issue` (`source`, `signal`, `sensor_name`, `time_type`, `geo_type`, `geo_value`, `time_value`, `issue`),
  KEY `by_lag` (`source`, `signal`, `sensor_name`, `time_type`, `geo_type`, `geo_value`, `time_value`, `lag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
