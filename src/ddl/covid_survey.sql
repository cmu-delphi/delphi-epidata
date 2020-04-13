/*
These tables store various transformed, filtered, and aggregated views of the
Facebook-linked COVID-19 survey.

All tables contain the following common fields:

- `id`
  unique identifier for each record
- `ili`
  estimated percent of sample experiencing influenza-like illness (ILI)
- `ili_stdev`
  standard deviation for the ILI estimate
- `cli`
  estimated percent of sample experiencing codid-19-like illness (CLI)
- `cli_stdev`
  standard deviation for the CLI estimate
- `denominator`
  estimated sample size

Each table is an aggregation over some temporal and spatial combination of the
follow fields:

- `epiweek`
  the epidemiological week during which the survey was submitted
- `date`:
  the date on which the survey was submitted
- `county`
  assumed fips 6-4 county code
- `hrr`
  assumed hospital referral region (HRR) identifier
- `msa`
  assumed metropolitan statistical area (MSA), identified by core based
  statistical area (CBSA) code
*/

/*
`covid_survey_county_weekly` stores derived data aggregated by weeks and
counties.

Data is public.

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

/*
`covid_survey_hrr_daily` stores derived data aggregated by days and hospital
referral regions (HRRs).

Data is public.

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

/*
`covid_survey_msa_daily` stores derived data aggregated by days and
metropolitan statistical areas (MSAs).

Data is public.

+-------------+---------+------+-----+---------+----------------+
| Field       | Type    | Null | Key | Default | Extra          |
+-------------+---------+------+-----+---------+----------------+
| id          | int(11) | NO   | PRI | NULL    | auto_increment |
| date        | date    | NO   | MUL | NULL    |                |
| msa         | int(11) | NO   | MUL | NULL    |                |
| ili         | double  | NO   |     | NULL    |                |
| ili_stdev   | double  | NO   |     | NULL    |                |
| cli         | double  | NO   |     | NULL    |                |
| cli_stdev   | double  | NO   |     | NULL    |                |
| denominator | double  | NO   |     | NULL    |                |
+-------------+---------+------+-----+---------+----------------+
*/

CREATE TABLE `covid_survey_msa_daily` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `msa` int(11) NOT NULL,
  `ili` double NOT NULL,
  `ili_stdev` double NOT NULL,
  `cli` double NOT NULL,
  `cli_stdev` double NOT NULL,
  `denominator` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`date`, `msa`),
  KEY (`msa`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
