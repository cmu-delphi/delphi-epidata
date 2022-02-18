# *******************************************************************************************************
# File:     signal_dim_add_new_load.py
# Purpose:  Add entries from signal_load that are unmatched to signal_dim
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
INSERT INTO <param1>.signal_dim 
(`source`,`signal`,`compressed_signal_key`) 
SELECT DISTINCT `source`,`signal`,compressed_signal_key 
FROM <param1>.signal_load 
WHERE compressed_signal_key NOT IN 
(SELECT distinct compressed_signal_key 
FROM <param1>.signal_dim)
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
