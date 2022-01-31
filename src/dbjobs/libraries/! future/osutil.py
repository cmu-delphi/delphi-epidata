# *******************************************************************************************************
#
# Module:  osutil.py
# Version: 7.1
#
# Purpose: Utility functions to work with the operating system
#
# *******************************************************************************************************
# Imports

import json
import argparse
import importlib

# *******************************************************************************************************
# Global variables






prompt = False
batch = False
dir = ""
job = ""
task = ""

target = ""
params = ""
param1 = ""
param2 = ""
param3 = ""
threads = 1
start = 1

job_tasks = []
num_tasks = 0

# *******************************************************************************************************
# *******************************************************************************************************
# *******************************************************************************************************
# processOsArgs- process command line arguments to see if they want to set things

def processOsArgsx(arguments):

    global num_args
    
    global batch
    global dir
    global job
    global task
    global prompt

    global target
    global params
    global param1
    global param2
    global param3
    global threads
    global start

    try:

        parser = argparse.ArgumentParser(description='OS arguments')

        parser.add_argument('--batch', help='', action='store_true', required=False)
        parser.add_argument('--dir', type=str, help='', default='none', required=False)
        parser.add_argument('--job', type=str, help='', default='none', required=False)
        parser.add_argument('--task', type=str, help='', default='none', required=False)
        parser.add_argument('--prompt', help='', action='store_true', required=False)

        parser.add_argument('--target', type=str, help='', default='prompt', required=False)
        parser.add_argument('--params', type=str, help='', default='none', required=False)
        parser.add_argument('--param1', type=str, help='', default='none', required=False)
        parser.add_argument('--param2', type=str, help='', default='none', required=False)
        parser.add_argument('--param3', type=str, help='', default='none', required=False)
        parser.add_argument('--threads', type=int, help='', default=1, required=False)
        parser.add_argument('--start', type=int, help='', default=1, required=False)

        args = parser.parse_args()

        batch=args.batch
        dir=args.dir
        job = args.job
        task = args.task
        prompt=args.prompt

        target=args.target
        params=args.params
        param1=args.param1
        param2=args.param2
        param3=args.param3
        threads=args.threads
        start=args.start

        num_args = len(arguments) - 1

        return True

    except Exception as err2:

        print("processOsArgs error: " + str(err2))
        return False

# *******************************************************************************************************
# processJobFile- processes the database job file

def processJobFilex():

    global job
    global dir

    global target
    global params
    global param1
    global param2
    global param3
    global threads
    global start

    global job_tasks
    global num_tasks

    try:

        print("==> Processing Job File")

        # ***** Read the job file

        job_file = "tools." + dir + "." + job

        # ***** Import task file

        job_config = importlib.import_module(job_file)

        # ***** Pull out the key variables

        testlist = json.loads(job_config.params)

        for tline in testlist:

            parvalue = tline.split("=")

            if (parvalue[0] == "target"):
                target = parvalue[1]
            elif (parvalue[0] == "params"):
                params = parvalue[1]
            elif (parvalue[0] == "param1"):
                param1 = parvalue[1]
            elif (parvalue[0] == "param2"):
                param2 = parvalue[1]
            elif (parvalue[0] == "param3"):
                param3 = parvalue[1]
            elif (parvalue[0] == "threads"):
                threads = parvalue[1]
            elif (parvalue[0] == "start"):
                start = parvalue[1]
            else:
                retString = "Error: parameter " + parvalue[1] + " not recognized in job file"
                print(retString)
                return retString

        if hasattr(job_config, 'tasks'):
            job_tasks = job_config.tasks.splitlines()
            print(job_tasks[0])
        else:
            retString = "ERROR job file has no tasks"
            print(retString)
            return retString

        job_tasks = job_tasks[1:]
        num_tasks = len(job_tasks)

        return ("Job file loaded")

    except Exception as err2:

        retString = "ERROR processJobFile: " + str(err2)
        print(retString)
        return retString

# *******************************************************************************************************
# processParamFile- processes the parameter file

def processParameterFilex():

    global job
    global dir


    try:

        # ***** Read the job file

        #job_file = "tools." + dir + "." + job

        # ***** Import task file

        #job_config = importlib.import_module(job_file)



        #if hasattr(job_config, 'tasks'):
        #    job_tasks = job_config.tasks.splitlines()
        #    print(job_tasks[0])
        #else:
        #    retString = "ERROR job file has no tasks"
        #    print(retString)
        #    return retString

        #job_tasks = job_tasks[1:]
        #num_tasks = len(job_tasks)

        print("==> Processing Parameter File")

        return ("Parameter file loaded")

    except Exception as err2:

        retString = "ERROR processParameterFile: " + str(err2)
        print(retString)
        return retString

# *******************************************************************************************************
# promptBatch- prompts at os level for the batch flag

def promptBatch():

    global batch

    try:

        batchin = input("Batch Flag (True or False, Default is False): ")
        if (batchin == "True" or batchin == "true"):
            batch = True
        else:
            batch = False

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptBatch error: " + outerror)
        return False

# *******************************************************************************************************
# promptDir- prompts at os level for the directory for job/task/parameter files

def promptDir():

    global dir

    try:

        dir = input("Job/Task/Param File Directory(relative to tools directory: ")
        if (dir == ""):
            dir = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptDir error: " + outerror)
        return False

# *******************************************************************************************************
# promptJob- prompts at os level for the job

def promptJob():

    global job

    try:

        job = input("Job File (<file in specified directory without .py extension>): ")
        if (job == ""):
            job = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptJob error: " + outerror)
        return False

# *******************************************************************************************************
# promptTask- prompts at os level for the task

def promptTask():

    global task

    try:

        task = input("Task File (<file in specified directory without .py extension>): ")
        if (task == ""):
            task = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptTask error: " + outerror)
        return False

# *******************************************************************************************************
# promptTarget- prompts at os level for the target

def promptTarget():

    global target

    try:

        target = input("Target: ")
        if (target == ""):
            target = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptTarget error: " + outerror)
        return False

# *******************************************************************************************************
# promptParams- prompts at os level for the parameter file

def promptParams():

    global params

    try:

        params = input("Parameters File (<file in specified directory without .py extension>): ")
        if (params == ""):
            params = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptParams error: " + outerror)
        return False

# *******************************************************************************************************
# promptParam1- prompts at os level for parameter 1

def promptParam1():

    global param1

    try:

        param1 = input("Parameter 1 value (return if using parameter file): ")
        if (param1 == ""):
            param1 = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptParam1 error: " + outerror)
        return False

# *******************************************************************************************************
# promptParam2- prompts at os level for parameter 2

def promptParam2():

    global param2

    try:

        param2 = input("Parameter 2 value (return if using parameter file): ")
        if (param2 == ""):
            param2 = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptParam2 error: " + outerror)
        return False

# *******************************************************************************************************
# promptParam3- prompts at os level for parameter 3

def promptParam3():

    global param3

    try:

        param3 = input("Parameter 3 value (return if using parameter file): ")
        if (param3 == ""):
            param3 = "none"

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptParam3 error: " + outerror)
        return False

# *******************************************************************************************************
# promptThreads- prompts at os level for number of threads

def promptThreads():

    global threads

    try:

        threads = input("Number of threads (integer, default 1): ")
        if (threads == ""):
            threads = 1

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptThreads error: " + outerror)
        return False

# *******************************************************************************************************
# promptStart- prompts at os level for starting parameter in list

def promptStart():

    global start

    try:

        start = input("Starting parameter (integer, default 1): ")
        if (start == ""):
            start = 1

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("promptStart error: " + outerror)
        return False

# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
