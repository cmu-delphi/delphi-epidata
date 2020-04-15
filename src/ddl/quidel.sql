/*
TODO: document
*/

/*
+-------------+------------+------+-----+---------+----------------+
| Field       | Type       | Null | Key | Default | Extra          |
+-------------+------------+------+-----+---------+----------------+
| id          | int(11)    | NO   | PRI | NULL    | auto_increment |
| location    | varchar(8) | NO   | MUL | NULL    |                |
| epiweek     | int(11)    | NO   | MUL | NULL    |                |
| value       | float      | NO   |     | NULL    |                |
| num_rows    | int(11)    | NO   |     | NULL    |                |
| num_devices | int(11)    | NO   |     | NULL    |                |
+-------------+------------+------+-----+---------+----------------+
*/

CREATE TABLE `quidel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `location` varchar(8) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `value` float NOT NULL,
  `num_rows` int(11) NOT NULL,
  `num_devices` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ew_loc` (`epiweek`,`location`),
  KEY `ew` (`epiweek`),
  KEY `loc` (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
