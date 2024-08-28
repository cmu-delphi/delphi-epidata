USE epidata;

CREATE TABLE agg_geo_dim (
    `geo_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `geo_type` VARCHAR(12) NOT NULL,
    `geo_value` VARCHAR(12) NOT NULL,

    UNIQUE INDEX `agg_geo_dim_index` (`geo_type`, `geo_value`)
) ENGINE=InnoDB;

CREATE TABLE plant_dim (
    `plant_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `wwtp_jurisdiction` VARCHAR(3) NOT NULL, -- may only need CHAR(2), it's a state id
    `wwtp_id` INT(10) UNSIGNED NOT NULL,

    UNIQUE INDEX `plant_index` (`wwtp_jurisdiction`, `wwtp_id`)
) ENGINE=InnoDB;

CREATE TABLE signal_dim (
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `pathogen` VARCHAR(64) NOT NULL,
    `provider` VARCHAR(64) NOT NULL,
    `normalization` VARCHAR(64) NOT NULL,

    UNIQUE INDEX `signal_dim_index` (`source`, `signal`, `pathogen`, `provider`, `normalization`)
) ENGINE=InnoDB;

CREATE TABLE sample_site_dim (
    `site_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `plant_id` INT(10) UNSIGNED NOT NULL,
    `sample_method` VARCHAR(20) NOT NULL,
    `sample_loc_specify` INT(10) NOT NULL, -- nulls are represented as -1

    UNIQUE INDEX `sample_site_dim_index` (`plant_id`, `sample_loc_specify`),
    FOREIGN KEY (`plant_id`)
        REFERENCES `plant_dim`(`plant_id`)
        ON DELETE RESTRICT ON UPDATE RESTRICT -- plant_id shouldn't change, it's auto_increment
) ENGINE=InnoDB;


CREATE TABLE site_county_cross (
    `site_county_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `site_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `county_fips_id` CHAR(5) NOT NULL,

    UNIQUE INDEX `site_county_index` (`site_key_id`, `county_fips_id`),
    FOREIGN KEY (`site_key_id`)
        REFERENCES `sample_site_dim`(`site_key_id`)
        ON DELETE RESTRICT ON UPDATE RESTRICT -- plant_id shouldn't change, it's auto_increment
) ENGINE=InnoDB;



CREATE TABLE wastewater_granular_full (
    `wastewater_id` BIGINT(20) UNSIGNED NOT NULL PRIMARY KEY,
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `site_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `version` DATE NOT NULL,
    `reference_date` DATE NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` DATETIME NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `missing_value` INT(1) DEFAULT '0',

    UNIQUE INDEX `value_key_tig` (`signal_key_id`, `reference_date`, `version`, `site_key_id`),
    UNIQUE INDEX `value_key_tgi` (`signal_key_id`, `reference_date`, `site_key_id`, `version`),
    UNIQUE INDEX `value_key_itg` (`signal_key_id`, `version`, `reference_date`, `site_key_id`),
    UNIQUE INDEX `value_key_igt` (`signal_key_id`, `version`, `site_key_id`, `reference_date`),
    UNIQUE INDEX `value_key_git` (`signal_key_id`, `site_key_id`, `version`, `reference_date`),
    UNIQUE INDEX `value_key_gti` (`signal_key_id`, `site_key_id`, `reference_date`, `version`),
    FOREIGN KEY (`site_key_id`)
        REFERENCES `sample_site_dim`(`site_key_id`)
        ON DELETE RESTRICT ON UPDATE RESTRICT, -- plant_id shouldn't change, it's auto_increment
    FOREIGN KEY (`signal_key_id`)
        REFERENCES `signal_dim`(`signal_key_id`)
        ON DELETE RESTRICT ON UPDATE RESTRICT -- plant_id shouldn't change, it's auto_increment
) ENGINE=InnoDB;

CREATE TABLE wastewater_granular_latest (
    PRIMARY KEY (`wastewater_id`),
    UNIQUE INDEX `value_key_tg` (`signal_key_id`, `reference_date`, `site_key_id`),
    UNIQUE INDEX `value_key_gt` (`signal_key_id`, `site_key_id`, `reference_date`)
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
    `version` DATE NOT NULL,
    -- signal_dim
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `pathogen` VARCHAR(64) NOT NULL,
    `provider` VARCHAR(64) NOT NULL, -- null for potential future use
    `normalization` VARCHAR(64) NOT NULL, -- current data contains nulls in metric nwss source
    -- sample_site_dim
    `sample_loc_specify` INT(10) NOT NULL,
    `sample_method` VARCHAR(20) NOT NULL,
    -- plant_dim
    `wwtp_jurisdiction` VARCHAR(3) NOT NULL, -- may only need CHAR(2), it's a state id
    `wwtp_id` INT(10) UNSIGNED NOT NULL,
    -- full
    `reference_date` DATE NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` DATETIME NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `is_latest_version` BINARY(1) NOT NULL DEFAULT '1', -- default to including
    `missing_value` INT(1) DEFAULT '0',

    UNIQUE INDEX (`source`, `signal`, `reference_date`, `site_key_id`, `version`)
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

CREATE OR REPLACE VIEW wastewater_granular_latest_v AS
    SELECT
        1 AS `is_latest_version`, -- provides column-compatibility to match `wastewater_granular` table
        NULL AS `direction`, -- provides column-compatibility to match `wastewater_granular` table
        -- signal_dim
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t2`.`pathogen` AS `pathogen`,
        `t2`.`provider` AS `provider`,
        `t2`.`normalization` AS `normalization`,
        -- plant_dim
        `t4`.`wwtp_id` AS `wwtp_id`,
        `t4`.`wwtp_jurisdiction` AS `wwtp_jurisdiction`,
        -- sample_site_dim
        `t3`.`sample_loc_specify` AS `sample_loc_specify`,
        `t3`.`sample_method` AS `sample_method`,
        `t1`.`wastewater_id` AS `wastewater_id`,
        `t1`.`version` AS `version`,
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
    FROM `wastewater_granular_latest` `t1`
        JOIN `signal_dim` `t2` USING (`signal_key_id`)
        JOIN `sample_site_dim` `t3` USING (`site_key_id`)
        JOIN `plant_dim` `t4` USING (`plant_id`); -- TODO not sure if this is the right way to do a join of a join

CREATE TABLE `wastewater_meta_cache` (
    `timestamp` int(11) NOT NULL,
    `epidata` LONGTEXT NOT NULL,

    PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB;
INSERT INTO wastewater_meta_cache VALUES (0, '[]');
