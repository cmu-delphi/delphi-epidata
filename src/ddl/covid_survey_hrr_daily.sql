/*
Stores a subset of data from the COVID-19 survey, aggregated by days and
Hospital Referral Regions (HRRs).

+-------------+---------+------+-----+---------+----------------+
| Field       | Type    | Null | Key | Default | Extra          |
+-------------+---------+------+-----+---------+----------------+
| id          | int(11) | NO   | PRI | NULL    | auto_increment |
| date        | date    | NO   | MUL | NULL    |                |
| hrr         | int(11) | NO   |     | NULL    |                |
| ili         | double  | NO   |     | NULL    |                |
| ili_stdev   | double  | NO   |     | NULL    |                |
| cli         | double  | NO   |     | NULL    |                |
| cli_stdev   | double  | NO   |     | NULL    |                |
| denominator | double  | NO   |     | NULL    |                |
+-------------+---------+------+-----+---------+----------------+

id:
  unique identifier for each record
date:
  the date on which the survey was submitted
hrr:
  assumed hospital referral region (HRR) identifier
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

CREATE TABLE `covid_survey_hrr_daily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `hrr` int(11) NOT NULL,
  `ili` double NOT NULL,
  `ili_stdev` double NOT NULL,
  `cli` double NOT NULL,
  `cli_stdev` double NOT NULL,
  `denominator` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`date`, `hrr`),
  KEY (`hrr`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
