# *******************************************************************************************************
# mig_history_load.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
insert into covid.signal_history 
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
is_latest_issue,
missing_value,
missing_stderr,
missing_sample_size,
`id`
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
is_latest_issue,
missing_value,
missing_stderr,
missing_sample_size,
`id`
from covid.signal_load sl
INNER JOIN covid.signal_dim sd
USE INDEX(`compressed_signal_key_ind`)
ON sd.compressed_signal_key = sl.compressed_signal_key
INNER JOIN covid.geo_dim gd
USE INDEX(`compressed_geo_key_ind`)
ON gd.compressed_geo_key = sl.compressed_geo_key
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
