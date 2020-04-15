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
| raw         | double      | NO   |     | NULL    |                |
| scaled      | double      | NO   |     | NULL    |                |
| direction   | int(11)     | NO   |     | NULL    |                |
| sample_size | double      | NO   |     | NULL    |                |
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
- `raw`
  raw view of the data (e.g. contrast with `scaled`)
- `scaled`
  view of the data which is centered and scaled relative to "normal" (mean
  is zero, standard deviation is one)
- `direction`
  trend classifier:
  - +1 means trend is increasing
  - 0 means trend is steady, or not determined
  - -1 means trend is decreasing
- `sample_size`
  number of "data points" used to produce the value in `raw`, or `NULL` if not
  known or applicable
*/

CREATE TABLE `covidcast` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `date` date NOT NULL,
  `geo_id` varchar(12) NOT NULL,
  `raw` double,
  `scaled` double,
  `direction` int(11),
  `sample_size` double,
  `p_up` double,
  `p_down` double,
  PRIMARY KEY (`id`),
  -- for uniqueness, and also fast lookup of all locations on a given date
  UNIQUE KEY (`name`, `geo_type`, `date`, `geo_id`),
  -- for fast lookup of a time-series for a given location
  KEY (`name`, `geo_type`, `geo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
