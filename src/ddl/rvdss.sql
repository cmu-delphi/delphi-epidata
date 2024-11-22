USE epidata;
/*
TODO: briefly describe data source and define all columns.
*/

CREATE TABLE `rvdss_repiratory_detections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `geo_type` char(20) NOT NULL,
  `geo_value` char(20) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `flua_positive_tests` int(11) NOT NULL,
  `flua_percent_positive_tests` double NOT NULL,
  `flu_total_tests` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`geo_value`),
  KEY `state` (`state`),
  KEY `epiweek` (`epiweek`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `rvdss_testing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `geo_type` char(20) NOT NULL,
  `geo_value` char(20) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `flua_positive_tests` int(11) NOT NULL,
  `flua_percent_positive_tests` double NOT NULL,
  `flu_total_tests` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`geo_value`),
  KEY `state` (`state`),
  KEY `epiweek` (`epiweek`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `rvdss_detections_counts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `geo_type` char(20) NOT NULL,
  `geo_value` char(20) NOT NULL,
  `epiweek` int(11) NOT NULL,
  `flua_positive_tests` int(11) NOT NULL,
  `flua_percent_positive_tests` double NOT NULL,
  `flu_total_tests` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`geo_value`),
  KEY `state` (`state`),
  KEY `epiweek` (`epiweek`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
