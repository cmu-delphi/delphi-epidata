#!/bin/sh
# ============================================================
# Script:  loadmigrate
# Purpose: Shell script to call the covidcast data migration job
# ============================================================

logfile="./log/loadmigrate.log"

echo " " | tee -a ${logfile}
echo "===========================================================" | tee -a ${logfile}
echo " "
echo "***** Migration Load *****" | tee -a  ${logfile}
echo " " | tee -a ${logfile}

# ============================================================

cd libraries
logfile="../log/loadmigrate.log"

date | tee -a  ${logfile}
echo " " | tee -a  ${logfile}
python3 runner.py --dir=epidata --job=migrate_j --target=main $1 $2 | tee -a  ${logfile}
echo " " | tee -a  ${logfile}
date | tee -a  ${logfile}
echo " " | tee -a  ${logfile}

cd ..

# ============================================================