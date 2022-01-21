# *******************************************************************************************************
# cr_tbl_signal_history.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
CREATE TABLE <param1>.signal_history (
	`signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`signal_key_id` bigint(20) unsigned,
	`geo_key_id` bigint(20) unsigned,
	`demog_key_id` bigint(20) unsigned,
	`issue` INT(11),
	`data_as_of_dt` datetime(0),
	`source` VARCHAR(32) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`signal` VARCHAR(64) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`geo_type` VARCHAR(12) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`geo_value` VARCHAR(12) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`time_type` VARCHAR(12) NOT NULL,
	`time_value` INT(11) NOT NULL,
	`reference_dt` datetime(0),
	`value` DOUBLE NULL DEFAULT NULL,
	`stderr` DOUBLE NULL DEFAULT NULL,
	`sample_size` DOUBLE NULL DEFAULT NULL,
	`lag` INT(11) NOT NULL,
	`value_updated_timestamp` INT(11) NOT NULL,
	`computation_as_of_dt` datetime(0),
	`is_latest_issue` BINARY(1) NOT NULL DEFAULT '0',
	`missing_value` INT(1) NULL DEFAULT '0',
	`missing_stderr` INT(1) NULL DEFAULT '0',
	`missing_sample_size` INT(1) NULL DEFAULT '0',
	`id` BIGINT(20) UNSIGNED NULL DEFAULT NULL,
	PRIMARY KEY (`signal_data_id`) USING BTREE,
	INDEX `comp_geo_key` (`signal_key_id`,`geo_key_id`,`issue`,`time_type`,`time_value`) USING BTREE
)
ENGINE=InnoDB
AUTO_INCREMENT=4000000001
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************

