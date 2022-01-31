# *******************************************************************************************************
#
# Module:  dbutil.py
#
# Purpose: Utility functions to work with databases including threading
#
# *******************************************************************************************************
# Imports

import importlib
import datetime
import threading

import db_config
import pymysql
import redshift_connector

# *******************************************************************************************************
# Global variables

db_alias = "none"
db_type = "none"
job_file = "none"
task_file = "none"
param_file = "none"
log_file = "none"
num_threads = 1
start_param = 0
num_args = 0

param1_lines = []
param2_lines = []
param3_lines = []

l_param1_lines = 0
l_param2_lines = 0
l_param3_lines = 0

task_command = "none"
mod_command = ""
thread_results = ""

data_columns = []
data_rows = []
data_length = 0

db_list = []
db_length = 0

# *******************************************************************************************************
# ***** Main Calls *****
# *******************************************************************************************************
# runDbJob- Coordinates running of a DB job file

def runDbJob():

    global log_file
    global job_file
    global db_alias

    try:

        status_ok = True
        log_file = job_file + ".log"
        log_file = job_file.replace(".cfg",""
                                    )
        log_string = "\n\nProcessing Job File\n\n"
        log_string += "Job File: " + job_file + "\n"
        log_string += "DB Alias: " + db_alias + "\n"
        log_string += "Log File: " + log_file + "\n"
        log_string += "\n====================================================\n\n"

        addLog(log_string)
        print(log_string)
        log_string = ""

        # ***** Process Job File *****

        results = processJobFile()

        if (results[0:5] == "ERROR"):
            status_ok = False
        log_string += "\n==> " + results + "\n"

        # ***** Startup log entry *****

        addLog(log_string)
        print(log_string)

        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("runDbJob error: " + outerror)
        return False

# *******************************************************************************************************
# runDbTask- Coordinates running of a DB task file

def runDbTask():

    global db_alias
    global db_type
    global task_file
    global param_file
    global log_file
    global num_threads
    global start_param
    global num_args
    global mod_command

    try:

        status_ok = True
        job_output = ""

        # ****************************************
        # Process the task file

        return_message = processTaskFile()

        if (return_message[0:5] == "ERROR"):
            status_ok = False
        job_output += "==> " + return_message + "\n"

        # ****************************************
        # Process the parameters file (if any)

        if (status_ok == True):
            return_message = processParamFile()

            if (return_message[0:5] == "ERROR"):
                status_ok = False
            job_output += "==> " + return_message + "\n"

        # ****************************************
        # Entry for startup to screen and log

        start_time = datetime.datetime.now()

        start_message  = "\nStarting Task\n"
        start_message += "=============\n\n"

        start_message += "Task: " + task_file + "\n"
        start_message += "DB Alias: " + db_alias + "\n"
        start_message += "Log File: " + log_file + "\n"

        if (num_threads != 1):
            start_message += "Threads: " + str(num_threads) + "\n"

        if (param_file != "none"):
            start_message += "Parameter File: " + param_file + "\n"
            start_message += "Start Parameter: " + str(start_param)

        addLog(start_message)
        print(start_message)

        # ****************************************
        # Non threaded connect and call to DB

        if (num_threads == 1 and status_ok == True):

            conn = getDbConnection()
            test = str(conn)

            if (test[0:5] == "ERROR"):
                status_ok = False
                job_output += "==> ERROR connecting to alias " + db_alias + " (check db_config)\n"
                job_output += "==> " + conn + "\n"
            else:
                job_output += "==> Connected to database " + db_alias + "\n"

        # Non-threaded, process parameters

        if (num_threads == 1 and status_ok == True):

            test = processCommandParam(start_param)

            if (test[0:5] == "ERROR"):
                status_ok = False
                job_output += "==> " + test + "\n"

        # Non-threaded, execute SQL

        if (num_threads == 1 and status_ok == True):

            results = execSql(conn, mod_command)
            job_output += "--> Result: " + results + "\n"

        # ****************************************
        # Threaded create and join threads

        if (num_threads > 1 and status_ok == True):

            # Create threads for multi-threaded

            threads = []

            first_param = start_param
            last_param = start_param + num_threads

            for index in range(first_param, last_param):
                processCommandParam(index)
                t = threading.Thread(target=thread_task, args=(index,mod_command))
                threads.append(t)
                t.start()

        # Process threads for multi-threaded

        if (num_threads > 1 and status_ok == True):

            for t in threads:
                t.join()

            job_output += thread_results

        # ****************************************
        # Calculate time duration

        end_time = datetime.datetime.now()

        diff_time = end_time - start_time
        diff_time = diff_time.total_seconds()

        diff_hours = int(diff_time / 3600)
        diff_time = diff_time - diff_hours * 3600
        diff_minutes = int(diff_time / 60)
        diff_time = diff_time - diff_minutes * 60
        diff_seconds = "{:2.3f}".format(diff_time)

        diff_string = str(diff_hours) + " hours " + str(diff_minutes) + " minutes " + str(diff_seconds) + " seconds"

        job_output += "--> Elapsed time: " + diff_string + "\n"

        # ****************************************
        # Ending output

        end_message = "\nProcessing\n"
        end_message += "==========\n\n" + job_output

        end_message += "\nTask Completed\n"
        end_message += "==============\n\n"

        # Output any data rows

        if (status_ok == True):

            end_message += "DB Type: " + db_type + "\n\n"
            end_message += getDelimData()

        addLog(end_message)
        print(end_message)

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("runDbJob error: " + outerror)
        return False

# *******************************************************************************************************
# processJobArgs- process command line arguments to see if they want to set things

def processJobArgs(arguments):

    global db_alias
    global job_file
    global num_args

    try:

        num_args = len(arguments) - 1

        if len(arguments) > 1:
            job_file = arguments[1]

        if len(arguments) > 2:
            db_alias = arguments[2]

        return True

    except Exception as err2:

        print("processJobArgs error: " + str(err2))
        return False

# *******************************************************************************************************
# processTaskArgs- process command line arguments to see if they want to set things

def processTaskArgs(arguments):

    global db_alias
    global task_file
    global param_file
    global log_file
    global num_threads
    global start_param
    global num_args

    try:

        num_args = len(arguments) - 1

        if len(arguments) > 1:
            task_file = arguments[1]

        if len(arguments) > 2:
            db_alias = arguments[2]

        if len(arguments) > 3:
            log_file = arguments[3]

        if len(arguments) > 4:
            param_file = arguments[4]

        if len(arguments) > 5:
            num_threads = int(arguments[5])

        if len(arguments) > 6:
            start_param = int(arguments[6])

        return True

    except Exception as err2:

        print("processTaskArgs error: " + str(err2))
        return False

# *******************************************************************************************************
# processJobFile- processes the database job file

def processJobFile():

    global job_file
    global db_alias
    global log_file

    try:

        output = ""
        status_check = True

        job_db_alias = db_alias
        job_log_file = log_file

        # Read the job file

        job_file = "../jobs/" + job_file + ".cfg"

        if len(job_file) > 0:
            f = open(job_file,'r')
            file_text = f.read()
            f.close()
        else:
            output = "No job file specified"
            status_check = False

        # Break into lines

        if (status_check == True):

            file_lines = file_text.splitlines()

            for work_line in file_lines:

                if (len(work_line) != 0 and work_line[0] != "#"):

                    # Break line into parts

                    work_parts = work_line.split()
                    task_log = "none"

                    # Set values for tasks

                    if (len(work_parts) < 3):
                        task_type = "none"
                    else:
                        task_type = work_parts[0]
                        setTaskFile(work_parts[1])

                        if (work_parts[2] == "input"):
                            setDbAlias(job_db_alias)
                        else:
                            setDbAlias(work_parts[2])

                    if (len(work_parts) > 3):
                        task_log = work_parts[3]
                        setLogFile(task_log)
                    else:
                        setLogFile("none")

                    if (len(work_parts) > 4):
                        setParamFile(work_parts[4])
                    else:
                        setParamFile("none")

                    if (len(work_parts) > 5):
                        task_threads = int(work_parts[5])
                    else:
                        task_threads = 1

                    if (len(work_parts) > 6):
                        task_start = int(work_parts[6])
                    else:
                        task_start = 1

                    setThreading(task_threads,task_start)

                    # ***** Now run the job if it is valid

                    if (task_type != "dbtask"):
                        output += "Invalid job task entry: " + work_line
                    else:

                        output += "Running Task: " + work_parts[1] + " to DB " + db_alias

                        if (task_log == "none"):
                            output += " no log file ==> "
                        else:
                            output += " logging to " + job_log_file + ".log"

                        log_file = job_log_file
                        addLog(output)
                        print(output)
                        output = ""

                        log_file = job_log_file
                        runDbTask()

                        output += "\n\n====================================================\n\n"

                        log_file = job_log_file
                        addLog(output)
                        print(output)

                        output = ""
                        clearData()

        return "Job Completed"

    except Exception as err2:

        retString = "ERROR processJobFile: " + str(err2)
        return retString

# *******************************************************************************************************
# processTaskFile- processes the database task file (import)

def processTaskFile():

    global task_file
    global task_command

    try:

        # Import task file

        task_config = importlib.import_module(task_file)

        # Parse out the task config- mandatory

        if hasattr(task_config, 'command'):
            task_command = task_config.command
            retString = "Task file " + task_file + " loaded"
        else:
            return "ERROR Task file not found: " + task_file

        if (task_command[0] == "\n"):
            task_command = task_command[1:]

        return retString

    except Exception as err2:

        retString = "ERROR processTaskFile: " + str(err2)
        return retString

# *******************************************************************************************************
# processParamFile- processes the parameter file (import)

def processParamFile():

    global param_file
    global job_command

    global param1_lines
    global param2_lines
    global param3_lines
    global l_param1_lines
    global l_param2_lines
    global l_param3_lines

    try:

        # Import param file

        if (param_file == "none"):
            return "No parameter file"

        param_config = importlib.import_module(param_file)

        # ******************************
        # Capture the parameter strings

        if hasattr(param_config, 'param1'):
            s_param1 = param_config.param1
        else:
            s_param1 = ""

        if (s_param1[0] == "\n"):
            s_param1 = s_param1[1:]

        if hasattr(param_config, 'param2'):
            s_param2 = param_config.param2
        else:
            s_param2 = ""

        if (s_param2[0] == "\n"):
            s_param2 = s_param2[1:]

        if hasattr(param_config, 'param3'):
            s_param3 = param_config.param3
        else:
            s_param3 = ""

        if (s_param3[0] == "\n"):
            s_param3 = s_param3[1:]

        # ******************************
        # Split the parameters into line arrays

        param1_lines = s_param1.splitlines()
        param2_lines = s_param2.splitlines()
        param3_lines = s_param3.splitlines()

        l_param1_lines = len(param1_lines)
        l_param2_lines = len(param2_lines)
        l_param3_lines = len(param3_lines)

        retString = "Parameter file " + param_file + " loaded\n"
        retString += "    Param1: " + str(l_param1_lines)
        retString += " || Param2: " + str(l_param2_lines)
        retString += " || Param3: " + str(l_param3_lines)

        return retString

    except Exception as err2:

        retString = "ERROR processParamFile: " + str(err2)
        return retString

# *******************************************************************************************************

def processCommandParam(in_row):

    global task_command
    global mod_command
    global l_param1_lines
    global l_param2_lines
    global l_param3_lines
    global param1_lines
    global param2_lines
    global param3_lines

    in_row = in_row - 1     # zero based arrays

    try:

        mod_command = task_command

        if (l_param1_lines > in_row):
            mod_command = mod_command.replace("<param1>", param1_lines[in_row])
        elif (l_param1_lines != 0):
            return "ERROR insufficient param1 entries to process param1 item " + str(in_row+1)

        if (l_param2_lines > in_row):
            mod_command = mod_command.replace("<param2>", param2_lines[in_row])
        elif (l_param2_lines != 0):
            return "ERROR insufficient param1 entries to process param2 item " + str(in_row + 1)

        if (l_param3_lines > in_row):
            mod_command = mod_command.replace("<param3>", param3_lines[in_row])
        elif (l_param3_lines != 0):
            return "ERROR insufficient param3 entries to process param1 item " + str(in_row + 1)

        return "Command updated with parameters"

    except Exception as err2:

        return "ERROR processCommandParam: " + str(err2)

# *******************************************************************************************************
# addLog- adds content to log file

def addLog(strContent):

    global log_file

    try:

        if log_file == "none" or log_file == "nolog":
            return "No log file produced\n"
        else:

            out_file = "../log/" + log_file + ".log"
            dt_start = datetime.datetime.now()
            out_time = dt_start.strftime("%Y-%m-%d %H:%M:%S")

            strContent = "\n*************************\n\n" + out_time + ":\n" + strContent + "\n"

            if len(out_file) > 0:
                f = open (out_file,'a')
                f.write(strContent)
                f.close()
                retString = "Wrote to log file " + out_file + "\n"
            else:
                retString = "ERROR Add log: log file not specified\n"

        # ================================================================
        # Return results

        return retString

    # ================================================================
    # Exception handling

    except Exception as err2:

        retString = "ERROR addLog: " + str(err2)

        return retString

# *******************************************************************************************************
# Clear data- clears out the data columsn and rows arrays

def clearData():

    global data_columns
    global data_rows
    global data_length

    try:

        data_length = 0
        data_columns.clear()
        data_rows.clear()

        return "OK"

    except Exception as err2:

        outerror = str(err2)
        print("clearData:  " + outerror)

# *******************************************************************************************************
# execSql- executes SQL

def execSql(conn, db_sql):

    # ================================================================
    # Set up variables

    return_message = ""

    try:

        # ================================================================
        # Process/analyze SQL

        db_sql = db_sql.strip()

        word_array = db_sql.split(" ")
        first_word = word_array[0].lower()

        # ================================================================
        # Run sql- select

        if first_word == "select":

            # ****** Query the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)
            resultset = cursor.fetchall()

            # ***** Get counts *****

            column_count = len(cursor.description)
            return_rowcount = cursor.rowcount

            # ***** Parse column names to row 0 out *****

            rowsout = ""
            column_tuple = cursor.description

            for index, tuple in enumerate(column_tuple):
                rowsout += ',\"'
                rowsout += str(tuple[0])
                rowsout += '\"'

            rowsout = rowsout[1:]
            setDataColumns(rowsout)

            # ***** Add rows to the output

            rowsout = ""

            rCount = 0

            for resultrow in resultset:
                rowsout += ',['

                colsout = ""

                for counter in range(column_count):
                    colsout += ',\"' + str(resultrow[counter]) + '\"'

                colsout = colsout[1:]
                rowsout += colsout + ']'

                rCount = rCount + 1

            setDataRows(rowsout)

            # ***** Return status and message *****

            if (return_rowcount == -1):
                return_rowcount = rCount

            return_message = "Query selected " + str(return_rowcount) + " rows"

            # ***** Close *****

            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- insert

        if first_word == "insert":

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = str(cursor.rowcount) + " rows inserted"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- load

        if first_word == "load":

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = str(cursor.rowcount) + " rows loaded"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- truncate

        if first_word == "truncate":

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = "Table truncated"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- update

        if first_word == "update":

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = str(cursor.rowcount) + " rows updated"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- delete

        if first_word == "delete":

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = str(cursor.rowcount) + " rows deleted"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- create

        if first_word == "create":

            # ***** Get table name *****

            return_tablename = word_array[2]
            object_type = word_array[1]

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = object_type + " " + return_tablename + " created"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- alter

        if first_word == "alter":

            # ***** Get table name *****

            return_tablename = word_array[2]
            object_type = word_array[1]

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = object_type + " " + return_tablename + " altered"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- grant

        if first_word == "grant":

            # ***** Get table name *****

            return_tablename = ""
            object_type = word_array[1]

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = "Grant completed"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- drop

        if first_word == "drop":

            # ***** Get table name *****

            return_tablename = word_array[2]
            object_type = word_array[1]

            # ****** Insert the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)

            # ***** Return status and message *****

            return_message = object_type + " " + return_tablename + " dropped"

            # ***** Commit and Close *****

            conn.commit()
            cursor.close()
            conn.close()

        # ================================================================
        # Run sql- show

        if first_word == "show":

            # ****** Query the data *****

            cursor = conn.cursor()
            dataout = cursor.execute(db_sql)
            resultset = cursor.fetchall()

            # ***** Get counts *****

            column_count = len(cursor.description)
            return_rowcount = cursor.rowcount

            # ***** Parse column names to row 0 out *****

            rowsout = ""
            column_tuple = cursor.description

            for index, tuple in enumerate(column_tuple):
                rowsout += ',\"'
                rowsout += str(tuple[0])
                rowsout += '\"'

            rowsout = rowsout[1:]
            setDataColumns(rowsout)

            # ***** Add rows to the output

            rowsout = ""

            for resultrow in resultset:
                rowsout += ',['

                colsout = ""

                for counter in range(column_count):
                    colsout += ',\"' + str(resultrow[counter]) + '\"'

                colsout = colsout[1:]
                rowsout += colsout + ']'

            setDataRows(rowsout)

            # **************************************************

            # ***** Return status and message *****

            return_message = "Show selected " + str(return_rowcount) + " rows"

            # ***** Close *****

            cursor.close()
            conn.close()

    # ================================================================
    # Exception handling

    except pymysql.MySQLError as err:

        outerror = str(err).replace('"', '')
        return "ERROR execSql DB error:  " + outerror

    except Exception as err2:

        outerror = str(err2)
        return "ERROR execSql:  " + outerror

    # ================================================================
    # Return results

    return return_message

# *******************************************************************************************************

def getDbConfigs():

    global db_list
    global db_length

    try:

        local_dict = dir(db_config)

        for name in local_dict:

            if (name[:7] == "dbtype_"):
                if (name[7:] != ""):
                    db_list.append(name[7:])

        return "OK"

    except Exception as err2:

        outerror = str(err2)
        print("getDbConfigs:  " + outerror)

# *******************************************************************************************************
# getDbConnection- returns database connection

def getDbConnection():

    global db_alias
    global db_type

    try:

        # ================================================================
        # Get configuration

        keystring = "dbtype_" + db_alias
        if hasattr(db_config, keystring):
            db_type = getattr(db_config, keystring)
        else:
            db_type = "NOT FOUND"

        keystring = "host_" + db_alias
        if hasattr(db_config, keystring):
            dbhost = getattr(db_config, keystring)
        else:
            dbhost = "NOT FOUND"

        keystring = "user_" + db_alias
        if hasattr(db_config, keystring):
            dbuser = getattr(db_config, keystring)
        else:
            dbuser = "NOT FOUND"

        keystring = "password_" + db_alias
        if hasattr(db_config, keystring):
            dbpassword = getattr(db_config, keystring)
        else:
            dbpassword = "NOT FOUND"

        keystring = "dbname_" + db_alias
        if hasattr(db_config, keystring):
            dbname = getattr(db_config, keystring)
        else:
            dbname = "NOT FOUND"

        keystring = "port_" + db_alias
        if hasattr(db_config, keystring):
            dbport = getattr(db_config, keystring)
        else:
            dbport = 0

        # ================================================================
        # Set up variables

        if (db_type == "mysql"):

            db_conn = pymysql.connect(host=dbhost,
                                      port=dbport,
                                      database=dbname,
                                      user=dbuser,
                                      password=dbpassword)

        elif (db_type == "redshift"):

            db_conn = redshift_connector.connect(host=dbhost,
                                                 port=dbport,
                                                 database=dbname,
                                                 user=dbuser,
                                                 password=dbpassword)

        else:

            return "ERROR getDbConnection: db_type " + db_type + " not supported"

        return db_conn

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        return "ERROR getDbConnection: " + outerror

# *******************************************************************************************************

def getDelimData():

    global data_columns
    global data_rows
    global data_length

    try:

        dataout = ""

        for row in range(data_length):

            # ***** Column Headings *****

            column_list = data_columns[row].replace('","', ' || ')
            column_list = column_list.replace('["', '')
            column_list = column_list.replace('"]', '')

            heading_length = len(column_list)
            column_list += "\n"
            for item in range(heading_length):
                column_list += "-"
            column_list += "\n"

            dataout += column_list

            # ***** Rows of Data *****

            data_list = data_rows[row]
            data_list = data_list.replace('"],["', '\n')
            data_list = data_list.replace('","', ' || ')
            data_list = data_list.replace('"]', '')
            data_list = data_list.replace(',["', '')

            dataout += data_list + "\n\n"

        return dataout

    except Exception as err2:

        outerror = str(err2)
        print("getDelimData:  " + outerror)

# *******************************************************************************************************

def getJsonData():

    global data_columns
    global data_rows
    global data_length

    try:

        dataout = ""

        for row in range(data_length):

            if (row == 0):
                dataout += data_columns[row]
            else:
                dataout += "," + data_columns[row]

            dataout += data_rows[row]

        return dataout

    except Exception as err2:

        outerror = str(err2)
        print("getJsonData:  " + outerror)

# *******************************************************************************************************

def setDataColumns(strColumns):

    global data_columns
    global data_length

    try:

        strColumns = "[" + strColumns + "]"
        strColumns = strColumns.replace("b'", "")
        strColumns = strColumns.replace("'", "")

        data_columns.append(strColumns)
        data_length = data_length + 1

    except Exception as err2:

        outerror = str(err2)
        print("setDataColumns:  " + outerror)

# *******************************************************************************************************

def setDataRows(strRows):

    global data_rows
    global data_length

    try:

        data_rows.append(strRows)

    except Exception as err2:

        outerror = str(err2)
        print("setDataRows:  " + outerror)

# *******************************************************************************************************

def thread_task(thread_index,run_sql):

    global job_db
    global thread_results
    global tout_rows
    global mod_command

    dbconn = getDbConnection()

    results = execSql(dbconn, run_sql)

    thread_results += "--> Thread " + str(thread_index) + " : "
    thread_results += results + "\n"

# *******************************************************************************************************
# promptDbAlias- prompts at os level for the database alias

def promptDbAlias():

    global db_alias

    try:

        db_alias = input("Database Alias (mandatory): ")
        if (db_alias == ""):
            print("\n***** Database Alias required, try again\n")
            return False

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptDbAlias error: " + outerror)
        return False

# *******************************************************************************************************
# promptJobFile- prompts at os level for the job file

def promptJobFile():

    global job_file

    try:

        job_file = input("Job File (mandatory, <file in jobs folder without .cfg extension>): ")
        if (job_file == ""):
            print("\n***** Job File required, try again\n")
            return False

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptJobFile error: " + outerror)
        return False

# *******************************************************************************************************
# promptLogFile- prompts at os level for the log file

def promptLogFile():

    global log_file

    try:

        log_file = input("Job Log File (default none, without .log extension): ")

        if (log_file == ""):
            log_file = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptLogFile error: " + outerror)
        return False

# *******************************************************************************************************
# promptParamFile- prompts at os level for the parameter file

def promptParamFile():

    global param_file

    try:

        param_file = input("Job Parameter File (optional. <directory.file> without .py extension): ")
        if (param_file == ""):
            param_file = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptParamFile error: " + outerror)
        return False

# *******************************************************************************************************
# promptTaskFile- prompts at os level for the task file

def promptTaskFile():

    global task_file

    try:

        task_file = input("Task File (mandatory, <directory.file> without .py extension): ")
        if (task_file == ""):
            print("\n***** Task File required, try again\n")
            return False

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptTaskFile error: " + outerror)
        return False

# *******************************************************************************************************
# promptThreading- prompts at os level for the threading parameters

def promptThreading():

    global num_threads
    global start_param

    try:

        num_threads = input("Number of threads (integer, default 1): ")
        if (num_threads == ""):
            num_threads = 1
        else:
            num_threads = int(num_threads)
        start_param = input("Starting parameter (integer, default 1): ")
        if (start_param == ""):
            start_param = 1
        else:
            start_param = int(start_param)

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptThreading error: " + outerror)
        return False

# *******************************************************************************************************
# setDbAlias- sets the database alias

def setDbAlias(strAlias):

    global db_alias

    try:

        db_alias = strAlias

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("setDbAlias error: " + outerror)
        return False

# *******************************************************************************************************
# setJobFile- sets the job file

def setJobFile(strFile):

    global job_file

    try:

        job_file = strFile

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("setJobFile error: " + outerror)
        return False

# *******************************************************************************************************
# setLogFile- sets the log file

def setLogFile(strFile):

    global log_file

    try:

        log_file = strFile

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("setLogFile error: " + outerror)
        return False

# *******************************************************************************************************
# setParamFile- sets the parameter file

def setParamFile(strFile):

    global param_file

    try:

        param_file = strFile

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("setParamFile error: " + outerror)
        return False

# *******************************************************************************************************
# setTaskFile- sets the task file

def setTaskFile(strFile):

    global task_file

    try:

        task_file = strFile

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("setTaskFile error: " + outerror)
        return False

# *******************************************************************************************************
# setThreading- sets the threading parameters

def setThreading(intThreads, intStart):

    global num_threads
    global start_param

    try:

        num_threads = intThreads
        start_param = intStart

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("setThreading error: " + outerror)
        return False

# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
