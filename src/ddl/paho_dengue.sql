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
| region         | varchar(12) | NO   |     | NULL    |                |
| total_pop      | int(11)     | NO   |     | NULL    |                |
| serotype       | varchar(12) | NO   |     | NULL    |                |
| num_dengue     | int(11)     | NO   |     | NULL    |                |
| incidence_rate | double      | NO   |     | NULL    |                |
| num_severe     | int(11)     | NO   |     | NULL    |                |
| num_deaths     | int(11)     | NO   |     | NULL    |                |
+----------------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `paho_dengue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `release_date` date NOT NULL,
  `issue` int(11) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `lag` int(11) NOT NULL,
  `region` varchar(12) NOT NULL,
  `total_pop` int(11) NOT NULL,
  `serotype` varchar(12) NOT NULL,
  `num_dengue` int(11) NOT NULL,
  `incidence_rate` double NOT NULL,
  `num_severe` int(11) NOT NULL,
  `num_deaths` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue` (`issue`,`epiweek`,`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
