# *******************************************************************************************************
# File:     signal_load_j.py
# Purpose:  Job to task data loaded into signal_load by acquisition and populate schema
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

params = '''
'''

tasks = '''
dbtask task=signal_load_set_comp_keys param1=covid
dbtask task=signal_load_mark_batch param1=covid
#
dbtask task=signal_dim_add_new_load param1=covid
dbtask task=geo_dim_add_new_load param1=covid
dbtask task=signal_history_load param1=covid
dbtask task=signal_latest_load param1=covid
#
dbtask task=signal_load_delete_processed param1=covid
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
