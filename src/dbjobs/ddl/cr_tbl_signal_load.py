# *******************************************************************************************************
# cr_tbl_signal_load.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
CREATE TABLE <param1>.signal_load (
	`signal_key_id` bigint(20) unsigned,
	`geo_key_id` bigint(20) unsigned,
	`demog_key_id` bigint(20) unsigned,
	`time_value` INT(11) NOT NULL,
	`issue` INT(11),
	`time_type` VARCHAR(12) NOT NULL,
	`value` DOUBLE NULL DEFAULT NULL,
	`stderr` DOUBLE NULL DEFAULT NULL,
	`sample_size` DOUBLE NULL DEFAULT NULL,
	`missing_value` INT(1) NULL DEFAULT '0',
	`missing_stderr` INT(1) NULL DEFAULT '0',
	`missing_sample_size` INT(1) NULL DEFAULT '0',
	`lag` INT(11) NOT NULL,
	`data_as_of_dt` datetime(0),
	`value_updated_timestamp` INT(11) NOT NULL,
	`computation_as_of_dt` datetime(0),
	`reference_dt` datetime(0),
	`signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`compressed_signal_key` varchar(100),
	`compressed_geo_key` varchar(100),
	`compressed_demog_key` varchar(100),
	`source` VARCHAR(32) NOT NULL,
	`signal` VARCHAR(64) NOT NULL,
	`geo_type` VARCHAR(12) NOT NULL,
	`geo_value` VARCHAR(12) NOT NULL,
	`is_latest_issue` BINARY(1) NOT NULL DEFAULT '0',
	`id` BIGINT(20) UNSIGNED,
	`process_status` varchar(2) default 'l',
	PRIMARY KEY (`signal_data_id`) USING BTREE,
	INDEX `comp_signal_key` (`compressed_signal_key`) USING BTREE,
	INDEX `comp_geo_key` (`compressed_geo_key`) USING BTREE
)
ENGINE=InnoDB
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
param1=prompt target=prompt --dir=ddl
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
