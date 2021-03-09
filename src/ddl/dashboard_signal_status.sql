/*

This table stores the status for signals in the public signal dashboard.

+-------------------+---------+------+-----+---------+-------+
| Field             | Type    | Null | Key | Default | Extra |
+-------------------+---------+------+-----+---------+-------+
| indicator_id      | int(11) | NO   | PRI | NULL    |       |
| date              | date    | NO   | PRI | NULL    |       |
| latest_issue_date | date    | NO   |     | NULL    |       |
| latest_data_date  | date    | NO   |     | NULL    |       |
+-------------------+---------+------+-----+---------+-------+

*/

CREATE TABLE `dashboard_signal_status` (
  `indicator_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `latest_issue_date` date DEFAULT NULL,
  `latest_data_date` date DEFAULT NULL,
  PRIMARY KEY (`indicator_id`,`date`),
  CONSTRAINT `dashboard_signal_status_ibfk_1` 
  FOREIGN KEY (`indicator_id`) REFERENCES `dashboard_signal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
