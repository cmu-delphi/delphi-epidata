/*

This table stores the coverage for signals in the public signal dashboard.

+--------------+-------------+------+-----+---------+-------+
| Field        | Type        | Null | Key | Default | Extra |
+--------------+-------------+------+-----+---------+-------+
| indicator_id | int(11)     | NO   | PRI | NULL    |       |
| date         | date        | NO   | PRI | NULL    |       |
| geo_type     | varchar(12) | NO   | PRI | NULL    |       |
| geo_value    | varchar(12) | NO   | PRI | NULL    |       |
+--------------+-------------+------+-----+---------+-------+

*/

CREATE TABLE `dashboard_signal_coverage` (
  `indicator_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `geo_value` varchar(12) NOT NULL,
  PRIMARY KEY (`indicator_id`,`date`,`geo_type`,`geo_value`),
  CONSTRAINT `dashboard_signal_coverage_ibfk_1` 
  FOREIGN KEY (`indicator_id`) REFERENCES `dashboard_signal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
