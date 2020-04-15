/*
TODO: document
*/

/*
+---------+-------------+------+-----+---------+----------------+
| Field   | Type        | Null | Key | Default | Extra          |
+---------+-------------+------+-----+---------+----------------+
| id      | int(11)     | NO   | PRI | NULL    | auto_increment |
| system  | varchar(64) | NO   | MUL | NULL    |                |
| epiweek | int(11)     | NO   | MUL | NULL    |                |
| json    | mediumtext  | NO   |     | NULL    |                |
+---------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `forecasts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `system` varchar(64) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `json` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `system` (`system`,`epiweek`),
  KEY `system_2` (`system`),
  KEY `epiweek` (`epiweek`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
