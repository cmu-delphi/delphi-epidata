# *******************************************************************************************************
#
# Module:  dbutil.py
# Version: 7.1
#
# Purpose: Utility functions to work with databases including threading
#
# *******************************************************************************************************
# Imports

import db_config
import pymysql
import redshift_connector
import json

# *******************************************************************************************************
# Global variables

db_alias = "none"
db_type = "none"

gMessage = "none"
gColumnCount = 0
gRowCount = 0
gDataJsonList = []
gDataLength = 0
gConn = ""
gCursor = False
gResultSet = ""
gSqlWords = []
gDbObject = ""

data_columns = []
data_rows = []
data_length = 0

db_list = []
db_length = 0

# *******************************************************************************************************
# ***** Processing Modules *****
# *******************************************************************************************************

# getDbConnection- sets database connection

def getDbConnection(in_db_alias):

    global db_alias
    global db_type

    global gMessage
    global gConn
    global gCursor

    try:

        # ================================================================
        # Get configuration

        db_alias = in_db_alias

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

            gConn = pymysql.connect(host=dbhost,
                                      port=dbport,
                                      database=dbname,
                                      user=dbuser,
                                      password=dbpassword)

        elif (db_type == "redshift"):

            gConn = redshift_connector.connect(host=dbhost,
                                                 port=dbport,
                                                 database=dbname,
                                                 user=dbuser,
                                                 password=dbpassword)

        else:

            gMessage = "ERROR getDbConnection: db_alias " + db_alias + " not found"
            return gMessage

        gMessage = "Connected to " + db_alias + " (" + db_type + ")"
        return gMessage

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        gMessage = "ERROR getDbConnection: " + outerror
        return gMessage

# *******************************************************************************************************

# closeDbConnection- closes database connection and cursor

def closeDbConnection():

    global db_alias
    global db_type
    global gMessage

    global gConn
    global gCursor

    try:

        # ================================================================
        # Get configuration

        if (gCursor != False):
            gCursor.close()
            gConn.close()
            gMessage = "Closed connection and cursor to " + db_alias
        else:
            gMessage = "Connection not open"

        db_alias = "none"
        db_type = "none"

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        gMessage = "ERROR closeDbConnection: " + outerror
        return False

# *******************************************************************************************************

# execSql- executes SQL

def execSql(db_sql):

    # ================================================================
    # Set up variables

    global gSqlWords
    global gConn
    global gMessage

    try:

        # ================================================================
        # Process/analyze SQL

        db_sql = db_sql.strip()

        lConn = gConn

        lCursor = lConn.cursor()
        lCursor.execute(db_sql)
        lConn.commit()

        pOut = processResults(lCursor,db_sql)

        lCursor.close()

        return pOut

    # ================================================================
    # Exception handling

    except pymysql.MySQLError as err:

        outerror = str(err).replace('"', '')
        pOut = "ERROR execSql DB error:  " + outerror
        return pOut

    except Exception as err2:

        outerror = str(err2)
        pOut = "ERROR execSql:  " + outerror
        return pOut

# *******************************************************************************************************

# processResults- process the cursor results

def processResults(inCursor, inSql):

    # ================================================================
    # Set up variables

    global gRowCount
    global gColumnCount

    global gDataJsonList
    global gDataLength

    global gDbObject

    try:

        # ================================================================
        # Determine global counts

        lSqlWords = inSql.split(" ")

        gRowCount = inCursor.rowcount
        gColumnCount = 0

        # ================================================================
        # Process result sets

        if lSqlWords[0].lower() == "select" or lSqlWords[0].lower() == "show":

            # Clear out the data lists for future work

            gDataLength = 0

            # ****** Query the data *****

            resultset = inCursor.fetchall()

            # ***** Get counts *****

            gColumnCount = len(inCursor.description)

            # ***** Parse column names to row 0 out *****

            rowsout = ""
            column_tuple = inCursor.description

            for index, tuple in enumerate(column_tuple):
                rowsout += ',\"'
                rowsout += str(tuple[0]).replace("b'", "")
                rowsout += '\"'

            rowsout = "[" + rowsout[1:] + "]"
            gDataJsonList.append(rowsout)

            # ***** Add rows to the output

            rowsout = ""

            rCount = 0

            for resultrow in resultset:
                rowsout = '['

                colsout = ""

                for counter in range(gColumnCount):
                    colsout += ',\"' + str(resultrow[counter]) + '\"'

                colsout = colsout[1:]
                rowsout += colsout + ']'

                gDataJsonList.append(rowsout)

                rCount = rCount + 1

            # ***** Return status and message *****

            if (gRowCount == -1):
                gRowCount = rCount

        # ================================================================
        # Set message with results

        lMessage = "processResults"

        # ********************

        if lSqlWords[0].lower() == "show":

            lDbObject = lSqlWords[1]
            gDbObject = lDbObject
            lMessage = str(gRowCount) + " results shown from " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "select":

            lDbObject = "table"

            for idx, sWord in enumerate(gSqlWords):
                if (sWord.lower() == "from"):
                    lDbObject = lSqlWords[idx+1]

            gDbObject = lDbObject
            lMessage = str(gRowCount) + " rows selected from " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "insert":

            lDbObject = lSqlWords[2]
            gDbObject = lDbObject
            lMessage = str(gRowCount) + " rows inserted into " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "update":

            lDbObject = lSqlWords[1]
            gDbObject = lDbObject
            lMessage = str(gRowCount) + " rows updated in " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "delete":

            lDbObject = lSqlWords[2]
            gDbObject = lDbObject
            lMessage = str(gRowCount) + " rows deleted from " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "truncate":

            lDbObject = lSqlWords[2]
            gDbObject = lDbObject
            lMessage = "Truncated " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "load":

            lDbObject = lSqlWords[7]
            gDbObject = lDbObject
            lMessage = str(gRowCount) + " rows loaded into " + lDbObject

        # ********************

        elif lSqlWords[0].lower() == "create":

            if (lSqlWords[1] == "or"):
                lDbObject = lSqlWords[4]
            else:
                lDbObject = lSqlWords[2]

            gDbObject = lDbObject

            lMessage = lDbObject + " created"

        # ********************

        elif lSqlWords[0].lower() == "alter":

            lDbObject = lSqlWords[2]
            gDbObject = lDbObject
            lMessage = lDbObject + " altered"

        # ********************

        elif lSqlWords[0].lower() == "drop":

            lDbObject = lSqlWords[2]
            gDbObject = lDbObject
            lMessage = lDbObject + " dropped"

        # ********************

        elif lSqlWords[0].lower() == "grant":

            lDbObject = "grant"

            for idx, sWord in enumerate(lSqlWords):
                if (sWord.lower() == "to"):
                    lDbObject = lSqlWords[idx + 1]

            gDbObject = lDbObject
            lMessage = "Grant completed for " + gDbObject

        # ********************

        else:

            lMessage = "Processed command " + lSqlWords[0]

            # ********************

        return lMessage

    # ================================================================
    # Exception handling

    except pymysql.MySQLError as err:

        outerror = str(err).replace('"', '')
        lMessage = "ERROR processResults DB error:  " + outerror
        return lMessage

    except Exception as err2:

        outerror = str(err2)
        lMessage = "ERROR processResults:  " + outerror
        return lMessage

# *******************************************************************************************************
# ***** Data Modules *****
# *******************************************************************************************************







# *******************************************************************************************************
# ***** Support Modules *****
# *******************************************************************************************************

def getDbConfigs():

    global db_list
    global db_length
    global gMessage

    try:

        local_dict = dir(db_config)

        for name in local_dict:

            if (name[:7] == "dbtype_"):
                if (name[7:] != ""):
                    db_list.append(name[7:])

        return "OK"

    except Exception as err2:

        outerror = str(err2)
        print("ERROR getDbConfigs:  " + outerror)

# *******************************************************************************************************

def getMessage():

    global gMessage
    return gMessage

# *******************************************************************************************************

def getColumnCount():

    global gColumnCount
    return gColumnCount

# *******************************************************************************************************

def getRowCount():

    global gRowCount
    return gRowCount

# *******************************************************************************************************

def getDataRow(intRow):

    global gDataJsonList

    if (intRow >=0 and intRow <= len(gDataJsonList)):
        return gDataJsonList[intRow]
    else:
        return "Row Not Found"

# *******************************************************************************************************

def getDataColumnNames():

    global gDataJsonList
    return gDataJsonList[0]

# *******************************************************************************************************

def getDataCell(intRow,intCol):

    global gDataJsonList


    if (intRow >=0 and intRow <= len(gDataJsonList)):

        workRow = gDataJsonList[intRow]
        rowData = json.loads(workRow)

        if (intCol >= 0 and intCol <= len(rowData)):
            outData = rowData[intCol - 1]
        else:
            outData = "Cell not found"

    else:
        outData = "Row Not Found"

    return outData

# *******************************************************************************************************

def getJsonData():

    global gDataJsonList

    outString = ""

    for wRow in gDataJsonList:
        outString += "," + wRow

    outString = "{" + outString[1:] + "}"

    return outString

# *******************************************************************************************************

def getDelimData():

    global gDataJsonList

    outString = ""

    for wRow in gDataJsonList:

        wRow = wRow.replace('["', '')
        wRow = wRow.replace('"]','')
        wRow = wRow.replace('","',' || ')
        outString += wRow + "\n"

    outString = outString.replace("\n","\n\n",1)

    return outString

# *******************************************************************************************************

# Clear data- clears out the data columsn and rows arrays

def clearData():

    global gDataJsonList
    global gRowCount
    global gColumnCount
    global gMessage

    gRowCount = 0
    gColumnCount = 0
    gDataJsonList = []
    gMessage = "Data Cleared"

# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
