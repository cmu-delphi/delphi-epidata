# *******************************************************************************************************
# File:     replica_status.py
# Purpose:  show status of replication from a secondary server
# *******************************************************************************************************
# *******************************************************************************************************
# Command to be run

command = '''
SELECT 'Primary Host' __Param__, HOST __Value__
FROM mysql.slave_master_info
UNION
SELECT 'Primary User',user_name
FROM mysql.slave_master_info
UNION
SELECT 'Primary Port',port
FROM mysql.slave_master_info
UNION
SELECT 'Primary Log Name',master_log_name
FROM mysql.slave_master_info
UNION
SELECT 'Read Primary Log Pos',master_log_pos
FROM mysql.slave_master_info
UNION
SELECT 'Exec Primary Log Pos',master_log_pos
FROM mysql.slave_relay_log_info
UNION
SELECT 'Secondary Running',service_state
FROM performance_schema.replication_connection_status
UNION
SELECT 'Last IO Error #',last_error_number
FROM performance_schema.replication_connection_status
UNION
SELECT 'Last UI Error Message',last_error_message
FROM performance_schema.replication_connection_status
UNION
SELECT 'Secondary SQL Running',service_state
FROM performance_schema.replication_applier_status_by_worker
UNION
SELECT 'Last SQL Error #',last_error_number
FROM performance_schema.replication_applier_status_by_worker
UNION
SELECT 'Last SQL Error',last_error_message
FROM performance_schema.replication_applier_status_by_worker
UNION
SELECT 'Secondary IO State',t.processlist_state
FROM performance_schema.threads t
RIGHT JOIN 
performance_schema.replication_applier_status_by_worker rss
ON rss.thread_id = t.thread_id
UNION
SELECT 'Seconds Behind Primary',t.processlist_time
FROM performance_schema.threads t
RIGHT JOIN
performance_schema.replication_connection_status rcs
ON rcs.thread_id = t.thread_id
UNION
SELECT 'Secondary SQL Running State',processlist_state
FROM performance_schema.threads t
RIGHT JOIN
performance_schema.replication_connection_status rcs
ON rcs.thread_id = t.thread_id
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
