USE epidata;
/*
TODO: document
*/

/*
+-------+--------------+------+-----+---------+----------------+
| Field | Type         | Null | Key | Default | Extra          |
+-------+--------------+------+-----+---------+----------------+
| id    | int(11)      | NO   | PRI | NULL    | auto_increment |
| date  | date         | NO   | MUL | NULL    |                |
| page  | varchar(128) | NO   | MUL | NULL    |                |
| state | char(2)      | NO   | MUL | NULL    |                |
| num   | int(11)      | NO   |     | NULL    |                |
+-------+--------------+------+-----+---------+----------------+
*/

CREATE TABLE `cdc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `page` varchar(128) NOT NULL,
  `state` char(2) NOT NULL,
  `num` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`page`,`state`),
  KEY `date_2` (`date`),
  KEY `page` (`page`),
  KEY `state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
+---------+---------+------+-----+---------+----------------+
| Field   | Type    | Null | Key | Default | Extra          |
+---------+---------+------+-----+---------+----------------+
| id      | int(11) | NO   | PRI | NULL    | auto_increment |
| epiweek | int(11) | NO   | MUL | NULL    |                |
| state   | char(2) | NO   | MUL | NULL    |                |
| num1    | int(11) | NO   |     | NULL    |                |
| num2    | int(11) | NO   |     | NULL    |                |
| num3    | int(11) | NO   |     | NULL    |                |
| num4    | int(11) | NO   |     | NULL    |                |
| num5    | int(11) | NO   |     | NULL    |                |
| num6    | int(11) | NO   |     | NULL    |                |
| num7    | int(11) | NO   |     | NULL    |                |
| num8    | int(11) | NO   |     | NULL    |                |
| total   | int(11) | NO   |     | NULL    |                |
+---------+---------+------+-----+---------+----------------+
*/

CREATE TABLE `cdc_extract` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `epiweek` int(11) NOT NULL,
  `state` char(2) NOT NULL,
  `num1` int(11) NOT NULL,
  `num2` int(11) NOT NULL,
  `num3` int(11) NOT NULL,
  `num4` int(11) NOT NULL,
  `num5` int(11) NOT NULL,
  `num6` int(11) NOT NULL,
  `num7` int(11) NOT NULL,
  `num8` int(11) NOT NULL,
  `total` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `epiweek` (`epiweek`,`state`),
  KEY `epiweek_2` (`epiweek`),
  KEY `state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
+---------+---------+------+-----+---------+----------------+
| Field   | Type    | Null | Key | Default | Extra          |
+---------+---------+------+-----+---------+----------------+
| id      | int(11) | NO   | PRI | NULL    | auto_increment |
| date    | date    | NO   | MUL | NULL    |                |
| epiweek | int(11) | NO   | MUL | NULL    |                |
| state   | char(2) | NO   | MUL | NULL    |                |
| total   | int(11) | NO   |     | NULL    |                |
+---------+---------+------+-----+---------+----------------+
*/

CREATE TABLE `cdc_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `epiweek` int(11) NOT NULL,
  `state` char(2) NOT NULL,
  `total` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`state`),
  KEY `date_2` (`date`),
  KEY `state` (`state`),
  KEY `epiweek` (`epiweek`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
