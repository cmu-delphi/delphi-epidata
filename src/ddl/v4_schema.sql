-- --------------------------------
-- TODO: REMOVE THESE HACKS!!!  (find a better way to do this
-- 
-- the database schema `epidata` is created by ENV variables specified in the docker image definition found at:
--     ../../dev/docker/database/epidata/Dockerfile
-- and the user 'user' is created with permissions on that database.
-- here we create the `covid` schema and extend permissions to the same user,
-- as the ENV options do not appear to be expressive enough to do this as well.
-- this is incredibly permissive and easily guessable, but is reqd for testing our environment.
--
CREATE DATABASE covid;
USE covid;
GRANT ALL ON covid.* TO 'user';
-- END TODO
-- --------------------------------

CREATE TABLE geo_dim (
    `geo_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `geo_type` VARCHAR(12),
    `geo_value` VARCHAR(12),
    `compressed_geo_key` VARCHAR(100),
    
    PRIMARY KEY (`geo_key_id`) USING BTREE,
    UNIQUE INDEX `compressed_geo_key_ind` (`compressed_geo_key`) USING BTREE
);


CREATE TABLE signal_dim (
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, 
    `source` VARCHAR(32),
    `signal` VARCHAR(64),
    `compressed_signal_key` VARCHAR(100),
    
    PRIMARY KEY (`signal_key_id`) USING BTREE,
    UNIQUE INDEX `compressed_signal_key_ind` (`compressed_signal_key`) USING BTREE
) ENGINE=InnoDB;


-- Merged dim table combines geo_dim and signal_dim
-- merged_key_id added to signal tables and views
CREATE TABLE merged_dim
    (`merged_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `signal_key_id` INT,
    `geo_key_id` INT,
    `source` VARCHAR(32),
    `signal` VARCHAR(64),
    `geo_type` VARCHAR(12),
    `geo_value` VARCHAR(12),
    PRIMARY KEY (`merged_key_id`) USING BTREE,
    UNIQUE INDEX `values` (`source`, `signal`, `geo_type`, `geo_value`) USING BTREE,
    INDEX `dim_ids` (`signal_key_id`, `geo_key_id`) USING BTREE
) COLLATE='utf8mb4_0900_ai_ci' ENGINE=InnoDB;


CREATE TABLE signal_history (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL,
    `merged_key_id` BIGINT(19) NULL DEFAULT NULL,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `demog_key_id` BIGINT(20) UNSIGNED,  -- TODO: for future use ; also rename s/demog/stratification/
    `issue` INT(11),
    `data_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE NULL DEFAULT NULL,
    `stderr` DOUBLE NULL DEFAULT NULL,
    `sample_size` DOUBLE NULL DEFAULT NULL,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `is_latest_issue` BINARY(1) NOT NULL DEFAULT '0', -- TODO: delete this, its hard to keep updated and its not currently used
    `missing_value` INT(1) NULL DEFAULT '0',
    `missing_stderr` INT(1) NULL DEFAULT '0',
    `missing_sample_size` INT(1) NULL DEFAULT '0',
    `legacy_id` BIGINT(20) UNSIGNED NULL DEFAULT NULL, -- not used beyond import of previous data into the v4 schema
 
    PRIMARY KEY (`signal_data_id`) USING BTREE,
    UNIQUE INDEX `value_key` (`signal_key_id`,`geo_key_id`,`issue`,`time_type`,`time_value`) USING BTREE
) ENGINE=InnoDB;


CREATE TABLE signal_latest (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL,
    `merged_key_id` BIGINT(19) NULL DEFAULT NULL,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `demog_key_id` BIGINT(20) UNSIGNED,  -- TODO: for future use ; also rename s/demog/stratification/
    `issue` INT(11),
    `data_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE NULL DEFAULT NULL,
    `stderr` DOUBLE NULL DEFAULT NULL,
    `sample_size` DOUBLE NULL DEFAULT NULL,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `missing_value` INT(1) NULL DEFAULT '0',
    `missing_stderr` INT(1) NULL DEFAULT '0',
    `missing_sample_size` INT(1) NULL DEFAULT '0',
    
    PRIMARY KEY (`signal_data_id`) USING BTREE,
    UNIQUE INDEX `value_key` (`signal_key_id`,`geo_key_id`,`time_type`,`time_value`) USING BTREE
) ENGINE=InnoDB;


-- NOTE: In production or any non-testing system that should maintain consistency,
--       **DO NOT** 'TRUNCATE' this table.
--       Doing so will function as a DROP/CREATE and reset the AUTO_INCREMENT counter for the `signal_data_id` field.
--       This field is used to populate the non-AUTO_INCREMENT fields of the same name in `signal_latest` and `signal_history`,
--       and resetting it will ultimately cause PK collisions.
--       To restore the counter, a row must be written with a `signal_data_id` value greater than the maximum
--       of its values in the other tables.
CREATE TABLE signal_load (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `merged_key_id` BIGINT(19) NULL DEFAULT NULL,
    `demog_key_id` BIGINT(20) UNSIGNED,  -- TODO: for future use ; also rename s/demog/stratification/
    `issue` INT(11),
    `data_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `geo_type` VARCHAR(12) NOT NULL,
    `geo_value` VARCHAR(12) NOT NULL,
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE NULL DEFAULT NULL,
    `stderr` DOUBLE NULL DEFAULT NULL,
    `sample_size` DOUBLE NULL DEFAULT NULL,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `is_latest_issue` BINARY(1) NOT NULL DEFAULT '0',
    `missing_value` INT(1) NULL DEFAULT '0',
    `missing_stderr` INT(1) NULL DEFAULT '0',
    `missing_sample_size` INT(1) NULL DEFAULT '0',
    `legacy_id` BIGINT(20) UNSIGNED, -- not used beyond import of previous data into the v4 schema
    `compressed_signal_key` VARCHAR(100),
    `compressed_geo_key` VARCHAR(100),
    `compressed_demog_key` VARCHAR(100),  -- TODO: for future use ; also rename s/demog/stratification/
    `process_status` VARCHAR(2) DEFAULT 'l', -- using codes: 'i' (I) for "inserting", 'l' (L) for "loaded", and 'b' for "batching"
        -- TODO: change `process_status` default to 'i' (I) "inserting" or even 'x'/'u' "undefined" ?

    PRIMARY KEY (`signal_data_id`) USING BTREE,
    INDEX `comp_signal_key` (`compressed_signal_key`) USING BTREE,
    INDEX `comp_geo_key` (`compressed_geo_key`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4000000001;


CREATE OR REPLACE VIEW covid.signal_history_v AS
    SELECT
        0 AS `is_latest_issue`,
        NULL AS `direction`,
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t2`.`geo_type` AS `geo_type`,
        `t2`.`geo_value` AS `geo_value`,
        `t1`.`signal_data_id` AS `signal_data_id`,
        `t1`.`demog_key_id` AS `demog_key_id`,
        `t1`.`issue` AS `issue`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`,
        `t1`.`time_type` AS `time_type`,
        `t1`.`time_value` AS `time_value`,
        `t1`.`reference_dt` AS `reference_dt`,
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`,
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`,
        `t1`.`geo_key_id` AS `geo_key_id`
    FROM covid.`signal_history` `t1`
         JOIN covid.`merged_dim` `t2`
             USE INDEX (PRIMARY)
             ON `t1`.`merged_key_id` = `t2`.`merged_key_id`;


CREATE OR REPLACE VIEW covid.signal_latest_v AS
    SELECT
        1 AS `is_latest_issue`,
        NULL AS `direction`,
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t2`.`geo_type` AS `geo_type`,
        `t2`.`geo_value` AS `geo_value`,
        `t1`.`signal_data_id` AS `signal_data_id`,
        `t1`.`demog_key_id` AS `demog_key_id`,
        `t1`.`issue` AS `issue`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`,
        `t1`.`time_type` AS `time_type`,
        `t1`.`time_value` AS `time_value`,
        `t1`.`reference_dt` AS `reference_dt`,
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`,
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`,
        `t1`.`geo_key_id` AS `geo_key_id`
    FROM covid.`signal_latest` `t1`
        JOIN covid.`merged_dim` `t2`
            USE INDEX (PRIMARY)
            ON `t1`.`merged_key_id` = `t2`.`merged_key_id`;


CREATE TABLE `covidcast_meta_cache` (
    `timestamp` int(11) NOT NULL,
    `epidata` LONGTEXT NOT NULL,

    PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO covidcast_meta_cache VALUES (0, '[]');
