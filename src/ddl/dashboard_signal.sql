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