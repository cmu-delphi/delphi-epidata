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
