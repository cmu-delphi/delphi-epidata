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
