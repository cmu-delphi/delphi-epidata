INSERT INTO `covid_hosp_facility_key`
  (`address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`)
SELECT
   `address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`
FROM `covid_hosp_facility` ORDER BY `id` DESC
ON DUPLICATE KEY UPDATE id=id;

-- -- considered this approach too (note the change of direction on the ORDER BY clause) :
-- INSERT INTO `covid_hosp_facility_key`
--   (`address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`)
-- SELECT
--    `address`,`ccn`,`city`,`fips_code`,`geocoded_hospital_address`,`hhs_ids`,`hospital_name`,`hospital_pk`,`hospital_subtype`,`is_metro_micro`,`state`,`zip`
-- FROM `covid_hosp_facility` ORDER BY `id` ASC
-- ON DUPLICATE KEY UPDATE `address`=`address`,`ccn`=`ccn`,`city`=`city`,`fips_code`=`fips_code`,`geocoded_hospital_address`=`geocoded_hospital_address`,`hhs_ids`=`hhs_ids`,`hospital_name`=`hospital_name`,`hospital_pk`=`hospital_pk`,`hospital_subtype`=`hospital_subtype`,`is_metro_micro`=`is_metro_micro`,`state`=`state`,`zip`=`zip`;

