/*
TODO: document
*/

/*
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| location | varchar(12) | YES  | MUL | NULL    |                |
| value    | float       | NO   |     | NULL    |                |
| std      | float       | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `nowcasts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `epiweek` int(11) NOT NULL,
  `location` varchar(12) DEFAULT NULL,
  `value` float NOT NULL,
  `std` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `epiweek` (`epiweek`,`location`),
  KEY `epiweek_2` (`epiweek`),
  KEY `location` (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
