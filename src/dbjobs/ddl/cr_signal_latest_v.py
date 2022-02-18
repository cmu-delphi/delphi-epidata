# *******************************************************************************************************
# cr_signal_latest_v.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
create or replace view <param1>.signal_latest_v as
select `t2`.`source` AS `source`,
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
from ((<param1>.`signal_latest` `t1` 
join <param1>.`signal_dim` `t2` 
USE INDEX (PRIMARY) 
on((`t1`.`signal_key_id` = `t2`.`signal_key_id`))) 
join <param1>.`geo_dim` `t3` 
USE INDEX (PRIMARY) 
on((`t1`.`geo_key_id` = `t3`.`geo_key_id`)))
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
