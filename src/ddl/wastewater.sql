USE epidata;

CREATE TABLE agg_geo_dim (
    `geo_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `geo_type` VARCHAR(12) NOT NULL,
    `geo_value` VARCHAR(12) NOT NULL,

    UNIQUE INDEX `agg_geo_dim_index` (`geo_type`, `geo_value`)
) ENGINE=InnoDB;

CREATE TABLE sample_site_dim (
    `site_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `plant_id` INT(10) UNSIGNED NOT NULL,
    `sample_loc_specify` INT(10) UNSIGNED, -- definitely can be null
    `sampling_method` VARCHAR(20),

    UNIQUE INDEX `sample_site_dim_index` (`plant_id`, `sample_loc_specify`)
) ENGINE=InnoDB;

CREATE TABLE plant_dim (
    `plant_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `wwtp_jurisdiction` CHAR(3) UNSIGNED NOT NULL, -- may only need CHAR(3), it's a state id + NYC
    `wwtp_id` INT(10) UNSIGNED NOT NULL

    UNIQUE INDEX `plant_index` (`wwtp_jurisdiction`, `wwtp_id`)
) ENGINE=InnoDB;

CREATE TABLE site_county_cross (
    `site_county_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `site_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `county_fips_id` CHAR(5) UNSIGNED NOT NULL

    UNIQUE INDEX `sit_county_index` (`site_key_id`, `county_fips_id`)
) ENGINE=InnoDB;


CREATE TABLE signal_dim (
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `pathogen` VARCHAR(64) NOT NULL,
    `provider` VARCHAR(64), -- null for potential future use
    `normalization` VARCHAR(64), -- null for potential future use

    UNIQUE INDEX `signal_dim_index` (`source`, `signal`, `pathogen`, `provider`, `normalization`)
) ENGINE=InnoDB;


CREATE TABLE wastewater_granular_full (
    `wastewater_id` BIGINT(20) UNSIGNED NOT NULL PRIMARY KEY,
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `site_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `version` INT(11) NOT NULL,
    `time_type` VARCHAR(12) NOT NULL,
    `reference_date` INT(11) NOT NULL,
    `value` DOUBLE,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `missing_value` INT(1) DEFAULT '0',

    UNIQUE INDEX `value_key_tig` (`signal_key_id`, `time_type`, `reference_date`, `version`, `site_key_id`),
    UNIQUE INDEX `value_key_tgi` (`signal_key_id`, `time_type`, `reference_date`, `site_key_id`, `version`),
    UNIQUE INDEX `value_key_itg` (`signal_key_id`, `version`, `time_type`, `reference_date`, `site_key_id`),
    UNIQUE INDEX `value_key_igt` (`signal_key_id`, `version`, `site_key_id`, `time_type`, `reference_date`),
    UNIQUE INDEX `value_key_git` (`signal_key_id`, `site_key_id`, `version`, `time_type`, `reference_date`),
    UNIQUE INDEX `value_key_gti` (`signal_key_id`, `site_key_id`, `time_type`, `reference_date`, `version`)
) ENGINE=InnoDB;

CREATE TABLE wastewater_granular_latest (
    PRIMARY KEY (`wastewater_id`),
    UNIQUE INDEX `value_key_tg` (`signal_key_id`, `time_type`, `reference_date`, `site_key_id`),
    UNIQUE INDEX `value_key_gt` (`signal_key_id`, `site_key_id`, `time_type`, `reference_date`)
) ENGINE=InnoDB
SELECT * FROM wastewater_granular_full;


-- NOTE: In production or any non-testing system that should maintain consistency,
--       **DO NOT** 'TRUNCATE' this table.
--       Doing so will function as a DROP/CREATE and reset the AUTO_INCREMENT counter for the `wastewater_id` field.
--       This field is used to populate the non-AUTO_INCREMENT fields of the same name in `wastewater_granular_latest` and `wastewater_granular_full`,
--       and resetting it will ultimately cause PK collisions.
--       To restore the counter, a row must be written with a `wastewater_id` value greater than the maximum
--       of its values in the other tables.
CREATE TABLE wastewater_granular_load (
    `wastewater_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `site_key_id` BIGINT(20) UNSIGNED,
    `version` INT(11) NOT NULL,
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `site_key_id` BIGINT(20) NOT NULL,
    `time_type` VARCHAR(12) NOT NULL,
    `reference_date` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `is_latest_version` BINARY(1) NOT NULL DEFAULT '0',
    `missing_value` INT(1) DEFAULT '0',

    UNIQUE INDEX (`source`, `signal`, `time_type`, `reference_date`, `site_key_id`, `version`)
) ENGINE=InnoDB;


CREATE OR REPLACE VIEW wastewater_granular_full_v AS
    SELECT
        0 AS `is_latest_version`, -- provides column-compatibility to match `wastewater_granular` table
        -- ^ this value is essentially undefined in this view, the notion of a 'latest' version is not encoded here and must be drawn from the 'latest' table or view or otherwise computed...
        NULL AS `direction`, -- provides column-compatibility to match `covidcast` table TODO: what is this??
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t2`.`pathogen` AS `pathogen`,
        `t2`.`provider` AS `provider`,
        `t2`.`normalization` AS `normalization`,
        `t4`.`wwtp_id` AS `wwtp_id`,
        `t4`.`wwtp_jurisdiction` AS `wwtp_jurisdiction`,
        `t3`.`sample_loc_specify` AS `sample_loc_specify`,
        `t1`.`wastewater_id` AS `wastewater_id`,
        `t1`.`version` AS `version`,
        `t1`.`time_type` AS `time_type`,
        `t1`.`reference_date` AS `reference_date`,
        `t1`.`reference_dt` AS `reference_dt`, -- TODO: for future use
        `t1`.`value` AS `value`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`signal_key_id` AS `signal_key_id`,
        `t1`.`site_key_id` AS `site_key_id`,
        `t3`.`plant_id` AS `plant_id`
    FROM `wastewater_granular_full` `t1`
        JOIN `signal_dim` `t2` USING (`signal_key_id`)
        JOIN `sample_site_dim` `t3` USING (`site_key_id`)
        JOIN `plant_dim` `t4` USING (`plant_id`); -- TODO not sure if this is the right way to do a join of a join

        --JOIN `site_county_cross` `t5` USING (`site_key_id`);
CREATE OR REPLACE VIEW wastewater_granular_latest_v AS
    SELECT
        1 AS `is_latest_version`, -- provides column-compatibility to match `covidcast` table
        NULL AS `direction`, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`wastewater_id` AS `wastewater_id`,
        `t1`.`version` AS `version`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`time_type` AS `time_type`,
        `t1`.`reference_date` AS `reference_date`,
        `t1`.`reference_dt` AS `reference_dt`, -- TODO: for future use
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`,
        `t1`.`site_key_id` AS `site_key_id`
    FROM `wastewater_granular_latest` `t1`
        JOIN `signal_dim` `t2` USING (`signal_key_id`)
        JOIN `agg_geo_dim` `t3` USING (`site_key_id`);

CREATE TABLE `wastewater_meta_cache` (
    `timestamp` int(11) NOT NULL,
    `epidata` LONGTEXT NOT NULL,

    PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB;
INSERT INTO wastewater_meta_cache VALUES (0, '[]');
