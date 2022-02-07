# *******************************************************************************************************
# File:     signal_load_migrate.py
# Purpose:  Migrate data from covidcast using signal load in batches
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
insert into covid.signal_load 
(`issue`,
`source`,
`signal`,
geo_type,
geo_value,
time_type,
time_value,
`value`,
stderr,
sample_size,
`lag`,
value_updated_timestamp,
is_latest_issue,
missing_value,
missing_stderr,
missing_sample_size,
`id`,
`compressed_signal_key`, 
`compressed_geo_key`) 
select `issue`,
`source`,
`signal`,
geo_type,
geo_value,
time_type,
time_value,
`value`,
stderr,
sample_size,
`lag`,
value_updated_timestamp,
is_latest_issue,
missing_value,
missing_stderr,
missing_sample_size,
`id`,
md5(CONCAT(`source`,`signal`)), 
md5(CONCAT(`geo_type`,`geo_value`)) 
from epidata.covidcast cc
use index(`primary`)
where cc.id >= <param1> 
and cc.id <= <param2>
'''

usage = '''
Usage:  --target=<db_alias> --param1=<start_id> --param2=<end_id>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
