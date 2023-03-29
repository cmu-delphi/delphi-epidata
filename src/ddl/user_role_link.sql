USE epidata;
/*
`user_roles` User roles
This data is private to Delphi.
+------------+---------------+------+-----+---------+----------------+
| Field      | Type          | Null | Key | Default | Extra          |
+------------+---------------+------+-----+---------+----------------+
| user_id    | int(11)       | NO   | PRI |         |                |
| role_id    | int(11)       | NO   | PRI |         |                |
+------------+---------------+------+-----+---------+----------------+
*/

CREATE TABLE IF NOT EXISTS `user_role_link` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;