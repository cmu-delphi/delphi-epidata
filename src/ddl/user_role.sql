USE epidata;
/*
`user_roles` User roles
This data is private to Delphi.
+------------+---------------+------+-----+---------+----------------+
| Field      | Type          | Null | Key | Default | Extra          |
+------------+---------------+------+-----+---------+----------------+
| id         | int(11)       | NO   | PRI |         | auto_increment |
| name       | varchar(50)   | NO   |     |         | unique         |
+------------+---------------+------+-----+---------+----------------+
*/

CREATE TABLE IF NOT EXISTS `user_role` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;