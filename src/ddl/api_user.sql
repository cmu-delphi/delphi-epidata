/*
`api_user` API key and user management

This data is private to Delphi.

+------------+---------------+------+-----+---------+----------------+
| Field      | Type          | Null | Key | Default | Extra          |
+------------+---------------+------+-----+---------+----------------+
| id         | int(11)       | NO   | PRI | NULL    | auto_increment |
| api_key    | varchar(50)   | NO   |     |         |                |
| roles      | varchar(255)  | NO   |     |         |                |
| tracking   | tinyint(1)	   | YES  |     |         |                |
| registered | tinyint(1)    | YES  |     |         |                |
+------------+---------------+------+-----+---------+----------------+
*/

CREATE TABLE `api_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api_key` varchar(50) NOT NULL,
  `roles` varchar(255) NOT NULL,
  `tracking` tinyint(1) NULL,
  `registered` tinyint(1) NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
