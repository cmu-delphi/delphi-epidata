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
    `geo_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `geo_type` VARCHAR(12) NOT NULL,
    `geo_value` VARCHAR(12) NOT NULL,

    UNIQUE INDEX `geo_dim_index` (`geo_type`, `geo_value`)
) ENGINE=InnoDB;


CREATE TABLE signal_dim (
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,

    UNIQUE INDEX `signal_dim_index` (`source`, `signal`)
) ENGINE=InnoDB;

CREATE TABLE strat_dim (
    `strat_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `stratification_name` VARCHAR(64) NOT NULL UNIQUE,
    `stratification_descr` VARCHAR(64) NOT NULL
) ENGINE=InnoDB;
INSERT INTO strat_dim VALUES (1, 'NO_STRATIFICATION', '');

CREATE TABLE signal_history (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL PRIMARY KEY,
    `signal_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `geo_key_id` BIGINT(20) UNSIGNED NOT NULL,
    `strat_key_id` BIGINT(20) UNSIGNED NOT NULL DEFAULT 1,  -- TODO: for future use
    `issue` INT(11) NOT NULL,
    `data_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE,
    `stderr` DOUBLE,
    `sample_size` DOUBLE,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `missing_value` INT(1) DEFAULT '0',
    `missing_stderr` INT(1) DEFAULT '0',
    `missing_sample_size` INT(1) DEFAULT '0',

    UNIQUE INDEX `value_key_tig` (`signal_key_id`, `time_type`, `time_value`, `issue`, `geo_key_id`),
    UNIQUE INDEX `value_key_tgi` (`signal_key_id`, `time_type`, `time_value`, `geo_key_id`, `issue`),
    UNIQUE INDEX `value_key_itg` (`signal_key_id`, `issue`, `time_type`, `time_value`, `geo_key_id`),
    UNIQUE INDEX `value_key_igt` (`signal_key_id`, `issue`, `geo_key_id`, `time_type`, `time_value`),
    UNIQUE INDEX `value_key_git` (`signal_key_id`, `geo_key_id`, `issue`, `time_type`, `time_value`),
    UNIQUE INDEX `value_key_gti` (`signal_key_id`, `geo_key_id`, `time_type`, `time_value`, `issue`)
) ENGINE=InnoDB;

CREATE TABLE signal_latest (
    PRIMARY KEY (`signal_data_id`),
    UNIQUE INDEX `value_key` (`signal_key_id`, `time_type`, `time_value`, `geo_key_id`),
    UNIQUE INDEX `value_key_also` (`signal_key_id`, `geo_key_id`, `time_type`, `time_value`)
) ENGINE=InnoDB
SELECT * FROM signal_history;


-- NOTE: In production or any non-testing system that should maintain consistency,
--       **DO NOT** 'TRUNCATE' this table.
--       Doing so will function as a DROP/CREATE and reset the AUTO_INCREMENT counter for the `signal_data_id` field.
--       This field is used to populate the non-AUTO_INCREMENT fields of the same name in `signal_latest` and `signal_history`,
--       and resetting it will ultimately cause PK collisions.
--       To restore the counter, a row must be written with a `signal_data_id` value greater than the maximum
--       of its values in the other tables.
CREATE TABLE signal_load (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `strat_key_id` BIGINT(20) UNSIGNED NOT NULL DEFAULT 1,  -- TODO: for future use
    `issue` INT(11) NOT NULL,
    `data_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `geo_type` VARCHAR(12) NOT NULL,
    `geo_value` VARCHAR(12) NOT NULL,
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),  -- TODO: for future use
    `value` DOUBLE,
    `stderr` DOUBLE,
    `sample_size` DOUBLE,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),  -- TODO: for future use ; also "as_of" is problematic and should be renamed
    `is_latest_issue` BINARY(1) NOT NULL DEFAULT '0',
    `missing_value` INT(1) DEFAULT '0',
    `missing_stderr` INT(1) DEFAULT '0',
    `missing_sample_size` INT(1) DEFAULT '0',

    UNIQUE INDEX (`source`, `signal`, `time_type`, `geo_type`, `time_value`, `geo_value`, `issue`)
) ENGINE=InnoDB;


CREATE OR REPLACE VIEW signal_history_v AS
    SELECT
        0 AS is_latest_issue, -- provides column-compatibility to match `covidcast` table
        -- ^ this value is essentially undefined in this view, the notion of a 'latest' issue is not encoded here and must be drawn from the 'latest' table or view or otherwise computed...
        NULL AS direction, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`signal_data_id` AS `signal_data_id`, -- TODO: unnecessary  ...remove?
        `t1`.`strat_key_id` AS `strat_key_id`, -- TODO: for future
        `t1`.`issue` AS `issue`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed  ...remove?
        `t1`.`time_type` AS `time_type`,
        `t1`.`time_value` AS `time_value`,
        `t1`.`reference_dt` AS `reference_dt`, -- TODO: for future use  ...remove?
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed  ...remove?
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`, -- TODO: unnecessary  ...remove?
        `t1`.`geo_key_id` AS `geo_key_id`  -- TODO: unnecessary  ...remove?
    FROM `signal_history` `t1`
        JOIN `signal_dim` `t2`
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`
        JOIN `geo_dim` `t3`
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`;


CREATE OR REPLACE VIEW signal_latest_v AS
    SELECT
        1 AS is_latest_issue, -- provides column-compatibility to match `covidcast` table
        NULL AS direction, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`signal_data_id` AS `signal_data_id`, -- TODO: unnecessary  ...remove?
        `t1`.`strat_key_id` AS `strat_key_id`, -- TODO: for future use
        `t1`.`issue` AS `issue`,
        `t1`.`data_as_of_dt` AS `data_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed  ...remove?
        `t1`.`time_type` AS `time_type`,
        `t1`.`time_value` AS `time_value`,
        `t1`.`reference_dt` AS `reference_dt`, -- TODO: for future use  ...remove?
        `t1`.`value` AS `value`,
        `t1`.`stderr` AS `stderr`,
        `t1`.`sample_size` AS `sample_size`,
        `t1`.`lag` AS `lag`,
        `t1`.`value_updated_timestamp` AS `value_updated_timestamp`,
        `t1`.`computation_as_of_dt` AS `computation_as_of_dt`, -- TODO: for future use ; also "as_of" is problematic and should be renamed  ...remove?
        `t1`.`missing_value` AS `missing_value`,
        `t1`.`missing_stderr` AS `missing_stderr`,
        `t1`.`missing_sample_size` AS `missing_sample_size`,
        `t1`.`signal_key_id` AS `signal_key_id`, -- TODO: unnecessary  ...remove?
        `t1`.`geo_key_id` AS `geo_key_id`  -- TODO: unnecessary  ...remove?
    FROM `signal_latest` `t1`
        JOIN `signal_dim` `t2`
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`
        JOIN `geo_dim` `t3`
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`;


CREATE TABLE `covidcast_meta_cache` (
    `timestamp` int(11) NOT NULL,
    `epidata` LONGTEXT NOT NULL,

    PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB;
INSERT INTO covidcast_meta_cache VALUES (0, '[]');
