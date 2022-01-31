# *******************************************************************************************************
# File:     temp_keys_signal_load.py
# Purpose:  Load temp keys with unique compressed values from signal_load
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
INSERT INTO <param1>.temp_keys
(compressed_key,col1,col2,key_id) 
SELECT DISTINCT compressed_signal_key,
`source`,
`signal`,
'0'
FROM <param1>.signal_load
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
