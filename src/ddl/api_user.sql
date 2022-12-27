USE epidata;
/*
`api_user` API key and user management
This data is private to Delphi.
+----------------------+---------------+------+-----+-------------------+----------------+
| Field                | Type          | Null | Key | Default           | Extra          |
+----------------------+---------------+------+-----+-------------------+----------------+
| id                   | int(11)       | NO   | PRI |                   | auto_increment |
| api_key              | varchar(50)   | NO   |     |                   | unique         |
| tracking             | tinyint(1)	   | YES  |     |                   |                |
| registered           | tinyint(1)    | YES  |     |                   |                |
| creation_date        | datetime      | NO   |     | current_timestamp |                |
| last_api_access_date | datetime      | NO   |     | current_timestamp |                |
+------------+---------------+------+-----+---------+------------------------------------+
*/

CREATE TABLE IF NOT EXISTS `api_user` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `api_key` varchar(50) NOT NULL,
  `tracking` tinyint(1) NULL,
  `registered` tinyint(1) NULL,
  UNIQUE KEY `api_key` (`api_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;