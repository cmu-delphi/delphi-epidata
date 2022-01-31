# ************************************************************************************
# Module:  job_test.py
# ************************************************************************************
# Imports

import sys
import os
import dbutil

# ************************************************************************************
# ***** Set path to include current directory

sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/..')

# ************************************************************************************
# ***** Print heading, set status

print("**************************************************\n")

print("Job Test\n")

target = input("Target: ")

# ************************************************************************************

wSql = "select * from covid.signal_dim"
#wSql = "show processlist"
#wSql = "insert into covid.signal_dim (source) values ('test')"
#wSql = "update covid.signal_dim set source='testing' where source='test'"
#wSql = "delete from covid.signal_dim where source='testing'"
#wSql = "truncate table covid.temp_keys"
#wSql = "create table covid.test1 (test1c varchar(10))"
#wSql = "ALTER TABLE covid.test1 ADD test4 VARCHAR(2)"
#wSql = "DROP TABLE covid.test1"
#wSql = "grant select on covid.signal_dim to awstest"
#wSql = "revoke select on covid.signal_dim from awstest"

outstatus = dbutil.getDbConnection(target)
print(str(outstatus) + "- " + dbutil.getMessage())

outstatus = dbutil.execSql(wSql)
print(str(outstatus) + "- " + dbutil.getMessage())

output = dbutil.closeDbConnection()
print(str(output) + "- " + dbutil.getMessage())

print("\nColumns: " + str(dbutil.getColumnCount()))
print("Rows: " + str(dbutil.getRowCount()))

print("\nData columns: " + dbutil.getDataColumnNames())
print("\nData row 1: " + dbutil.getDataRow(1))
print("Data row 2: " + dbutil.getDataRow(2))
print("Data row 22: " + dbutil.getDataRow(22))
print("Row 2 col 2: " + dbutil.getDataCell(2,2))
print("Row 1 col 5: " + dbutil.getDataCell(1,5))

workString = dbutil.getJsonData()
workString = workString.replace("],[","],\n[")
print("\nJSON data:\n\n" + workString)

print("\nDelim data:\n\n" + dbutil.getDelimData())

print("Rows: " + str(dbutil.getRowCount()))
print("Data row 1: " + dbutil.getDataRow(1))
print("Clear")
dbutil.clearData()
print("Rows: " + str(dbutil.getRowCount()))
print("Data row 1: " + dbutil.getDataRow(1))

# ************************************************************************************
# ************************************************************************************
