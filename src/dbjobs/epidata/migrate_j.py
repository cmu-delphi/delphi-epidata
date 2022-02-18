# *******************************************************************************************************
# File:     migrate_j.py
# Purpose:  Job to migrate a batch of covidcast data to the new schema
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

params = '''
'''

tasks = '''
dbtask task=signal_load_migrate parfile=migrate_p threads=1
#
dbtask task=signal_dim_add_new_load param1=covid
dbtask task=geo_dim_add_new_load param1=covid
dbtask task=signal_history_load param1=covid
dbtask task=signal_latest_load param1=covid
#
dbtask task=signal_load_drop_signal_index param1=covid
dbtask task=signal_load_drop_geo_index param1=covid
dbtask task=signal_load_delete_migrate param1=covid
dbtask task=signal_load_create_signal_index param1=covid
dbtask task=signal_load_create_geo_index param1=covid
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
