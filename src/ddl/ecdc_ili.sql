USE epidata;
/*
TODO: document
*/

/*
+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | int(11)     | NO   | PRI | NULL    | auto_increment |
| release_date   | date        | NO   |     | NULL    |                |
| issue          | int(11)     | NO   | MUL | NULL    |                |
| epiweek        | int(11)     | NO   |     | NULL    |                |
| lag            | int(11)     | NO   |     | NULL    |                |
| region         | varchar(30) | NO   |     | NULL    |                |
| incidence_rate | double      | NO   |     | NULL    |                |
+----------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `ecdc_ili` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `lag` int(11) NOT NULL,
  `region` varchar(30) NOT NULL,
  `incidence_rate` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`issue`,`epiweek`,`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
