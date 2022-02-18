#!/bin/sh
# ============================================================
# Script:  loadschema
# Purpose: Shell script to call the signal_load job to process data from acquisition
# ============================================================

logfile="./log/loadschema.log"

echo " " | tee -a ${logfile}
echo "===========================================================" | tee -a ${logfile}
echo " "
echo "***** Schema Load *****" | tee -a  ${logfile}
echo " " | tee -a ${logfile}

# ============================================================

cd libraries
logfile="../log/loadschema.log"

date | tee -a  ${logfile}
echo " " | tee -a  ${logfile}
python3 runner.py --dir=epidata --job=signal_load_j --target=main | tee -a  ${logfile}
echo " " | tee -a  ${logfile}
date | tee -a  ${logfile}
echo " " | tee -a  ${logfile}

cd ..

# ============================================================