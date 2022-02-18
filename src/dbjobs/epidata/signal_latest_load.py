# *******************************************************************************************************
# signal_latest_load.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
insert into <param1>.signal_latest 
(
signal_data_id,
signal_key_id,
geo_key_id,
demog_key_id,
issue,
data_as_of_dt,
time_type,
time_value,
`value`,
stderr,
sample_size,
`lag`,
value_updated_timestamp,
computation_as_of_dt,
missing_value,
missing_stderr,
missing_sample_size
) 
select 
signal_data_id,
sd.signal_key_id,
gd.geo_key_id,
0,
issue,
data_as_of_dt,
time_type,
time_value,
`value`,
stderr,
sample_size,
`lag`,
value_updated_timestamp,
computation_as_of_dt,
missing_value,
missing_stderr,
missing_sample_size
from <param1>.signal_load sl 
INNER JOIN <param1>.signal_dim sd 
USE INDEX(`compressed_signal_key_ind`) 
ON sd.compressed_signal_key = sl.compressed_signal_key 
INNER JOIN <param1>.geo_dim gd 
USE INDEX(`compressed_geo_key_ind`) 
ON gd.compressed_geo_key = sl.compressed_geo_key 
where process_status='b'
and is_latest_issue=1
on duplicate key update 
`value_updated_timestamp` = sl.`value_updated_timestamp`,
`value` = sl.`value`,
`stderr` = sl.`stderr`,
`sample_size` = sl.`sample_size`,
`lag` = sl.`lag`,
`missing_value` = sl.`missing_value`,
`missing_stderr` = sl.`missing_stderr`,
`missing_sample_size` = sl.`missing_sample_size` 
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
