/*
These tables store the mobility data collected during COVID
- Data source:
  https://covid19.apple.com/mobility
  https://www.google.com/covid19/mobility/
*/


/*
`Apple_Mobility_US` stores mobility data collected from Apple.

+----------------------+---------------+------+-----+---------+----------------+
| Field                | Type          | Null | Key | Default | Extra          |
+----------------------+---------------+------+-----+---------+----------------+
| id                   | int(14)       | NO   | PRI | NULL    | auto_increment |
| state		       | varchar(50)   | NO   |     | NULL    |                |
| county_and_city      | varchar(50)   | NO   |     | NULL    |                |
| geo_type             | varchar(50)   | NO   |     | NULL    |                |
| date                 | datetime      | NO   |     | NULL    |                |
| driving              | double        | NO   |     | NULL    |                |
| transit              | double        | NO   |     | NULL    |                |
| walking              | double        | NO   |     | NULL    |                |
+----------------------+---------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `state`
  state mobility data collected
- `county_and_city`
  county and city mobility data collected
- `geo type`
  type of region
- `date`
  date of mobility data collection
- `driving`
  driving data
- `transit`
  transit data
- `walking`
  walking data
*/

CREATE TABLE `Apple_Mobility_US` (
  `id` INT(14) NOT NULL AUTO_INCREMENT,
  `state` VARCHAR(50) NOT NULL,
  `county_and_city` VARCHAR(50) NOT NULL,
  `geo_type` VARCHAR(50) NOT NULL,	
  `date` DATETIME NOT NULL,
  `driving` DOUBLE NOT NULL,
  `transit` DOUBLE NOT NULL,
  `walking` DOUBLE NOT NULL,  	
  PRIMARY KEY (`id`),
  UNIQUE KEY (`state`,`county_and_city`,`geo_type`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
`Google_Mobility_US` stores mobility data collected from Google.

+----------------------+---------------+------+-----+---------+----------------+
| Field                | Type          | Null | Key | Default | Extra          |
+----------------------+---------------+------+-----+---------+----------------+
| id                   | int(14)       | NO   | PRI | NULL    | auto_increment |
| state		       | varchar(50)   | NO   |     | NULL    |                |
| county               | varchar(50)   | NO   |     | NULL    |                |
| date                 | datetime      | NO   |     | NULL    |                |
| retail and recreation| double        | NO   |     | NULL    |                |
| grocery and pharmacy | double        | NO   |     | NULL    |                |
| parks                | double        | NO   |     | NULL    |                |
| transit stations     | double        | NO   |     | NULL    |                |
| workplaces           | double        | NO   |     | NULL    |                |
| residential          | double        | NO   |     | NULL    |                |
+----------------------+---------------+------+-----+---------+----------------+

- `id`
  unique identifier for each record
- `state`
  state mobility data collected
- `county`
  county mobility data collected
- `date`
  date of mobility data collection
- `retail and recreation`
  retail and recreation data
- `grocery and pharmacy`
  grocery and pharmacy data
- `parks`
  parks data
- `transit stations`
  transit stations data
- `workplaces`
  workplaces data
- `residential`
  residential data
*/

CREATE TABLE `Google_Mobility_US` (
  `id` INT(14) NOT NULL AUTO_INCREMENT,
  `state` VARCHAR(50) NOT NULL,
  `county` VARCHAR(50) NOT NULL,	
  `date` DATETIME NOT NULL,
  `retail and recreation` DOUBLE NOT NULL,
  `grocery and pharmacy` DOUBLE NOT NULL,
  `parks` DOUBLE NOT NULL,
  `transit stations` DOUBLE NOT NULL,
  `workplaces` DOUBLE NOT NULL,
  `residential` DOUBLE NOT NULL,    	  	
  PRIMARY KEY (`id`),
  UNIQUE KEY (`state`,`county`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
