-- table definition copied from ../covid_hosp.sql
CREATE TABLE `covid_hosp_facility_key` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `address` VARCHAR(128),
  `ccn` VARCHAR(20),
  `city` VARCHAR(64),
  `fips_code` CHAR(5),
  `geocoded_hospital_address` VARCHAR(32), --  <--- not currently exposed by endpoint
  `hhs_ids` VARCHAR(127), --  <--- not currently exposed by endpoint
  `hospital_name` VARCHAR(256),
  `hospital_pk` VARCHAR(128) NOT NULL,
  `hospital_subtype` VARCHAR(64),
  `is_metro_micro` BOOLEAN,
  `state` CHAR(2) NOT NULL,
  `zip` CHAR(5),
  PRIMARY KEY (`id`),
  UNIQUE KEY (`hospital_pk`),
  -- for fast lookup of hospitals in a given location
  KEY (`state`, `hospital_pk`),
  KEY (`ccn`, `hospital_pk`),
  KEY (`city`, `hospital_pk`),
  KEY (`zip`, `hospital_pk`),
  KEY (`fips_code`, `hospital_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `covid_hosp_facility_key`
  (`address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`)
SELECT
   `address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`
FROM `covid_hosp_facility` ORDER BY `id` DESC
ON DUPLICATE KEY UPDATE hospital_pk=covid_hosp_facility_key.hospital_pk;

-- -- considered this approach too (note opposite direction in the ORDER BY clause) :
-- INSERT INTO `covid_hosp_facility_key`
--   (`address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`)
-- SELECT
--    `address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`
-- FROM `covid_hosp_facility` ORDER BY `id` ASC
-- ON DUPLICATE KEY UPDATE `address`=`address`,`ccn`=`ccn`,`city`=`city`,`fips_code`=`fips_code`,`geocoded_hospital_address`=`geocoded_hospital_address`,`hhs_ids`=`hhs_ids`,`hospital_name`=`hospital_name`,`hospital_subtype`=`hospital_subtype`,`is_metro_micro`=`is_metro_micro`,`state`=`state`,`zip`=`zip`;

-- -- or a query similar to the previous behavior of the covid_hosp_facility endpoint:
-- INSERT INTO `covid_hosp_facility_key`
--   (`hospital_pk`,`address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`)
-- SELECT
--    `hospital_pk`,MAX(`address`),MAX(`ccn`),MAX(`city`),MAX(`fips_code`),MAX(`geocoded_hospital_address`),MAX(`hhs_ids`),MAX(`hospital_name`),MAX(`hospital_subtype`),MAX(`is_metro_micro`),MAX(`state`),MAX(`zip`)
-- FROM `covid_hosp_facility`
-- GROUP BY `hospital_pk`;
