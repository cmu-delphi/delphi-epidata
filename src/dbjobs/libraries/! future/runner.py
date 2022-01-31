# ************************************************************************************
#
# Module:  runner.py
#
# Purpose: Executable to run job, task or batch based on parameters & config
#
# ************************************************************************************
# Imports

import osutil
import jobutil

import sys
import os

# ************************************************************************************
# ***** Set path to include current directory

sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/..')

# ************************************************************************************
# ***** Print heading, set status

print("**************************************************\n")
print("Run Job, Task or Batch\n")

status_ok = True

# ************************************************************************************
# ***** Process command line arguments & set jobutil parameters

osutil.processOsArgs(sys.argv)

# ************************************************************************************
# ***** If --prompt flag set, get job level information by prompting

if (osutil.prompt == True):

    osutil.promptBatch()
    osutil.promptDir()
    osutil.promptJob()
    osutil.promptTask()

# ************************************************************************************
# ***** If job is not none then process job file

if (osutil.job != "none"):
    osutil.processJobFile()

# ************************************************************************************
# ***** set parameters gathered on job into jobutil

jobutil.batch = osutil.batch
jobutil.dir = osutil.dir
jobutil.job = osutil.job
jobutil.task = osutil.task

jobutil.jtarget = osutil.target
jobutil.jparams = osutil.params
jobutil.jparam1 = osutil.param1
jobutil.jparam2 = osutil.param2
jobutil.jparam3 = osutil.param3
jobutil.jthreads = osutil.threads
jobutil.jstart = osutil.start

jobutil.job_tasks = osutil.job_tasks
jobutil.num_tasks = osutil.num_tasks

# ************************************************************************************
# ***** if --task option, set up for 1 task job using task file from --task

if (osutil.task != "none"):
    jobutil.job_tasks.append("['" + osutil.task + "']")
    jobutil.num_tasks = 1

# ************************************************************************************
# ***** prompt for parameters specified as prompt

if (jobutil.jtarget == "prompt"):
    osutil.promptTarget()
    jobutil.jtarget = osutil.target

if (jobutil.jparams == "prompt" or osutil.prompt):
    osutil.promptParams()
    jobutil.jparams = osutil.params

if (jobutil.jparam1 == "prompt" or osutil.prompt):
    osutil.promptParam1()
    jobutil.jparam1 = osutil.param1

if (jobutil.jparam2 == "prompt" or osutil.prompt):
    osutil.promptParam2()
    jobutil.jparam2 = osutil.param2

if (jobutil.jparam3 == "prompt" or osutil.prompt):
    osutil.promptParam3()
    jobutil.jparam3 = osutil.param3

if (jobutil.jthreads == "prompt" or osutil.prompt):
    osutil.promptThreads()
    jobutil.jthreads = osutil.threads

if (jobutil.jstart == "prompt" or osutil.prompt):
    osutil.promptStart()
    jobutil.jstart = osutil.start

# ************************************************************************************
# ***** If params is not none then process param file

if (osutil.params != "none"):
    osutil.processParameterFile()

# ************************************************************************************
# ***** Take actions based on parameters specified

print("\n**************************************************\n")

if (status_ok == True and jobutil.job != "none"):
    jobutil.processJob()
elif (status_ok == True and jobutil.task != "none"):
    jobutil.processTask()
elif (status_ok == True and jobutil.batch == True):
    print("--> Batch processing not yet implemented")
else:
    print("--> No work specified")



print("\n")
print("job: " + jobutil.job)
print("task: " + str(jobutil.task))
print("batch: " + str(jobutil.batch))
print("dir: " + str(jobutil.dir))
print("prompt: " + str(osutil.prompt))

print("jtarget: " + str(jobutil.jtarget))
print("jparams: " + str(jobutil.jparams))
print("jparam1: " + str(jobutil.jparam1))
print("jthreads: " + str(jobutil.jthreads))
print("jstart: " + str(jobutil.jstart))

print("target: " + jobutil.jtarget)
print("tasks: " + str(jobutil.num_tasks))
print("task 1:" + jobutil.job_tasks[0])

testlist = []
testlist = jobutil.job_tasks

print("task 1c:" + testlist[0])



print("\n**************************************************")


# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
