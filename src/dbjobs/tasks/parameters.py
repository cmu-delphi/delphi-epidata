# *******************************************************************************************************
# File:     parameters.py
# Purpose:  show key mysql parameters
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
SELECT 'autocommit' __parameter__,@@GLOBAL.autocommit __value__
UNION
SELECT 'character_set_database',@@GLOBAL.character_set_database
UNION
SELECT 'connect_timeout',@@GLOBAL.connect_timeout
UNION
SELECT 'datadir',@@GLOBAL.datadir
UNION
SELECT 'default_storage_engine',@@GLOBAL.default_storage_engine
UNION
SELECT 'general_log_file',@@GLOBAL.general_log_file
UNION
SELECT 'hostname',@@GLOBAL.hostname
UNION
SELECT 'init_file',@@GLOBAL.init_file
UNION
SELECT 'innodb_log_files_in_group',@@GLOBAL.innodb_log_files_in_group
UNION
SELECT 'innodb_log_file_size',@@GLOBAL.innodb_log_file_size
UNION
SELECT 'local_infile',@@GLOBAL.local_infile
UNION
SELECT 'log_error',@@GLOBAL.log_error
UNION
SELECT 'port',@@GLOBAL.port
UNION
SELECT 'system_time_zone',@@GLOBAL.system_time_zone
UNION
SELECT 'version',@@GLOBAL.version
'''

usage = '''
Usage:  --target=<db_alias>
'''

params = '''
target=prompt
'''

# *******************************************************************************************************
# End
# *******************************************************************************************************
