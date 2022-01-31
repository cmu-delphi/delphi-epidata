# *******************************************************************************************************
# File:     signal_dim_add_new_temp.py
# Purpose:  Add entries from temp_keys that are unmatched to signal_dim
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
INSERT INTO <param1>.signal_dim
(`source`,`signal`,`compressed_signal_key`)
SELECT col1,col2,compressed_key 
FROM <param1>.temp_keys
WHERE compressed_key NOT IN 
(SELECT compressed_signal_key 
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
