/*
These tables coordinate scraping of Wikipedia page visit stats and store page
visit counts for pages of interest (i.e. those which are epidemiologically
pertinent).
*/

/*
`wiki` is an optimized store of Wikipedia page visits per hour, per article,
per language (for pre-selected article and language combinations).

Data is public.

+----------+-------------+------+-----+---------+----------------+
| Field    | Type        | Null | Key | Default | Extra          |
+----------+-------------+------+-----+---------+----------------+
| id       | int(11)     | NO   | PRI | NULL    | auto_increment |
| datetime | datetime    | NO   | MUL | NULL    |                |
| article  | varchar(64) | NO   | MUL | NULL    |                |
| count    | int(11)     | NO   |     | NULL    |                |
| language | char(2)     | NO   |     | en      |                |
+----------+-------------+------+-----+---------+----------------+
*/

CREATE TABLE `wiki` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  `article` varchar(64) NOT NULL,
  `count` int(11) NOT NULL,
  `language` char(2) NOT NULL DEFAULT 'en',
  PRIMARY KEY (`id`),
  UNIQUE KEY `datetime` (`datetime`,`article`,`language`),
  KEY `datetime_2` (`datetime`),
  KEY `article` (`article`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
`wiki_meta` stores timing information (e.g. hour, day, week) and the overall
page visit denominator for a particular language.

Data is public.

+----------+----------+------+-----+---------+----------------+
| Field    | Type     | Null | Key | Default | Extra          |
+----------+----------+------+-----+---------+----------------+
| id       | int(11)  | NO   | PRI | NULL    | auto_increment |
| datetime | datetime | NO   | MUL | NULL    |                |
| date     | date     | NO   |     | NULL    |                |
| epiweek  | int(11)  | NO   |     | NULL    |                |
| total    | int(11)  | NO   |     | NULL    |                |
| language | char(2)  | NO   |     | en      |                |
+----------+----------+------+-----+---------+----------------+
*/

CREATE TABLE `wiki_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  `date` date NOT NULL,
  `epiweek` int(11) NOT NULL,
  `total` int(11) NOT NULL,
  `language` char(2) NOT NULL DEFAULT 'en',
  PRIMARY KEY (`id`),
  UNIQUE KEY `datetime` (`datetime`,`language`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*
`wiki_raw` stores information about a single pagedump file, including a "raw"
JSON dump containing the number of visits to particular pages of interest.

Data is public.

+----------+---------------+------+-----+---------+----------------+
| Field    | Type          | Null | Key | Default | Extra          |
+----------+---------------+------+-----+---------+----------------+
| id       | int(11)       | NO   | PRI | NULL    | auto_increment |
| name     | varchar(64)   | NO   | UNI | NULL    |                |
| hash     | char(32)      | NO   |     | NULL    |                |
| status   | int(11)       | NO   | MUL | 0       |                |
| size     | int(11)       | YES  |     | NULL    |                |
| datetime | datetime      | YES  |     | NULL    |                |
| worker   | varchar(256)  | YES  |     | NULL    |                |
| elapsed  | float         | YES  |     | NULL    |                |
| data     | varchar(4096) | YES  |     | NULL    |                |
+----------+---------------+------+-----+---------+----------------+
*/

CREATE TABLE `wiki_raw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `hash` char(32) NOT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `size` int(11) DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  `worker` varchar(256) DEFAULT NULL,
  `elapsed` float DEFAULT NULL,
  `data` varchar(4096) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
