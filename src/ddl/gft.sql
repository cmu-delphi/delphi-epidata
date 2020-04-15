/*
TODO: document
*/

/*
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| location | varchar(64) | NO   | MUL | NULL    |                |
| num      | int(11)     | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `gft` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `epiweek` int(11) NOT NULL,
  `location` varchar(64) NOT NULL,
  `num` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `epiweek` (`epiweek`,`location`),
  KEY `epiweek_2` (`epiweek`),
  KEY `location` (`location`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
