USE epidata;
/*
These tables are generally a mirror of what CDC publishes through the
interactive FluView web app at:
https://www.cdc.gov/flu/weekly/fluviewinteractive.htm

Exceptions include:

- `fluview_imputed` contains derived data
- `fluview_state` contains a one-time data-dump directly from CDC

All tables generally contain some subset of the following fields:

- `id`
  unique identifier for each record
- `release_date`
  the date when this record was first published by the CDC
- `issue`
  the epiweek of publication (e.g. issue 201453 includes epiweeks up to and
  including 2014w53, but not 2015w01 or following)
- `epiweek`
  the epiweek during which the data was collected
- `region`
  the name of the location (e.g. 'nat', 'hhs1', 'cen9', 'pa', 'jfk')
- `lag`
  number of weeks between `epiweek` and `issue`

Tables containing data from ILINet generally contain some subset of the
following fields:

- `num_ili`
  the number of ILI cases (numerator)
- `num_patients`
  the total number of patients (denominator)
- `num_providers`
  the number of reporting healthcare providers
- `wili`
  weighted percent ILI
- `ili`
  unweighted percent ILI
- `num_age_0`
  number of cases in ages 0-4
- `num_age_1`
  number of cases in ages 5-24
- `num_age_2`
  number of cases in ages 25-64
- `num_age_3`
  number of cases in ages 25-49
- `num_age_4`
  number of cases in ages 50-64
- `num_age_5`
  number of cases in ages 65+

Tables containing data from WHO/NREVSS generally contain some subset of the
following fields:

- `total_specimens`
- `percent_positive`
- `percent_a`
- `percent_b`
- `total_a`
- `total_a_h1n1`
- `total_a_h3`
- `total_a_h3n2v`
- `total_a_no_sub`
- `total_b`
- `total_b_vic`
- `total_b_yam`

Tables containing data from FluSurv-NET contain the following fields:

- `rate_age_0`
  hospitalization rate for ages 0-4
- `rate_age_1`
  hospitalization rate for ages 5-17
- `rate_age_2`
  hospitalization rate for ages 18-49
- `rate_age_3`
  hospitalization rate for ages 50-64
- `rate_age_4`
  hospitalization rate for ages 65+
- `rate_age_5`
  hospitalization rate for ages 65-74
- `rate_age_6`
  hospitalization rate for ages 75-84
- `rate_age_7`
  hospitalization rate for ages 85+
- `rate_overall`
  overall hospitalization rate
*/

/*
`fluview` stores ILINet data as published by CDC.

Data is public.

+---------------+-------------+------+-----+---------+----------------+
| Field         | Type        | Null | Key | Default | Extra          |
+---------------+-------------+------+-----+---------+----------------+
| id            | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date  | date        | NO   | MUL | NULL    |                |
| issue         | int(11)     | NO   | MUL | NULL    |                |
| epiweek       | int(11)     | NO   | MUL | NULL    |                |
| region        | varchar(12) | NO   | MUL | NULL    |                |
| lag           | int(11)     | NO   | MUL | NULL    |                |
| num_ili       | int(11)     | NO   |     | NULL    |                |
| num_patients  | int(11)     | NO   |     | NULL    |                |
| num_providers | int(11)     | NO   |     | NULL    |                |
| wili          | double      | NO   |     | NULL    |                |
| ili           | double      | NO   |     | NULL    |                |
| num_age_0     | int(11)     | YES  |     | NULL    |                |
| num_age_1     | int(11)     | YES  |     | NULL    |                |
| num_age_2     | int(11)     | YES  |     | NULL    |                |
| num_age_3     | int(11)     | YES  |     | NULL    |                |
| num_age_4     | int(11)     | YES  |     | NULL    |                |
| num_age_5     | int(11)     | YES  |     | NULL    |                |
+---------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `fluview` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `region` varchar(12) NOT NULL,
  `lag` int(11) NOT NULL,
  `num_ili` int(11) NOT NULL,
  `num_patients` int(11) NOT NULL,
  `num_providers` int(11) NOT NULL,
  `wili` double NOT NULL,
  `ili` double NOT NULL,
  `num_age_0` int(11) DEFAULT NULL,
  `num_age_1` int(11) DEFAULT NULL,
  `num_age_2` int(11) DEFAULT NULL,
  `num_age_3` int(11) DEFAULT NULL,
  `num_age_4` int(11) DEFAULT NULL,
  `num_age_5` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`issue`,`epiweek`,`region`),
  KEY `release_date` (`release_date`),
  KEY `issue_2` (`issue`),
  KEY `epiweek` (`epiweek`),
  KEY `region` (`region`),
  KEY `lag` (`lag`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
`fluview_imputed` stores ILINet data which is imputed from data in `fluview`.

This data is private to Delphi.

+---------------+-------------+------+-----+---------+----------------+
| Field         | Type        | Null | Key | Default | Extra          |
+---------------+-------------+------+-----+---------+----------------+
| id            | int(11)     | NO   | PRI | NULL    | auto_increment |
| issue         | int(11)     | NO   | MUL | NULL    |                |
| epiweek       | int(11)     | NO   | MUL | NULL    |                |
| region        | varchar(12) | NO   | MUL | NULL    |                |
| lag           | int(11)     | NO   | MUL | NULL    |                |
| num_ili       | int(11)     | NO   |     | NULL    |                |
| num_patients  | int(11)     | NO   |     | NULL    |                |
| num_providers | int(11)     | NO   |     | NULL    |                |
| ili           | double      | NO   |     | NULL    |                |
+---------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `fluview_imputed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `region` varchar(12) NOT NULL,
  `lag` int(11) NOT NULL,
  `num_ili` int(11) NOT NULL,
  `num_patients` int(11) NOT NULL,
  `num_providers` int(11) NOT NULL,
  `ili` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`issue`,`epiweek`,`region`),
  KEY `issue_2` (`issue`),
  KEY `epiweek` (`epiweek`),
  KEY `region` (`region`),
  KEY `lag` (`lag`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
`fluview_state` contains a one-time data dump from the CDC containing true
state-level ILINet data. The data was received on 2016-02-17 and uploaded to
the database on 2016-02-18.

This data is private to Delphi.

`state` is analogous to `region` in table `fluview`. It is a two-letter state
abbreviation.

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
*/

CREATE TABLE `fluview_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `epiweek` int(11) NOT NULL,
  `state` char(2) NOT NULL,
  `num_ili` int(11) DEFAULT NULL,
  `num_patients` int(11) DEFAULT NULL,
  `num_providers` int(11) DEFAULT NULL,
  `ili` double DEFAULT NULL,
  `num_age_0` int(11) DEFAULT NULL,
  `num_age_1` int(11) DEFAULT NULL,
  `num_age_2` int(11) DEFAULT NULL,
  `num_age_3` int(11) DEFAULT NULL,
  `num_age_4` int(11) DEFAULT NULL,
  `num_age_5` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `epiweek` (`epiweek`,`state`),
  KEY `epiweek_2` (`epiweek`),
  KEY `state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
`fluview_clinical` stores WHO/NREVSS data from clinical labs as published by
CDC.

Data is public.

+------------------+-------------+------+-----+---------+----------------+
| Field            | Type        | Null | Key | Default | Extra          |
+------------------+-------------+------+-----+---------+----------------+
| id               | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date     | date        | NO   | MUL | NULL    |                |
| issue            | int(11)     | NO   | MUL | NULL    |                |
| epiweek          | int(11)     | NO   | MUL | NULL    |                |
| region           | varchar(12) | NO   | MUL | NULL    |                |
| lag              | int(11)     | NO   | MUL | NULL    |                |
| total_specimens  | int(11)     | NO   |     | NULL    |                |
| total_a          | int(11)     | YES  |     | NULL    |                |
| total_b          | int(11)     | YES  |     | NULL    |                |
| percent_positive | double      | YES  |     | NULL    |                |
| percent_a        | double      | YES  |     | NULL    |                |
| percent_b        | double      | YES  |     | NULL    |                |
+------------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `fluview_clinical` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `region` varchar(12) NOT NULL,
  `lag` int(11) NOT NULL,
  `total_specimens` int(11) NOT NULL,
  `total_a` int(11) DEFAULT NULL,
  `total_b` int(11) DEFAULT NULL,
  `percent_positive` double DEFAULT NULL,
  `percent_a` double DEFAULT NULL,
  `percent_b` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `release_date_2` (`release_date`, `epiweek`, `region`),
  KEY `release_date` (`release_date`),
  KEY `issue` (`issue`),
  KEY `epiweek` (`epiweek`),
  KEY `region` (`region`),
  KEY `lag` (`lag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
`fluview_clinical` stores WHO/NREVSS data from public labs as published by CDC.

Data is public.

For state-wise data, public health labs do not report by epiweek, but by
season (e.g. season 2016/17). calculating the lag is not very  meaningful with
this. The epiweek field will be set to  201640 for season 2016/17,
and so on.

+-----------------+-------------+------+-----+---------+----------------+
| Field           | Type        | Null | Key | Default | Extra          |
+-----------------+-------------+------+-----+---------+----------------+
| id              | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date    | date        | NO   | MUL | NULL    |                |
| issue           | int(11)     | NO   | MUL | NULL    |                |
| epiweek         | int(11)     | NO   | MUL | NULL    |                |
| region          | varchar(12) | NO   | MUL | NULL    |                |
| lag             | int(11)     | NO   |     | NULL    |                |
| total_specimens | int(11)     | NO   |     | NULL    |                |
| total_a_h1n1    | int(11)     | YES  |     | NULL    |                |
| total_a_h3      | int(11)     | YES  |     | NULL    |                |
| total_a_h3n2v   | int(11)     | YES  |     | NULL    |                |
| total_a_no_sub  | int(11)     | YES  |     | NULL    |                |
| total_b         | int(11)     | YES  |     | NULL    |                |
| total_b_vic     | int(11)     | YES  |     | NULL    |                |
| total_b_yam     | int(11)     | YES  |     | NULL    |                |
+-----------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `fluview_public` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `region` varchar(12) NOT NULL,
  `lag` int(11) NOT NULL,
  `total_specimens` int(11) NOT NULL,
  `total_a_h1n1` int(11) DEFAULT NULL,
  `total_a_h3` int(11) DEFAULT NULL,
  `total_a_h3n2v` int(11) DEFAULT NULL,
  `total_a_no_sub` int(11) DEFAULT NULL,
  `total_b` int(11) DEFAULT NULL,
  `total_b_vic` int(11) DEFAULT NULL,
  `total_b_yam` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `release_date` (`release_date`),
  KEY `issue` (`issue`),
  KEY `epiweek` (`epiweek`),
  KEY `region` (`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
`flusurv` stores FluSurv-NET data (flu hospitaliation rates) as published by
CDC.

Data is public.

Note that the flusurv age groups are, in general, not the same as the ILINet
(fluview) age groups. However, the following groups are equivalent:

- flusurv age_0 == fluview age_0  (0-4 years)
- flusurv age_3 == fluview age_4  (50-64 years)
- flusurv age_4 == fluview age_5  (65+ years)

`location` is analogous to `region` in fluview data, however it is by
particular "catchment" (e.g. 'network_all', 'CA', 'NY_albany') rather than by
regions and states in general.

+--------------+-------------+------+-----+---------+----------------+
| Field        | Type        | Null | Key | Default | Extra          |
+--------------+-------------+------+-----+---------+----------------+
| id           | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date | date        | NO   | MUL | NULL    |                |
| issue        | int(11)     | NO   | MUL | NULL    |                |
| epiweek      | int(11)     | NO   | MUL | NULL    |                |
| location     | varchar(32) | NO   | MUL | NULL    |                |
| lag          | int(11)     | NO   | MUL | NULL    |                |
| rate_age_0   | double      | YES  |     | NULL    |                |
| rate_age_1   | double      | YES  |     | NULL    |                |
| rate_age_2   | double      | YES  |     | NULL    |                |
| rate_age_3   | double      | YES  |     | NULL    |                |
| rate_age_4   | double      | YES  |     | NULL    |                |
| rate_overall | double      | YES  |     | NULL    |                |
| rate_age_5   | double      | YES  |     | NULL    |                |
| rate_age_6   | double      | YES  |     | NULL    |                |
| rate_age_7   | double      | YES  |     | NULL    |                |
+--------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `flusurv` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `location` varchar(32) NOT NULL,
  `lag` int(11) NOT NULL,
  `rate_age_0` double DEFAULT NULL,
  `rate_age_1` double DEFAULT NULL,
  `rate_age_2` double DEFAULT NULL,
  `rate_age_3` double DEFAULT NULL,
  `rate_age_4` double DEFAULT NULL,
  `rate_overall` double DEFAULT NULL,
  `rate_age_5` double DEFAULT NULL,
  `rate_age_6` double DEFAULT NULL,
  `rate_age_7` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`issue`,`epiweek`,`location`),
  KEY `release_date` (`release_date`),
  KEY `issue_2` (`issue`),
  KEY `epiweek` (`epiweek`),
  KEY `region` (`location`),
  KEY `lag` (`lag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
