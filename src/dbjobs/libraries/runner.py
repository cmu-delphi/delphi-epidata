# ************************************************************************************
#
# Module:  runner.py
# Purpose: Executable to run job, task or batch based on parameters & config
#
# ************************************************************************************
# Imports

import sys
import os
import argparse

# ************************************************************************************
# ***** Global variables

gStatus = "ok"
gMessage = ""

job = ""
task = ""
log = "none"
batch = False
prompt = ""

target = ""
directory = "tasks"
parfile = "none"
param1 = ""
param2 = ""
param3 = ""
startpar = "1"
threads = "1"

# ************************************************************************************
# ***** Set path to include current directory

sys.path.append(os.path.dirname(os.path.realpath(__file__)) )
addPath = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(addPath)
addPath = os.path.dirname(os.path.realpath(__file__)) + "delphi\\epidata\\dbjobs\\libraries"
sys.path.append(addPath)

import jobutil

# *******************************************************************************************************
# Process command line arguments

def processRunnerArgs():

    global batch
    global job
    global task
    global log
    global prompt

    global directory
    global target
    global parfile
    global param1
    global param2
    global param3
    global threads
    global startpar

    # ************************************************************************************

    try:

        parser = argparse.ArgumentParser(description='OS arguments')

        parser.add_argument('--batch', help='', action='store_true', required=False)
        parser.add_argument('--job', type=str, help='', default='none', required=False)
        parser.add_argument('--task', type=str, help='', default='none', required=False)
        parser.add_argument('--log', type=str, help='', default='none', required=False)
        parser.add_argument('--prompt', help='', action='store_true', required=False)

        parser.add_argument('--dir', type=str, help='', default='none', required=False)
        parser.add_argument('--target', type=str, help='', default='none', required=False)
        parser.add_argument('--parfile', type=str, help='', default='none', required=False)
        parser.add_argument('--param1', type=str, help='', default='none', required=False)
        parser.add_argument('--param2', type=str, help='', default='none', required=False)
        parser.add_argument('--param3', type=str, help='', default='none', required=False)
        parser.add_argument('--threads', type=str, help='', default="1", required=False)
        parser.add_argument('--start', type=str, help='', default="1", required=False)

        args = parser.parse_args()

        batch = args.batch
        job = args.job
        task = args.task
        log = args.log
        prompt = args.prompt

        directory = args.dir
        target = args.target
        parfile = args.parfile
        param1 = args.param1
        param2 = args.param2
        param3 = args.param3
        threads = args.threads
        startpar = args.start

        return True

    except Exception as err2:

        jobutil.printAndLog("processRunnerArgs error: " + str(err2))
        return False

# ************************************************************************************
# ***** Prompt user for string value

def promptUser(strPrompt):

    try:

        inString = input(strPrompt + ": ")
        if (inString == ""):
            inString = "none"

        return inString

    except Exception as err2:

        jobutil.printAndLog("promptUser error: " + str(err2))
        return "error"

# ************************************************************************************
# ***** Process command line arguments & set jobutil parameters

if (processRunnerArgs() == False):
    gStatus = "error"
    exit()

jobutil.gTaskFile = task
jobutil.gJobFile = job
jobutil.gLogFile = log

if(job != "none"):
    jobutil.gJParfile = parfile

if(task != "none"):
    jobutil.gTParfile = parfile

jobutil.gJDir = directory
jobutil.gJTarget = target
jobutil.gJParam1 = param1
jobutil.gJParam2 = param2
jobutil.gJParam3 = param3

if startpar.isdigit() == True:
    jobutil.gJStartpar = startpar
else:
    jobutil.printAndLog("Error- starting parameter must be integer")
    exit()

if threads.isdigit() == True:
    jobutil.gJThreads = threads
else:
    jobutil.printAndLog("Error- threads must be integer")
    exit()

# ************************************************************************************
# If prompt, prompt for control paramters and set remaining paramters to prompt

if (prompt == True):

    target = "prompt"
    param1 = "prompt"
    param2 = "prompt"
    param3 = "prompt"
    threads = "prompt"
    startpar = "prompt"

if (prompt == True or jobutil.gJDir == "prompt"):
    directory = promptUser("Sub-directory name (use . vs /, default is tasks dir)")
    jobutil.gJDir = directory

if ((prompt == True or jobutil.gJobFile == "prompt" or jobutil.gJobFile == "none") and jobutil.gTaskFile == "none"):
    job = promptUser("Job file name (in dir specified above)")
    jobutil.gJobFile = job

if ((prompt == True or jobutil.gTaskFile == "prompt" or jobutil.gTaskFile == "none") and jobutil.gJobFile == "none"):
    task = promptUser("Task file name (in dir specified above)")
    jobutil.gTaskFile = task

if (prompt == True or jobutil.gLogFile == "prompt"):
    logfile = promptUser("Log file name (adds .log to end)")
    jobutil.gLogFile = logfile

if (prompt == True or jobutil.gJParfile == "prompt"):
    parfile = promptUser("Parameter file name (in dir specified above)")
    jobutil.gJParfile = parfile

jobutil.printAndLog("")

# ************************************************************************************
# ***** Print heading, set status

jobutil.printAndLog("**************************************************\n")
jobutil.printAndLog("Run Job, Task or Batch\n")

# ************************************************************************************
# Process job file if specified

if (jobutil.gTaskFile == "none" and jobutil.gJobFile != "none" and gStatus == "ok"):

    result = jobutil.processJobFile()
    jobutil.printAndLog(result)

# ************************************************************************************
# Process the task file if specified to build a single task job

if (jobutil.gTaskFile != "none" and gStatus == "ok"):

    result = jobutil.processTaskFile()
    jobutil.printAndLog(str(result))

# ************************************************************************************
# Process the job parmeter file if specified for the job

if (jobutil.gJobFile != "none" and jobutil.gJParfile != "none" and gStatus == "ok"):
    result = jobutil.processParfile("job")
    jobutil.printAndLog("--> " + result)

if (jobutil.gTaskFile != "none" and jobutil.gTParfile != "none" and gStatus == "ok"):
    result = jobutil.processParfile("task")
    jobutil.printAndLog("--> " + result)

# ************************************************************************************
# Handle prompt settings for non-control job parameters

if (prompt == True or jobutil.gTParam1 == "prompt" or jobutil.gTParam2 == "prompt" or jobutil.gTParam3 == "prompt"):
    jobutil.printAndLog(jobutil.gTUsage)

# ***** Job settings *****

if ((jobutil.gJDir == "prompt") and job != "none"):
    inpar = promptUser("Sub-directory name (use . vs /)")
    jobutil.gJDir = inpar

if ((jobutil.gJTarget == "prompt") and job != "none"):
    inpar = promptUser("Target")
    jobutil.gJTarget = inpar

if ((jobutil.gJParfile == "prompt") and job != "none"):
    inpar = promptUser("Parameter file name (no /)")
    jobutil.gJParfile = inpar

if ((jobutil.gJParam1 == "prompt") and job != "none"):
    inpar = promptUser("Parameter 1")
    jobutil.gJParam1 = inpar

if ((jobutil.gJParam2 == "prompt") and job != "none"):
    inpar = promptUser("Parameter 2")
    jobutil.gJParam2 = inpar

if ((jobutil.gJParam3 == "prompt") and job != "none"):
    inpar = promptUser("Parameter 3")
    jobutil.gJParam3 = inpar

if ((jobutil.gJStartpar == "prompt") and job != "none"):
    inpar = promptUser("Starting parameter (integer)")
    jobutil.gJStartpar = inpar

if ((jobutil.gJThreads == "prompt") and job != "none"):
    inpar = promptUser("Threads (integer)")
    jobutil.gJThreads = inpar

# ***** Task settings *****

if ((jobutil.gTDir == "prompt") and task != "none"):
    inpar = promptUser("Sub-directory name (no /)")
    jobutil.gJDir = inpar

if ((jobutil.gTTarget == "prompt") and task != "none"):
    inpar = promptUser("Target")
    jobutil.gJTarget = inpar

if ((jobutil.gTParfile == "prompt") and task != "none"):
    inpar = promptUser("Parameter file name (no /)")
    jobutil.gTParfile = inpar

if ((jobutil.gTParam1 == "prompt") and task != "none"):
    inpar = promptUser("Parameter 1")
    jobutil.gJParam1 = inpar

if ((jobutil.gTParam2 == "prompt") and task != "none"):
    inpar = promptUser("Parameter 2")
    jobutil.gJParam2 = inpar

if ((jobutil.gTParam3 == "prompt") and task != "none"):
    inpar = promptUser("Parameter 3")
    jobutil.gJParam3 = inpar

if ((jobutil.gTStartpar == "prompt") and task != "none"):
    inpar = promptUser("Starting parameter (integer)")
    jobutil.gJStartpar = inpar

if ((jobutil.gTThreads == "prompt") and task != "none"):
    inpar = promptUser("Threads (integer)")
    jobutil.gJThreads = inpar

# ************************************************************************************
# Process the job tasks array (even if only 1 task)

if (gStatus == "ok"):

    result = jobutil.processJobTasks()

    rData = jobutil.gData
    rData = rData.replace("{[","[")
    rData = rData.replace("]}","]")

    if (len(rData) > 0):

        job_output = "Results:\n\n"
        job_output += rData
        job_output = job_output.replace("],[", "]\n[")
        jobutil.printAndLog(job_output)

# ************************************************************************************
# Final output

jobutil.printAndLog("\n**************************************************\n")

# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
