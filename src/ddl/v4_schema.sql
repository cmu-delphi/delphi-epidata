
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


CREATE TABLE signal_history (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL,
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


CREATE TABLE signal_load (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
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


CREATE OR REPLACE VIEW signal_history_v AS
    SELECT
        0 AS is_latest_issue, -- provides column-compatibility to match `covidcast` table
        -- ^ this value is essentially undefined in this view, the notion of a 'latest' issue is not encoded here and must be drawn from the 'latest' table or view or otherwise computed...
        0 AS direction, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`signal_data_id` AS `signal_data_id`, -- TODO: unnecessary  ...remove?
        `t1`.`demog_key_id` AS `demog_key_id`, -- TODO: for future use ; also rename s/demog/stratification/  ...remove?
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
    FROM ((`signal_history` `t1` 
        JOIN `signal_dim` `t2` 
            USE INDEX (PRIMARY) 
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`)
        JOIN `geo_dim` `t3` 
            USE INDEX (PRIMARY) 
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`);


CREATE OR REPLACE VIEW signal_latest_v AS 
    SELECT
        1 AS is_latest_issue, -- provides column-compatibility to match `covidcast` table
        0 AS direction, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
        `t1`.`signal_data_id` AS `signal_data_id`, -- TODO: unnecessary  ...remove?
        `t1`.`demog_key_id` AS `demog_key_id`, -- TODO: for future use ; also rename s/demog/stratification/  ...remove?
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
    FROM ((`signal_latest` `t1` 
        JOIN `signal_dim` `t2` 
            USE INDEX (PRIMARY) 
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`) 
        JOIN `geo_dim` `t3` 
            USE INDEX (PRIMARY) 
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`);


CREATE TABLE `covidcast_meta_cache` (
    `timestamp` int(11) NOT NULL,
    `epidata` LONGTEXT NOT NULL,

    PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
INSERT INTO covidcast_meta_cache VALUES (0, '[]');
