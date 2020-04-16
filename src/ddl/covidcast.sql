/*
This table stores various transformed, filtered, and aggregated views of
Delphi's COVID-19 surveillance streams.
*/

/*
`covidcast` stores daily sensor readings at various geographic resolutions.

Data is public.

+-------------+-------------+------+-----+---------+----------------+
| Field       | Type        | Null | Key | Default | Extra          |
+-------------+-------------+------+-----+---------+----------------+
| id          | int(11)     | NO   | PRI | NULL    | auto_increment |
| name        | varchar(32) | NO   | MUL | NULL    |                |
| geo_type    | varchar(12) | NO   |     | NULL    |                |
| date        | date        | NO   |     | NULL    |                |
| geo_id      | varchar(12) | NO   |     | NULL    |                |
| value       | double      | NO   |     | NULL    |                |
| stderr      | double      | YES  |     | NULL    |                |
| sample_size | double      | YES  |     | NULL    |                |
| direction   | int(11)     | YES  |     | NULL    |                |
| prob        | double      | YES  |     | NULL    |                |
+-------------+-------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `name`
  data souce, and subtype if applicable (e.g. fb_survey_cli, fb_survey_ili)
- `geo_type`
  geographic resolution (e.g. county, HRR, MSA, DMA, state)
- `date`
  date on which underlying event happened
- `geo_id`
  a unique code for each location, depending on `geo_type`
  - county: use FIPS code
  - MSA: use core based statistical area (CBSA) code
  - HRR: HRR number
  - DMA: DMA code
  - state: two-letter state abbreviation
- `value`
  value (statistic) derived from the underlying data source
- `stderr` (NULL when not applicable)
  standard error of the statistic with respect to its sampling distribution
- `sample_size` (NULL when not applicable)
  number of "data points" used in computing the statistic
- `direction` (NULL when not applicable)
  trend classifier with possible values:
  - +1: `value` is increasing
  -  0: `value` is steady
  - -1: `value` is decreasing
- `prob` (NULL when not applicable)
  p-value reflecting surprise at the indicated `direction`
*/

CREATE TABLE `covidcast` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `date` date NOT NULL,
  `geo_id` varchar(12) NOT NULL,
  `value` double NOT NULL,
  `stderr` double,
  `sample_size` double,
  `direction` int(11),
  `prob` double,
  PRIMARY KEY (`id`),
  -- for uniqueness, and also fast lookup of all locations on a given date
  UNIQUE KEY (`name`, `geo_type`, `date`, `geo_id`),
  -- for fast lookup of a time-series for a given location
  KEY (`name`, `geo_type`, `geo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
