USE epidata;


-- `api_user` API key and user management

CREATE TABLE IF NOT EXISTS `api_user` (
  `id` int(11) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `api_key` varchar(50) UNIQUE NOT NULL,
  `email` varchar(320) UNIQUE NOT NULL,
  `created` date,
  `last_time_used` date,
  UNIQUE KEY `api_user` (`api_key`, `email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- `user_role` User roles

CREATE TABLE IF NOT EXISTS `user_role` (
  `id` int(11) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- `user_role_link` User roles link table

CREATE TABLE IF NOT EXISTS `user_role_link` (
  `user_id` int(11) UNSIGNED NOT NULL,
  `role_id` int(11) UNSIGNED NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
