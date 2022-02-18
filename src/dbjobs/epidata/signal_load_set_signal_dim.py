# *******************************************************************************************************
# File:     signal_load_set_signal_dim.py
# Purpose:  Sets signal key from the signal_dim table
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
UPDATE <param1>.signal_load t1
INNER JOIN covid.signal_dim t2
USE INDEX(`compressed_signal_key_ind`)
ON t1.compressed_signal_key = t2.compressed_signal_key
SET t1.signal_key_id = t2.signal_key_id
'''

usage = '''
Usage:  --target=<db_alias> --param1=<schema>
'''

params = '''
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
