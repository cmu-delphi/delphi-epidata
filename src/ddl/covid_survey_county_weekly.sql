/*
Stores a subset of data from the COVID-19 survey, aggregated by weeks and
counties.

+-------------+------------+------+-----+---------+----------------+
| Field       | Type       | Null | Key | Default | Extra          |
+-------------+------------+------+-----+---------+----------------+
| id          | int(11)    | NO   | PRI | NULL    | auto_increment |
| epiweek     | int(11)    | NO   | MUL | NULL    |                |
| county      | varchar(5) | NO   |     | NULL    |                |
| ili         | double     | NO   |     | NULL    |                |
| ili_stdev   | double     | NO   |     | NULL    |                |
| cli         | double     | NO   |     | NULL    |                |
| cli_stdev   | double     | NO   |     | NULL    |                |
| denominator | double     | NO   |     | NULL    |                |
+-------------+------------+------+-----+---------+----------------+

id:
  unique identifier for each record
epiweek:
  the epidemiological week during which the survey was submitted
county:
  assumed fips 6-4 county code
ili:
  estimated percent of sample experiencing influenza-like illness (ILI)
ili_stdev:
  standard deviation for the ILI estimate
cli:
  estimated percent of sample experiencing codid-19-like illness (CLI)
cli_stdev:
  standard deviation for the CLI estimate
denominator:
  estimated sample size
*/

CREATE TABLE `covid_survey_county_weekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `epiweek` int(11) NOT NULL,
  `county` varchar(5) NOT NULL,
  `ili` double NOT NULL,
  `ili_stdev` double NOT NULL,
  `cli` double NOT NULL,
  `cli_stdev` double NOT NULL,
  `denominator` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`epiweek`, `county`),
  KEY (`county`, `epiweek`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
