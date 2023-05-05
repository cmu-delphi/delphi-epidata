USE epidata;
/*
`api_analytics` logs API usage, which Delphi uses to improve the API.

This data is private to Delphi.

+----------+---------------+------+-----+---------+----------------+
| Field    | Type          | Null | Key | Default | Extra          |
+----------+---------------+------+-----+---------+----------------+
| id       | int(11)       | NO   | PRI | NULL    | auto_increment |
| datetime | datetime      | NO   | MUL | NULL    |                |
| ip       | varchar(15)   | NO   | MUL | NULL    |                |
| ua       | varchar(1024) | NO   |     | NULL    |                |
| source   | varchar(32)   | NO   | MUL | NULL    |                |
| result   | int(11)       | NO   |     | NULL    |                |
| num_rows | int(11)       | NO   |     | NULL    |                |
+----------+---------------+------+-----+---------+----------------+
*/

CREATE TABLE `api_analytics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  `ip` varchar(15) NOT NULL,
  `ua` varchar(1024) NOT NULL,
  `source` varchar(32) NOT NULL,
  `result` int(11) NOT NULL,
  `num_rows` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `datetime` (`datetime`),
  KEY `ip` (`ip`),
  KEY `source` (`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



/*
`api_user` API key and user management
This data is private to Delphi.
+----------------------+---------------+------+-----+-------------------+----------------+
| Field                | Type          | Null | Key | Default           | Extra          |
+----------------------+---------------+------+-----+-------------------+----------------+
| id                   | int(11)       | NO   | PRI |                   | auto_increment |
| api_key              | varchar(50)   | NO   |     |                   | unique         |
| email                | varcahr(320)  | No   |     |                   | unique         |
| creation_date        | datetime      | NO   |     | current_timestamp |                |
| last_api_access_date | datetime      | NO   |     | current_timestamp |                |
+------------+---------------+------+-----+---------+------------------------------------+
*/

CREATE TABLE IF NOT EXISTS `api_user` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `api_key` varchar(50) UNIQUE NOT NULL,
  `email` varchar(320) UNIQUE NOT NULL,
  `created` date,
  `last_time_used` date,
  UNIQUE KEY `api_user` (`api_key`, `email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



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