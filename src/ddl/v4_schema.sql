
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
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `demog_key_id` BIGINT(20) UNSIGNED,
    `issue` INT(11),
    `data_as_of_dt` DATETIME(0),
    `source` VARCHAR(32) NOT NULL ,-- #TODO: do we need these? COLLATE 'utf8mb4_0900_ai_ci',
    `signal` VARCHAR(64) NOT NULL ,-- COLLATE 'utf8mb4_0900_ai_ci',
    `geo_type` VARCHAR(12) NOT NULL ,-- COLLATE 'utf8mb4_0900_ai_ci',
    `geo_value` VARCHAR(12) NOT NULL ,-- COLLATE 'utf8mb4_0900_ai_ci',
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),
    `value` DOUBLE NULL DEFAULT NULL,
    `stderr` DOUBLE NULL DEFAULT NULL,
    `sample_size` DOUBLE NULL DEFAULT NULL,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),
    `is_latest_issue` BINARY(1) NOT NULL DEFAULT '0',
    `missing_value` INT(1) NULL DEFAULT '0',
    `missing_stderr` INT(1) NULL DEFAULT '0',
    `missing_sample_size` INT(1) NULL DEFAULT '0',
    `id` BIGINT(20) UNSIGNED NULL DEFAULT NULL,
    
    PRIMARY KEY (`signal_data_id`) USING BTREE,
    INDEX `comp_geo_key` (`signal_key_id`,`geo_key_id`,`issue`,`time_type`,`time_value`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4000000001;


CREATE TABLE signal_latest (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `demog_key_id` BIGINT(20) UNSIGNED,
    `issue` INT(11),
    `data_as_of_dt` DATETIME(0),
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),
    `value` DOUBLE NULL DEFAULT NULL,
    `stderr` DOUBLE NULL DEFAULT NULL,
    `sample_size` DOUBLE NULL DEFAULT NULL,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),
    `missing_value` INT(1) NULL DEFAULT '0',
    `missing_stderr` INT(1) NULL DEFAULT '0',
    `missing_sample_size` INT(1) NULL DEFAULT '0',
    
    PRIMARY KEY (`signal_data_id`) USING BTREE,
    INDEX `comp_geo_key` (`signal_key_id`,`geo_key_id`,`issue`,`time_type`,`time_value`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4000000001;


CREATE TABLE signal_load (
    `signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `signal_key_id` BIGINT(20) UNSIGNED,
    `geo_key_id` BIGINT(20) UNSIGNED,
    `demog_key_id` BIGINT(20) UNSIGNED,
    `issue` INT(11),
    `data_as_of_dt` DATETIME(0),
    `source` VARCHAR(32) NOT NULL,
    `signal` VARCHAR(64) NOT NULL,
    `geo_type` VARCHAR(12) NOT NULL,
    `geo_value` VARCHAR(12) NOT NULL,
    `time_type` VARCHAR(12) NOT NULL,
    `time_value` INT(11) NOT NULL,
    `reference_dt` DATETIME(0),
    `value` DOUBLE NULL DEFAULT NULL,
    `stderr` DOUBLE NULL DEFAULT NULL,
    `sample_size` DOUBLE NULL DEFAULT NULL,
    `lag` INT(11) NOT NULL,
    `value_updated_timestamp` INT(11) NOT NULL,
    `computation_as_of_dt` DATETIME(0),
    `is_latest_issue` BINARY(1) NOT NULL DEFAULT '0',
    `missing_value` INT(1) NULL DEFAULT '0',
    `missing_stderr` INT(1) NULL DEFAULT '0',
    `missing_sample_size` INT(1) NULL DEFAULT '0',
    `id` BIGINT(20) UNSIGNED,
    `compressed_signal_key` VARCHAR(100),
    `compressed_geo_key` VARCHAR(100),
    `compressed_demog_key` VARCHAR(100),
    `action_latest` VARCHAR(5),
    `latest_replace_data_id` BIGINT,

    PRIMARY KEY (`signal_data_id`) USING BTREE,
    INDEX `comp_signal_key` (`compressed_signal_key`) USING BTREE,
    INDEX `comp_geo_key` (`compressed_geo_key`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4000000001;


CREATE OR REPLACE VIEW signal_history_v AS
    SELECT
        1 AS is_latest_issue, -- provides column-compatibility to match `covidcast` table
        0 AS direction, -- provides column-compatibility to match `covidcast` table
        `t2`.`source` AS `source`,
        `t2`.`signal` AS `signal`,
        `t3`.`geo_type` AS `geo_type`,
        `t3`.`geo_value` AS `geo_value`,
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
    FROM ((`signal_latest` `t1` 
        JOIN `signal_dim` `t2` 
            USE INDEX (PRIMARY) 
            ON `t1`.`signal_key_id` = `t2`.`signal_key_id`) 
        JOIN `geo_dim` `t3` 
            USE INDEX (PRIMARY) 
            ON `t1`.`geo_key_id` = `t3`.`geo_key_id`);

