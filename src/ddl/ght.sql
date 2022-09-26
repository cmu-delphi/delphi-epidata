USE epidata;
/*
TODO: document
*/

/*
+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| query    | varchar(64) | NO   | MUL | NULL    |                |
| location | varchar(8)  | NO   | MUL | NULL    |                |
| epiweek  | int(11)     | NO   | MUL | NULL    |                |
| value    | float       | NO   |     | NULL    |                |
+----------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `ght` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `query` varchar(64) NOT NULL,
  `location` varchar(8) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `value` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `query` (`query`,`location`,`epiweek`),
  KEY `query_2` (`query`),
  KEY `location` (`location`),
  KEY `epiweek` (`epiweek`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
