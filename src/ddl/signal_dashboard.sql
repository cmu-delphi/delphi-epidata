/*

This table stores the signals used in the public signal dashboard.

+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| id      | int(11)      | NO   | PRI | NULL    | auto_increment |
| name    | varchar(255) | NO   |     | NULL    |                |
| source  | varchar(32)  | YES  |     | NULL    |                |
| enabled | binary(1)    | YES  |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+

*/

CREATE TABLE `dashboard_signal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `source` varchar(32) NOT NULL,
  `enabled` binary(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/*

This table stores the status for signals in the public signal dashboard.

+-------------------+---------+------+-----+---------+-------+
| Field             | Type    | Null | Key | Default | Extra |
+-------------------+---------+------+-----+---------+-------+
| signal_id         | int(11) | NO   | PRI | NULL    |       |
| date              | date    | NO   | PRI | NULL    |       |
| latest_issue_date | date    | NO   |     | NULL    |       |
| latest_data_date  | date    | NO   |     | NULL    |       |
+-------------------+---------+------+-----+---------+-------+

*/

CREATE TABLE `dashboard_signal_status` (
  `signal_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `latest_issue_date` date DEFAULT NULL,
  `latest_data_date` date DEFAULT NULL,
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
| geo_value    | varchar(12) | NO   | PRI | NULL    |       |
+--------------+-------------+------+-----+---------+-------+

*/

CREATE TABLE `dashboard_signal_coverage` (
  `signal_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `geo_type` varchar(12) NOT NULL,
  `geo_value` varchar(12) NOT NULL,
  PRIMARY KEY (`signal_id`,`date`,`geo_type`,`geo_value`),
  CONSTRAINT `dashboard_signal_coverage_ibfk_1` 
  FOREIGN KEY (`signal_id`) REFERENCES `dashboard_signal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;