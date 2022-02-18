# *******************************************************************************************************
#
# Module:  jobutil.py
# Version: 7.1
#
# Purpose: Utility functions to running batches, jobs and tasks
#
# *******************************************************************************************************
# Imports

import importlib
import dbutil
import datetime
import threading

# *******************************************************************************************************
# Global variables

# ***** Control *****

gStatus = "ok"
gMessage = ""
gData = ""

gTaskFile = "none"
gJobFile = "none"
gLogFile = "none"
gPrompt = False
gBatch = False

# ***** Jobs *****

gJTasks = ""
gJParams = ""

gJTarget = "none"
gJParfile = "none"
gJDir = "tasks"
gJParam1 = ""
gJParam2 = ""
gJParam3 = ""
gJStartpar = 1
gJThreads = 1
gTUsage = "No help available"

# ***** Tasks *****

gTCommand = ""
gTParams = ""

gTTarget = "none"
gTParfile = "none"
gTDir = "tasks"
gTParam1 = "none"
gTParam2 = "none"
gTParam3 = "none"
gTStartpar = 1
gTThreads = 1
gTType = "dbtask"

gModCommand = ""

# ***** Parfile *****

gPParlist = ""
gPParams = ""

gPParlist1 = []
gPParlist2 = []
gPParlist3 = []

gJParlist1 = []
gJParlist2 = []
gJParlist3 = []

wparam1 = []
wparam2 = []
wparam3 = []

job_tasks = []
thread_results = ""

# *******************************************************************************************************
# *******************************************************************************************************

# processJobFile- import and process the content of the job file

def processJobFile():

    global gJDir
    global gJobFile
    global gJParams
    global gJTasks
    global job_tasks

    try:

        # ***** Set full path with directory and file

        if (gJDir == "none"):
            load_file = "tasks." + gJobFile
        else:
            load_file = gJDir + "." + gJobFile

        # ***** Import job file

        load_mod = importlib.import_module(load_file)

        # ***** Parse out the task config- params

        if hasattr(load_mod, 'params'):
            gJParams = load_mod.params
        else:
            return "ERROR job file params not found: " + load_file

        if (gJParams[0] == "\n"):
            gJParams = gJParams[1:]
        if (len(gJParams) > 0):
            if (gJParams[-1] == "\n"):
                gJParams = gJParams[:-1]

        # ***** Parse out the task config- tasks

        if hasattr(load_mod, 'tasks'):
            gJTasks = load_mod.tasks
        else:
            return "ERROR job file tasks not found: " + load_file

        if (gJTasks[0] == "\n"):
            gJTasks = gJTasks[1:]
        if (len(gJTasks) > 0):
            if (gJTasks[-1] == "\n"):
                gJTasks = gJTasks[:-1]

        # ***** Parse out job params

        processParams('job',gJParams)

        # ***** Split tasks into lines and build array

        job_tasks = gJTasks.splitlines()

        # ================================================================
        # Return results

        retString = "Job file " + load_file + " loaded"
        return retString

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        return "ERROR processJobFile error: " + outerror

# *******************************************************************************************************

# processTaskFile- import and process content on the task file

def processParams(strType,strParams):

    global gJDir
    global gTDir

    global gJobFile
    global gJTarget
    global gJParfile
    global gJStartpar
    global gJThreads
    global gJParam1
    global gJParam2
    global gJParam3

    global gTaskFile
    global gTTarget
    global gTParfile
    global gTStartpar
    global gTThreads
    global gTParam1
    global gTParam2
    global gTParam3

    try:

        # ***** Remove os -- notation on parameters

        strParams = strParams + " "
        strParams.replace(" --"," ")
        pItems = strParams.split(" ")

        if(gJobFile != "none"):
            target = gJTarget
            parfile = gJParfile
            startpar = gJStartpar
            wthreads = gJThreads
            param1 = gJParam1
            param2 = gJParam2
            param3 = gJParam3
            wdir = gJDir

        if(gTaskFile != "none"):
            target = gTTarget
            parfile = gTParfile
            startpar = gTStartpar
            wthreads = gTThreads
            param1 = gTParam1
            param2 = gTParam2
            param3 = gTParam3
            wdir = gTDir

        for pItem in pItems:

            parValue = pItem.split("=")

            if (parValue[0] == "target"):
                target = parValue[1]
            elif (parValue[0] == "parfile"):
                parfile = parValue[1]
            elif (parValue[0] == "dir"):
                wdir = parValue[1]
            elif (parValue[0] == "startpar"):
                startpar = parValue[1]
            elif (parValue[0] == "threads"):
                wthreads = parValue[1]
            elif (parValue[0] == "param1"):
                param1 = parValue[1]
            elif (parValue[0] == "param2"):
                param2 = parValue[1]
            elif (parValue[0] == "param3"):
                param3 = parValue[1]

        # ***** Assign to job parameters if specified

        if (strType == "job"):

            gJTarget = target
            gJParfile = parfile
            gJDir = wdir
            gJParam1 = param1
            gJParam2 = param2
            gJParam3 = param3

            if startpar.isdigit() == True:
                gJStartpar = int(startpar)
            else:
                gJStartpar = 1

            if wthreads.isdigit() == True:
                gJThreads = int(wthreads)
            else:
                gJThreads = 1

        # ***** Assign to task parameters if specified

        if (strType == "task"):

            gTTarget = target
            gTParfile = parfile
            gTDir = wdir
            gTParam1 = param1
            gTParam2 = param2
            gTParam3 = param3

            startpar = str(startpar)
            wthreads = str(wthreads)

            if startpar.isdigit() == True:
                gTStartpar = int(startpar)
            else:
                gTStartpar = 1

            if wthreads.isdigit() == True:
                gTThreads = int(wthreads)
            else:
                gTThreads = 1

        # ================================================================
        # Return results

        return "Params processed"

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        return "ERROR processParams error: " + outerror

# *******************************************************************************************************

# processTaskFile- import and process content on the task file

def processTaskFile():

    global gTDir
    global gTaskFile
    global gTParams
    global gTCommand

    global gTTarget
    global gTParfile
    global gTParam1
    global gTParam2
    global gTParam3
    global gTStartpar
    global gTThreads
    global gTType

    global job_tasks
    global gTUsage

    try:

        # ***** Set full path with directory and file

        if (gJDir == "none"):
            load_file = "tasks." + gTaskFile
        else:
            load_file = gJDir + "." + gTaskFile

        # ***** Import job file

        load_mod = importlib.import_module(load_file)

        # ***** Parse out the task config- params

        if hasattr(load_mod, 'params'):
            gTParams = load_mod.params
        else:
            return "ERROR task file not found: " + load_file

        if (gTParams[0] == "\n"):
            gTParams = gTParams[1:]
        if (len(gTParams) > 0):
            if (gTParams[-1] == "\n"):
                gTParams = gTParams[:-1]

        # ***** Parse out the task config- tasks

        if hasattr(load_mod, 'command'):
            gTCommand = load_mod.command
        else:
            return "ERROR task file not found: " + load_file

        if (gTCommand[0] == "\n"):
            gTCommand = gTCommand[1:]
        if (len(gTCommand) > 0):
            if (gTCommand[-1] == "\n"):
                gTCommand = gTCommand[:-1]

        # ***** Parse out the task config- usage

        if hasattr(load_mod, 'usage'):
            gTUsage = load_mod.usage

        if (gTCommand[0] == "\n"):
            gTCommand = gTCommand[1:]
        if (len(gTCommand) > 0):
            if (gTCommand[-1] == "\n"):
                gTCommand = gTCommand[:-1]

        # ***** Parse out task params

        processParams('task', gTParams)

        # ***** Populate the job tasks array with 1 task

        job_tasks = []
        taskEntry = "dbtask task=" + gTaskFile + " "

        if (gTTarget != "none" and gTTarget != "prompt"):
            taskEntry += "target=" + gTTarget + " "

        if (gTDir != "none" and gTDir != "prompt"):
            taskEntry += "dir=" + gTDir + " "

        if (gTParfile != "none" and gTParfile != "prompt"):
            taskEntry += "parfile=" + gTParfile + " "

        if (gTParam1 != "none" and gTParam1 != "prompt"):
            taskEntry += "param1=" + gTParam1 + " "

        if (gTParam2 != "none" and gTParam2 != "prompt"):
            taskEntry += "param2=" + gTParam2 + " "

        if (gTParam3 != "none" and gTParam3 != "prompt"):
            taskEntry += "param3=" + gTParam3 + " "

        if (gTStartpar != 1):
            taskEntry += "startpar=" + str(gTStartpar) + " "

        if (gTThreads != 1):
            taskEntry += "threads=" + str(gTThreads) + " "

        # ***** Add output to tasks array, item 0

        job_tasks.append(taskEntry)

        # ================================================================
        # Return results

        retString = "Task file " + load_file + " loaded"
        return retString

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        return "ERROR processTaskFile error: " + outerror

# *******************************************************************************************************

# processParfile- import and process content for a parameter file

def processParfile(strType):

    global gJDir
    global gJParfile
    global gTParfile
    global gPParams
    global gPParlist
    global job_params
    global task_params

    try:

        load_file = "none"

        if (gTParfile != "none"):
            if (gTDir == "none"):
                load_file = "tasks." + gTParfile
            else:
                load_file = gTDir + "." + gTParfile

        if (gJParfile != "none"):
            if (gJDir == "none"):
                load_file = "tasks." + gJParfile
            else:
                load_file = gJDir + "." + gJParfile

        # ***** Import job file

        if (load_file != "none"):

            load_mod = importlib.import_module(load_file)

            # ***** Parse out the task config- params

            if hasattr(load_mod, 'params'):
                gPParams = load_mod.params
            else:
                return "ERROR parameter file not found: " + load_file

            if (gPParams[0] == "\n"):
                gPParams = gPParams[1:]
            if (len(gPParams) > 0):
                if (gPParams[-1] == "\n"):
                    gPParams = gPParams[:-1]

            # ***** Parse out the task config- tasks

            if hasattr(load_mod, 'parlist'):
                gPParlist = load_mod.parlist
            else:
                return "ERROR parameter file not found: " + load_file

            if (gPParlist[0] == "\n"):
                gPParlist = gPParlist[1:]
            if (len(gPParlist) > 0):
                if (gPParlist[-1] == "\n"):
                    gPParlist = gPParlist[:-1]

            # ***** Parse out job params

            processParams(strType, gPParams)

            # ***** Split parfile into lines and build array

            if (strType == "job"):
                job_params = gPParlist.splitlines()

            if (strType == "task"):
                task_params = gPParlist.splitlines()

        # ================================================================
        # Return results

        return "Processed Parameter File: " + load_file

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        return "ERROR processParfile error: " + outerror

# *******************************************************************************************************

# processParlist- parse out parameter list field

def processParlist():

    global gPParlist
    global gPParlist1
    global gPParlist2
    global gPParlist3

    try:

        if (len(gPParlist) > 0):

            gPParlist1 = []
            gPParlist2 = []
            gPParlist3 = []

            parlines = gPParlist.splitlines()

            for wline in parlines:

                witems = wline.split(" ")

                wlength = len(witems)

                if (wlength > 0):
                    gPParlist1.append(witems[0])

                if (wlength > 1):
                    gPParlist2.append(witems[1])

                if (wlength > 2):
                    gPParlist3.append(witems[2])

        # ================================================================
        # Return results

        return "Processed Parameter List"

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        return "ERROR processParlist error: " + outerror

# *******************************************************************************************************

def processCommandParam(intPar):

    global gTCommand
    global gModCommand

    global wparam1
    global wparam2
    global wparam3

    intPar = intPar - 1     # zero based arrays

    try:

        gModCommand = gTCommand

        par1lines = len(wparam1)
        par2lines = len(wparam2)
        par3lines = len(wparam3)

        if (par1lines > intPar):
            gModCommand = gModCommand.replace("<param1>", wparam1[intPar])
        elif (par1lines != 0):
            return "ERROR insufficient param1 entries to process param1 item " + str(intPar+1)

        if (par2lines > intPar):
            gModCommand = gModCommand.replace("<param2>", wparam2[intPar])
        elif (par2lines != 0):
            return "ERROR insufficient param1 entries to process param2 item " + str(intPar+ 1)

        if (par3lines > intPar):
            gModCommand = gModCommand.replace("<param3>", wparam3[intPar])
        elif (par3lines != 0):
            return "ERROR insufficient param3 entries to process param1 item " + str(intPar + 1)

        return "Command updated with parameters"

    except Exception as err2:

        return "ERROR processCommandParam: " + str(err2)

# *******************************************************************************************************

def startDbThread(thread_index,run_sql):

    global thread_results
    global gTTarget

    printAndLog("--> Starting thread:" + str(thread_index))

    dbutil.getDbConnection(gTTarget)
    results = dbutil.execSql(run_sql)

    thread_results += "--> Thread " + str(thread_index) + " : "
    thread_results += results + "\n"

# *******************************************************************************************************

def printAndLog(strEntry):

    global gLogFile

    if (gLogFile != "none"):

        out_file = gLogFile

        if len(out_file) > 0:
            f = open(out_file, 'a')
            f.write(strEntry + "\n")
            f.close()

    print(strEntry)

# *******************************************************************************************************

# processJobTasks- process the tasks in the task list

def processJobTasks():

    global job_tasks
    global thread_results
    global gData
    global gPParlist

    global gPParlist1
    global gPParlist2
    global gPParlist3

    global gJParlist1
    global gJParlist2
    global gJParlist3

    global gJTarget
    global gJParam1
    global gJParam2
    global gJParam3
    global gJParfile
    global gJThreads
    global gJStartpar

    global gTaskFile
    global gTCommand
    global gTTarget
    global gTParfile

    global wparam1
    global wparam2
    global wparam3

    try:

        status_ok = True
        wtarget = "none"

        wparam1 = []
        wparam2 = []
        wparam3 = []

        # Remove commented lines from list

        for index, wtaskline in reversed(list(enumerate(job_tasks))):

            if (wtaskline[0] == "#"):
                job_tasks.pop(index)

        # Process the job parameter list if applicable

        if (gJParfile != "none" and len(gPParlist) > 0):

            wOutput = processParlist()

            wparam1 = gPParlist1
            wparam2 = gPParlist2
            wparam3 = gPParlist3

            if (wOutput[0:5] == "ERROR"):
                status_ok = False
                printAndLog(wOutput)

        # Loop through job_tasks

        wnumtasks = len(job_tasks)

        outString = "Tasks to process: " + str(wnumtasks) + "\n"
        printAndLog(outString)
        outString = ""

        for item, wtaskline in enumerate(job_tasks):

            start_time = datetime.datetime.now()

            outString += "Processing task " + str(item+1) + ": " + wtaskline + "\n"
            outString += "--> Starting at: " + start_time.strftime("%b %d %Y %H:%M:%S") + "\n"

            # Load job parameters by default

            wstartpar = gJStartpar
            wthreads = gJThreads

            # If explicit job parameters specified, load them overriding any parlist

            if (gJTarget != "none"):
                wtarget = gJTarget

            if (gJParam1 != "none"):
                wparam1 = []
                wparam1.append(gJParam1)

            if (gJParam2 != "none"):
                wparam2 = []
                wparam2.append(gJParam2)

            if (gJParam3 != "none"):
                wparam3 = []
                wparam3.append(gJParam3)

            # Process job file task line parameters

            wOutput = processParams("task",wtaskline)

            if (wOutput[0:5] == "ERROR"):
                status_ok = False
                outString += wOutput

            # Parse out task line and update parameters

            wtask = ""
            wtype = "none"
            wparfile = ""

            wtaskline = wtaskline.replace(" --", " ")
            pItems = wtaskline.split(" ")

            for part in pItems:

                if (part == "dbtask"):
                    wtype = "db"
                else:

                    parValue = part.split("=")

                    # Update for any task parameters set on the job tasks line

                    if (parValue[0] == "target"):
                        wtarget = parValue[1]
                    elif (parValue[0] == "task"):
                        wtask = parValue[1]

                    elif (parValue[0] == "param1" and len(wparam1) > 0):
                        wparam1[0] = parValue[1]
                    elif (parValue[0] == "param1" and len(wparam1) == 0):
                        wparam1.append(parValue[1])

                    elif (parValue[0] == "param2" and len(wparam2) > 0):
                        wparam2[0] = parValue[1]
                    elif (parValue[0] == "param2" and len(wparam2) == 0):
                        wparam2.append(parValue[1])

                    elif (parValue[0] == "param3" and len(wparam3) > 0):
                        wparam3[0] = parValue[1]
                    elif (parValue[0] == "param3" and len(wparam3) == 0):
                        wparam3.append(parValue[1])

                    elif (parValue[0] == "parfile"):
                        gTParfile = parValue[1]
                    elif (parValue[0] == "startpar"):
                        wstartpar = parValue[1]
                    elif (parValue[0] == "threads"):
                        wthreads = parValue[1]

            # Process task file

            gTaskFile = wtask
            gTTarget = wtarget

            wOutput = processTaskFile()

            if (wOutput[0:5] == "ERROR"):
                status_ok = False
                outString += wOutput

            # Process parfile if set for task

            processParfile("task")
            gTParfile = "none"

            # Load task parlist items if applicable

            if (len(gPParlist) > 0):

                wOutput = processParlist()

                if (wOutput[0:5] == "ERROR"):
                    status_ok = False
                    outString += wOutput

                wparam1 = gPParlist1
                wparam2 = gPParlist2
                wparam3 = gPParlist3

            else:

                wstartpar = 1

            # Update command with parameters

            wstartpar = int(wstartpar)
            wthreads = int(wthreads)
            wOutput = processCommandParam(wstartpar)
            gPParlist = ""

            outString += "--> Starting parameter: " + str(wstartpar)

            if (wOutput[0:5] == "ERROR"):
                status_ok = False
                outString +=wOutput

            printAndLog(outString)
            outString = ""

            # *************************************************
            # single threaded task- connect to target

            if (status_ok == True and wthreads == 1):

                wOutput = dbutil.getDbConnection(wtarget)

                if (wOutput[0:5] == "ERROR"):
                    status_ok = False
                    outString += "--> ERROR connecting to alias " + wtarget + " (check db_config)\n"
                    outString += "--> " + wOutput
                else:
                    outString += "--> Connected to database " + wtarget + "\n"

            # *************************************************
            # single threaded task- execute SQL

            if (status_ok == True and wthreads == 1):

                wOutput = dbutil.execSql(gModCommand)

                if (wOutput[0:5] == "ERROR"):
                    status_ok = False
                    outString += "--> " + wOutput + "\n"
                else:
                    outString += "--> Result: " + wOutput + "\n"

            # *************************************************
            # spawn threads for multi-threaded task

            if (wthreads > 1 and status_ok == True):

                # Create/process threads for multi-threaded

                threads = []
                thread_results = ""

                first_param = wstartpar
                last_param = wstartpar + wthreads

                for index in range(first_param, last_param):
                    wpcp = processCommandParam(index)
                    if (wpcp[0:5] != "ERROR"):
                        t = threading.Thread(target=startDbThread, args=(index, gModCommand))
                        threads.append(t)
                        t.start()
                    else:
                        outString += "--> Insufficient parameters for thread " + str(index) + "\n"

                for t in threads:
                    t.join()

                outString += thread_results

            # *************************************************
            # End of task output

            end_time = datetime.datetime.now()

            diff_time = end_time - start_time
            diff_time = diff_time.total_seconds()

            diff_hours = int(diff_time / 3600)
            diff_time = diff_time - diff_hours * 3600
            diff_minutes = int(diff_time / 60)
            diff_time = diff_time - diff_minutes * 60
            diff_seconds = "{:2.3f}".format(diff_time)

            diff_string = str(diff_hours) + " hours "
            diff_string += str(diff_minutes) + " minutes "
            diff_string += str(diff_seconds) + " seconds"

            outString += "--> Ended at: " + end_time.strftime("%b %d %Y %H:%M:%S")
            outString += " (" + diff_string + ")\n"

            printAndLog(outString)
            outString = ""

            # *************************************************
            # Output and logging

            if (dbutil.getJsonData() != "{}"):
                gData += dbutil.getJsonData()

        # ================================================================
        # Return results

        return "Completed task processing"

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        printAndLog("ERROR processJobTasks error: " + outerror)
        return False

# *******************************************************************************************************





# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
