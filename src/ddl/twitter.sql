/*
TODO: document
*/

/*
+-------+---------+------+-----+---------+----------------+
| Field | Type    | Null | Key | Default | Extra          |
+-------+---------+------+-----+---------+----------------+
| id    | int(11) | NO   | PRI | NULL    | auto_increment |
| date  | date    | NO   | MUL | NULL    |                |
| state | char(2) | NO   | MUL | NULL    |                |
| num   | int(11) | NO   |     | NULL    |                |
| total | int(11) | NO   |     | NULL    |                |
+-------+---------+------+-----+---------+----------------+
*/

CREATE TABLE `twitter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `state` char(2) NOT NULL,
  `num` int(11) NOT NULL,
  `total` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`state`),
  KEY `date_2` (`date`),
  KEY `state` (`state`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
