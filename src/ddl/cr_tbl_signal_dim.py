# *******************************************************************************************************
# cr_tbl_signal_dim.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
CREATE TABLE <param1>.signal_dim (
	`signal_key_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT, 
	`source` varchar(32),
	`signal` varchar(64),
	`compressed_signal_key` varchar(100),
	PRIMARY KEY (`signal_key_id`) USING BTREE,
	unique INDEX `compressed_signal_key_ind` (`compressed_signal_key`) USING BTREE
)
ENGINE=InnoDB
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************

