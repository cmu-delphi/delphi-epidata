# *******************************************************************************************************
# cr_tbl_signal_load.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
CREATE TABLE <param1>.signal_load (
	`signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`signal_key_id` bigint(20) unsigned,
	`geo_key_id` bigint(20) unsigned,
	`demog_key_id` bigint(20) unsigned,
	`issue` INT(11),
	`data_as_of_dt` datetime(0),
	`source` VARCHAR(32) NOT NULL,
	`signal` VARCHAR(64) NOT NULL,
	`geo_type` VARCHAR(12) NOT NULL,
	`geo_value` VARCHAR(12) NOT NULL,
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
	`id` BIGINT(20) UNSIGNED,
	`compressed_signal_key` varchar(100),
	`compressed_geo_key` varchar(100),
	`compressed_demog_key` varchar(100),
	`action_latest` varchar(5),
	`latest_replace_data_id` bigint,
	PRIMARY KEY (`signal_data_id`) USING BTREE,
	INDEX `comp_signal_key` (`compressed_signal_key`) USING BTREE,
	INDEX `comp_geo_key` (`compressed_geo_key`) USING BTREE
)
ENGINE=InnoDB
AUTO_INCREMENT=4000000001
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
param1=prompt target=prompt
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
