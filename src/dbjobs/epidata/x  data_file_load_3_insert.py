# *******************************************************************************************************
# data_file_load_3_insert.py
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
insert into epidata.covidcast
(`source`,
`signal`,
`time_type`,
`geo_type`,
`time_value`,
`geo_value`,
`value_updated_timestamp`,
`value`,
`stderr`,
`sample_size`,
`direction_updated_timestamp`,
`direction`,
`issue`,
`lag`,
`is_latest_issue`,
`is_wip`,
`missing_value`,
`missing_stderr`,
`missing_sample_size`)
select
`source`,
`signal`,
`time_type`,
`geo_type`,
`time_value`,
`geo_value`,
`value_updated_timestamp`,
`value`,
`stderr`,
`sample_size`,
`direction_updated_timestamp`,
`direction`,
`issue`,
`lag`,
`is_latest_issue`,
`is_wip`,
`missing_value`,
`missing_stderr`,
`missing_sample_size`
from epidata.signal_load sl
on duplicate key update
`value_updated_timestamp` = sl.`value_updated_timestamp`,
`value` = sl.`value`,
`stderr` = sl.`stderr`,
`sample_size` = sl.`sample_size`,
`direction_updated_timestamp` = sl.`direction_updated_timestamp`,
`direction` = sl.`direction`,
`lag` = sl.`lag`,
`is_latest_issue` = sl.`is_latest_issue`,
`is_wip` = sl.`is_wip`,
`missing_value` = sl.`missing_value`,
`missing_stderr` = sl.`missing_stderr`,
`missing_sample_size` = sl.`missing_sample_size`
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
