# *******************************************************************************************************
#
# Module:  jobutil.py
#
# Purpose: Utility functions to running batches, jobs and tasks
#
# *******************************************************************************************************
# Imports


# *******************************************************************************************************
# Global variables

batch = False
dir = "none"
job = "none"
task = "none"

jtarget = "prompt"
jparams = "none"
jparam1 = "none"
jparam2 = "none"
jparam3 = "none"
jthreads = 1
jstart = 1

job_tasks = []
num_tasks = 0

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
# *******************************************************************************************************
# processJob- main job processing engine

def processJob():

    global threads

    try:

        print("==> Processing Job")

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("processJob error: " + outerror)
        return False

# *******************************************************************************************************
# processTask- main task processing engine

def processTask():

    global threads

    try:

        print("==> Processing Task")

        # ================================================================
        # Return results

        return True

    # ================================================================
    # Exception handling

    except Exception as err2:

        outerror = str(err2)
        print("processTask error: " + outerror)
        return False

# *******************************************************************************************************

# *******************************************************************************************************
# *******************************************************************************************************
# End
# *******************************************************************************************************
