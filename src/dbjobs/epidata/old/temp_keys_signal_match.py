# *******************************************************************************************************
# File:     temp_keys_signal_match.py
# Purpose:  Match temp keys with entries in signal_dim
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
UPDATE <param1>.temp_keys t1
INNER JOIN <param1>.signal_dim t2
force index (`compressed_signal_key_ind`)
ON t1.compressed_key = t2.compressed_signal_key
SET t1.key_id = t2.signal_key_id
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
