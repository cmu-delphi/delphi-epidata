USE epidata;
/*

This table stores the signals used in the public signal dashboard.

+------------------------+--------------+------+-----+------------+----------------+
| Field                  | Type         | Null | Key | Default    | Extra          |
+------------------------+--------------+------+-----+------------+----------------+
| id                     | int(11)      | NO   | PRI | NULL       | auto_increment |
| name                   | varchar(255) | NO   |     | NULL       |                |
| source                 | varchar(32)  | NO   |     | NULL       |                |
| covidcast_signal       | varchar(64)  | NO   |     | NULL       |                |
| enabled                | tinyint(1)   | NO   |     | NULL       |                |
| latest_coverage_update | date         | NO   |     | 2020-01-01 |                |
| latest_status_update   | date         | NO   |     | 2020-01-01 |                |
+------------------------+--------------+------+-----+------------+----------------+

*/

CREATE TABLE `dashboard_signal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `covidcast_signal` varchar(64) NOT NULL,
  `enabled` boolean NOT NULL,
  `latest_coverage_update` date DEFAULT "2020-01-01" NOT NULL,
  `latest_status_update` date DEFAULT "2020-01-01" NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*

This table stores the status for signals in the public signal dashboard.

+-------------------+---------+------+-----+---------+-------+
| Field             | Type    | Null | Key | Default | Extra |
+-------------------+---------+------+-----+---------+-------+
| signal_id         | int(11) | NO   | PRI | NULL    |       |
| date              | date    | NO   | PRI | NULL    |       |
| latest_issue      | date    | YES  |     | NULL    |       |
| latest_time_value | date    | YES  |     | NULL    |       |
+-------------------+---------+------+-----+---------+-------+

*/

CREATE TABLE `dashboard_signal_status` (
  `signal_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `latest_issue` date DEFAULT NULL,
  `latest_time_value` date DEFAULT NULL,
  PRIMARY KEY (`signal_id`,`date`),
  CONSTRAINT `dashboard_signal_status_ibfk_1` 
  FOREIGN KEY (`signal_id`) REFERENCES `dashboard_signal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*

This table stores the coverage for signals in the public signal dashboard.

+--------------+-------------+------+-----+---------+-------+
| Field        | Type        | Null | Key | Default | Extra |
+--------------+-------------+------+-----+---------+-------+
| signal_id    | int(11)     | NO   | PRI | NULL    |       |
| date         | date        | NO   | PRI | NULL    |       |
| geo_type     | varchar(12) | NO   | PRI | NULL    |       |
| count        | int(11)     | NO   |     | NULL    |       |
+--------------+-------------+------+-----+---------+-------+

*/

CREATE TABLE `dashboard_signal_coverage` (
  `signal_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `count` int(11) NOT NULL,
  PRIMARY KEY (`signal_id`,`date`,`geo_type`),
  CONSTRAINT `dashboard_signal_coverage_ibfk_1` 
  FOREIGN KEY (`signal_id`) REFERENCES `dashboard_signal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;