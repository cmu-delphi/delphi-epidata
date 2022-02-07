# *******************************************************************************************************
# File:     geo_dim_add_new_load.py
# Purpose:  Add entries from signal_load that are unmatched to geo_dim
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
INSERT INTO <param1>.geo_dim
(`geo_type`,`geo_value`,`compressed_geo_key`)
SELECT DISTINCT `geo_type`,`geo_value`,compressed_geo_key 
FROM <param1>.signal_load
WHERE compressed_geo_key NOT IN 
(SELECT distinct compressed_geo_key 
FROM <param1>.geo_dim)
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
