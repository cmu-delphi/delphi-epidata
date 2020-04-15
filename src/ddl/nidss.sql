/*
TODO: document
*/

/*
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| location | varchar(32) | NO   | MUL | NULL    |                |
| region   | varchar(12) | NO   | MUL | NULL    |                |
| count    | int(11)     | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `nidss_dengue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `epiweek` int(11) NOT NULL,
  `location` varchar(32) NOT NULL,
  `region` varchar(12) NOT NULL,
  `count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`epiweek`,`location`),
  KEY `epiweek` (`epiweek`),
  KEY `location` (`location`),
  KEY `region` (`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
+--------------+-------------+------+-----+---------+----------------+
| Field        | Type        | Null | Key | Default | Extra          |
+--------------+-------------+------+-----+---------+----------------+
| id           | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date | date        | NO   | MUL | NULL    |                |
| issue        | int(11)     | NO   | MUL | NULL    |                |
| epiweek      | int(11)     | NO   | MUL | NULL    |                |
| region       | varchar(12) | NO   | MUL | NULL    |                |
| lag          | int(11)     | NO   | MUL | NULL    |                |
| visits       | int(11)     | NO   |     | NULL    |                |
| ili          | double      | NO   |     | NULL    |                |
+--------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `nidss_flu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `region` varchar(12) NOT NULL,
  `lag` int(11) NOT NULL,
  `visits` int(11) NOT NULL,
  `ili` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`issue`,`epiweek`,`region`),
  KEY `release_date` (`release_date`),
  KEY `issue_2` (`issue`),
  KEY `epiweek` (`epiweek`),
  KEY `region` (`region`),
  KEY `lag` (`lag`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
