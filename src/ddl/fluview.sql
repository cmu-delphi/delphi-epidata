/*
Stores ILI data from the CDC.

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

id:
  unique identifier for each record
release_date:
  the date when this record was first published by the CDC
issue:
  the epiweek of publication (e.g. issue 201453 includes epiweeks up to and
  including 2014w53, but not 2015w01 or following)
epiweek:
  the epiweek during which the data was collected
region:
  the name of the location (e.g. 'nat', 'hhs1', 'cen9', 'pa', 'jfk')
lag:
  number of weeks between `epiweek` and `issue`
num_ili:
  the number of ILI cases (numerator)
num_patients:
  the total number of patients (denominator)
num_providers:
  the number of reporting healthcare providers
wili:
  weighted percent ILI
ili:
  unweighted percent ILI
num_age_0:
  number of cases in ages 0-4
num_age_1:
  number of cases in ages 5-24
num_age_2:
  number of cases in ages 25-64
num_age_3:
  number of cases in ages 25-49
num_age_4:
  number of cases in ages 50-64
num_age_5:
  number of cases in ages 65+
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
