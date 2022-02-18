# *******************************************************************************************************
# cr_tbl_signal_latest.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
CREATE TABLE <param1>.signal_latest (
	`signal_data_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
	`signal_key_id` bigint(20) unsigned,
	`geo_key_id` bigint(20) unsigned,
	`demog_key_id` bigint(20) unsigned,
	`issue` INT(11),
	`time_type` VARCHAR(12) NOT NULL,
	`time_value` INT(11) NOT NULL,
	`data_as_of_dt` datetime(0),
	`reference_dt` datetime(0),
	`value` DOUBLE NULL DEFAULT NULL,
	`stderr` DOUBLE NULL DEFAULT NULL,
	`sample_size` DOUBLE NULL DEFAULT NULL,
	`lag` INT(11) NOT NULL,
	`value_updated_timestamp` INT(11) NOT NULL,
	`computation_as_of_dt` datetime(0),
	`missing_value` INT(1) NULL DEFAULT '0',
	`missing_stderr` INT(1) NULL DEFAULT '0',
	`missing_sample_size` INT(1) NULL DEFAULT '0',
	PRIMARY KEY (`signal_data_id`) USING BTREE,
	UNIQUE INDEX `value_key` (`signal_key_id`,`geo_key_id`,`time_value`) USING BTREE
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
